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

        wsgi = kwargs['wsgi']
        wsgi.register(GreenMSTAPIController, {'green_mst_api_app': self})

class GreenMSTAPIController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(GreenMSTAPIController, self).__init__(req, link, data, **config)
        self.topology_api_app = data['green_mst_api_app']

    @route('greenmst', '/wm/greenmst/topocosts/json', methods=['GET'])
    def list_topocosts(self, req, **kwargs):
        topo_costs = TopologyCosts()
        body = json.dumps(topo_costs.costs, cls=LinkEncoder)
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
