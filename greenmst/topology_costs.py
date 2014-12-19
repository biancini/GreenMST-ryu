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

def singleton(class_):
  instances = {}
  def getinstance(*args, **kwargs):
    if class_ not in instances:
        instances[class_] = class_(*args, **kwargs)
    return instances[class_]
  return getinstance

@singleton
class TopologyCosts():
    DEFAULT_COST = 1

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
            self.costs['%s,%s' % (destination, source)] = self.DEFAULT_COST
            return self.DEFAULT_COST