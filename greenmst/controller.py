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
from iotop import data

__author__ = 'Andrea Biancini <andrea.biancini@gmail.com>'

from ryu.topology import event, switches
from ryu.controller.handler import set_ev_cls
from ryu.topology.api import get_switch

from greenmst.simple_switch import SimpleSwitch
from link import Link

class Controller(SimpleSwitch):
    _CONTEXTS = {
        'switches': switches.Switches,
    }

    close_port = False

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.topo_edges = []
        self.redundant_edges = []
        self.mst_edges = []

    @set_ev_cls(event.EventLinkAdd)
    def _event_link_add_handler(self, ev):
        link = Link(link=ev.link)
        if (link in self.topo_edges or link.link_inverse() in self.topo_edges): return

        self.topo_edges.append(link)
        self.logger.debug('Link added: %s.', link)
        self.update_links()

    @set_ev_cls(event.EventLinkDelete)
    def _event_link_delete_handler(self, ev):
        link = Link(link=ev.link)
        removed = False

        if (link in self.topo_edges):
            self.topo_edges.remove(link)
            removed = True
        if (link.link_inverse() in self.topo_edges):
            self.topo_edges.remove(link.link_inverse())
            removed = True

        if removed:
            self.logger.debug('Link removed: %s.', link)
            self.update_links()

    def update_links(self):
        self.logger.debug('Updating MST because of topology change...')
        old_redundant_edges = self.redundant_edges

        from algorithm import kruskal as algorithm
        self.mst_edges = algorithm.perform(self.topo_edges)
        self.logger.debug('mstEdges = %s', self.mst_edges)

        new_redundant_edges = self.find_redundant_edges(self.mst_edges)
        self.logger.debug('newRedundantEdges = %s.', new_redundant_edges)

        if len(new_redundant_edges) == 0: return

        # Close edges in redundantEdges
        for edge in new_redundant_edges:
            if not edge in old_redundant_edges:
                self.logger.debug('Closing edge %s.', edge)
                self.mod_port(edge.src, edge.src_port, False)
                self.mod_port(edge.dst, edge.dst_port, False)

        # Re-open ports in MSP which were closed in previous iterations
        # (ie edges in the redundantEdges, from previous execution, and not in the current execution)
        for edge in old_redundant_edges:
            if not edge in new_redundant_edges:
                self.logger.debug('Opening edge %s.', edge)
                self.mod_port(edge.src, edge.src_port, True)
                self.mod_port(edge.dst, edge.dst_port, True)

        # Clone redundantEdges in redundantEdges for future iterations
        self.redundant_edges = new_redundant_edges

        self.logger.debug('New topoEdges = %s.', self.topo_edges)
        self.logger.debug('New redundantEdges = %s.', self.redundant_edges)

    def find_redundant_edges(self, mst_edges):
        redundant_edges = []

        for topo_edge in self.topo_edges:
            if topo_edge not in mst_edges and topo_edge.link_inverse() not in mst_edges:
                redundant_edges.append(topo_edge)

        return redundant_edges

    def mod_port(self, switch_id, port_num, open):
        switch = get_switch(self, switch_id)[0]
        datapath = switch.dp
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        hw_addr = switch.ports[port_num-1].hw_addr
        config = 0 if (open) else 63
        mask = ofp.OFPPC_PORT_DOWN if self.close_port else ofp.OFPPC_NO_FLOOD
        advertise = (ofp.OFPPF_10MB_HD | ofp.OFPPF_100MB_FD |
                     ofp.OFPPF_1GB_FD | ofp.OFPPF_COPPER |
                     ofp.OFPPF_AUTONEG | ofp.OFPPF_PAUSE |
                     ofp.OFPPF_PAUSE_ASYM)

        req = ofp_parser.OFPPortMod(datapath, port_num, hw_addr, config, mask, advertise)
        self.logger.info('Sending ModPort command to switch %s - %s port %s (hw address %s).', switch_id, "opening" if open else "closing", port_num, hw_addr)
        datapath.send_msg(req)