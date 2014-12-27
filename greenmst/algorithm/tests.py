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

from nose.tools import assert_equals
from kruskal import kruskal

def test_empty_graph():
    # arrange
    graph = {
        'vertices': [],
        'edges': set()
    }
    expected = set()

    # act
    result = kruskal(graph)    

    # assert
    assert_equals(expected, result)

def test_execution():
    # arrange
    graph = {
        'vertices': ['A', 'B', 'C', 'D', 'E', 'F'],
        'edges': set([(1, 'A', 'B'), (5, 'A', 'C'), (3, 'A', 'D'), (4, 'B', 'C'), (2, 'B', 'D'), (1, 'C', 'D')])
    }
    expected = set([(1, 'A', 'B'), (2, 'B', 'D'), (1, 'C', 'D')])

    # act
    result = kruskal(graph)    

    # assert
    assert_equals(expected, result)
