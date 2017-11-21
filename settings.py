# KYTOS Napps endpoints
# Pathfinder Napp endpoint
KYTOS_NAPP_SERVER = 'http://localhost:8181'

FLOW_MANAGER_INSTALL_FLOW_URL = KYTOS_NAPP_SERVER + '/api/kytos/flow_manager/v1/flows/{dpid}'

PATHFINDER_URL = \
    KYTOS_NAPP_SERVER + \
    '/api/kytos/pathfinder/v1/{dpid_a}:{port_a}/{dpid_z}:{port_z}'
INSTALL_INTERVAL = 40

# Flow template to use do call the flow manager
flow_dict_v10 = {'idle_timeout': 0, 'hard_timeout': 0, 'table_id': 0, 'buffer_id': None,
                 'in_port': 0, 'dl_src': '00:00:00:00:00:00', 'dl_dst': '00:00:00:00:00:00',
                 'dl_vlan': 0, 'dl_type': 0, 'nw_src': '0.0.0.0', 'nw_dst': '0.0.0.0',
                 'tp_src': 0, 'tp_dst': 0, 'priority': 0,
                 'actions': [{"action_type": "output", 'port': 1}]}
