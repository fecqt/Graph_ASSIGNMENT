"""
Bellman-Ford Algorithm
=======================
Concrete time complexity — this implementation, this graph:

Graph internals relevant here:
  - get_vertices() returns list(dict.keys())  →  builds a NEW list every call  →  O(v)
  - neighbors(v)   returns list(dict[v].keys()) →  builds a new list           →  O(deg(v))
  - get_weight(u,v) is a plain dict lookup                                      →  O(1)

Initialisation  (lines: distance/previous dicts + number_of_vertices):
  - get_vertices() is called TWICE: once for the for-loop, once for len(get_vertices()).
    Each call costs O(v).  The loop body is O(1) per vertex  →  total init: Θ(v).

While loop  (runs at most v iterations, since number_of_iterations < number_of_vertices):
  - get_vertices() is called once PER ITERATION inside the for-loop header.
    Cost: O(v) per while-iteration  →  O(v) across all iterations.
  - The inner for (over neighbors of vertex1):
      neighbors(vertex1) costs O(deg(vertex1)).
      get_weight costs O(1) per neighbor.
      Summed over all vertices in one while-iteration: Σ deg(v) = e  →  O(e).
      Across v iterations:  O(v*e).

Total:  O(v)  +  O(v)  +  O(v*e)  =  O(v + v*e)  =  O(v*e)

"""

from Graph import Graph

def ford(g : Graph, starting_vertex):
    distance = {}
    previous = {}
    vertices = g.get_vertices()

    for vertex in vertices:
        distance[vertex] = float('inf')
        previous[vertex] = -1
    distance[starting_vertex] = 0
    changed = True
    number_of_iterations = 0
    number_of_vertices = len(vertices)
    """ 
    - Lecture Implementation 
    More or less a loyal copy of the professor's notes
    while changed and number_of_iterations < number_of_vertices:
        changed = False
        number_of_iterations += 1
        for vertex1, vertex2, cost in g.get_edges():
            if (distance[vertex1] != float('inf')):
                distance_with_vertex1 = distance[vertex1] + cost
                if distance[vertex2] > distance_with_vertex1:
                    distance[vertex2] = distance_with_vertex1
                    previous[vertex2] = vertex1
                    changed = True

    return distance, previous
    -------------------------------------------------------------------
    - Now to optimize this truly we can do the following implementation
    What's different from the previous implementation is that it no longer
    checks the neighbours of those vertices with distance infinity. Since it's
    obviously useless.
    """
    while changed and number_of_iterations < number_of_vertices:
        changed = False
        number_of_iterations += 1
        for vertex1 in vertices:
            if distance[vertex1] != float('inf'):
                for vertex2 in g.neighbors(vertex1):
                    cost = g.get_weight(vertex1, vertex2)
                    distance_with_vertex1 = distance[vertex1] + cost
                    if distance[vertex2] > distance_with_vertex1:
                        distance[vertex2] = distance_with_vertex1
                        previous[vertex2] = vertex1
                        changed = True
    if number_of_iterations == number_of_vertices:
        raise ValueError("This graph has negative cost edges! Burn it.")
    return distance, previous

