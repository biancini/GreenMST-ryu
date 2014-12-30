# Copyright (C) 2014 Andrea Biancini <andrea.biancini@gmail.com>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Andrea Biancini <andrea.biancini@gmail.com>'

import random
from nose.tools import assert_equals, assert_true
from mock import Mock, call, patch
from link import Link
from controller import Controller
from simple_switch import SimpleSwitch
from topology_costs import TopologyCosts
from ryu.ofproto import ofproto_v1_0, ofproto_v1_0_parser, ether
from ryu.lib.packet.ethernet import ethernet
from ryu.lib.packet import bfd

def random_mac():
    mac = [0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    return mac

def verify_port_mod(msg, hw_addr, port_num, config):
    assert_equals(msg.hw_addr, hw_addr)
    assert_equals(msg.port_no, port_num)
    assert_equals(msg.mask, ofproto_v1_0.OFPPC_NO_FLOOD)
    assert_equals(msg.config, config)

def test_update_links():
    # arrange
    topo_edges = []
    topo_edges.append(Link(src=1, src_port=1, dst=2, dst_port=1, cost=1))
    topo_edges.append(Link(src=1, src_port=2, dst=3, dst_port=1, cost=4))
    topo_edges.append(Link(src=1, src_port=3, dst=4, dst_port=1, cost=2))
    topo_edges.append(Link(src=2, src_port=2, dst=3, dst_port=2, cost=3))
    topo_edges.append(Link(src=2, src_port=3, dst=4, dst_port=2, cost=4))
    topo_edges.append(Link(src=3, src_port=3, dst=4, dst_port=3, cost=1))

    redundant_expected = []
    redundant_expected.append(Link(src=1, src_port=2, dst=3, dst_port=1, cost=4))
    redundant_expected.append(Link(src=2, src_port=3, dst=4, dst_port=2, cost=4))
    redundant_expected.append(Link(src=2, src_port=2, dst=3, dst_port=2, cost=3))

    controller = Controller()
    controller.mod_port = Mock()

    mod_ports = []
    mod_ports.append(call(1, 2, False))
    mod_ports.append(call(2, 3, False))
    mod_ports.append(call(2, 2, False))
    mod_ports.append(call(3, 1, False))
    mod_ports.append(call(4, 2, False))
    mod_ports.append(call(3, 2, False))

    # act
    controller.topo_edges = topo_edges
    controller.update_links()
    result = controller.redundant_edges

    # assert
    assert_equals(len(redundant_expected), len(result))
    for expected_link in redundant_expected:
        assert_true(expected_link in result)

        for cur_link in result:
            if cur_link == expected_link:
                assert_equals(cur_link.cost, expected_link.cost)

    assert_equals(len(mod_ports), controller.mod_port.call_count)
    controller.mod_port.assert_has_calls(mod_ports, any_order=True)

def test_find_redundant_edges():
    # arrange
    topo_edges = []
    topo_edges.append(Link(src=1, src_port=1, dst=2, dst_port=1, cost=1))
    topo_edges.append(Link(src=1, src_port=2, dst=3, dst_port=1, cost=4))
    topo_edges.append(Link(src=1, src_port=3, dst=4, dst_port=1, cost=2))
    topo_edges.append(Link(src=2, src_port=2, dst=3, dst_port=2, cost=3))
    topo_edges.append(Link(src=2, src_port=3, dst=4, dst_port=2, cost=4))
    topo_edges.append(Link(src=3, src_port=3, dst=4, dst_port=3, cost=1))

    mst_edges = []
    mst_edges.append(Link(src=1, src_port=1, dst=2, dst_port=1, cost=1))
    mst_edges.append(Link(src=1, src_port=3, dst=4, dst_port=1, cost=2))
    mst_edges.append(Link(src=3, src_port=3, dst=4, dst_port=3, cost=1))

    redundant_expected = []
    redundant_expected.append(Link(src=1, src_port=2, dst=3, dst_port=1, cost=4))
    redundant_expected.append(Link(src=2, src_port=3, dst=4, dst_port=2, cost=4))
    redundant_expected.append(Link(src=2, src_port=2, dst=3, dst_port=2, cost=3))

    controller = Controller()

    # act
    controller.topo_edges = topo_edges
    result = controller.find_redundant_edges(mst_edges)

    # assert
    assert_equals(len(redundant_expected), len(result))
    for expected_link in redundant_expected:
        assert_true(expected_link in result)

        for cur_link in result:
            if cur_link == expected_link:
                assert_equals(cur_link.cost, expected_link.cost)

@patch('ryu.topology.api.get_switch')
def test_mod_port_open(mock_get_switch):
    # arrange
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)

    ports = []
    for i in range(4):
        port = Mock()
        port.hw_addr = random_mac()
        ports.append(port)

    switch = Mock(dp=mock_datapath, ports=ports)
    mock_get_switch.return_value = [switch]
    controller = Controller()

    # act
    controller.mod_port(1, 2, True)

    # assert
    assert_equals(1, mock_datapath.send_msg.call_count)
    verify_port_mod(mock_datapath.send_msg.call_args[0][0], ports[1].hw_addr, 2, 0)

