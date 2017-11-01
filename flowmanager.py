"""
    Module to interact with Kytos FlowManager Napp.
"""
import requests
from http import HTTPStatus

from kytos.core import log
from napps.kytos.of_core.v0x01.flow import Flow

from napps.amlight.mef_eline import settings
from napps.amlight.mef_eline.models import Endpoint


class FlowManager(object):

    # Receive Kytos controller
    def __init__(self, controller):
        """
        Args:
            controller (Controller): Receive Kytos controller
        """
        self.controller = controller

    def install_circuit(self, circuit):
        if circuit is not None and circuit._path is not None:
            endpoints = circuit._path._endpoints
            for i in range(len(endpoints) - 1):
                if i%2 == 0:
                    self._install_flow(endpoints[i], endpoints[i + 1])
        else:
            raise ValueError("Circuit is missing.")


    def _install_flow(self, endpoint_a, endpoint_b):
        if endpoint_a is None:
            raise ValueError("Endpoint A is missing.")
        if endpoint_b is None:
            raise ValueError("Endpoint Z is missing.")

        # Build flow_manager URL
        flow_manager_install_url = settings.FLOW_MANAGER_INSTALL_FLOW_URL.format(dpid=endpoint_a._dpid)
        # Generate flow_manager request body
        flow = self._install_flow_req_body_generator(endpoint_a, endpoint_b)

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

        flow.match.in_port = endpoint_a._port
        flow.actions[0].value = endpoint_b._port
        flow.actions[0].port = endpoint_b._port

        # Setting endpoint A vlan
        if endpoint_a._tag is not None and endpoint_a._tag.type == 'vlan':
            flow.match.dl_vlan = endpoint_a._tag.value
        # Setting endpoint B vlan
        if endpoint_b._tag is not None and endpoint_b._tag.type == 'vlan':
            flow.match.dl_vlan = endpoint_b.tag.value

        return flow
