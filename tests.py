from Graph import Graph
from utils import TraversalType


def collect_traversal(iterator):
    result = []
    while iterator.is_valid():
        result.append(iterator.getCurrent())
        iterator.next()
    return result


def make_graph():
    """
    Graph:
        1 -> 2, 3
        2 -> 4, 5
        3 -> 6
    """
    g = Graph(directed=True, weighted=False)

    for v in [1, 2, 3, 4, 5, 6]:
        g.add_vertex(v)

    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    g.add_edge(2, 5)
    g.add_edge(3, 6)

    return g


def test_iterator_starts_at_given_vertex():
    g = Graph(directed=True, weighted=False)
    g.add_vertex(1)

    it = g.iterator(1, TraversalType.BFS)

    assert it.is_valid() is True
    assert it.getCurrent() == 1


def test_first_resets_bfs_iterator():
    g = make_graph()
    it = g.iterator(1, TraversalType.BFS)

    assert it.getCurrent() == 1
    it.next()
    assert it.getCurrent() == 2

    it.first()

    assert it.is_valid() is True
    assert it.getCurrent() == 1

    result = collect_traversal(it)
    assert result == [1, 2, 3, 4, 5, 6]


def test_first_resets_dfs_iterator():
    g = make_graph()
    it = g.iterator(1, TraversalType.DFS)

    first_value = it.getCurrent()
    it.next()

    it.first()

    assert first_value == 1
    assert it.is_valid() is True
    assert it.getCurrent() == 1

    result = collect_traversal(it)
    assert result[0] == 1
    assert set(result) == {1, 2, 3, 4, 5, 6}
    assert len(result) == 6


def test_invalid_iterator_when_started_with_empty_string():
    g = Graph(directed=True, weighted=False)
    g.add_vertex("")

    it = g.iterator("", TraversalType.BFS)

    assert it.is_valid() is False


def test_get_current_raises_when_iterator_invalid():
    g = Graph(directed=True, weighted=False)
    g.add_vertex("")

    it = g.iterator("", TraversalType.BFS)

    try:
        it.getCurrent()
        assert False, "Expected exception was not raised"
    except Exception as e:
        assert str(e) == "Iterator is not valid"


def test_next_raises_when_iterator_invalid():
    g = Graph(directed=True, weighted=False)
    g.add_vertex("")

    it = g.iterator("", TraversalType.BFS)

    try:
        it.next()
        assert False, "Expected exception was not raised"
    except Exception as e:
        assert str(e) == "Iterator is not valid"


def test_bfs_traversal_order_directed_graph():
    g = make_graph()
    it = g.iterator(1, TraversalType.BFS)

    result = collect_traversal(it)

    assert result == [1, 2, 3, 4, 5, 6]


def test_bfs_becomes_invalid_after_full_traversal():
    g = make_graph()
    it = g.iterator(1, TraversalType.BFS)

    result = collect_traversal(it)

    assert result == [1, 2, 3, 4, 5, 6]
    assert it.is_valid() is False


def test_dfs_visits_all_reachable_vertices():
    g = make_graph()
    it = g.iterator(1, TraversalType.DFS)

    result = collect_traversal(it)

    assert result[0] == 1
    assert set(result) == {1, 2, 3, 4, 5, 6}
    assert len(result) == 6


def test_dfs_becomes_invalid_after_full_traversal():
    g = make_graph()
    it = g.iterator(1, TraversalType.DFS)

    result = collect_traversal(it)

    assert set(result) == {1, 2, 3, 4, 5, 6}
    assert it.is_valid() is False


def test_single_vertex_graph_for_both_traversals():
    for traversal_type in [TraversalType.BFS, TraversalType.DFS]:
        g = Graph(directed=True, weighted=False)
        g.add_vertex(10)

        it = g.iterator(10, traversal_type)
        result = collect_traversal(it)

        assert result == [10]
        assert it.is_valid() is False


def test_only_visits_reachable_vertices_for_both_traversals():
    for traversal_type in [TraversalType.BFS, TraversalType.DFS]:
        g = Graph(directed=True, weighted=False)

        for v in [1, 2, 3, 4]:
            g.add_vertex(v)

        g.add_edge(1, 2)
        g.add_edge(3, 4)

        it = g.iterator(1, traversal_type)
        result = collect_traversal(it)

        assert result[0] == 1
        assert set(result) == {1, 2}
        assert len(result) == 2


