"""
    Module to interact with Kytos FlowManager Napp.
"""
import requests
from http import HTTPStatus

from kytos.core import log
from kytos.core.switch import Switch
from kytos.core.controller import Controller
from napps.kytos.of_core.flow import ActionFactoryBase
from napps.kytos.of_core.v0x01.flow import Flow, ActionSetVlan

from napps.amlight.mef_eline import settings
from napps.amlight.mef_eline.models import Endpoint, Circuit, Link, Tag


class FlowManager(object):

    # Receive Kytos controller
    def __init__(self, controller: Controller):
        """
        Args:
            controller (Controller): Receive Kytos controller
        """
        self.controller: Controller = controller

    def install_circuit(self, circuit: Circuit):
        if circuit is not None and circuit._path is not None:
            log.info('Installing 2')

            # Translate all vlans through the path
            self._vlan_translation(circuit)
            # FIXME path should be an object
            endpoints = circuit._path._endpoints
            #endpoints = circuit._path
            for i in range(len(endpoints) - 1):
                # install flows using pairs of endpoints
                if i % 2 == 0:
                    self._install_flow(endpoints[i], endpoints[i + 1])
        else:
            raise ValueError("Circuit is missing.")

    def _vlan_translation(self, circuit: Circuit):
        """Translate all vlans through the circuit path."""
        if circuit is not None and circuit._path is not None:
            # FIXME path should be an object
            # endpoints = circuit._path._endpoints
            client_vlan = None
            endpoints = circuit._path._endpoints
            for i, endpoint in enumerate(endpoints):
                log.info('Installing 3 %s' % endpoint._dpid)
                # save client vlan
                if i == 0 and endpoint._tag is not None:
                    client_vlan = endpoint._tag._value

                # Translate vlans between nodes
                if i % 2 != 0 and i < len(endpoints) - 2:
                    link = Link()
                    link._endpoint_a = endpoints[i]
                    link._endpoint_b = endpoints[i+1]
                    self._generate_link_vlan(link, client_vlan)

                # install client vlan in the the last link
                if i == len(endpoints) - 2:
                    # if last endpoint has a vlan defined, we leave it alone,
                    # otherwise we set the initial vlan
                    if endpoints[i + 1]._tag is not None \
                            and endpoints[i + 1]._tag._type == 'ctag' \
                            and endpoints[i + 1]._tag._value is not None:
                        pass
                    else:
                        self._set_endpoint_vlan(endpoints[i+1], client_vlan)
        else:
            raise ValueError("Circuit is missing.")

    def _install_flow(self, endpoint_a: Endpoint, endpoint_b: Endpoint):
        """Install flow between two endpoints.
        The method call a install flow REST request."""
        if endpoint_a is None:
            raise ValueError("Endpoint A is missing.")
        if endpoint_b is None:
            raise ValueError("Endpoint Z is missing.")

        # Build flow_manager URL
        flow_manager_install_url = settings.FLOW_MANAGER_INSTALL_FLOW_URL.format(dpid=endpoint_a._dpid)
        # Generate flow_manager request body
        flow: Flow = self._generate_install_flow_req_body(endpoint_a, endpoint_b)

        log.info("Installing flow: %s" % flow.as_dict())

        # Send request to flow_manager NAppp
        result = requests.post(flow_manager_install_url, json=[flow.as_dict()])

        if result.status_code == HTTPStatus.ACCEPTED or result.status_code == HTTPStatus.OK:
            # Flow message sent
            return flow
        else:
            raise Exception(flow_manager_install_url + '\ncode: ' + str(result.status_code))

    def _generate_install_flow_req_body(self, endpoint_a: Endpoint, endpoint_b: Endpoint):
        """Generate a Flow object to be uses as a body to the install flow request."""
        if endpoint_a is None:
            raise ValueError("Endpoint A is missing.")
        if endpoint_b is None:
            raise ValueError("Endpoint Z is missing.")

        # Build a basic flow from settings template
        flow_dict = settings.flow_dict_v10  # Future expansion to OF1.3

        # Change flow values to match endpoint A to output to endpoint B
        flow = Flow.from_dict(flow_dict, self.controller.get_switch_by_dpid(endpoint_a._dpid))

        flow.match.in_port = int(endpoint_a._port)
        flow.actions[0].value = int(endpoint_b._port)
        flow.actions[0].port = int(endpoint_b._port)

        # Setting endpoint A vlan
        if endpoint_a._tag is not None and endpoint_a._tag._type == 'ctag':
            flow.match.dl_vlan = int(endpoint_a._tag._value)

        # Setting endpoint B vlan
        if endpoint_b._tag is not None and endpoint_b._tag._type == 'ctag':
            action = ActionSetVlan(int(endpoint_b._tag._value))
            flow.actions.append(action)

        return flow

    def _generate_link_vlan(self, link: Link, default_vlan = 0):
        """Generate the vlan between a link
        It is not guarantee that the
        value will be used. If the value is already in use
        by the port we generate a new vlan value.

        Args:
            link (Link): link with two endpoints to install the vlan
            default_vlan: default vlan to check.
        """
        vlans = []
        log.info('Installing 4 %s' % default_vlan)
        endpoint_a: Endpoint = link._endpoint_a
        endpoint_b: Endpoint = link._endpoint_b

        # Find all vlans installed between the nodes
        vlans.extend(self._find_switch_vlans(endpoint_a))
        vlans.extend(self._find_switch_vlans(endpoint_b))

        log.info('VLANs %s' % vlans)

        # Find the min vlan value, or 100 to use as a base to
        # create a new vlan
        if default_vlan is not None:
            initial_vlan = int(default_vlan)
        else:
            if len(vlans) > 0:
                initial_vlan = min(vlans)
            else:
                initial_vlan = 100

        result_vlan = initial_vlan

        if len(vlans) > 0:
            # Find a vlan value
            vlan_counter = initial_vlan

            while vlan_counter in vlans:
                vlan_counter += 1
            result_vlan = vlan_counter

        log.info('Result vlan %s' % result_vlan)
        # Set the vlan value to the endpoints
        if result_vlan is not None:
            self._set_endpoint_vlan(endpoint_a, result_vlan)
            self._set_endpoint_vlan(endpoint_b, result_vlan)

        return result_vlan

    def _find_switch_vlans(self, endpoint: Endpoint):
        """Find the vlans configured to the endpoint (dpid/port)"""
        vlans = []
        switch: Switch = self.controller.get_switch_by_dpid(endpoint._dpid)

        for flow in switch.flows:
            if int(endpoint._port) == int(flow.match.in_port) and flow.match.dl_vlan is not None:
                vlans.append(int(flow.match.dl_vlan))

        return vlans

    def _set_endpoint_vlan(self, endpoint: Endpoint, vlan):
        """Set a vlan value to an endpoint object"""
        log.info('Installing 6 %s' %  vlan)
        if vlan is not None:
            if endpoint._tag is None:
                endpoint._tag = Tag('ctag', vlan)
            else:
                endpoint._tag._type = 'ctag'
                endpoint._tag._value = vlan
