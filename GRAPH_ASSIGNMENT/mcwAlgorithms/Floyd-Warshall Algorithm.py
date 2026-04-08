from Graph import Graph
import numpy as np

def floydWarshall(g: Graph):
    v = g.get_v()
    Distance = np.full((v + 1, v + 1), float('inf'))
    np.fill_diagonal(Distance,0)

    Next = np.full( (v + 1, v + 1), -1, dtype = int)

    for vertex1, vertex2, cost in g.get_edges():
        Distance[vertex1][vertex2] = cost
        Next[vertex1][vertex2] = vertex2

    for k in range(1, v + 1):
        for i in range(1, v + 1):
            for j in range(1, v + 1):
                distance_with_k = Distance[i][k] + Distance[k][j];
                if (Distance[i][j] > distance_with_k):
                    Distance[i][j] = distance_with_k
                    Next[i][j] = Next[i][k]

    return Distance, Next