def test_does_not_repeat_vertices_for_both_traversals():
    for traversal_type in [TraversalType.BFS, TraversalType.DFS]:
        g = Graph(directed=True, weighted=False)

        for v in [1, 2, 3, 4]:
            g.add_vertex(v)

        g.add_edge(1, 2)
        g.add_edge(1, 3)
        g.add_edge(2, 4)
        g.add_edge(3, 4)

        it = g.iterator(1, traversal_type)
        result = collect_traversal(it)

        assert set(result) == {1, 2, 3, 4}
        assert len(result) == len(set(result))


def test_iterator_works_on_undirected_graph_too():
    g = Graph(directed=False, weighted=False)

    for v in [1, 2, 3]:
        g.add_vertex(v)

    g.add_edge(1, 2)
    g.add_edge(2, 3)

    it = g.iterator(1, TraversalType.BFS)
    result = collect_traversal(it)

    assert result == [1, 2, 3]


def test_iterator_ignores_weights_for_traversal():
    g = Graph(directed=True, weighted=True)

    for v in [1, 2, 3]:
        g.add_vertex(v)

    g.add_edge(1, 2, 7)
    g.add_edge(1, 3, 11)

    it = g.iterator(1, TraversalType.BFS)
    result = collect_traversal(it)

    assert result == [1, 2, 3]

from Graph import Graph
from utils import TraversalType


def collect_traversal_with_paths(iterator):
    result = []
    while iterator.is_valid():
        result.append(
            (
                iterator.getCurrent(),
                iterator.get_path_length(),
                iterator.get_path()
            )
        )
        iterator.next()
    return result



#TEST BONUS FEATURES
def make_graph2():
    """
    Graph:
        1 -> 2, 3
        2 -> 4, 5
        3 -> 6
        5 -> 7
    """
    g = Graph(directed=True, weighted=False)

    for v in [1, 2, 3, 4, 5, 6, 7]:
        g.add_vertex(v)

    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    g.add_edge(2, 5)
    g.add_edge(3, 6)
    g.add_edge(5, 7)

    return g


def test_path_length_at_start_bfs():
    g = make_graph2()
    it = g.iterator(1, TraversalType.BFS)

    assert it.getCurrent() == 1
    assert it.get_path_length() == 0
    assert it.get_path() == [1]


def test_path_length_at_start_dfs():
    g = make_graph2()
    it = g.iterator(1, TraversalType.DFS)

    assert it.getCurrent() == 1
    assert it.get_path_length() == 0
    assert it.get_path() == [1]


def test_bfs_path_and_length():
    g = make_graph2()
    it = g.iterator(1, TraversalType.BFS)

    result = collect_traversal_with_paths(it)

    assert result == [
        (1, 0, [1]),
        (2, 1, [1, 2]),
        (3, 1, [1, 3]),
        (4, 2, [1, 2, 4]),
        (5, 2, [1, 2, 5]),
        (6, 2, [1, 3, 6]),
        (7, 3, [1, 2, 5, 7]),
    ]


def test_dfs_path_and_length():
    g = make_graph2()
    it = g.iterator(1, TraversalType.DFS)

    result = collect_traversal_with_paths(it)

    visited_vertices = [x[0] for x in result]
    assert visited_vertices[0] == 1
    assert set(visited_vertices) == {1, 2, 3, 4, 5, 6, 7}
    assert len(visited_vertices) == 7

    for current, length, path in result:
        assert path[0] == 1
        assert path[-1] == current
        assert length == len(path) - 1


def test_bfs_path_is_shortest_distance():
    g = Graph(directed=True, weighted=False)

    for v in [1, 2, 3, 4]:
        g.add_vertex(v)

    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    g.add_edge(3, 4)

    it = g.iterator(1, TraversalType.BFS)
    result = collect_traversal_with_paths(it)

    info = {current: (length, path) for current, length, path in result}

    assert info[1] == (0, [1])
    assert info[2] == (1, [1, 2])
    assert info[3] == (1, [1, 3])

    assert info[4][0] == 2
    assert info[4][1] in ([1, 2, 4], [1, 3, 4])


def test_dfs_path_is_valid_tree_path():
    g = Graph(directed=True, weighted=False)

    for v in [1, 2, 3, 4]:
        g.add_vertex(v)

    g.add_edge(1, 2)
    g.add_edge(1, 3)
    g.add_edge(2, 4)
    g.add_edge(3, 4)

    it = g.iterator(1, TraversalType.DFS)
    result = collect_traversal_with_paths(it)

    for current, length, path in result:
        assert path[0] == 1
        assert path[-1] == current
        assert length == len(path) - 1


