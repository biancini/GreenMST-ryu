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

import json
from nose.tools import assert_equals, assert_true, raises
from mock import Mock
from rest_api import ControllerWithRestAPI, GreenMSTAPIController
from encoder import LinkEncoder
from ..link import Link
from ..topology_costs import TopologyCosts

MAC_ADDRESS = '01:b5:87:3b:73:b1:de:cb'

def test_to_hex_string():
    # arrange
    link = Link(src=123153254236413643, src_port=1, dst=2, dst_port=1, cost=1)
 
    # act 
    result = link.to_hex_string(link.src)
 
    # assert
    expected = MAC_ADDRESS
    assert_equals(expected, result)

def test_link_to_json():
    # arrange
    link = Link(src=1, src_port=1, dst=2, dst_port=1, cost=1)
 
    # act 
    result = link.to_json()
 
    # assert
    curitem = { 'sourceSwitch': link.to_hex_string(link.src),
                'sourcePort': link.src_port,
                'cost': link.cost,
                'destinationSwitch': link.to_hex_string(link.dst),
                'destinationPort': link.dst_port }
    assert_equals(curitem, result)

def test_encoder_link():
    # arrange
    link = Link(src=1, src_port=1, dst=2, dst_port=1, cost=1)
    encoder = LinkEncoder()
 
    # act 
    result = encoder.default(link)
 
    # assert
    assert_equals(result, link.to_json())

@raises(TypeError)
def test_encoder_string():
    # arrange
    string = 'test string'
    encoder = LinkEncoder()
 
    # act 
    result = encoder.default(string)
 
    # assert

def test_list_topocosts():
    # arrange 
    costs = { '1,2': 10, '2,3': 5, '1,3': 1 } 
 
    apis = ControllerWithRestAPI()
    apis.set_costs(costs) 
    controller = GreenMSTAPIController(None, None, {'green_mst_api_app': apis }) 
 
    # act 
    result = controller.list_topocosts(None)
 
    # assert
    body = result.json
    assert_equals(200, result.status_code) 
    assert_equals('application/json', result.content_type)
    
    for key, val in costs.items():
        assert_true(key in body)
        assert_equals(val, body[key])

def test_set_topocosts_valid():
    # arrange 
    costs = [{"1,2": 10, "1,3": 40, "1,4": 20, "2,3": 30, "2,4": 10, "3,4": 40}]
 
    apis = ControllerWithRestAPI()
    apis.set_costs = Mock()
    controller = GreenMSTAPIController(None, None, {'green_mst_api_app': apis })
    req = Mock(body=json.dumps(costs))
 
    # act 
    result = controller.set_topocosts(req)
 
    # assert
    body = result.json
    assert_equals(200, result.status_code) 
    assert_equals('application/json', result.content_type)
    assert_equals('new topology costs set', body['status'])

    assert_equals(1, apis.set_costs.call_count)
    assert_equals(costs, apis.set_costs.call_args[0][0])

def test_set_topocosts_invalid():
    # arrange 
    costs = 'invalid input'
 
    apis = ControllerWithRestAPI()
    apis.set_costs = Mock()
    controller = GreenMSTAPIController(None, None, {'green_mst_api_app': apis })
    req = Mock(body=json.dumps(costs))
 
    # act 
    result = controller.set_topocosts(req)
 
    # assert
    body = result.json
    assert_equals(200, result.status_code) 
    assert_equals('application/json', result.content_type)
    assert_equals('Error! Could not parse new topology costs, see log for details.', body['status'])

    assert_equals(0, apis.set_costs.call_count)