@patch('ryu.topology.api.get_switch')
def test_mod_port_close(mock_get_switch):
    # arrange
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)

    ports = []
    for i in range(4):
        port = Mock()
        port.hw_addr = random_mac()
        ports.append(port)

    switch = Mock(dp=mock_datapath, ports=ports)
    mock_get_switch.return_value = [switch]
    controller = Controller()

    # act
    controller.mod_port(1, 2, False)

    # assert
    assert_equals(1, mock_datapath.send_msg.call_count)
    verify_port_mod(mock_datapath.send_msg.call_args[0][0], ports[1].hw_addr, 2, 63)

def test_event_link_add():
    # arrange
    link = Mock()
    link.to_dict.return_value = {'src': { 'dpid': 1, 'port_no': 1 }, 'dst': {'dpid': 2, 'port_no': 1 }}
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)

    event = Mock(link=link)

    controller = Controller()
    controller.update_links = Mock()

    # act
    controller._event_link_add_handler(event)

    # assert
    assert_equals([Link(src=1, src_port=1, dst=2, dst_port=1)], controller.topo_edges)
    assert_equals(1, controller.update_links.call_count)

def test_event_link_add_inverse():
    # arrange
    link = Mock()
    link.to_dict.return_value = {'src': { 'dpid': 1, 'port_no': 1 }, 'dst': {'dpid': 2, 'port_no': 1 }}
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)

    event = Mock(link=link)

    controller = Controller()
    controller.update_links = Mock()
    controller.topo_edges = [Link(src=2, src_port=1, dst=1, dst_port=1)]

    # act
    controller._event_link_add_handler(event)

    # assert
    assert_equals([Link(src=2, src_port=1, dst=1, dst_port=1)], controller.topo_edges)
    assert_equals(0, controller.update_links.call_count)

def test_event_link_delete():
    # arrange
    link = Mock()
    link.to_dict.return_value = {'src': { 'dpid': 1, 'port_no': 1 }, 'dst': {'dpid': 2, 'port_no': 1 }}
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)

    event = Mock(link=link)

    controller = Controller()
    controller.update_links = Mock()
    controller.topo_edges = [Link(src=1, src_port=1, dst=2, dst_port=1)]

    # act
    controller._event_link_delete_handler(event)

    # assert
    assert_equals([], controller.topo_edges)
    assert_equals(1, controller.update_links.call_count)

def test_event_link_delete_inverse():
    # arrange
    link = Mock()
    link.to_dict.return_value = {'src': { 'dpid': 1, 'port_no': 1 }, 'dst': {'dpid': 2, 'port_no': 1 }}
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)

    event = Mock(link=link)

    controller = Controller()
    controller.update_links = Mock()
    controller.topo_edges = [Link(src=2, src_port=1, dst=1, dst_port=1)]

    # act
    controller._event_link_delete_handler(event)

    # assert
    assert_equals([], controller.topo_edges)
    assert_equals(1, controller.update_links.call_count)

