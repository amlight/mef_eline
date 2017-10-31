"""
    Module to interact with Pathfinder Napp.
"""

import sys
import requests
import json
from kytos.core import log
from napps.kytos.of_core.flow import Flow

from . import settings


class FlowManager(object):

    def install_circuit(self, circuit):
        if circuit is not None and circuit.path is not None:
            endpoints = circuit.path._endpoints
            for i in range(len(endpoints) - 1):
                self.install_flow(endpoints[i], endpoints[i + 1])
        else:
            raise ValueError("Circuit is missing.")


    def install_flow(self, endpoint_a, endpoint_b):

        try:
            flow_manager_install_url = settings.FLOW_MANAGER_INSTALL_FLOW_URL.format(dpid=endpoint_a.dpid)
            flow = self._flow_body_generator(endpoint_a, endpoint_b)

            result = requests.post(flow_manager_install_url, json=[flow.as_dict()['flow']])

            log.debug(flow_manager_install_url)

            if result.status_code == 202:
                # Flow message sent
                return flow
            else:
                raise Exception(result.status_code)
        except:
            e = sys.exc_info()
            log.error('Error: Can not connect to Kytos/FlowManager: %s %s', e[0], e[1])




    def _flow_body_generator(self, endpoint_a, endpoint_b):
        if endpoint_a is None:
            raise ValueError("Endpoint A is missing.")
        if endpoint_b is None:
            raise ValueError("Endpoint Z is missing.")

        flow = Flow()

        #r = requests.post(self._flow_mgr_url % dpid, json=[flow.as_dict()['flow']])

        flow_dict = settings.flow_dict_v10  # Future expansion to OF1.3
        flow = Flow.from_dict(flow_dict)

        flow.match.in_port = endpoint_a.port
        flow.actions[0].value = endpoint_b.port

        # Setting vlan
        if endpoint_a.tag is not None and endpoint_a.tag.type == 'vlan':
            flow.match.dl_vlan = endpoint_a.tag.value
        # Setting vlan
        if endpoint_b.tag is not None and endpoint_b.tag.type == 'vlan':
            flow.match.dl_vlan = endpoint_a.tag.value

        return flow