def test_get_path_length_single_vertex():
    g = Graph(directed=True, weighted=False)
    g.add_vertex(10)

    it = g.iterator(10, TraversalType.BFS)

    assert it.get_path_length() == 0
    assert it.get_path() == [10]

    it.next()
    assert it.is_valid() is False


def test_first_resets_path_information_bfs():
    g = make_graph2()
    it = g.iterator(1, TraversalType.BFS)

    it.next()
    it.next()

    assert it.getCurrent() == 3
    assert it.get_path_length() == 1
    assert it.get_path() == [1, 3]

    it.first()

    assert it.getCurrent() == 1
    assert it.get_path_length() == 0
    assert it.get_path() == [1]


def test_first_resets_path_information_dfs():
    g = make_graph2()
    it = g.iterator(1, TraversalType.DFS)

    it.next()

    assert it.getCurrent() != 1

    it.first()

    assert it.getCurrent() == 1
    assert it.get_path_length() == 0
    assert it.get_path() == [1]


def test_get_path_raises_when_iterator_invalid():
    g = Graph(directed=True, weighted=False)
    g.add_vertex(1)

    it = g.iterator(1, TraversalType.BFS)
    it.next()

    assert it.is_valid() is False

    try:
        it.get_path()
        assert False, "Expected exception was not raised"
    except Exception as e:
        assert str(e) == "Iterator is not valid"


def test_get_path_length_raises_when_iterator_invalid():
    g = Graph(directed=True, weighted=False)
    g.add_vertex(1)

    it = g.iterator(1, TraversalType.BFS)
    it.next()

    assert it.is_valid() is False

    try:
        it.get_path_length()
        assert False, "Expected exception was not raised"
    except Exception as e:
        assert str(e) == "Iterator is not valid"

#TESTS FOR CREATING GRAPH FROM FILE

import os
from Graph import Graph


def write_input_file(content):
    with open("input.txt", "w") as f:
        f.write(content)


def test_create_directed_unweighted_graph_from_file():
    write_input_file("""directed unweighted
1 2
1 3
4
""")

    g = Graph.create_from_file("input.txt")

    assert g.get_v() == 4
    assert g.is_edge("1", "2") is True
    assert g.is_edge("1", "3") is True
    assert "4" in g.get_vertices()
    assert g.neighbors("4") == []
    assert g.get_e() == 2


def test_create_undirected_unweighted_graph_from_file():
    write_input_file("""undirected unweighted
1 2
2 3
""")

    g = Graph.create_from_file("input.txt")

    assert g.get_v() == 3
    assert g.is_edge("1", "2") is True
    assert g.is_edge("2", "1") is True
    assert g.is_edge("2", "3") is True
    assert g.is_edge("3", "2") is True
    assert g.get_e() == 2


def test_create_directed_weighted_graph_from_file():
    write_input_file("""directed weighted
1 2 7
1 3 11
4
""")

    g = Graph.create_from_file("input.txt")

    assert g.get_v() == 4
    assert g.is_edge("1", "2") is True
    assert g.is_edge("1", "3") is True
    assert g.get_weight("1", "2") == 7
    assert g.get_weight("1", "3") == 11
    assert g.neighbors("4") == []
    assert g.get_e() == 2


def test_create_undirected_weighted_graph_from_file():
    write_input_file("""undirected weighted
1 2 5
2 3 8
""")

    g = Graph.create_from_file("input.txt")

    assert g.get_v() == 3
    assert g.is_edge("1", "2") is True
    assert g.is_edge("2", "1") is True
    assert g.is_edge("2", "3") is True
    assert g.is_edge("3", "2") is True
    assert g.get_weight("1", "2") == 5
    assert g.get_weight("2", "1") == 5
    assert g.get_weight("2", "3") == 8
    assert g.get_weight("3", "2") == 8
    assert g.get_e() == 2


def test_create_graph_with_isolated_vertices_only():
    write_input_file("""undirected unweighted
a
b
c
""")

    g = Graph.create_from_file("input.txt")

    assert g.get_v() == 3
    assert "a" in g.get_vertices()
    assert "b" in g.get_vertices()
    assert "c" in g.get_vertices()
    assert g.neighbors("a") == []
    assert g.neighbors("b") == []
    assert g.neighbors("c") == []
    assert g.get_e() == 0


def test_create_graph_adds_missing_vertices_from_edges():
    write_input_file("""directed unweighted
x y
y z
""")

    g = Graph.create_from_file("input.txt")

    assert set(g.get_vertices()) == {"x", "y", "z"}
    assert g.is_edge("x", "y") is True
    assert g.is_edge("y", "z") is True


