from Graph import *
from GraphIterator import *


# To obtain connected components we will choose a random vertex and perform a traversal
# from it to find all reachable vertices.
# The component is a tree if the number of edges E = V - 1
# The component is a bipartite graph if we can colour the vertices with 2 colours such that
# no adjacent vertices have the same colour. (Basically that we have edges only between vertices
# of different partitions)
# The component is a complete bipartite graph if it is bipartite and number of edges E = number of
# vertices from partition 1 * number of vertices from partition 2

def check_bipartite(graph, start_vertex):
    colours = {start_vertex: "baby blue"}
    partition_A = {start_vertex}
    partition_B = set()
    queue = [start_vertex]
    visited = {start_vertex}
    while queue:
        vertex = queue.pop(0)
        for v in graph.neighbors(vertex):
            if v not in colours:
                colours[v] = "pastel yellow" if colours[vertex] == "baby blue" else "baby blue"
                visited.add(v)
                queue.append(v)
                if colours[v] == "baby blue":
                    partition_A.add(v)
                elif colours[v] == "pastel yellow":
                    partition_B.add(v)
            elif colours[v] == colours[vertex]:
                return False, set(), set()

    return True, partition_A, partition_B


def classify_component(graph: Graph):
    all_vertices = set(graph.get_vertices())
    visited = set()
    component_count = 1
    while len(visited) < len(all_vertices):
        start_vertex = list(all_vertices - visited)[0]  # Picks a vertex that's not been visited
        component_vertices = []
        it = graph.iterator(start_vertex, TraversalType.BFS)
        while it.is_valid():
            current = it.getCurrent()
            component_vertices.append(current)
            visited.add(current)
            it.next()
        v_count = len(component_vertices)
        e_count = 0
        for vertex in component_vertices:
            e_count += len(graph.neighbors(vertex))
        e_count //= 2
        is_bipartite, partition_A, partition_B = check_bipartite(graph, start_vertex)
        classification = "general graph"
        if is_bipartite:
            classification = "bipartite"
            n, m = len(partition_A), len(partition_B)
            if e_count == v_count - 1:
                classification = "tree"
            elif e_count == n * m:
                classification = "complete bipartite"
        print(f"Component {component_count}: {set(component_vertices)}")
        print(f"Type: {classification}")
        print("-" * 30)
        component_count += 1

