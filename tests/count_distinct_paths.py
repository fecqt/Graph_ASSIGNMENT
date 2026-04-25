import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from domain.Graph import Graph
from DAG.TopologicalSort import topological_sort
from DAG.NumberOfDistinctPaths import count_paths_dag


# -----------------------------
# Helper: build graph quickly
# -----------------------------
def build_graph(edges):
    g = Graph(directed=True)

    vertices = set()
    for u, v in edges:
        vertices.add(u)
        vertices.add(v)

    for v in vertices:
        g.add_vertex(v)

    for u, v in edges:
        g.add_edge(u, v)

    return g


# -----------------------------
# Tests
# -----------------------------
def run_tests():
    tests_passed = 0

    # 1. Simple linear graph: 1 path
    # A → B → C
    g1 = build_graph([('A', 'B'), ('B', 'C')])
    assert count_paths_dag(g1, 'A', 'C') == 1
    print("Test 1 passed (linear graph)")
    tests_passed += 1

    # 2. Two paths
    # A → B → D
    # A → C → D
    g2 = build_graph([
        ('A', 'B'),
        ('B', 'D'),
        ('A', 'C'),
        ('C', 'D')
    ])
    assert count_paths_dag(g2, 'A', 'D') == 2
    print("Test 2 passed (two paths)")
    tests_passed += 1

    # 3. DAG with branching
    # A → B → D
    # A → C → D
    # B → C (extra connection)
    g3 = build_graph([
        ('A', 'B'),
        ('A', 'C'),
        ('B', 'C'),
        ('B', 'D'),
        ('C', 'D')
    ])
    assert count_paths_dag(g3, 'A', 'D') == 3
    print("Test 3 passed (branching DAG)")
    tests_passed += 1

    # 4. No path exists
    # A → B, C → D
    g4 = build_graph([
        ('A', 'B'),
        ('C', 'D')
    ])
    assert count_paths_dag(g4, 'A', 'D') == 0
    print("Test 4 passed (no path)")
    tests_passed += 1

    # 5. Start == end
    g5 = build_graph([])
    g5.add_vertex('A')
    assert count_paths_dag(g5, 'A', 'A') == 1
    print("Test 5 passed (start == end)")
    tests_passed += 1

    # 6. Larger DAG
    # A → B → D
    # A → C → D
    # B → E
    # C → E
    # E → D
    g6 = build_graph([
        ('A', 'B'),
        ('A', 'C'),
        ('B', 'D'),
        ('C', 'D'),
        ('B', 'E'),
        ('C', 'E'),
        ('E', 'D')
    ])
    assert count_paths_dag(g6, 'A', 'D') == 4
    print("Test 6 passed (larger DAG)")
    tests_passed += 1

    # 7. Single node graph
    g7 = build_graph([])
    g7.add_vertex('A')
    assert count_paths_dag(g7, 'A', 'A') == 1
    print("Test 7 passed (single node)")
    tests_passed += 1

    print(f"\n{tests_passed}/7 tests passed.")


if __name__ == "__main__":
    run_tests()