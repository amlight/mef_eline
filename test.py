"""Test kytos.core.controller module."""
import json
import logging
import warnings
from copy import copy
from unittest import TestCase
from unittest.mock import Mock, patch

# from .main import CircuitManager
from .models import Endpoint
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
    def test_install_flow(self):
        flowmanager = FlowManager()

        endpoint_a = Endpoint()
        endpoint_b = Endpoint()

        flowmanager.install_flow(endpoint_a, endpoint_b)

        # TODO test
        self.fail()