"""Main module of amlight/mef_eline Kytos Network Application.

NApp to provision circuits from user request
"""

from kytos.core import KytosNApp, log, rest
from flask import request, abort
from napps.amlight.mef_eline.models import NewCircuit, Endpoint, Circuit, Path, Tag
from napps.amlight.mef_eline.flowmanager import FlowManager
import json
import requests
import hashlib
from sortedcontainers import SortedDict

from . import settings
from .models import Endpoint


class Main(KytosNApp):
    """Main class of amlight/mef_eline_old NApp.

    This class is the entry point for this napp.
    """

    def setup(self):
        """Replace the '__init__' method for the KytosNApp subclass.

        The setup method is automatically called by the controller when your
        application is loaded.

        So, if you have any setup routine, insert it here.
        """
        self._scheduled_circuits = []
        self._installed_circuits = {'ids': SortedDict(), 'ports': SortedDict()}
        self._pathfinder_url = 'http://localhost:8181/api/kytos/pathfinder/v1/%s/%s'

        self.execute_as_loop(60)

    def execute(self):
        """This method is executed right after the setup method execution.

        You can also use this method in loop mode if you add to the above setup
        method a line like the following example:

            self.execute_as_loop(30)  # 30-second interval.
        """
        self._install_scheduled_circuit()

    def shutdown(self):
        """This method is executed when your napp is unloaded.

        If you have some cleanup procedure, insert it here.
        """
        pass

    def add_circuit(self, circuit):
        self._installed_circuits['ids'][circuit._id] = circuit
        for endpoint in circuit._path._endpoints:
            if self._installed_circuits['ports'].get('%s:%s' % (endpoint._dpid, endpoint._port)) is None:
                self._installed_circuits['ports']['%s:%s' % (endpoint._dpid, endpoint._port)] = []
            self._installed_circuits['ports']['%s:%s' % (endpoint._dpid, endpoint._port)].append(circuit._id)

    @rest('/circuit', methods=['POST'])
    def create_circuit(self):
        """
        Receive a user request to create a new circuit, find a path for the circuit,
        install the necessary flows and stores the information about it.
        :return: 
        """
        data = request.get_json()

        if NewCircuit.validate(data):
            uni_a = data['uni_a']
            uni_z = data['uni_z']
            url = self._pathfinder_url % ('%s:%s' % (uni_a['dpid'], uni_a['port']),
                                          '%s:%s' % (uni_z['dpid'], uni_z['port']))
            log.info("Pathfinder URL: %s" % url)
            r = requests.get(url)
            if r.status_code // 100 != 2:
                log.error('Pathfinder returned error code %s.' % r.status_code)
                return json.dumps(False)
            paths = r.json()['paths']
            if len(paths) < 1:
                log.error('Pathfinder returned no path.')
                return json.dumps(False)
            path = paths[0]['hops']
            endpoints = []
            m = hashlib.md5()
            m.update(uni_a['dpid'].encode('utf-8'))
            m.update(uni_a['port'].encode('utf-8'))
            m.update(uni_z['dpid'].encode('utf-8'))
            m.update(uni_z['port'].encode('utf-8'))
            for endpoint in path:
                dpid = endpoint[:23]
                if len(endpoint) > 23:
                    port = endpoint[24:]
                    if dpid == uni_a['dpid'] and port == uni_a['port']:
                            tag = Tag(uni_a['tag']['type'], uni_a['tag']['value'])
                    elif dpid == uni_z['dpid'] and port == uni_z['port']:
                        tag = Tag(uni_a['tag']['type'], uni_a['tag']['value'])
                    else:
                        tag = None
                    endpoints.append(Endpoint(dpid, port, tag))
            circuit = Circuit(m.hexdigest(), data['name'], Path(endpoints))
            self._scheduled_circuits.append(circuit)
        else:
            abort(400)
        return json.dumps(circuit._id), 200, {'Content-Type' : 'application/json; charset=utf-8'}

    @rest('/circuit/<circuit_id>', methods=['GET', 'POST', 'DELETE'])
    def circuit_operation(self, circuit_id):
        if request.method == 'GET':
            try:
                circuit = self._installed_circuits['ids'].get(circuit_id)
                return json.dumps(circuit.to_dict()), 200, {'Content-Type' : 'application/json; charset=utf-8'}
            except KeyError:
                abort(404)
        elif request.method == 'POST':
            try:
                circuit = self._installed_circuits['ids'].get(circuit_id)
                data = request.get_json()
                if Circuit.validate(data):
                    circuit._name = data['name']
                    endpoints = []
                    try:
                        for endpoint in data['path']['endpoints']:
                            dpid = endpoint['dpid']
                            port = endpoint['port']
                            endpoints.append(Endpoint(dpid, port))
                    except KeyError:
                        pass
                    circuit._path = Path(endpoints)
                    # Remove old circuit path from ports dict
                    for circuits in self._installed_circuits['ports'].values():
                        try:
                            circuits.remove(circuit_id)
                        except ValueError:
                            pass
                    self.add_circuit(circuit)
                else:
                    abort(400)
                return json.dumps(circuit_id), 200, {'Content-Type' : 'application/json; charset=utf-8'}
            except KeyError:
                abort(404)
        elif request.method == 'DELETE':
            circuit = self._installed_circuits['ids'].get(circuit_id)
            if circuit:
                # TODO: remove flows from switches
                del self._installed_circuits['ids'][circuit_id]
                for circuits in self._installed_circuits['ports'].values():
                    try:
                        circuits.remove(circuit_id)
                    except ValueError:
                        pass
                return json.dumps("Ok"), 200, {'Content-Type' : 'application/json; charset=utf-8'}
            else:
                abort(404)

    @rest('/circuits', methods=['GET'])
    def get_circuits(self):
        circuits = []
        for circuit in self._installed_circuits['ids'].values():
            circuits.append(circuit.to_dict())
        return json.dumps(circuits), 200, {'Content-Type' : 'application/json; charset=utf-8'}

    @rest('/circuits/byLink/<link_id>')
    def circuits_by_link(self, link_id):
        pass

    @rest('/circuits/byUNI/<dpid>/<port>')
    def circuits_by_uni(self, dpid, port):
        port = '%s:%s' % (dpid, port)
        circuits = []
        if not self._installed_circuits['ports'].get(port):
            abort(404)
        for circuit_id in self._installed_circuits['ports'][port]:
            circuit = self._installed_circuits['ids'].get(circuit_id)
            circuits.append(circuit.to_dict())
        return json.dumps(circuits), 200, {'Content-Type' : 'application/json; charset=utf-8'}

    @rest('/circuits/triggerinstall')
    def triggerinstall(self):
        self._install_scheduled_circuit()
        return json.dumps({"response": "OK"}), 200

    def _install_scheduled_circuit(self):
        # Install path flows from all scheduled circuits.
        # The method remove the circuit from the schedule list and try to install the flows.
        # In case of error, the circuit returns for the schedule list

        if len(self._scheduled_circuits):
            log.info('Installing %d circuits.' % len(self._scheduled_circuits))

        rollback_circuits = []
        for circuit in self._scheduled_circuits:
            try:
                # Remove circuit from scheduled circuits, so it will not be
                # installed more than once in case of timeout in any step
                self._scheduled_circuits.remove(circuit)

                # TODO check start date to install circuit
                # Install circuit flows
                self._install_circuit(circuit)
            except:
                # In case of error, save the circuit for later treatment
                self.rollback_circuits.append(circuit)

        # Register rollback circuits to scheduled circuits to try again
        self._scheduled_circuits.extend(rollback_circuits)

    def _install_circuit(self, circuit: Circuit):
        """Install the flows of a circuit path.
        Only the main path will be installed. The backup path will not be used here.

        Args:
            circuit (Circuit): Circuit with a path specified to be installed
        """

        # Save the circuit
        self.add_circuit(circuit)

        # Install the circuit path
        flowmanager = FlowManager(self.controller)
        flowmanager.install_circuit(circuit)
