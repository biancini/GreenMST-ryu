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

from topology_costs import TopologyCosts

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
        return 'Link (%s, %s) with cost: %s' % (self.src, self.dst, self.cost)

    def __unicode__(self):
        return u'Link (%s, %s) with cost: %s' % (self.src, self.dst, self.cost)

    def link_inverse(self):
        return Link(src=self.dst, dst=self.src, src_port=self.src_port, dst_port=self.dst_port, cost=self.cost)