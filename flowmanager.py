"""
    Module to interact with Kytos FlowManager Napp.
"""
import requests
from http import HTTPStatus

from kytos.core import log
from kytos.core.switch import Switch
from kytos.core.controller import Controller
from napps.kytos.of_core.v0x01.flow import Flow

from napps.amlight.mef_eline import settings
from napps.amlight.mef_eline.models import Endpoint, Circuit


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
            #FIXME path should be an object
            #endpoints = circuit._path._endpoints
            endpoints = circuit._path
            for i in range(len(endpoints) - 1):
                if i%2 == 0:
                    self._install_flow(endpoints[i], endpoints[i + 1])
        else:
            raise ValueError("Circuit is missing.")


    def _install_flow(self, endpoint_a: Endpoint, endpoint_b: Endpoint):
        if endpoint_a is None:
            raise ValueError("Endpoint A is missing.")
        if endpoint_b is None:
            raise ValueError("Endpoint Z is missing.")

        # Build flow_manager URL
        flow_manager_install_url = settings.FLOW_MANAGER_INSTALL_FLOW_URL.format(dpid=endpoint_a._dpid)
        # Generate flow_manager request body
        flow: Flow = self._install_flow_req_body_generator(endpoint_a, endpoint_b)

        log.info("Installing flow: %s" % flow.as_dict())

        # Send request to flow_manager NAppp
        result = requests.post(flow_manager_install_url, json=[flow.as_dict()])

        if result.status_code == HTTPStatus.ACCEPTED:
            # Flow message sent
            return flow
        else:
            raise Exception(flow_manager_install_url + '\ncode: ' + str(result.status_code))


    def _install_flow_req_body_generator(self, endpoint_a: Endpoint, endpoint_b: Endpoint):
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
        if endpoint_a._tag is not None and endpoint_a._tag.type == 'vlan':
            flow.match.dl_vlan = endpoint_a._tag.value
        else:
            # vlan must be checked agains switch port
            flow.match.dl_vlan = self._generate_vlan(endpoint_a, endpoint_b)

        return flow

    def _generate_vlan(self, endpoint_a: Endpoint, endpoint_b: Endpoint):
        switch:Switch = self.controller.get_switch_by_dpid(endpoint_a._dpid)
        vlans = [100]
        for flow in switch.flows:
            if int(endpoint_a._port) == int(flow.match.in_port) and flow.match.dl_vlan is not None:
                vlans.append(flow.match.dl_vlan)

        vlan = max(vlans) + 1
        return vlan