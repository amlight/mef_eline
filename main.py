"""Main module of amlight/mef_eline Kytos Network Application.

NApp to provision circuits from user request
"""

from kytos.core import KytosNApp, log, rest
from flask import request

from . import settings
from .models import Endpoint


class Main(KytosNApp):
    """Main class of amlight/mef_eline_old NApp.

    This class is the entry point for this napp.
    """
    def __init__(self):
        pass

    def setup(self):
        """Replace the '__init__' method for the KytosNApp subclass.

        The setup method is automatically called by the controller when your
        application is loaded.

        So, if you have any setup routine, insert it here.
        """
        pass

    def execute(self):
        """This method is executed right after the setup method execution.

        You can also use this method in loop mode if you add to the above setup
        method a line like the following example:

            self.execute_as_loop(30)  # 30-second interval.
        """
        pass

    def shutdown(self):
        """This method is executed when your napp is unloaded.

        If you have some cleanup procedure, insert it here.
        """
        pass

    @rest('/circuit', methods=['POST'])
    def create_circuit(self):
        pass

    @rest('/circuit/<circuit_id>', methods=['GET', 'POST', 'DELETE'])
    def circuit_operation(self, circuit_id):
        if request.method == 'GET':
            pass
        elif request.method == 'POST':
            pass
        elif request.method == 'DELETE':
            pass

    @rest('/circuits', methods=['GET'])
    def get_circuits(self):
        pass

    @rest('/circuits/byLink/<link_id>')
    def circuits_by_link(self, link_id):
        pass

    @rest('/circuits/byUNI/<dpid>/<port>')
    def circuits_by_uni(self, dpid, port):
        pass

#     def install_circuit_flows(self):
#         circuits = []
#
#         self.circuitManager.install_flows()
#
# #
# class CircuitManager():
#     def __init__(self):
#         self.circuits = []
#         self.id_counter = 0
#
#     def _new_circuit_id(self):
#         self.id_counter = self.id_counter + 1
#         return self.id_counter
#
#     def save_circuit(self, circuit):
#         if circuit is not None:
#             circuit_id = self._new_circuit_id()
#             self.circuits[circuit_id] = circuit
#
#     def retrieve_circuit(self, endpoint_a, endpoit_z):
#         for c in self.circuits:
#             for e in c.path._endpoints:
#                 e._dpid
#                 e._port
#         pass
#
#     def install_circuit_flows(self):
#
#         for circuit in self.circuits:
#             for link in circuit.links:
#                 link.endpoint_a
#                 link.endpoint_b
#
#                 _install_flow(link.endpoint_a, link.endpoint_b)
#
#
#     def _install_flow(self, endpoint_a, endpoit_z):
#
#         try:
#             flow_manager_install_url = settings.FLOW_MANAGER_INSTALL_FLOW_URL.format(dpid=endpoint_a.dpid)
#             result = requests.get(url=pathfinder_url)
#
#             log.debug(pathfinder_url)
#
#             if result.status_code == 200:
#                 result = json.loads(result.content)
#                 self._paths = result['paths']
#             else:
#                 raise Exception(result.status_code)
#         except:
#             e = sys.exc_info()
#             log.error('Error: Can not connect to Kytos/Pathfinder: %s %s', e[0], e[1])
#         endpoint_a
#         endpoint_a
#
#
#         result = requests.get(url=pathfinder_url)
