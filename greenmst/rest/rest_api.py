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
import re

from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.topology import switches
from webob import Response

from encoder import LinkEncoder
from ..controller import Controller
from ..topology_costs import TopologyCosts

class ControllerWithRestAPI(Controller):
    _CONTEXTS = {
        'switches': switches.Switches,
        'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(ControllerWithRestAPI, self).__init__(*args, **kwargs)

        if 'wsgi' in kwargs:
            wsgi = kwargs['wsgi']
            wsgi.register(GreenMSTAPIController, {'green_mst_api_app': self})

class GreenMSTAPIController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(GreenMSTAPIController, self).__init__(req, link, data, **config)
        self.topology_api_app = data['green_mst_api_app']

    @route('greenmst', '/wm/greenmst/topocosts/json', methods=['GET'])
    @classmethod
    def list_topocosts(cls, req, **kwargs):
        topo_costs = TopologyCosts()
        body = json.dumps(topo_costs.costs, cls=LinkEncoder)
        return Response(content_type='application/json', body=body)

    @staticmetod
    def validate_input(body):
        if not body:
            return False

        new_costs = json.loads(body)
        if not isinstance(new_costs, list):
            return False
        pattern = re.compile(r'\d+,\d+')

        for newcost in new_costs:
            if not isinstance(newcost, dict):
                return False
            for key,val in newcost.iteritems():
                if not pattern.match(key) and isinstance(val, (int, long, float)):
                    return False

        return True

    @route('greenmst', '/wm/greenmst/topocosts/json', methods=['POST'])
    @classmethod
    def set_topocosts(cls, req, **kwargs):
        topo_costs = TopologyCosts()
        new_costs = topo_costs.costs
        # Validate JSON passed as input
        valid_input = validate_input(req.body)

        if valid_input:
            self.topology_api_app.set_costs(new_costs)
            body = json.dumps({ 'status': 'new topology costs set' })
        else:
            body = json.dumps({ 'status': 'Error! Could not parse new topology costs, see log for details.' })

        return Response(content_type='application/json', body=body)

    @route('greenmst', '/wm/greenmst/mstedges/json', methods=['GET'])
    def list_mstedges(self, req, **kwargs):
        body = json.dumps(self.topology_api_app.mst_edges, cls=LinkEncoder)
        return Response(content_type='application/json', body=body)

    @route('greenmst', '/wm/greenmst/topoedges/json', methods=['GET'])
    def list_topoedges(self, req, **kwargs):
        body = json.dumps(self.topology_api_app.topo_edges, cls=LinkEncoder)
        return Response(content_type='application/json', body=body)

    @route('greenmst', '/wm/greenmst/redundantedges/json', methods=['GET'])
    def list_redundant_edges(self, req, **kwargs):
        body = json.dumps(self.topology_api_app.redundant_edges, cls=LinkEncoder)
        return Response(content_type='application/json', body=body)
