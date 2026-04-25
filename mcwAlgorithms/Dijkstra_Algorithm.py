"""
Dijkstra's Shortest Path Algorithm
====================================
Input:
    g               : a weighted graph with strictly positive edge weights
    starting_vertex : the source vertex s

Output:
    distance : map where distance[v] = cost of the minimum-cost walk from s to v
    previous : map where previous[v] = the vertex before v on that minimum-cost walk
               (previous[v] == -1 means v is the source or unreachable)

How it works:
-------------
Dijkstra is a greedy algorithm. It grows a "cloud" of vertices whose shortest distance
from s is already known for certain. At every step it picks the vertex outside the cloud
that has the smallest tentative distance, adds it to the cloud (marks it visited), and
then relaxes all its outgoing edges — i.e. checks whether going through that vertex
offers a shorter path to each of its neighbours.

This works correctly because all edge weights are positive: once a vertex is popped with
cost d, no future path through unvisited vertices can produce a smaller cost (they would
all have to travel through edges with positive weight, making the cost strictly larger).

Step-by-step:
  1. Initialise distance[v] = ∞ and previous[v] = -1 for every vertex v.         Θ(v)
  2. Set distance[s] = 0 and push (0, s) onto a min-heap (priority queue).
  3. While the heap is not empty:
       a. Pop (current_cost, current_vertex) — the cheapest unprocessed entry.
       b. If current_vertex is already in visited, skip it (stale heap entry).
       c. Add current_vertex to visited (it is now finalised).
       d. For every neighbour n of current_vertex:
            - If n is already visited, skip (its distance is already optimal).
            - Compute dist_with_current = distance[current_vertex] + cost(current_vertex, n)
            - If dist_with_current < distance[n]:
                  distance[n] = dist_with_current
                  previous[n] = current_vertex
                  Push (dist_with_current, n) onto the heap.
  4. Return distance, previous.

Why the "if current is visited: continue" check is needed:
  We use a simple heap and re-push a vertex with a better cost instead of updating its
  existing entry. This means the heap can hold multiple entries for the same vertex.
  When we eventually pop the stale (higher-cost) duplicate, we skip it via the visited
  check. This is implementation variant (b.i) from the lecture.

Complexity of THIS implementation — heap with duplicate entries (option b.i):
  - Initialisation                           : Θ(v)
  - Each vertex is finalised exactly once,
    but may be pushed multiple times (once per incoming edge in the worst case).
    → heap size is O(e) in the worst case.
  - Each heap push / pop costs O(log e).
  - Total pushes: O(v + e)  (at least v, at most v + e for all relaxations)
  - Total pops:   O(e)      (at most e stale entries + v real pops)
  - Neighbour iteration across all while-loop steps: Θ(e)  (each edge visited once)

  Overall: O((v + e) · log e)

  Note: if an advanced priority queue that supports decrease-key in O(log v) were used
  (option b.ii), the heap would hold at most v entries and the complexity would improve
  to O((v + e) · log v).  The naive linear-scan approach (option a) gives Θ(v² + e) = Θ(v²).

Concrete time complexity — this implementation, this graph:

Graph internals relevant here:
  - get_vertices() → list(dict.keys())     builds a new list every call  →  O(v)
  - neighbors(v)   → list(dict[v].keys())  builds a new list             →  O(deg(v))
  - get_weight(u,v) → plain dict lookup                                  →  O(1)

Initialisation:
  - get_vertices() called once  →  O(v)  to build the list.
  - Loop over v vertices, O(1) body  →  O(v).
  - Total: Θ(v).

While loop (heap-based):
  - At most one push per edge (each relaxation pushes once)  →  total pushes ≤ e.
  - Including the initial push of the source: total pushes = O(e).
  - Heap size at any point ≤ e  →  each push/pop costs O(log e).
  - Total pops  ≤ e  (v real finalisations + at most e − v stale entries)  →  O(e log e).
  - Total pushes  ≤ e                                                       →  O(e log e).
  - neighbors(v) is called once per finalised vertex; creating the list costs O(deg(v)).
    Summed over all v vertices:  Σ deg(v) = e  →  O(e) total for list creation.
  - get_weight called once per neighbour  →  O(1) each  →  O(e) total.

Total:  Θ(v)  +  O(e log e)  +  O(e)  =  O(v + e log e)

For any connected graph e ≥ v − 1, so e log e dominates and the result is O(e log e).

Comparison with the lecture's O((v + e) log e):
  Both are equivalent for connected graphs; the lecture formula is slightly more careful
  about accounting for both pushes (O(v + e)) and pops (O(e)) as separate terms before
  combining, but the result is the same asymptotic class.
"""

import heapq
from Graph import Graph

def dijkstra(g: Graph, starting_vertex):
    distance = {}
    previous = {}
    for vertex in g.get_vertices():
        distance[vertex] = float('inf')
        previous[vertex] = -1
    distance[starting_vertex] = 0

    #min-heap (cost, vertex)
    #we use a visited set so each vertex is finalized only once (greedy property)
    heap = [(0, starting_vertex)]
    visited = set()

    while heap:
        current_cost, current_vertex = heapq.heappop(heap)

        #if already finalized, skip (stale entry in heap)
        if current_vertex in visited:
            continue
        visited.add(current_vertex)

        for neighbor in g.neighbors(current_vertex):
            cost = g.get_weight(current_vertex, neighbor)
            new_cost = current_cost + cost
            if new_cost < distance[neighbor]:
                distance[neighbor] = new_cost
                previous[neighbor] = current_vertex
                heapq.heappush(heap, (new_cost, neighbor))

    return distance, previous
