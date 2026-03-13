from GRAPH_ASSIGNMENT import Graph

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
except Exception as e:
    print(e)