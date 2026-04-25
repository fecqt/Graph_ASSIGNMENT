"""
Floyd-Warshall Algorithm
=========================
Concrete time complexity — this implementation, this graph:

Graph internals relevant here:
  - get_v()     is len(dict)                                →  O(1)
  - get_edges() iterates every adjacency list once          →  O(v + e)
  - Distance[i][k], Distance[k][j], Next[i][k] etc. are
    NumPy scalar element accesses on a 2-D array            →  O(1) each
    (NumPy stores the matrix in a contiguous C array;
     row indexing returns a view — no copy — and column
     indexing is a single pointer offset, both O(1).)

Initialisation:
  - get_v()                            →  O(1)
  - np.full((v+1, v+1), inf)           →  O(v²)   (fills every cell)
  - np.fill_diagonal(Distance, 0)      →  O(v)
  - np.full((v+1, v+1), -1, dtype=int) →  O(v²)
  - get_edges() + edge loop            →  O(v + e)  (builds edge list once, then O(e) loop)
  Total initialisation: Θ(v²)

Triple nested loop (the algorithm body):
  - Three loops each of size v  →  v³ iterations.
  - Body: two array reads, one addition, one comparison, at most two array writes → O(1).
  Total: Θ(v³)

Total:  Θ(v²)  +  O(v + e)  +  Θ(v³)  =  Θ(v³)

This matches the standard textbook complexity exactly.
The NumPy matrix gives genuinely O(1) per cell access (as opposed to a dict-of-dicts
which would also be O(1) average but with a higher constant), so no hidden overhead
is introduced by the data structure choice here.
Note: vertices must be integers in [1, v] for the array indexing to work correctly,
which is indeed the case in our graph files.
"""

from Graph import Graph
import numpy as np


def floydWarshall(g: Graph):
    v_count = g.get_v()
    vertices = g.get_vertices()

    # Create a dictionary to map names to numbers: {"A": 0, "B": 1, ...}
    name_to_id = {name: i for i, name in enumerate(vertices)}

    Dist = np.full((v_count, v_count), float('inf'))
    np.fill_diagonal(Dist, 0)
    Next = np.full((v_count, v_count), -1, dtype=int)

    # Populate edges using the mapping
    for v1, v2, cost in g.get_edges():
        u, v = name_to_id[v1], name_to_id[v2]
        Dist[u][v] = cost
        Next[u][v] = v

    # The Core Algorithm
    for k in range(v_count):
        for i in range(v_count):
            for j in range(v_count):
                if Dist[i][j] > Dist[i][k] + Dist[k][j]:
                    Dist[i][j] = Dist[i][k] + Dist[k][j]
                    Next[i][j] = Next[i][k]

    return Dist, Next, name_to_id