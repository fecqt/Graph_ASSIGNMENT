from Graph import Graph

def ford(g : Graph, starting_vertex):
    distance = {}
    previous = {}
    for vertex in g.get_vertices():
        distance[vertex] = float('inf')
        previous[vertex] = -1
    distance[starting_vertex] = 0
    changed = True
    number_of_iterations = 0
    number_of_vertices = len(g.get_vertices())
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
        for vertex1 in g.get_vertices():
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

