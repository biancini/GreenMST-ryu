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

"""
An OpenFlow 1.0 GreenMST loop free module.
"""

from ryu.base import app_manager
from simple_switch import SimpleSwitch
from topology_costs import TopologyCosts
from ryu.topology import event, switches
from ryu.controller.handler import set_ev_cls

class GreenMST(SimpleSwitch):
    _CONTEXTS = {
        'switches': switches.Switches,
    }

    def __init__(self, *args, **kwargs):
        super(GreenMST, self).__init__(*args, **kwargs)
        self.topo_costs = TopologyCosts()
        self.topo_edges = []

    def _link_with_cost(self, link):
        msg = link.to_dict()
        src = int(msg['src']['dpid'])
        dst = int(msg['dst']['dpid'])
        cost = self.topo_costs.get_cost(src, dst)
        return ((src, dst), cost)

    def _link_inverse(self, link):
        ((dst, src), cost) = link
        return ((src, dst), cost)

    @set_ev_cls(event.EventLinkAdd)
    def _event_link_add_handler(self, ev):
        link = self._link_with_cost(ev.link)
        if (link in self.topo_edges or self._link_inverse(link) in self.topo_edges): return

        self.topo_edges.append(link)
        self.logger.info('Link added: Link %s.', link)

    @set_ev_cls(event.EventLinkDelete)
    def _event_link_delete_handler(self, ev):
        link = self._link_with_cost(ev.link)
        removed = False

        if (link in self.topo_edges):
            self.topo_edges.remove(link)
            removed = True
        if (self._link_inverse(link) in self.topo_edges):
            self.topo_edges.remove(self._link_inverse(link))
            removed = True

        if removed:
            self.logger.info('Link removed: Link %s.', link)
