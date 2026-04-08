"""
Algorithm Comparison Tool
==========================
Pairs compared:
  - Positive only dataset  ->  Dijkstra  vs  UCS
        single walk: vertex 1 -> vertex N
  - Dataset with negatives ->  Bellman-Ford  vs  Floyd-Warshall
        ALL-PAIRS: BF runs once per source vertex (v calls total);
        FW produces all-pairs in a single pass.

For each graph file the script records:
  • The minimum-cost walk (path + cost) for one example pair (1 -> N)
  • Wall-clock time (BF: summed over all source runs)
  • Step-count table:
      g.cost calls        - number of calls to get_weight(u,v)   [O(1), main work unit]
      neighbors calls     - number of calls to neighbors(v)       [O(deg(v)), non-Θ(1)]
      get_vertices calls  - number of calls to get_vertices()     [O(v),      non-Θ(1)]
      get_edges calls     - number of calls to get_edges()        [O(v+e),    non-Θ(1)]
      pq.push             - heapq.heappush calls                  [O(log e),  non-Θ(1)]
      pq.pop              - heapq.heappop  calls                  [O(log e),  non-Θ(1)]
      loop_iters          - Floyd-Warshall innermost loop count   [v3 total]

Size limits (algorithms become impractical beyond these):
  Floyd-Warshall : skipped when v > MAX_V_FOR_FW  (O(v3) memory and time)
  Bellman-Ford   : skipped when v > MAX_V_FOR_BF  (O(v(v+e)) per source)

All analysis is written to comparison_results.txt.
Progress updates are printed to the terminal as the run proceeds.
"""

import os
import sys
import time
import heapq

import numpy as np

# Allow running from any working directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Graph import Graph

# -----------------------------------------------------------------
#  Thresholds - algorithms are skipped for graphs larger than these
# -----------------------------------------------------------------

MAX_V_FOR_FW = 150    # Floyd-Warshall: O(v3) steps, O(v²) memory
MAX_V_FOR_BF = 5_000  # Bellman-Ford:   O(v(v+e)) per source run

# Capture the real terminal stdout NOW, at import time, before any redirect.
# This is more reliable than sys.__stdout__ which can be None in some IDEs.
_TERMINAL = sys.stdout


# -----------------------------------------------------------------
#  Terminal progress helper
#  Writes directly to the real terminal even while sys.stdout is
#  redirected to the output file.
# -----------------------------------------------------------------

def _progress(msg):
    _TERMINAL.write(msg + "\n")
    _TERMINAL.flush()


def _output(msg):
    """Write to both the output file (via current sys.stdout) and the terminal."""
    print(msg)
    _TERMINAL.write(msg + "\n")
    _TERMINAL.flush()


# -----------------------------------------------------------------
#  Step counter
# -----------------------------------------------------------------

class StepCounter:
    """
    Accumulates counts for every non-Θ(1) operation called during an algorithm run.
    All fields start at 0; the instrumented graph wrapper and algorithm code
    increment them directly.
    """
    def __init__(self):
        self.get_weight   = 0   # g.cost(u,v)      - O(1) but counted as the main work unit
        self.neighbors    = 0   # g.neighbors(v)   - O(deg(v)), builds a Python list
        self.get_vertices = 0   # g.get_vertices()  - O(v),     builds a Python list
        self.get_edges    = 0   # g.get_edges()    - O(v+e),   builds a list of all edges
        self.pq_push      = 0   # heapq.heappush   - O(log n)
        self.pq_pop       = 0   # heapq.heappop    - O(log n)
        self.loop_iters   = 0   # Floyd-Warshall innermost loop iterations (v3 total)


# -----------------------------------------------------------------
#  Counting graph wrapper
# -----------------------------------------------------------------

