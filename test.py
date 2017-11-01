"""Test kytos.core.controller module."""
import json
import logging
import warnings
from copy import copy
from unittest import TestCase
from unittest.mock import Mock, patch
from unittest.mock import MagicMock

from kytos.core.controller import Controller
from kytos.core.switch import Switch

# from .main import CircuitManager
from napps.amlight.mef_eline.models import Endpoint, Circuit, Path
# from .pathfinder import Pathfinder
from .flowmanager import FlowManager

#
#
# class TestCircuitManager(TestCase):
#
#     def test_circuit(self):
#         circuitManager = CircuitManager()
#         _id = circuitManager._new_circuit_id()
#         self.assertEqual(1, _id)
#
#         for num in range(2, 10):
#             _id = circuitManager._new_circuit_id()
#             self.assertEqual(num, _id)
#
#
# class TestPathfinder(TestCase):
#     def test_get_paths(self):
#         pathfinder = Pathfinder()
#         endpoint_a = '00:00:00:00:00:00:00:01:1'
#         endpoint_b = '00:00:00:00:00:00:00:02:1'
#
#         pathfinder._get_paths(endpoint_a, endpoint_b)
#
#         for h in pathfinder._paths:
#             self.assertEqual(h['hops'][0], '00:00:00:00:00:00:00:01:1')
#             self.assertEqual(h['hops'][ len(h['hops'])-1 ], '00:00:00:00:00:00:00:02:1')



class TestFlowManager(TestCase):
    # def test_install_flow(self):
    #     def get_switch_by_dpid(*args, **kwargs):
    #         return Switch('00:00:00:00:00:00:00:01')
    #
    #     c = Controller()
    #     c.get_switch_by_dpid = get_switch_by_dpid
    #
    #     flowmanager = FlowManager(c)
    #
    #     endpoint_a = Endpoint('00:00:00:00:00:00:00:01', 3)
    #     endpoint_b = Endpoint('00:00:00:00:00:00:00:01', 4)
    #
    #     flow = flowmanager.install_flow(endpoint_a, endpoint_b)
    #
    #     self.assertIsNotNone(flow)


    def test_install_circuit(self):
        print ('test_install_circuit')
        def get_switch_by_dpid(*args, **kwargs):
            return Switch(args[0])

        c = Controller()
        c.get_switch_by_dpid = get_switch_by_dpid

        flowmanager = FlowManager(c)

        endpoint_a = Endpoint('00:00:00:00:00:00:00:01', 1)
        endpoint_b = Endpoint('00:00:00:00:00:00:00:01', 2)
        endpoint_c = Endpoint('00:00:00:00:00:00:00:02', 1)
        endpoint_d = Endpoint('00:00:00:00:00:00:00:02', 2)
        endpoint_e = Endpoint('00:00:00:00:00:00:00:04', 1)
        endpoint_f = Endpoint('00:00:00:00:00:00:00:04', 2)

        path = Path()
        path._endpoints = [endpoint_a, endpoint_b, endpoint_c, endpoint_d, endpoint_e, endpoint_f]

        circuit = Circuit(0, 'circuitA', path)

        flow = flowmanager.install_circuit(circuit)

        self.assertIsNotNone(flow)

