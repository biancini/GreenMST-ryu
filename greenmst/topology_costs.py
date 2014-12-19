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

import logging

class TopologyCosts():
    DEFAULT_COST = 1

    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TopologyCosts, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        self.costs = {}

    def set_cost(self, source, destination, cost):
        self.costs['%s,%s' % (source, destination)] = cost

    def get_cost(self, source, destination):
        if '%s,%s' % (source, destination) in self.costs:
            return int(self.costs['%s,%s' % (source, destination)])
        elif '%s,%s' % (destination, source) in self.costs:
            return int(self.costs['%s,%s' % (destination, source)])
        else:
            return self.DEFAULT_COST