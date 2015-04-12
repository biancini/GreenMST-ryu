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

from ryu.topology.api import get_switch
from topology_costs import TopologyCosts
import json

__author__ = 'Andrea Biancini <andrea.biancini@gmail.com>'

class Link():
    def __init__(self, src=None, dst=None, src_port=None, dst_port=None, link=None, cost=None):
        topo_costs = TopologyCosts()

        if link:
            msg = link.to_dict()
            self.src = int(msg['src']['dpid'])
            self.dst = int(msg['dst']['dpid'])
            self.src_port = int(msg['src']['port_no'])
            self.dst_port = int(msg['dst']['port_no'])
        else:
            topo_costs = TopologyCosts()
            self.src = src
            self.dst = dst
            self.src_port = src_port
            self.dst_port = dst_port

        self.cost = cost or topo_costs.get_cost(self.src, self.dst)

    def __str__(self):
        return 'Link (%s, %s) with cost: %s' % (self.src, self.dst, self.cost)

    def __repr__(self):
        return '<%s(src=%s, dst=%s, src_port=%s, dst_port=%s, cost=%s)>' % (self.__class__, self.src, self.dst, self.src_port, self.dst_port, self.cost)

    def __unicode__(self):
        return u'Link (%s, %s) with cost: %s' % (self.src, self.dst, self.cost)

    def __eq__(self, other):
        return self.src == other.src and self.dst == other.dst and self.src_port == other.src_port and self.dst_port == other.dst_port

    def link_inverse(self):
        return Link(src=self.dst, dst=self.src, src_port=self.src_port, dst_port=self.dst_port, cost=self.cost)

    @classmethod
    def to_hex_string(cls, val, pad_to=8):
        arr = str(hex(val))[2:]
        ret = ''
        # prepend the right number of leading zeros
        i = 0
        while i < (pad_to * 2 - len(arr)):
            ret += '0'
            if (i % 2) != 0:
                ret += ':'
            i = i+1

        for j in range(0, len(arr)):
            ret += arr[j]
            if (((i + j) % 2) != 0) and (j < (len(arr) - 1)):
                ret += ':'
        return ret;

    def to_json(self):
        return {
            'sourceSwitch': self.to_hex_string(self.src),
            'sourcePort': self.src_port,
            'destinationSwitch': self.to_hex_string(self.dst),
            'destinationPort': self.dst_port,
            'cost': self.cost
        }
