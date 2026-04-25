import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Graph         import Graph
from mcwAlgorithms.Dijkstra_Algorithm import *
from mcwAlgorithms.Uniform_Cost_Search import *
from mcwAlgorithms.Floyd_Warshall_Algorithm import *
from mcwAlgorithms.Bellman_Ford_Algorithm import *

MAX_V_FOR_FW = 150
MAX_V_FOR_BF = 5000

_TERMINAL = sys.stdout


def _progress(msg):
    _TERMINAL.write(msg + "\n")
    _TERMINAL.flush()


def _output(msg):
    print(msg)
    _TERMINAL.write(msg + "\n")
    _TERMINAL.flush()


# -----------------------------------------------------------------
#  Step counter + counting graph wrapper
# -----------------------------------------------------------------

class StepCounter:
    def __init__(self):
        self.get_weight   = 0  # g.get_weight(u,v) -- O(1) dict lookup, main work unit
        self.neighbors    = 0  # g.neighbors(v)    -- O(deg v), builds a list
        self.get_vertices = 0  # g.get_vertices()  -- O(v),     builds a list
        self.get_edges    = 0  # g.get_edges()     -- O(v+e),   builds a list


class CountingGraph:
    """
    Thin proxy around Graph. Passed to your algorithm functions in place of
    the real Graph so every non-O(1) call is transparently intercepted and counted.
    Your algorithm code is completely unchanged.
    """
    def __init__(self, graph, counter):
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
        return self._g.get_v()

    def get_e(self):
        return self._g.get_e()


# -----------------------------------------------------------------
#  Path reconstruction
# -----------------------------------------------------------------

def _path_from_previous(previous, start, end):
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
    return []


def _path_from_next(Next, start, end):
    if Next[start][end] == -1:
        return []
    path = [start]
    cur = start
    while cur != end:
        cur = int(Next[cur][end])
        path.append(cur)
        if len(path) > 200_000:
            return []
    return path


# -----------------------------------------------------------------
#  Formatting
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
    return f"{n:>12,}" if n >= 0 else f"{'-':>12}"


# -----------------------------------------------------------------
#  Positive graph: Dijkstra vs UCS
# -----------------------------------------------------------------

def compare_positive(graph_file, start, end):
    g = Graph.create_from_file(graph_file)
    fname = os.path.basename(graph_file)
    v, e = g.get_v(), g.get_e()

    _output(f"\n{'=' * 62}")
    _output(f"  POSITIVE GRAPH  |  {fname}")
    _output(f"  {v} vertices, {e} edges")
    _output(f"  Walk: {start} -> {end}")
    _output(f"{'=' * 62}")

    # -- Dijkstra --------------------------------------------------
    _progress("      Dijkstra ...")
    c_d = StepCounter()
    t0 = time.perf_counter()
    dist_d, prev_d = dijkstra(CountingGraph(g, c_d), start)
    t_d = time.perf_counter() - t0
    path_d = _path_from_previous(prev_d, start, end)
    cost_d = dist_d.get(end, float('inf'))

    # -- UCS -------------------------------------------------------
    _progress("      UCS ...")
    c_u = StepCounter()
    t0 = time.perf_counter()
    cost_u, path_u = ucs_literal(CountingGraph(g, c_u), start, end)
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
    _output(f"  {'-' * 58}")
    _output(f"  {'g.cost calls':<22} {_fmt_n(c_d.get_weight)} {_fmt_n(c_u.get_weight)}  O(1), main work unit")
    _output(f"  {'neighbors() calls':<22} {_fmt_n(c_d.neighbors)} {_fmt_n(c_u.neighbors)}  O(deg v), builds list")
    _output(f"  {'get_vertices() calls':<22} {_fmt_n(c_d.get_vertices)} {_fmt_n(c_u.get_vertices)}  O(v), builds list")
    _output("")


# -----------------------------------------------------------------
#  Negative graph: Bellman-Ford vs Floyd-Warshall
# -----------------------------------------------------------------