class CountingGraph:
    """
    Thin proxy around Graph that increments a StepCounter on every
    non-Θ(1) method call.  Passed to the instrumented algorithm functions
    in place of the real Graph so all calls are transparently intercepted.
    """
    def __init__(self, graph: Graph, counter: StepCounter):
        self._g = graph
        self._c = counter

    def get_weight(self, u, v):
        self._c.get_weight += 1
        return self._g.get_weight(u, v)

    def neighbors(self, v):
        self._c.neighbors += 1
        return self._g.neighbors(v)

    def get_vertices(self):
        self._c.get_vertices += 1
        return self._g.get_vertices()

    def get_edges(self):
        self._c.get_edges += 1
        return self._g.get_edges()

    def get_v(self):
        # O(1) - not counted
        return self._g.get_v()


# -----------------------------------------------------------------
#  Instrumented algorithm implementations
#  (Faithful copies of the originals; every non-Θ(1) op is counted)
# -----------------------------------------------------------------

def _dijkstra(g: CountingGraph, start, c: StepCounter, total_v=None):
    """
    Dijkstra with step counting.
    Non-Θ(1) ops counted: get_vertices (×1 at init), neighbors (×1 per pop),
    get_weight (×1 per neighbour), pq.push, pq.pop.
    """
    distance = {}
    previous = {}
    for vertex in g.get_vertices():          # O(v) - counted
        distance[vertex] = float('inf')
        previous[vertex] = -1
    distance[start] = 0

    heap = [(0, start)]
    c.pq_push += 1                           # initial push
    visited = set()
    t0 = time.perf_counter()
    nodes_done = 0

    while heap:
        cost, vertex = heapq.heappop(heap)
        c.pq_pop += 1                        # O(log e) - counted

        if vertex in visited:
            continue
        visited.add(vertex)
        nodes_done += 1

        if total_v and nodes_done % 1000 == 0:
            elapsed = time.perf_counter() - t0
            rate = nodes_done / elapsed if elapsed > 0 else 0
            eta = (total_v - nodes_done) / rate if rate > 0 else float('inf')
            _progress(
                f"        Dijkstra: {nodes_done:,}/{total_v:,} nodes  |"
                f"  elapsed {_fmt_time(elapsed)}  |  ETA {_fmt_time(eta)}"
            )

        for neighbor in g.neighbors(vertex): # O(deg(v)) - counted
            w = g.get_weight(vertex, neighbor)  # O(1) - counted as main work unit
            new_cost = cost + w
            if new_cost < distance[neighbor]:
                distance[neighbor] = new_cost
                previous[neighbor] = vertex
                heapq.heappush(heap, (new_cost, neighbor))
                c.pq_push += 1              # O(log e) - counted

    return distance, previous


def _ucs(g: CountingGraph, start, goal, c: StepCounter, total_v=None):
    """
    UCS with step counting.
    Non-Θ(1) ops counted: neighbors (×1 per pop), get_weight (×1 per neighbour),
    pq.push, pq.pop.
    Note: get_vertices is NOT called (UCS has no init loop over all vertices).
    """
    frontier = [(0, start, [start])]
    c.pq_push += 1                           # initial push
    explored = {}
    t0 = time.perf_counter()
    nodes_done = 0

    while frontier:
        cost, vertex, path = heapq.heappop(frontier)
        c.pq_pop += 1                        # O(log e) - counted

        if vertex == goal:
            return cost, path

        if vertex in explored and explored[vertex] <= cost:
            continue
        explored[vertex] = cost
        nodes_done += 1

        if total_v and nodes_done % 1000 == 0:
            elapsed = time.perf_counter() - t0
            rate = nodes_done / elapsed if elapsed > 0 else 0
            eta = (total_v - nodes_done) / rate if rate > 0 else float('inf')
            _progress(
                f"        UCS: {nodes_done:,}/{total_v:,} nodes  |"
                f"  elapsed {_fmt_time(elapsed)}  |  ETA {_fmt_time(eta)}"
            )

        for neighbor in g.neighbors(vertex): # O(deg(v)) - counted
            w = g.get_weight(vertex, neighbor)  # O(1) - counted as main work unit
            new_cost = cost + w
            if neighbor not in explored or explored[neighbor] > new_cost:
                heapq.heappush(frontier, (new_cost, neighbor, path + [neighbor]))
                c.pq_push += 1              # O(log e) - counted

    return float('inf'), []


