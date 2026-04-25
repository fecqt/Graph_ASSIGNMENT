"""
Uniform Cost Search (UCS)
==========================
Input:
    g               : a weighted graph with non-negative edge weights
    starting_vertex : the source vertex s
    goal_vertex     : the target vertex we want to reach

Output:
    cost : the total cost of the optimal (minimum-cost) path from s to goal_vertex,
           or float('inf') if goal_vertex is unreachable from s
    path : list of vertices representing that optimal path (empty if unreachable)

How it works:
-------------
UCS is Dijkstra applied as a goal-directed search. Instead of computing shortest paths
to ALL vertices, it expands nodes in order of increasing path cost and stops the moment
the goal vertex is popped from the frontier — at that point we are guaranteed to have
found the cheapest path to it.

The greedy argument is identical to Dijkstra: because all edge weights are non-negative,
the first time a vertex is popped from the min-heap its recorded cost is already optimal.
Any alternative path would pass through edges with non-negative weights and therefore
cannot be cheaper.

Step-by-step:
  1. Initialise explored = {} and push (0, starting_vertex, [starting_vertex]) onto
     a min-heap (the frontier). Each entry stores: cumulative cost, current vertex,
     and the path taken so far.
  2. While the frontier is not empty:
       a. Pop (current_cost, current_vertex, path) — the cheapest frontier entry.
          This is the get_min_vertex() step, implemented via the heap.
       b. GOAL TEST — performed on pop, not on push, to guarantee optimality:
            If current_vertex == goal_vertex → return current_cost, path.
       c. If current_vertex was already explored with a cost ≤ current_cost, skip it
          (stale duplicate entry — same role as "if current is visited: continue").
       d. Mark current_vertex as explored with current_cost.
       e. For every neighbour n of current_vertex:
            - If n is already explored (finalised), skip it.
            - Compute new_cost = current_cost + cost(current_vertex, n)
            - If new_cost improves on what we know for n:
                  Push (new_cost, n, path + [n]) onto the frontier.
  3. If the heap empties without finding goal_vertex, return float('inf'), [].

Difference from Dijkstra:
  - Dijkstra runs until the heap is empty and returns shortest paths to ALL vertices.
  - UCS stops as soon as the goal is finalised (early termination).
  - UCS carries the full path inside each heap entry so it can be returned directly,
    instead of reconstructing it via a previous map after the fact.

Complexity — same analysis as Dijkstra, with the same three implementation options:

  We consider all Map/Set operations Θ(1), g.get_neighbors() Θ(e/v) on average,
  and edge-cost lookup Θ(1).

  Initialisation: Θ(v) (one entry per vertex in explored dict, one push for source).
  The neighbour loop across all while-iterations visits each edge once → Θ(e) total.
  What changes across options is how get_min_vertex (the heap pop) is implemented:

  a) Naive linear scan over all unvisited vertices to find the minimum:
       - Each call: Θ(v).  Called once per vertex → Θ(v) × v = Θ(v²) total.
       - Combined with the Θ(e) neighbour work: Θ(v² + e).
       - Since e < v², we have v² + e < 2v², so Θ(v² + e) = Θ(v²).

  b) Priority queue (min-heap):

     i.  Simple heap — re-push with updated cost, ignore stale pops via the
         explored check (THIS is what our implementation uses):
           - Heap can hold up to O(e) entries (one per edge relaxation in worst case).
           - Each push/pop: O(log e).
           - Total pushes: O(v + e)  →  O((v + e) · log e)  for all push operations.
           - Total pops:   O(e)      →  O(e · log e)         for all pop operations.
           - Overall: O((v + e) · log e).

     ii. Advanced heap with decrease-key (e.g. Fibonacci heap):
           - At most v entries in the heap at any time → each operation O(log v).
           - Each vertex pushed once: O(v · log v).
           - Each edge may trigger a decrease-key: O(e · log v).
           - Overall: O(v · log v + e · log v) = O((v + e) · log v).

  This implementation uses option (b.i): O((v + e) · log e).
  Early termination means UCS is often faster in practice than running Dijkstra to
  completion, especially when the goal vertex is "close" to the source.

Concrete time complexity — this implementation, this graph:

Graph internals relevant here:
  - neighbors(v)    → list(dict[v].keys())  builds a new list  →  O(deg(v))
  - get_weight(u,v) → plain dict lookup                        →  O(1)
  (No get_vertices() call — UCS has no initialisation loop over all vertices.)

Initialisation:
  - Single heappush of the source tuple  →  O(1).
  - explored = {}                        →  O(1).
  - Total: O(1).  ← key difference from Dijkstra's Θ(v) init.

While loop (heap-based, same option b.i as Dijkstra):
  - Heap ops:  at most e pushes, each O(log e)  →  O(e log e).
               at most e pops,  each O(log e)   →  O(e log e).
  - neighbors(v) + get_weight per pop:  O(deg(v)) + O(deg(v))  =  O(deg(v)).
    Summed over all popped vertices (≤ e pops): O(e) total.

  CRITICAL DIFFERENCE FROM DIJKSTRA — path list copies:
  Every heappush executes `path + [neighbor]`, which allocates and copies a new list.
  The path for a vertex at search depth d has length d, so this copy costs O(d).
    - In the worst case (goal not found, or goal is the last vertex reached), the
      search explores all e edges. A vertex at depth d contributes O(d) to the copy cost.
    - Worst-case total copy cost: O(e × v) — if every pushed vertex is at depth O(v).
      (e.g. a long chain: v vertices in a line, every edge triggers a push with a path
       that grows by 1 each step → total copy cost = 1 + 2 + ... + v = O(v²); for a
       denser graph the e pushes each copying up to O(v) give O(e × v).)
    - Dijkstra avoids this entirely by storing only a previous[] map (O(1) per update)
      and reconstructing the path after the fact.

Total worst case:  O(e log e)  +  O(e)  +  O(e × v)  =  O(e(v + log e))

With early termination (goal found at depth d, exploring k nodes before it):
  - Heap ops:   O(k log k)  where k ≤ e.
  - Path copies: O(k × d)  where d ≤ v.
  - In the best case (goal is adjacent to the source): O(log v) — nearly instant.
  The further the goal, the closer the concrete cost gets to the worst-case O(e(v + log e)).
"""
"""
import heapq
from Graph import Graph

def ucs(g: Graph, starting_vertex, goal_vertex):
    frontier = [(0, starting_vertex, [starting_vertex])]
    explored = {}

    while frontier:
        current_cost, current_vertex, path = heapq.heappop(frontier)

        #perform it when a node is popped (not pushed), guaranteeing optimality
        if current_vertex == goal_vertex:
            return current_cost, path

        #if we already found a cheaper way to this vertex, skip
        if current_vertex in explored and explored[current_vertex] <= current_cost:
            continue
        explored[current_vertex] = current_cost

        for neighbor in g.neighbors(current_vertex):
            edge_cost = g.get_weight(current_vertex, neighbor)
            new_cost = current_cost + edge_cost
            #only push if we haven't confirmed a cheaper cost yet
            if neighbor not in explored or explored[neighbor] > new_cost:
                heapq.heappush(frontier, (new_cost, neighbor, path + [neighbor]))

# Goal is unreachable
    return float('inf'), []
"""

import heapq
from Graph import Graph


def ucs_literal(g: Graph, starting_vertex, goal_vertex):
    distance = {}
    previous = {}
    for v in g.get_vertices():
        distance[v] = float('inf')
        previous[v] = -1

    distance[starting_vertex] = 0
    pq = [(0, starting_vertex)]

    while pq:
        current_dist, current = heapq.heappop(pq)

        #stop immediately when the goal is popped
        if current == goal_vertex:
            #Follow parents back to start to reconstruct
            path = []
            temp = goal_vertex
            while temp != -1:
                path.append(temp)
                temp = previous[temp]
            return distance[goal_vertex], path[::-1]  #COST and PATH list

        if current_dist > distance[current]:
            continue

        for n in g.neighbors(current):
            weight = g.get_weight(current, n)
            if distance[n] > distance[current] + weight:
                distance[n] = distance[current] + weight
                previous[n] = current
                heapq.heappush(pq, (distance[n], n))

    return float('inf'), []  #unreachable