def compare_negative(graph_file, start, end):
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
        _output(f"  Bellman-Ford   : SKIPPED - v={v:,} > {MAX_V_FOR_BF:,}")
    if not run_fw:
        _output(f"  Floyd-Warshall : SKIPPED - v={v:,} > {MAX_V_FOR_FW}")
    if not run_bf and not run_fw:
        return

    # -- Bellman-Ford: all-pairs (v single-source runs) ------------
    c_bf = StepCounter()
    cost_bf = path_bf = t_bf = None
    bf_ok = False

    if run_bf:
        _progress(f"      Bellman-Ford: {v:,} single-source passes ...")
        t0 = time.perf_counter()
        try:
            cg_bf = CountingGraph(g, c_bf)

            # first run captures the example walk result
            dist_bf, prev_bf = ford(cg_bf, start)
            path_bf = _path_from_previous(prev_bf, start, end)
            cost_bf = dist_bf.get(end, float('inf'))

            # remaining sources — counts accumulate into the same c_bf
            sources_done = 1
            for s in vertices:
                if s == start:
                    continue
                ford(cg_bf, s)
                sources_done += 1
                if sources_done % 1000 == 0 or sources_done == v:
                    elapsed = time.perf_counter() - t0
                    rate = sources_done / elapsed if elapsed > 0 else 0
                    eta = (v - sources_done) / rate if rate > 0 else float('inf')
                    _progress(
                        f"      BF: {sources_done:,}/{v:,} sources  |"
                        f"  elapsed {_fmt_time(elapsed)}  |  ETA {_fmt_time(eta)}"
                    )

            t_bf = time.perf_counter() - t0
            bf_ok = True
        except ValueError as err:
            t_bf = time.perf_counter() - t0
            _output(f"  Bellman-Ford   : {err}")

    # -- Floyd-Warshall: all-pairs (single run) --------------------
    c_fw = StepCounter()
    cost_fw = path_fw = t_fw = None
    fw_ok = False

    if run_fw:
        _progress("      Floyd-Warshall: all-pairs pass ...")
        t0 = time.perf_counter()
        Dist, Next = floydWarshall(CountingGraph(g, c_fw))
        t_fw = time.perf_counter() - t0
        istart, iend = int(start), int(end)
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
        _output(f"  Floyd-Warshall : time={_fmt_time(t_fw):>10} (1 all-pairs run)"
                f"   example cost={cost_fw}")
        _output(f"                   path={_fmt_path(path_fw)}")

    # -- Step-count table ------------------------------------------
    col_bf = f"BF (×{v} src)" if run_bf else "(skipped)"
    col_fw = "Floyd-Warshall"  if run_fw else "(skipped)"
    _output("")
    _output(f"  {'Metric':<22} {col_bf:>14} {col_fw:>16}  note")
    _output(f"  {'-' * 66}")

    def _row(label, val_bf, val_fw, note):
        sb = _fmt_n(val_bf) if run_bf else f"{'-':>12}"
        sf = _fmt_n(val_fw) if run_fw else f"{'-':>14}"
        _output(f"  {label:<22} {sb:>14} {sf:>16}  {note}")

    _row("g.cost calls",         c_bf.get_weight,   c_fw.get_weight,   "O(1), main work unit")
    _row("neighbors() calls",    c_bf.neighbors,    c_fw.neighbors,    "O(deg v), builds list")
    _row("get_vertices() calls", c_bf.get_vertices, c_fw.get_vertices, "O(v), builds list")
    _row("get_edges() calls",    c_bf.get_edges,    c_fw.get_edges,    "O(v+e), builds list")
    _output("")


# -----------------------------------------------------------------
#  Dataset helpers
# -----------------------------------------------------------------

def _v_from_filename(fname):
    for part in fname.replace(".txt", "").split("_"):
        if part.startswith("v") and part[1:].isdigit():
            return int(part[1:])
    return None


def _dataset_files(folder):
    return sorted(
        f for f in os.listdir(folder)
        if f.endswith(".txt") and "position" not in f
    )


# -----------------------------------------------------------------
#  Entry point
# -----------------------------------------------------------------

if __name__ == "__main__":
    base     = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pos_dir  = os.path.join(base, "Positive only dataset")
    neg_dir  = os.path.join(base, "Dataset with negatives")
    out_path = os.path.join(os.path.dirname(__file__), "comparison_results.txt")

    _progress("=" * 62)
    _progress("  Algorithm Comparison  -  starting run")
    _progress(f"  Output file: {out_path}")
    _progress("=" * 62)

    with open(out_path, "w", encoding="utf-8") as _out:
        sys.stdout = _out

        _output("\n" + "#" * 62)
        _output("  POSITIVE GRAPHS  -  Dijkstra  vs  UCS")
        _output("#" * 62)

        for fname in _dataset_files(pos_dir):
            v = _v_from_filename(fname)
            if v is None:
                continue
            compare_positive(os.path.join(pos_dir, fname), start="1", end=str(v))

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
    _progress(f"  Done.  Results written to:")
    _progress(f"  {out_path}")
    _progress(f"{'=' * 62}")