def _bellman_ford(g: CountingGraph, start, c: StepCounter):
    """
    Bellman-Ford with step counting.
    Non-Θ(1) ops counted: get_vertices (×(2 + actual_iterations)),
    neighbors (×v per iteration), get_weight (×e per iteration).
    No heap - pq fields stay 0.
    """
    distance = {}
    previous = {}
    for v in g.get_vertices():               # O(v) - counted (call #1)
        distance[v] = float('inf')
        previous[v] = -1
    distance[start] = 0

    changed = True
    iters = 0
    n = len(g.get_vertices())                # O(v) - counted (call #2)

    while changed and iters < n:
        changed = False
        iters += 1
        for v1 in g.get_vertices():          # O(v) - counted (1 call per while-iter)
            if distance[v1] != float('inf'):
                for v2 in g.neighbors(v1):   # O(deg(v)) - counted
                    w = g.get_weight(v1, v2) # O(1) - counted as main work unit
                    d = distance[v1] + w
                    if distance[v2] > d:
                        distance[v2] = d
                        previous[v2] = v1
                        changed = True

    if iters == n:
        raise ValueError("Negative cycle detected - Bellman-Ford did not converge.")
    return distance, previous


def _floyd_warshall(g: CountingGraph, c: StepCounter):
    """
    Floyd-Warshall with step counting.
    Non-Θ(1) ops counted: get_edges (×1), loop_iters (v3 innermost iterations).
    get_weight is NOT called - the matrix is populated via get_edges and then
    accessed directly as O(1) numpy operations.
    """
    v = g.get_v()
    Dist = np.full((v + 1, v + 1), float('inf'))
    np.fill_diagonal(Dist, 0)
    Next = np.full((v + 1, v + 1), -1, dtype=int)

    for v1, v2, cost in g.get_edges():       # O(v+e) - counted (call #1)
        Dist[int(v1)][int(v2)] = cost        # create_from_file stores vertex names as
        Next[int(v1)][int(v2)] = int(v2)    # strings; convert to int for numpy indexing

    t0 = time.perf_counter()
    for k in range(1, v + 1):
        for i in range(1, v + 1):
            for j in range(1, v + 1):
                c.loop_iters += 1            # v3 total - counted
                d = Dist[i][k] + Dist[k][j]
                if Dist[i][j] > d:
                    Dist[i][j] = d
                    Next[i][j] = Next[i][k]
        if k % max(1, v // 10) == 0 or k == v:
            elapsed = time.perf_counter() - t0
            rate = k / elapsed if elapsed > 0 else 0
            eta = (v - k) / rate if rate > 0 else float('inf')
            _progress(
                f"        Floyd-Warshall: k={k:,}/{v:,}  |"
                f"  elapsed {_fmt_time(elapsed)}  |  ETA {_fmt_time(eta)}"
            )

    return Dist, Next


# -----------------------------------------------------------------
#  Path reconstruction
# -----------------------------------------------------------------

def _path_from_previous(previous, start, end):
    """Reconstruct path from a previous-map (Dijkstra / Bellman-Ford output)."""
    if end not in previous:
        return []
    path = []
    cur = end
    while cur != -1:
        path.append(cur)
        if cur == start:
            path.reverse()
            return path
        cur = previous[cur]
    return []   # end was unreachable from start


def _path_from_next(Next, start, end):
    """Reconstruct path from Floyd-Warshall Next matrix."""
    if Next[start][end] == -1:
        return []
    path = [start]
    cur = start
    while cur != end:
        cur = int(Next[cur][end])
        path.append(cur)
        if len(path) > 200_000:      # guard against bugs / negative cycles
            return []
    return path


# -----------------------------------------------------------------
#  Output formatting helpers
# -----------------------------------------------------------------

def _fmt_path(path, max_nodes=12):
    if not path:
        return "(unreachable)"
    if len(path) <= max_nodes:
        return " -> ".join(str(v) for v in path)
    half = max_nodes // 2
    head = " -> ".join(str(v) for v in path[:half])
    tail = " -> ".join(str(v) for v in path[-half:])
    return f"{head} -> ... -> {tail}  (length {len(path)})"


def _fmt_time(seconds):
    ms = seconds * 1_000
    if ms < 1:
        return f"{ms * 1_000:.1f} us"
    if ms < 1_000:
        return f"{ms:.2f} ms"
    return f"{seconds:.2f} s"


def _fmt_n(n):
    return f"{n:>12,}" if n > 0 else f"{'-':>12}"


def _separator(width=62):
    return "-" * width




# -----------------------------------------------------------------
#  Comparison runners
# -----------------------------------------------------------------

def compare_positive(graph_file, start, end):
    """
    Load a positive-weight graph and compare Dijkstra vs UCS.
    Both algorithms find the minimum-cost walk from start to end.
    """
    g = Graph.create_from_file(graph_file)
    fname = os.path.basename(graph_file)
    v, e = g.get_v(), g.get_e()

    _output(f"\n{'=' * 62}")
    _output(f"  POSITIVE GRAPH  |  {fname}")
    _output(f"  {v} vertices, {e} edges")
    _output(f"  Walk: {start} -> {end}")
    _output(f"{'=' * 62}")

    # -- Dijkstra --------------------------------------------------
    _progress(f"      Dijkstra ...")
    c_d = StepCounter()
    t0 = time.perf_counter()
    dist_d, prev_d = _dijkstra(CountingGraph(g, c_d), start, c_d, total_v=v)
    t_d = time.perf_counter() - t0
    path_d = _path_from_previous(prev_d, start, end)
    cost_d = dist_d.get(end, float('inf'))

    # -- UCS -------------------------------------------------------
    _progress(f"      UCS ...")
    c_u = StepCounter()
    t0 = time.perf_counter()
    cost_u, path_u = _ucs(CountingGraph(g, c_u), start, end, c_u, total_v=v)
    t_u = time.perf_counter() - t0

    # -- Results ---------------------------------------------------
    match = "[OK] match" if cost_d == cost_u else "[!!] MISMATCH"
    _output(f"  Dijkstra : time={_fmt_time(t_d):>10}   cost={cost_d}   {match}")
    _output(f"             path={_fmt_path(path_d)}")
    _output(f"  UCS      : time={_fmt_time(t_u):>10}   cost={cost_u}")
    _output(f"             path={_fmt_path(path_u)}")

    # -- Step-count table ------------------------------------------
    _output("")
    _output(f"  {'Metric':<22} {'Dijkstra':>12} {'UCS':>12}  note")
    _output(f"  {_separator(58)}")
    _output(f"  {'g.cost calls':<22} {_fmt_n(c_d.get_weight)} {_fmt_n(c_u.get_weight)}  O(1), main work unit")
    _output(f"  {'neighbors() calls':<22} {_fmt_n(c_d.neighbors)} {_fmt_n(c_u.neighbors)}  O(deg v), builds list")
    _output(f"  {'get_vertices() calls':<22} {_fmt_n(c_d.get_vertices)} {_fmt_n(c_u.get_vertices)}  O(v), builds list")
    _output(f"  {'pq.push':<22} {_fmt_n(c_d.pq_push)} {_fmt_n(c_u.pq_push)}  O(log e)")
    _output(f"  {'pq.pop':<22} {_fmt_n(c_d.pq_pop)} {_fmt_n(c_u.pq_pop)}  O(log e)")
    _output("")

    # -- Observations ----------------------------------------------
    _observe_positive(c_d, c_u, t_d, t_u, v, e)


def _observe_positive(c_d, c_u, t_d, t_u, v, e):
    """Print a short interpretation of the step counts for the positive pair."""
    notes = []

    # UCS uses fewer pq ops when the goal is found before exhausting the graph
    if c_u.pq_pop < c_d.pq_pop:
        saved = c_d.pq_pop - c_u.pq_pop
        notes.append(
            f"  UCS popped {saved:,} fewer heap entries than Dijkstra "
            f"({c_u.pq_pop:,} vs {c_d.pq_pop:,}): early termination saved work."
        )
    else:
        notes.append(
            "  UCS and Dijkstra popped a similar number of heap entries; "
            "the goal vertex was near the last finalized vertex."
        )

    # Dijkstra calls get_vertices once; UCS never calls it
    if c_d.get_vertices > 0 and c_u.get_vertices == 0:
        notes.append(
            f"  Dijkstra called get_vertices() {c_d.get_vertices}× (O(v) init loop); "
            "UCS skipped this entirely - no pre-initialisation of all vertices."
        )

    # g.cost ratio: UCS visits fewer edges due to early stop
    if c_u.get_weight < c_d.get_weight:
        ratio = c_d.get_weight / max(c_u.get_weight, 1)
        notes.append(
            f"  Dijkstra checked {ratio:.1f}× more edges than UCS "
            f"({c_d.get_weight:,} vs {c_u.get_weight:,} g.cost calls)."
        )

    if notes:
        _output("  Observations:")
        for n in notes:
            _output(n)
        _output("")


def compare_negative(graph_file, start, end):
    """
    Load a graph with negative weights and compare Bellman-Ford vs Floyd-Warshall.

    Bellman-Ford is a single-source algorithm; to produce all-pairs results it is
    called once for every vertex in the graph (v calls total).  Step counts and
    wall-clock time are accumulated across all v runs.  The example walk
    (start -> end) is captured from the first run for display.

    Floyd-Warshall computes all-pairs in a single pass.

    Floyd-Warshall is skipped when v > MAX_V_FOR_FW.
    Bellman-Ford is skipped when v > MAX_V_FOR_BF.
    """
    g = Graph.create_from_file(graph_file)
    fname = os.path.basename(graph_file)
    v, e = g.get_v(), g.get_e()
    vertices = g.get_vertices()

    _output(f"\n{'=' * 66}")
    _output(f"  NEGATIVE GRAPH  |  {fname}")
    _output(f"  {v} vertices, {e} edges")
    _output(f"  BF: all-pairs via {v} single-source runs   |   FW: 1 all-pairs run")
    _output(f"  Example walk shown: {start} -> {end}")
    _output(f"{'=' * 66}")

    run_bf = v <= MAX_V_FOR_BF
    run_fw = v <= MAX_V_FOR_FW

    if not run_bf:
        _output(f"  Bellman-Ford   : SKIPPED - v={v:,} > {MAX_V_FOR_BF:,} "
              f"(estimated steps per source: {v * (v + e):,.0f})")
    if not run_fw:
        _output(f"  Floyd-Warshall : SKIPPED - v={v:,} > {MAX_V_FOR_FW} "
              f"(would need {v}×{v} matrix and {v**3:,.0f} inner loop steps)")
    if not run_bf and not run_fw:
        return

    # -- Bellman-Ford: all-pairs (v single-source runs) ---------------
    c_bf = StepCounter()
    cost_bf = path_bf = t_bf = None
    bf_ok = False

    if run_bf:
        _progress(f"      Bellman-Ford: {v:,} single-source passes ...")
        t0 = time.perf_counter()
        try:
            cg_bf = CountingGraph(g, c_bf)
            # First run from 'start' — capture result for the example walk
            dist_bf, prev_bf = _bellman_ford(cg_bf, start, c_bf)
            path_bf = _path_from_previous(prev_bf, start, end)
            cost_bf = dist_bf.get(end, float('inf'))
            # Remaining sources — accumulate step counts, discard results
            update_every = 1000
            sources_done = 1
            for s in vertices:
                if s == start:
                    continue
                _bellman_ford(cg_bf, s, c_bf)
                sources_done += 1
                if sources_done % update_every == 0 or sources_done == v:
                    elapsed = time.perf_counter() - t0
                    rate = sources_done / elapsed
                    eta = (v - sources_done) / rate if rate > 0 else float('inf')
                    _progress(
                        f"      BF: {sources_done:,}/{v:,} sources done  |"
                        f"  elapsed {_fmt_time(elapsed)}  |  ETA {_fmt_time(eta)}"
                    )
            t_bf = time.perf_counter() - t0
            bf_ok = True
        except ValueError as err:
            t_bf = time.perf_counter() - t0
            _output(f"  Bellman-Ford   : {err}")

    # -- Floyd-Warshall: all-pairs (single run) -----------------------
    c_fw = StepCounter()
    cost_fw = path_fw = t_fw = None
    fw_ok = False

    if run_fw:
        _progress(f"      Floyd-Warshall: all-pairs pass ...")
        t0 = time.perf_counter()
        Dist, Next = _floyd_warshall(CountingGraph(g, c_fw), c_fw)
        t_fw = time.perf_counter() - t0
        istart, iend = int(start), int(end)  # vertex names are strings; cast for numpy
        cost_fw = float(Dist[istart][iend]) if Dist[istart][iend] != float('inf') else float('inf')
        path_fw = _path_from_next(Next, istart, iend)
        fw_ok = True

    # -- Results ---------------------------------------------------
    if bf_ok and fw_ok:
        match = "[OK] match" if abs(cost_bf - cost_fw) < 1e-9 else "[!!] MISMATCH"
    else:
        match = ""

    if bf_ok:
        _output(f"  Bellman-Ford   : time={_fmt_time(t_bf):>10} ({v} sources total)"
              f"   example cost={cost_bf}   {match}")
        _output(f"                   path={_fmt_path(path_bf)}")
    if fw_ok:
        _output(f"  Floyd-Warshall : time={_fmt_time(t_fw):>10} (1 all-pairs run) "
              f"  example cost={cost_fw}")
        _output(f"                   path={_fmt_path(path_fw)}")

    # -- Step-count table ------------------------------------------
    _output("")
    col_bf = f"BF (×{v} src)" if run_bf else "(skipped)"
    col_fw = "Floyd-Warshall" if run_fw else "(skipped)"
    _output(f"  {'Metric':<22} {col_bf:>14} {col_fw:>16}  note")
    _output(f"  {_separator(66)}")

    def _row(label, val_bf, val_fw, note):
        sb = _fmt_n(val_bf) if run_bf else f"{'-':>12}"
        sf = _fmt_n(val_fw) if run_fw else f"{'-':>12}"
        _output(f"  {label:<22} {sb:>14} {sf:>16}  {note}")

    _row("g.cost calls",         c_bf.get_weight,   c_fw.get_weight,   "O(1), main work unit")
    _row("neighbors() calls",    c_bf.neighbors,    c_fw.neighbors,    "O(deg v), builds list")
    _row("get_vertices() calls", c_bf.get_vertices, c_fw.get_vertices, "O(v), builds list")
    _row("get_edges() calls",    c_bf.get_edges,    c_fw.get_edges,    "O(v+e)")
    _row("inner loop iters",     c_bf.loop_iters,   c_fw.loop_iters,   "v3 for F-W")
    _output("")

    # -- Observations ----------------------------------------------
    if bf_ok and fw_ok:
        _observe_negative(c_bf, c_fw, t_bf, t_fw, v, e)


def _observe_negative(c_bf, c_fw, t_bf, t_fw, v, e):
    """Print a short interpretation of the step counts for the negative pair."""
    notes = []

    # BF ran v times; total g.cost calls accumulated across all source runs
    notes.append(
        f"  Bellman-Ford ran from all {v:,} sources ({v:,} single-source calls). "
        f"Total g.cost calls = {c_bf.get_weight:,}  "
        f"(≈ v × iters_per_run × e; standard O(v·e) per run, O(v²·e) all-pairs)."
    )

    # FW: no g.cost at all - uses its own matrix
    notes.append(
        f"  Floyd-Warshall made 0 g.cost calls - edges were loaded once via "
        f"get_edges() into a NumPy matrix accessed in O(1) per cell."
    )

    # Inner loop count vs v3
    expected_fw = v ** 3
    notes.append(
        f"  Floyd-Warshall inner loop: {c_fw.loop_iters:,} iterations "
        f"(= v³ = {expected_fw:,} [OK])."
    )

    notes.append(
        f"  Bellman-Ford called get_vertices() {c_bf.get_vertices:,}× across all {v:,} runs "
        f"(each call rebuilds a {v}-element Python list). "
        f"That is ~{c_bf.get_vertices // v if v else 0} calls/run × {v} runs — "
        f"O(v²) overhead per source in this implementation."
    )

    _output("  Observations:")
    for n in notes:
        _output(n)
    _output("")


# -----------------------------------------------------------------
#  Helpers - discover dataset files and extract vertex count
# -----------------------------------------------------------------

def _v_from_filename(fname):
    """
    Extract the vertex count from filenames like 'positives_3_v50_e200.txt'.
    Returns None if the pattern is not found.
    """
    for part in fname.replace(".txt", "").split("_"):
        if part.startswith("v") and part[1:].isdigit():
            return int(part[1:])
    return None


def _dataset_files(folder):
    """Return sorted list of graph data files (excludes vertex-positions files)."""
    return sorted(
        f for f in os.listdir(folder)
        if f.endswith(".txt") and "position" not in f
    )


# -----------------------------------------------------------------
#  Entry point
# -----------------------------------------------------------------

if __name__ == "__main__":
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pos_dir = os.path.join(base, "Positive only dataset")
    neg_dir = os.path.join(base, "Dataset with negatives")
    out_path = os.path.join(os.path.dirname(__file__), "comparison_results.txt")

    _progress("=" * 62)
    _progress("  Algorithm Comparison  -  starting run")
    _progress(f"  Output file: {out_path}")
    _progress("=" * 62)

    with open(out_path, "w", encoding="utf-8") as _out:
        sys.stdout = _out

        # -- Positive graphs: Dijkstra vs UCS --------------------------
        _output("\n" + "#" * 62)
        _output("  POSITIVE GRAPHS  -  Dijkstra  vs  UCS")
        _output("#" * 62)

        for fname in _dataset_files(pos_dir):
            v = _v_from_filename(fname)
            if v is None:
                continue
            compare_positive(os.path.join(pos_dir, fname), start="1", end=str(v))

        # -- Negative graphs: Bellman-Ford vs Floyd-Warshall -----------
        _output("\n" + "#" * 62)
        _output("  NEGATIVE GRAPHS  -  Bellman-Ford  vs  Floyd-Warshall")
        _output("  (Bellman-Ford: all-pairs via v single-source runs)")
        _output("#" * 62)

        for fname in _dataset_files(neg_dir):
            v = _v_from_filename(fname)
            if v is None:
                continue
            compare_negative(os.path.join(neg_dir, fname), start="1", end=str(v))

        sys.stdout = sys.__stdout__

    _progress(f"\n{'=' * 62}")
    _progress(f"  All done.  Analysis written to:")
    _progress(f"  {out_path}")
    _progress(f"{'=' * 62}")