def test_event_link_delete_none():
    # arrange
    link = Mock()
    link.to_dict.return_value = {'src': { 'dpid': 1, 'port_no': 1 }, 'dst': {'dpid': 2, 'port_no': 1 }}
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)

    event = Mock(link=link)

    controller = Controller()
    controller.update_links = Mock()
    controller.topo_edges = [Link(src=1, src_port=2, dst=3, dst_port=1)]

    # act
    controller._event_link_delete_handler(event)

    # assert
    assert_equals([Link(src=1, src_port=2, dst=3, dst_port=1)], controller.topo_edges)
    assert_equals(0, controller.update_links.call_count)

def test_set_costs():
    # arrange
    costs = { '1,2': 10, '2,3': 5, '1,3': 1 }

    controller = Controller()
    controller.update_links = Mock()

    # act
    controller.set_costs(costs)

    # assert
    topo_costs = TopologyCosts()
    assert_equals(costs, topo_costs.costs)
    assert_equals(1, controller.update_links.call_count)

def test_set_cost():
    # arrange
    source = 1
    destination = 2
    cost = 10

    topo_costs = TopologyCosts()
    topo_costs.costs = {}

    # act
    topo_costs.set_cost(source, destination, cost)

    # assert
    assert_equals({'%s,%s' % (source,destination): cost}, topo_costs.costs)

def test_get_cost():
    # arrange
    source = 1
    destination = 2
    cost = 10

    topo_costs = TopologyCosts()
    topo_costs.costs = {'%s,%s' % (source,destination): cost}

    # act
    result = topo_costs.get_cost(source, destination)

    # assert
    assert_equals(result, cost)

def test_get_cost_default():
    # arrange
    source = 1
    destination = 2
    default_cost = 1

    topo_costs = TopologyCosts()
    topo_costs.costs = {}

    # act
    result = topo_costs.get_cost(source, destination)

    # assert
    assert_equals(result, default_cost)

def test_add_flow_singleport():
    # arrange
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)

    in_port = 1
    out_port = 3
    destination = 2
    actions = [ofproto_v1_0_parser.OFPActionOutput(out_port)]
    controller = SimpleSwitch()

    # act
    controller.add_flow(mock_datapath, in_port, destination, actions)

    # assert
    assert_equals(1, mock_datapath.send_msg.call_count)

    mod = mock_datapath.send_msg.call_args[0][0]
    assert_equals(in_port, mod.match.in_port)
    assert_equals(ofproto_v1_0.OFPFC_ADD, mod.command)
    assert_equals(0, mod.idle_timeout)
    assert_equals(0, mod.hard_timeout)
    assert_equals(ofproto_v1_0.OFP_DEFAULT_PRIORITY, mod.priority)
    assert_equals(1, len(mod.actions))
    assert_true(isinstance(mod.actions[0], ofproto_v1_0_parser.OFPActionOutput))
    assert_equals(out_port, mod.actions[0].port)

def test_add_flow_flood():
    # arrange
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)

    in_port = 1
    out_port = ofproto_v1_0.OFPP_FLOOD
    destination = 2
    actions = [ofproto_v1_0_parser.OFPActionOutput(out_port)]
    controller = SimpleSwitch()

    # act
    controller.add_flow(mock_datapath, in_port, destination, actions)

    # assert
    assert_equals(1, mock_datapath.send_msg.call_count)

    mod = mock_datapath.send_msg.call_args[0][0]
    assert_equals(in_port, mod.match.in_port)
    assert_equals(ofproto_v1_0.OFPFC_ADD, mod.command)
    assert_equals(0, mod.idle_timeout)
    assert_equals(0, mod.hard_timeout)
    assert_equals(ofproto_v1_0.OFP_DEFAULT_PRIORITY, mod.priority)
    assert_equals(1, len(mod.actions))
    assert_true(isinstance(mod.actions[0], ofproto_v1_0_parser.OFPActionOutput))
    assert_equals(out_port, mod.actions[0].port)