def test_list_mstedges():
    # arrange
    mst_edges = []
    mst_edges.append(Link(src=1, src_port=1, dst=2, dst_port=1, cost=1))
    mst_edges.append(Link(src=1, src_port=3, dst=4, dst_port=1, cost=2))
    mst_edges.append(Link(src=3, src_port=3, dst=4, dst_port=3, cost=1))
 
    apis = ControllerWithRestAPI()
    apis.mst_edges = mst_edges
    controller = GreenMSTAPIController(None, None, {'green_mst_api_app': apis }) 
 
    # act 
    result = controller.list_mstedges(None)
 
    # assert
    body = result.json
    assert_equals(200, result.status_code) 
    assert_equals('application/json', result.content_type)
    
    assert_equals(len(mst_edges), len(body))
    for curlink in mst_edges:
        curitem = { 'sourceSwitch': curlink.to_hex_string(curlink.src),
                    'sourcePort': curlink.src_port,
                    'cost': curlink.cost,
                    'destinationSwitch': curlink.to_hex_string(curlink.dst),
                    'destinationPort': curlink.dst_port }
        curitem_rev = { 'sourceSwitch': curlink.to_hex_string(curlink.dst),
                        'sourcePort': curlink.dst_port,
                        'destinationSwitch': curlink.to_hex_string(curlink.src),
                        'destinationPort': curlink.src_port, 
                        'cost': curlink.cost }
        assert_true(curitem in body or curitem_rev in body)

def test_list_topoedges():
    # arrange
    topo_edges = []
    topo_edges.append(Link(src=1, src_port=1, dst=2, dst_port=1, cost=1))
    topo_edges.append(Link(src=1, src_port=2, dst=3, dst_port=1, cost=4))
    topo_edges.append(Link(src=1, src_port=3, dst=4, dst_port=1, cost=2))
    topo_edges.append(Link(src=2, src_port=2, dst=3, dst_port=2, cost=3))
    topo_edges.append(Link(src=2, src_port=3, dst=4, dst_port=2, cost=4))
    topo_edges.append(Link(src=3, src_port=3, dst=4, dst_port=3, cost=1))
 
    apis = ControllerWithRestAPI()
    apis.topo_edges = topo_edges
    controller = GreenMSTAPIController(None, None, {'green_mst_api_app': apis }) 
 
    # act 
    result = controller.list_topoedges(None)
 
    # assert
    body = result.json
    assert_equals(200, result.status_code) 
    assert_equals('application/json', result.content_type)
    
    assert_equals(len(topo_edges), len(body))
    for curlink in topo_edges:
        curitem = { 'sourceSwitch': curlink.to_hex_string(curlink.src),
                    'sourcePort': curlink.src_port,
                    'cost': curlink.cost,
                    'destinationSwitch': curlink.to_hex_string(curlink.dst),
                    'destinationPort': curlink.dst_port }
        curitem_rev = { 'sourceSwitch': curlink.to_hex_string(curlink.dst),
                        'sourcePort': curlink.dst_port,
                        'destinationSwitch': curlink.to_hex_string(curlink.src),
                        'destinationPort': curlink.src_port, 
                        'cost': curlink.cost }
        assert_true(curitem in body or curitem_rev in body)

def test_list_redundant_edges():
    # arrange
    redundant_edges = []
    redundant_edges.append(Link(src=1, src_port=2, dst=3, dst_port=1, cost=4))
    redundant_edges.append(Link(src=2, src_port=3, dst=4, dst_port=2, cost=4))
    redundant_edges.append(Link(src=2, src_port=2, dst=3, dst_port=2, cost=3))
 
    apis = ControllerWithRestAPI()
    apis.redundant_edges = redundant_edges
    controller = GreenMSTAPIController(None, None, {'green_mst_api_app': apis }) 
 
    # act 
    result = controller.list_redundant_edges(None)
 
    # assert
    body = result.json
    assert_equals(200, result.status_code) 
    assert_equals('application/json', result.content_type)
    
    assert_equals(len(redundant_edges), len(body))
    for curlink in redundant_edges:
        curitem = { 'sourceSwitch': curlink.to_hex_string(curlink.src),
                    'sourcePort': curlink.src_port,
                    'cost': curlink.cost,
                    'destinationSwitch': curlink.to_hex_string(curlink.dst),
                    'destinationPort': curlink.dst_port }
        curitem_rev = { 'sourceSwitch': curlink.to_hex_string(curlink.dst),
                        'sourcePort': curlink.dst_port,
                        'destinationSwitch': curlink.to_hex_string(curlink.src),
                        'destinationPort': curlink.src_port, 
                        'cost': curlink.cost }
        assert_true(curitem in body or curitem_rev in body)
