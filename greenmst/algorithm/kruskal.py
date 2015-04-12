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

"""
Kruskal's algorithm for minimum spanning trees. D. Eppstein, April 2006.
"""

from ..link import Link

parent = dict()
rank = dict()

def _make_set(vertex):
    parent[vertex] = vertex
    rank[vertex] = 0

def _find(vertex):
    if parent[vertex] != vertex:
        parent[vertex] = _find(parent[vertex])
    return parent[vertex]

def _union(vertex1, vertex2):
    root1 = _find(vertex1)
    root2 = _find(vertex2)
    if root1 != root2:
        if rank[root1] > rank[root2]:
            parent[root2] = root1
        else:
            parent[root1] = root2
            if rank[root1] == rank[root2]:
                rank[root2] += 1

def kruskal(graph):
    for vertice in graph['vertices']:
        _make_set(vertice)

    minimum_spanning_tree = set()
    edges = list(graph['edges'])
    edges.sort()
    for edge in edges:
        weight, vertice1, vertice2 = edge
        if _find(vertice1) != _find(vertice2):
            _union(vertice1, vertice2)
            minimum_spanning_tree.add(edge)
    return minimum_spanning_tree

def perform(topo_edges):
    vertices = []
    edges = []
    for edge in topo_edges:
        vertices.append(edge.src)
        vertices.append(edge.dst)
        edges.append((edge.cost, edge.src, edge.dst))

    graph = { 'vertices': list(set(vertices)), 'edges': set(edges) }
    mst = kruskal(graph)

    links = []
    for curedge in topo_edges:
        if (curedge.cost, curedge.src, curedge.dst) in mst or
           (curedge.cost, curedge.dst, curedge.src) in mst:
            links.append(curedge)
    return links
