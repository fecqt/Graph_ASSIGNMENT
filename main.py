from Graph import Graph
from utils import TraversalType
from mcwAlgorithms.compare import *
from Kruskal.kruskal import *
from DAG.NumberOfDistinctPaths import *
from DAG.TopologicalSort import *
from mcwAlgorithms.Uniform_Cost_Search import *
from mcwAlgorithms.Bellman_Ford_Algorithm import *
from mcwAlgorithms.Floyd_Warshall_Algorithm import *
from mcwAlgorithms.Dijkstra_Algorithm import *
PATH1 = "./A2/Graph1.txt"
PATH2 = "./A2/Graph2.txt"
PATH3 = "./A2/Graph3.txt"
PATH4 = "./A2/Graph4.txt"


def print_result(algo_name, distance_map, previous_map, start, end):
    print(f"\n[{algo_name} Result]")
    cost = distance_map.get(end, float('inf'))

    if cost == float('inf'):
        print(f"No path found from {start} to {end}")
        return

    #reconstruct path from previous map
    path = []
    curr = end
    while curr != -1 and curr is not None:
        path.append(curr)
        curr = previous_map.get(curr, -1)
    path.reverse()

    print(f"Path: {' -> '.join(map(str, path))}")
    print(f"Total Cost: {cost}")


try:

#----------KRUSKAL----------
    graph1 = Graph.create_from_file(PATH1)
    print(graph1)
    mst1 = kruskal(graph1)
    print(f"MST Total Weight: {sum(w for u, v, w in mst1.get_edges())}")

    print(f"Height from 4: {get_tree_height(mst1, '4')}")
    print(f"Height from 3: {get_tree_height(mst1, '3')}")
    seen = set()
    for u, v, w in mst1.get_edges():
        edge = tuple(sorted((u, v)))
        if edge not in seen:
            print(f"{u} - {v} (weight: {w})")
            seen.add(edge)

    disc = Graph(directed=False, weighted=True)
    disc.add_vertex('1')
    disc.add_vertex('2')
    disc.add_vertex('3')
    disc.add_vertex('4')
    disc.add_edge('1', '2', 1)
    disc.add_edge('3', '4', 1)

    try:
        kruskal(disc)
    except ValueError as e:
        print(f"Caught expected error: {e}")

#----------DAG----------

    g = Graph(directed=True, weighted=False)
    for v in ['A', 'B', 'C', 'D']: g.add_vertex(v)

    g.add_edge('A', 'B')
    g.add_edge('A', 'C')
    g.add_edge('B', 'D')
    g.add_edge('C', 'D')


    print(f"Paths A to D: {count_paths_dag(g, 'A', 'D')}")

    g2 = Graph(directed=True, weighted=False)
    for i in range(1, 7): g2.add_vertex(str(i))

    g2.add_edge('1', '2')
    g2.add_edge('1', '3')
    g2.add_edge('2', '4')
    g2.add_edge('3', '4')
    g2.add_edge('3', '5')
    g2.add_edge('4', '6')
    g2.add_edge('5', '6')

    print(f"Paths 1 to 6: {count_paths_dag(g2, '1', '6')}")

    g3 = Graph(directed=True, weighted=False)
    for v in ['X', 'Y', 'Z']: g3.add_vertex(v)

    g3.add_edge('X', 'Y')
    g3.add_edge('Y', 'Z')
    g3.add_edge('Z', 'X')

    try:
        count_paths_dag(g3, 'X', 'Z')
    except ValueError as e:
        print(f"Caught expected error: {e}")

    g4 = Graph(directed=True, weighted=False)
    g4.add_vertex('Start')
    g4.add_vertex('Mid')
    g4.add_vertex('End')
    g4.add_edge('Start', 'Mid')

    print(f"Paths Start to End: {count_paths_dag(g4, 'Start', 'End')}")
except Exception as e:
    print(e)