def test_create_from_empty_file_raises():
    write_input_file("")

    try:
        Graph.create_from_file("input.txt")
        assert False, "Expected ValueError was not raised"
    except ValueError as e:
        assert str(e) == "The file is empty."


def test_invalid_first_line_raises():
    write_input_file("""directed
1 2
""")

    try:
        Graph.create_from_file("input.txt")
        assert False, "Expected ValueError was not raised"
    except ValueError as e:
        assert str(e) == "First line must contain exactly 2 words."


def test_invalid_orientation_raises():
    write_input_file("""sideways unweighted
1 2
""")

    try:
        Graph.create_from_file("input.txt")
        assert False, "Expected ValueError was not raised"
    except ValueError as e:
        assert str(e) == "Graph orientation must be 'directed' or 'undirected'."


def test_invalid_weight_type_raises():
    write_input_file("""directed heavy
1 2
""")

    try:
        Graph.create_from_file("input.txt")
        assert False, "Expected ValueError was not raised"
    except ValueError as e:
        assert str(e) == "Graph type must be 'weighted' or 'unweighted'."


def test_weighted_graph_without_weight_raises():
    write_input_file("""directed weighted
1 2
""")

    try:
        Graph.create_from_file("input.txt")
        assert False, "Expected ValueError was not raised"
    except ValueError as e:
        assert str(e) == "Weighted graphs must specify a weight for each edge."


def test_unweighted_graph_with_weighted_edge_raises():
    write_input_file("""directed unweighted
1 2 7
""")

    try:
        Graph.create_from_file("input.txt")
        assert False, "Expected ValueError was not raised"
    except ValueError as e:
        assert str(e) == "Unweighted graphs cannot have weighted edges in file."


def test_invalid_weight_value_raises():
    write_input_file("""directed weighted
1 2 abc
""")

    try:
        Graph.create_from_file("input.txt")
        assert False, "Expected ValueError was not raised"
    except ValueError as e:
        assert str(e) == "Invalid weight 'abc'. Weight must be an integer."


def test_invalid_line_with_too_many_elements_raises():
    write_input_file("""directed unweighted
1 2 3 4
""")

    try:
        Graph.create_from_file("input.txt")
        assert False, "Expected ValueError was not raised"
    except ValueError as e:
        assert str(e) == "Invalid line in file: '1 2 3 4'"

#tests the basic iterator functions
test_iterator_starts_at_given_vertex()
test_first_resets_bfs_iterator()
test_first_resets_dfs_iterator()
test_invalid_iterator_when_started_with_empty_string()
test_get_current_raises_when_iterator_invalid()
test_next_raises_when_iterator_invalid()
test_bfs_traversal_order_directed_graph()
test_bfs_becomes_invalid_after_full_traversal()
test_dfs_visits_all_reachable_vertices()
test_dfs_becomes_invalid_after_full_traversal()
test_single_vertex_graph_for_both_traversals()
test_only_visits_reachable_vertices_for_both_traversals()
test_does_not_repeat_vertices_for_both_traversals()
test_iterator_works_on_undirected_graph_too()
test_iterator_ignores_weights_for_traversal()

#tests bonus task for traversals
test_path_length_at_start_bfs()
test_path_length_at_start_dfs()
test_bfs_path_and_length()
test_dfs_path_and_length()
test_bfs_path_is_shortest_distance()
test_dfs_path_is_valid_tree_path()
test_get_path_length_single_vertex()
test_first_resets_path_information_bfs()
test_first_resets_path_information_dfs()
test_get_path_raises_when_iterator_invalid()
test_get_path_length_raises_when_iterator_invalid()


#tests create graph from file
test_create_directed_unweighted_graph_from_file()
test_create_undirected_unweighted_graph_from_file()
test_create_directed_weighted_graph_from_file()
test_create_undirected_weighted_graph_from_file()
test_create_graph_with_isolated_vertices_only()
test_create_graph_adds_missing_vertices_from_edges()
test_create_from_empty_file_raises()
test_invalid_first_line_raises()
test_invalid_orientation_raises()
test_invalid_weight_type_raises()
test_weighted_graph_without_weight_raises()
test_unweighted_graph_with_weighted_edge_raises()
test_invalid_weight_value_raises()
test_invalid_line_with_too_many_elements_raises()

if os.path.exists("input.txt"):
    os.remove("input.txt")

print("All tests passed.")