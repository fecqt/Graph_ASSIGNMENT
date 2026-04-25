import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from domain.Graph import Graph
from DAG.TopologicalSort import topological_sort


# --- Helper --- -> topological sort is not unique but can be verified manually
def is_valid_topo_order(g, order):
    position = {node: i for i, node in enumerate(order)}

    for u in g.get_vertices():
        for v in g.neighbors(u):
            if position[u] > position[v]:
                return False
    return True


def build_graph(edges, directed=True):
    g = Graph(directed=directed)

    # collect all vertices
    vertices = set()
    for u, v in edges:
        vertices.add(u)
        vertices.add(v)

    for v in vertices:
        g.add_vertex(v)

    for u, v in edges:
        g.add_edge(u, v)

    return g


def run_tests():
    tests_passed = 0

    # 1. Simple DAG
    g1 = build_graph([('A', 'B'), ('B', 'C')])
    result1 = topological_sort(g1)
    assert is_valid_topo_order(g1, result1)
    print("Test 1 passed:", result1)
    tests_passed += 1

    # 2. Multiple valid orders
    g2 = build_graph([('A', 'C'), ('B', 'C')])
    result2 = topological_sort(g2)
    assert is_valid_topo_order(g2, result2)
    print("Test 2 passed:", result2)
    tests_passed += 1

    # 3. Disconnected graph
    g3 = build_graph([('A', 'B'), ('C', 'D')])
    result3 = topological_sort(g3)
    assert is_valid_topo_order(g3, result3)
    print("Test 3 passed:", result3)
    tests_passed += 1

    # 4. Single node
    g4 = Graph(directed=True)
    g4.add_vertex('A')
    result4 = topological_sort(g4)
    assert result4 == ['A']
    print("Test 4 passed:", result4)
    tests_passed += 1

    # 5. Empty graph
    g5 = Graph(directed=True)
    result5 = topological_sort(g5)
    assert result5 == []
    print("Test 5 passed:", result5)
    tests_passed += 1

    # 6. Cycle
    g6 = build_graph([('A', 'B'), ('B', 'C'), ('C', 'A')])
    try:
        topological_sort(g6)
        print("Test 6 FAILED (cycle not detected)")
    except ValueError:
        print("Test 6 passed (cycle detected)")
        tests_passed += 1

    # 7. Mixed graph (your favorite case)
    g7 = build_graph([
        ('A', 'B'),
        ('B', 'C'),
        ('C', 'D'),
        ('D', 'E'),
        ('E', 'F'),
        ('F', 'D')  # cycle
    ])
    try:
        topological_sort(g7)
        print("Test 7 FAILED (cycle not detected)")
    except ValueError:
        print("Test 7 passed (cycle detected)")
        tests_passed += 1

    print(f"\n{tests_passed}/7 tests passed.")


if __name__ == "__main__":
    run_tests()