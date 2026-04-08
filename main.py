from Graph import Graph
from utils import TraversalType

PATH1 = "./A2/Graph1.txt"
PATH2 = "./A2/Graph2.txt"
PATH3 = "./A2/Graph3.txt"
PATH4 = "./A2/Graph4.txt"

try:
    # 1. Initialize as a Directed, Weighted Graph
    g = Graph(directed=True, weighted=True)

    print("--- Initializing Directed Weighted Graph ---")
    g.add_vertex("A")
    g.add_vertex("B")
    g.add_vertex("C")

    # 2. Add some weighted edges
    g.add_edge("A", "B", 10)
    g.add_edge("B", "C", 20)
    g.add_edge("C", "A", 30)
    print(g)
    # Expected: A->B(10), B->C(20), C->A(30)

    print("\n--- Testing Weights ---")
    print(f"Weight of A-B: {g.get_weight('A', 'B')}")
    g.set_weight("A", "B", 15)
    print(f"New weight of A-B: {g.get_weight('A', 'B')}")

    print("\n--- Testing Neighbors ---")
    print(f"Neighbors of B: {g.neighbors('B')}")  # Outbound: ['C']
    print(f"Inbound to B: {g.inbound_neighbors('B')}")  # Inbound: ['A']

    print("\n--- Converting to Undirected ---")

    g.change_if_directed(False)
    print(g)

    print("\n--- Converting to Unweighted ---")
    # This should set all weights to None
    g.change_if_weighted(False)
    print(g)

    print("\n--- Testing Removal ---")
    g.remove_edge("A", "B")
    print(f"Is there an edge A-B? {g.is_edge('A', 'B')}")
    g.remove_vertex("C")
    print(f"Vertices remaining: {g.get_vertices()}")

    print("\n--- Final Graph State ---")
    print(g)


    print("\n" + "=" * 30)
    print("--- TESTING TRAVERSALS (BFS & DFS) ---")
    print("=" * 30)
    # A -> B -> D
    # A -> C -> D
    traversal_graph = Graph(directed=True, weighted=False)
    for v in ["A", "B", "C", "D"]:
        traversal_graph.add_vertex(v)

    traversal_graph.add_edge("A", "B")
    traversal_graph.add_edge("A", "C")
    traversal_graph.add_edge("B", "D")
    traversal_graph.add_edge("C", "D")

    print("\nGraph Structure for Traversals:")
    print(traversal_graph)


    print("\n[ BFS Traversal from A ]")
    """
    it_bfs = traversal_graph.iterator("A", TraversalType.BFS)
    while it_bfs.is_valid():
        current = it_bfs.getCurrent()
        path = it_bfs.get_path()
        dist = it_bfs.get_path_length()
        print(f"Visited: {current} | Path: {' -> '.join(path)} | Distance: {dist}")
        it_bfs.next()
    """


    # --- DFS TEST ---
    print("\n[ DFS Traversal from A ]")
    """
    it_dfs = traversal_graph.iterator("A", TraversalType.DFS)
    while it_dfs.is_valid():
        current = it_dfs.getCurrent()
        path = it_dfs.get_path()
        depth = it_dfs.get_path_length()  # Note: path length in DFS is the branch depth
        print(f"Visited: {current} | Path: {' -> '.join(path)} | Depth: {depth}")
        it_dfs.next()

    print("\n--- Testing 'First' (Reset) ---")
    it_bfs.first()
    print(f"After reset, BFS is back at: {it_bfs.getCurrent()}")
    """

    graph1 = Graph.create_from_file(PATH1)
    print(graph1)

    it_dfs = graph1.iterator("4", TraversalType.DFS)
    while it_dfs.is_valid():
        current = it_dfs.getCurrent()
        path = it_dfs.get_path()
        depth = it_dfs.get_path_length()  # Note: path length in DFS is the branch depth
        print(f"Visited: {current} | Path: {' -> '.join(path)} | Depth: {depth}")
        it_dfs.next()

    # --- BFS TEST ---
    it_bfs = graph1.iterator("4", TraversalType.BFS)
    while it_bfs.is_valid():
        current = it_bfs.getCurrent()
        path = it_bfs.get_path()
        dist = it_bfs.get_path_length()
        print(f"Visited: {current} | Path: {' -> '.join(path)} | Distance: {dist}")
        it_bfs.next()

except Exception as e:
    print(e)