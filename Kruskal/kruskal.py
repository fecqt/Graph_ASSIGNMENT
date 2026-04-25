from Graph import *
from GraphIterator import *

def kruskal(g: Graph):

    #We must have an undirected graph with weights since we must
    #find the minimum spanning tree.

    mst = Graph(directed=False, weighted=True)

    #We know that the minimum spanning tree has the same vertices
    #as our initial graph. The difference is that we must find
    #a minimum cost of edges such that the graph is still connected.

    for vertex in g.get_vertices():
        mst.add_vertex(vertex)

    sorted_edges = g.get_edges()
    unique_edges = []
    visited = set()

    #Since this is an undirected graph the edge (v1, v2) is the same as
    #the edge (v2, v1). There's no worth in storing both.

    for v1, v2, w in sorted_edges:
        edge = tuple(sorted((v1, v2)))
        if edge not in visited:
            visited.add(edge)
            unique_edges.append((v1, v2, w))

    #We store the edges we've found based on their weights. This allows us to always
    #pick first the edges with the lowest costs.

    unique_edges.sort(key=lambda x: x[2])
    forest = {}

    #The forest dictionary allows us to know in which tree each vertex is currently.
    #At first each vertex will be a tree of its own (a tree with 1 vertex and no edges).

    for v in g.get_vertices():
        forest[v] = {v}

    #The function find_tree allows us to find the tree where a vertex currently is.

    def find_tree(vertex):
        return forest[vertex]

    #The process of finding a minimum spanning tree using Kruskal's algorithm entails
    #starting from individual trees (those with one vertex and 0 edges) and later on merging them
    #depending on the cost of the edges. The function make_union is vital in this process as
    #it merges two trees.

    def make_union(set1, set2):
        if len(set1) < len(set2):
            small, large = set1, set2
        else:
            small, large = set2, set1

        #For efficiency reasons, it's preferable to add vertices to the larger tree, rather
        #than adding vertices to the smaller tree.

        for vertex in small:
            large.add(vertex)
            forest[vertex] = large

    edges_count = 0
    v_count = g.get_v()
    i = 0

    #Since we're trying to build a tree, we know that it has to have
    #v - 1 edges. Any more than that will lead to the birth of a cycle, which
    #is blasphemous when it comes to the intention of giving birth to a tree.

    while edges_count < v_count - 1:
        if i >= len(unique_edges):
            raise ValueError("g is disconnected.")

        v1, v2, weight = unique_edges[i]
        tree_v1 = find_tree(v1)
        tree_v2 = find_tree(v2)

        #We now unite the trees we've found. If it's not
        #the same component then we add it to the resulting tree.

        if tree_v1 is not tree_v2:
            mst.add_edge(v1, v2, weight)
            make_union(tree_v1, tree_v2)
            edges_count += 1
        i = i + 1

    return mst


def get_tree_height(tree, root):

    #To find the height we just have to iterate through our tree
    #using one of the traversal methods.

    iterator = tree.iterator(root, TraversalType.BFS)
    max_height = 0

    while iterator.is_valid():
        current_depth = iterator.get_path_length()
        if current_depth > max_height:
            max_height = current_depth
        iterator.next()

    return max_height