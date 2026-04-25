import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from domain.Graph import Graph
from DAG.TopologicalSort import topological_sort

def count_paths_dag(graph, start, end):
    topo = topological_sort(graph)

    dp = {v: 0 for v in graph.get_vertices()}
    dp[start] = 1

    for u in topo:
        for v in graph.neighbors(u):
            dp[v] += dp[u]

    return dp[end]