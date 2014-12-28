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
from kruskal import perform
from ..link import Link

def test_empty_graph():
    # arrange
    edges = []
    expected = []

    # act
    result = perform(edges)

    # assert
    assert_equals(expected, result)

def test_execution():
    # arrange
    edges = []
    for curedge in [(1, 'A', 'B'), (5, 'A', 'C'), (3, 'A', 'D'), (4, 'B', 'C'), (2, 'B', 'D'), (1, 'C', 'D')]:
        curlink = Link(src=curedge[1], dst=curedge[2], cost=curedge[0])
        edges.append(curlink)

    expected = []
    expected.append(Link(src='A', dst='B', cost=1))
    expected.append(Link(src='B', dst='D', cost=2))
    expected.append(Link(src='C', dst='D', cost=1))

    # act
    result = perform(edges)

    # assert
    assert_equals(expected, result)