def test_packet_in_lldp():
    # arrange
    src = 'ff:00:00:00:00:01'
    dst = 'ff:00:00:00:00:02'
    packet = ethernet(src=src, dst=dst, ethertype=ether.ETH_TYPE_LLDP)
    mock_datapath = Mock(ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)
    message = Mock(datapath=mock_datapath, data=packet.serialize(None, None))
    event = Mock(msg=message)

    controller = SimpleSwitch()

    # act
    controller._packet_in_handler(event)

    # assert
    assert_equals(0, mock_datapath.send_msg.call_count)

def test_packet_in_flood():
    # arrange
    src = 'ff:00:00:00:00:01'
    dst = 'ff:00:00:00:00:02'
    in_port = 1
    out_port = ofproto_v1_0.OFPP_FLOOD
    packet = ethernet(src=src, dst=dst, ethertype=ether.ETH_TYPE_IP)
    mock_datapath = Mock(id=1, ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)
    message = Mock(datapath=mock_datapath, data=packet.serialize(None, None), in_port=in_port)
    event = Mock(msg=message)

    controller = SimpleSwitch()
    controller.add_flow = Mock()

    # act
    controller._packet_in_handler(event)

    # assert
    assert_true(1 in controller.mac_to_port)
    assert_equals({'ff:00:00:00:00:01': in_port}, controller.mac_to_port[1])

    assert_equals(0, controller.add_flow.call_count)
    assert_equals(1, mock_datapath.send_msg.call_count)

    mod = mock_datapath.send_msg.call_args[0][0]
    assert_equals(in_port, mod.in_port)
    assert_equals(1, len(mod.actions))
    assert_true(isinstance(mod.actions[0], ofproto_v1_0_parser.OFPActionOutput))
    assert_equals(out_port, mod.actions[0].port)

def test_packet_in_noflood():
    # arrange
    src = 'ff:00:00:00:00:01'
    dst = 'ff:00:00:00:00:02'
    in_port = 1
    out_port = 3
    packet = ethernet(src=src, dst=dst, ethertype=ether.ETH_TYPE_IP)
    mock_datapath = Mock(id=1, ofproto=ofproto_v1_0, ofproto_parser=ofproto_v1_0_parser)
    message = Mock(datapath=mock_datapath, data=packet.serialize(None, None), in_port=in_port)
    event = Mock(msg=message)

    controller = SimpleSwitch()
    controller.add_flow = Mock()
    controller.mac_to_port[1] = {'ff:00:00:00:00:02': out_port}

    # act
    controller._packet_in_handler(event)

    # assert
    assert_true(1 in controller.mac_to_port)
    assert_equals({'ff:00:00:00:00:01': in_port, 'ff:00:00:00:00:02': out_port}, controller.mac_to_port[1])

    assert_equals(1, controller.add_flow.call_count)
    assert_equals(mock_datapath, controller.add_flow.call_args[0][0])
    assert_equals(in_port, controller.add_flow.call_args[0][1])
    assert_equals(dst, controller.add_flow.call_args[0][2])
    assert_equals(1, len(controller.add_flow.call_args[0][3]))
    assert_equals(out_port, controller.add_flow.call_args[0][3][0].port)
    assert_equals(1, mock_datapath.send_msg.call_count)

    mod = mock_datapath.send_msg.call_args[0][0]
    assert_equals(in_port, mod.in_port)
    assert_equals(1, len(mod.actions))
    assert_true(isinstance(mod.actions[0], ofproto_v1_0_parser.OFPActionOutput))
    assert_equals(out_port, mod.actions[0].port)
