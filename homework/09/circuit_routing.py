#!/usr/bin/env python3
"""
Homework 9 (5/5): The circuit routing problem in IC design.

A chip has blocks (macros) in the way and several nets. Each net must connect
two or more pins with metal wire. Wires may not cross obstacles and wires of
different nets may not overlap (that would be a short circuit). The goal is to
connect everything with short wires and few vias (layer changes).

"Many methods" - this program implements and compares:
  A. Lee algorithm (maze router): a BFS wave, shortest path on one layer
  B. Dijkstra on two layers with a cost model (preferred direction, via penalty)
  C. A*: same cost model, plus a Manhattan-distance heuristic -> same cost, fewer nodes
  D. Multi-pin nets: grow a Steiner-like tree, using the whole routed tree as the
     multi-source start for the next pin
  E. Net ordering: nets are routed one after another and earlier nets block later
     ones, so all 5! = 120 orders are tried
  F. A simplified rip-up and reroute: if a net is blocked, tear everything up,
     move that net to the front and route again

Model:
  * two metal layers: M1 prefers horizontal wires, M2 prefers vertical wires
  * cost: step in the preferred direction 1, other direction 3, via 6
  * some macros block only M1 (M2 may pass over them), two walls block both layers

Usage:  python circuit_routing.py
"""
import heapq
import itertools
import os
import sys
import time
from collections import deque

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.system("")

USE_COLOR = not os.environ.get("NO_COLOR") and (
    sys.stdout.isatty() or os.environ.get("FORCE_COLOR")
)


def paint(text, fg=None, bg=None, bold=False):
    if not USE_COLOR:
        return text
    codes = ("\033[1m" if bold else "") + (f"\033[38;5;{fg}m" if fg is not None else "") \
        + (f"\033[48;5;{bg}m" if bg is not None else "")
    return f"{codes}{text}\033[0m"


def banner(title):
    line = "=" * 72
    return "\n" + paint(line, fg=39) + "\n" + paint("  " + title, fg=51, bold=True) + "\n" + paint(line, fg=39)


# ==================================================================
# Part A: Lee algorithm demo (one layer, BFS wave)
# ==================================================================
def lee_demo():
    W, H = 24, 11
    g = [[0] * W for _ in range(H)]
    for x in range(W):
        g[0][x] = g[H - 1][x] = 1
    for y in range(H):
        g[y][0] = g[y][W - 1] = 1
    for y in range(1, 8):
        g[y][8] = 1                      # long wall (gap at the bottom)
    for y in range(3, H - 1):
        g[y][15] = 1                     # long wall (gap at the top)
    for x in range(10, 14):
        g[5][x] = 1
    src, dst = (2, 2), (21, 8)

    # expansion phase: fill distances outwards from the source
    dist = {src: 0}
    q = deque([src])
    while q and dst not in dist:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if g[n[1]][n[0]] == 0 and n not in dist:
                dist[n] = dist[(x, y)] + 1
                q.append(n)
    # retrace phase: from the target, step to a neighbour whose distance is one less
    path = [dst]
    cur = dst
    while cur != src:
        x, y = cur
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if dist.get(n, -9) == dist[cur] - 1:
                cur = n
                break
        path.append(cur)
    path_set = set(path)

    def show(with_path):
        rows = []
        for y in range(H):
            s = ""
            for x in range(W):
                p = (x, y)
                if g[y][x]:
                    s += paint("###", fg=240)
                elif p == src:
                    s += paint(" S ", fg=16, bg=46, bold=True)
                elif p == dst:
                    s += paint(" T ", fg=16, bg=208, bold=True)
                elif with_path and p in path_set:
                    s += paint(" * " if not USE_COLOR else f"{dist[p]:>3}", fg=16, bg=226, bold=True)
                elif p in dist:
                    col = [51, 45, 39, 33, 27, 21][min(5, dist[p] // 8)]
                    s += paint(f"{dist[p]:>3}", fg=col)
                else:
                    s += paint(" . ", fg=238)
            rows.append(s)
        return "\n".join(rows)

    print(banner("A. Lee algorithm demo (one layer, BFS wave): S -> T"))
    print("  1) Expansion: from S, fill in the distance ring by ring until T is reached")
    print("     (number = shortest number of steps from S).")
    print(show(False))
    print(f"\n  2) Retrace: from T walk to neighbours with distance one less -> "
          f"shortest wire length = {len(path) - 1}  (yellow / * = chosen path)")
    print(show(True))
    print("\n  3) Clear: mark the path as occupied, wipe the numbers, go on with the next net.")
    print(f"  cells filled = {len(dist)} of {sum(1 for r in g for v in r if v == 0)} free cells"
          "  -> Lee is optimal on one layer but blind: it floods almost the whole map.")


# ==================================================================
# Part B: two-layer router (Dijkstra / A*)
# ==================================================================
W, H = 34, 15
STEP, WRONG, VIA = 1, 3, 6         # preferred step / wrong-direction step / via

# (x1, y1, x2, y2, blocked layers): '0' = blocks M1 only; '01' = blocks M1 and M2
MACROS = [(4, 2, 10, 5, "0"), (14, 7, 20, 10, "0"), (24, 1, 29, 4, "01"), (5, 10, 10, 12, "0"),
          (27, 8, 31, 12, "01"),
          (16, 0, 17, 5, "01"), (22, 6, 23, 14, "01")]   # last two: staggered walls -> S-shaped channel
NETS = [
    ("A", [(2, 3), (31, 13)]),
    ("B", [(11, 4), (12, 13)]),
    ("C", [(3, 13), (21, 2), (32, 6)]),         # 3-pin net
    ("D", [(1, 7), (33, 7)]),
    ("E", [(21, 13), (13, 1)]),
]
NET_COLOR = {"A": 196, "B": 46, "C": 33, "D": 208, "E": 201}


def make_board():
    occ = {}
    for x1, y1, x2, y2, layers in MACROS:
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for ly in layers:
                    occ[(int(ly), x, y)] = "#"
    for name, pins in NETS:
        for x, y in pins:
            assert occ.get((0, x, y)) is None, f"pin {name}{(x, y)} lies on an obstacle"
            occ[(0, x, y)] = name
    return occ


def in_range(x, y):
    return 0 <= x < W and 0 <= y < H


def moves(state, net, occ):
    l, x, y = state
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if not in_range(nx, ny):
            continue
        o = occ.get((l, nx, ny))
        if o is None or o == net:
            horizontal = dy == 0
            prefer = (l == 0) == horizontal       # M1 prefers horizontal, M2 vertical
            yield (l, nx, ny), (STEP if prefer else WRONG)
    ol = 1 - l
    o = occ.get((ol, x, y))
    if o is None or o == net:
        yield (ol, x, y), VIA


def route_to(sources, target_xy, net, occ, mode):
    """
    Multi-source -> single target. mode: 'astar' (f = g + h) or 'dijkstra' (f = g).
    Returns (path, cost, expanded); path is None if the net is blocked.
    """
    tx, ty = target_xy
    goal = (0, tx, ty)

    def h(s):
        return (abs(s[1] - tx) + abs(s[2] - ty)) if mode == "astar" else 0   # cheapest step is 1 -> admissible

    heap, g, parent, cnt = [], {}, {}, 0
    for s in sources:
        g[s] = 0
        parent[s] = None
        heapq.heappush(heap, (h(s), cnt, s))
        cnt += 1
    closed = set()
    while heap:
        _, _, cur = heapq.heappop(heap)
        if cur in closed:
            continue
        closed.add(cur)
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return path[::-1], g[goal], len(closed)
        for nb, c in moves(cur, net, occ):
            ng = g[cur] + c
            if ng < g.get(nb, 1e18):
                g[nb] = ng
                parent[nb] = cur
                cnt += 1
                heapq.heappush(heap, (ng + h(nb), cnt, nb))
    return None, float("inf"), len(closed)


def route_all(order, mode):
    """Route the nets one after another in the given order."""
    occ = make_board()
    net_pins = dict(NETS)
    edges = {n: set() for n in net_pins}
    stats = {"expanded": 0, "cost": 0, "failed": [], "per_net": {}}
    for net in order:
        pins = net_pins[net]
        tree = {(0, pins[0][0], pins[0][1])}
        remaining = list(pins[1:])
        net_cost, net_exp, ok = 0, 0, True
        while remaining:
            # connect the pin closest to the current tree first (Prim-like / Steiner-like)
            remaining.sort(key=lambda p: min(abs(p[0] - t[1]) + abs(p[1] - t[2]) for t in tree))
            tgt = remaining.pop(0)
            path, cost, exp = route_to(tree, tgt, net, occ, mode)
            net_exp += exp
            if path is None:
                ok = False
                break
            net_cost += cost
            for a, b in zip(path, path[1:]):
                edges[net].add(frozenset((a, b)))
            for c in path:
                occ[c] = net
                tree.add(c)
        stats["expanded"] += net_exp
        if ok:
            stats["cost"] += net_cost
        else:
            stats["failed"].append(net)
        stats["per_net"][net] = (ok, net_cost, net_exp)
    wl = vias = 0
    for net, es in edges.items():
        for e in es:
            a, b = tuple(e)
            if a[0] != b[0]:
                vias += 1
            else:
                wl += 1
    stats.update({"wirelength": wl, "vias": vias, "occ": occ, "edges": edges, "order": list(order)})
    return stats


# ------------------------------------------------------------------ drawing
GLYPH = {
    (0, 0, 0, 0): ".", (1, 0, 1, 0): "│", (0, 1, 0, 1): "─",
    (1, 1, 0, 0): "└", (1, 0, 0, 1): "┘", (0, 1, 1, 0): "┌", (0, 0, 1, 1): "┐",
    (1, 1, 1, 0): "├", (1, 0, 1, 1): "┤", (0, 1, 1, 1): "┬", (1, 1, 0, 1): "┴", (1, 1, 1, 1): "┼",
    (1, 0, 0, 0): "╵", (0, 0, 1, 0): "╷", (0, 1, 0, 0): "╶", (0, 0, 0, 1): "╴",
}


def render_layer(res, layer):
    occ, edges = res["occ"], res["edges"]
    pins = {(x, y): n for n, ps in NETS for x, y in ps}
    out = []
    for y in range(H):
        s = ""
        for x in range(W):
            c = (layer, x, y)
            o = occ.get(c)
            if o == "#":
                both = occ.get((1 - layer, x, y)) == "#"
                s += paint("▓▓", fg=240) if both else paint("▒▒", fg=95)
                continue
            if o is None:
                s += paint(". ", fg=238)
                continue
            col = NET_COLOR[o]
            e = edges[o]
            N = frozenset((c, (layer, x, y - 1))) in e
            S = frozenset((c, (layer, x, y + 1))) in e
            E = frozenset((c, (layer, x + 1, y))) in e
            Wd = frozenset((c, (layer, x - 1, y))) in e
            has_via = frozenset((c, (1 - layer, x, y))) in e
            if layer == 0 and pins.get((x, y)) == o:
                ch = paint(o, fg=16, bg=col, bold=True)
            elif has_via:
                ch = paint("◉", fg=col, bold=True)
            else:
                ch = paint(GLYPH[(int(N), int(E), int(S), int(Wd))], fg=col, bold=True)
            s += ch + (paint("─", fg=col) if E else " ")
        out.append(s)
    return "\n".join(out)


# ------------------------------------------------------------------ main
def main():
    print(banner("IC CIRCUIT ROUTING  x  Lee / Dijkstra / A* / Steiner / net ordering"))
    print("  Routing is a core step of EDA (electronic design automation). It is usually split into")
    print("  global routing (rough plan) and detailed routing (exact wires on a grid).")
    print("  This program implements the heart of detailed routing: grid search that connects pins.")

    lee_demo()

    print(banner("B. Two-layer routing problem: the chip before routing"))
    base = {"occ": make_board(), "edges": {n: set() for n, _ in NETS}}
    print(paint("  M1 (horizontal preferred): ▒▒ = macro blocking M1 only (M2 may pass over), "
                "▓▓ = wall blocking both layers, letters = pins", fg=221))
    print(render_layer(base, 0))
    print("\n  Nets: " + "   ".join(
        paint(f"{n}", fg=16, bg=NET_COLOR[n], bold=True) + f" {len(p)} pins" for n, p in NETS))
    print("  Cost model: preferred step = 1, other-direction step = 3, via = 6 (M1 horizontal, M2 vertical).")

    # ---- C. ordering search + simplified rip-up and reroute
    names = [n for n, _ in NETS]
    t0 = time.perf_counter()
    all_results = [route_all(order, "astar") for order in itertools.permutations(names)]
    t_perm = time.perf_counter() - t0
    ok = [r for r in all_results if not r["failed"]]
    bad = [r for r in all_results if r["failed"]]
    print(banner("C. Does the routing order matter?  (net ordering and rip-up and reroute)"))
    print("  Two staggered walls squeeze the free space into an S-shaped channel: a net routed early")
    print("  can use up the narrow channel and block the nets routed later.")
    print(f"  Tried all {len(all_results)} orders (5!) in {t_perm:.2f}s -> "
          f"{len(ok)} orders connect every net, {len(bad)} orders leave a net blocked.")
    freq = {}
    for r in bad:
        for n in r["failed"]:
            freq[n] = freq.get(n, 0) + 1
    if freq:
        print("  Blocked nets (how often): " + "  ".join(
            paint(n, fg=16, bg=NET_COLOR[n], bold=True) + f" x{c}" for n, c in sorted(freq.items(), key=lambda kv: -kv[1])))
    if not ok:
        print("  No order connects every net.")
        return
    best = min(ok, key=lambda r: (r["cost"], r["vias"]))
    worst = max(ok, key=lambda r: (r["cost"], r["vias"]))
    default = route_all(names, "astar")
    print(f"\n  {'order':<12}{'cost':>7}{'wire':>7}{'vias':>6}   note")
    for label, r in (("default order", default), ("best order", best), ("worst that works", worst)):
        od = "->".join(r["order"])
        status = f"blocked: {','.join(r['failed'])}" if r["failed"] else "all nets connected"
        print(f"  {od:<12}{r['cost']:>7}{r['wirelength']:>7}{r['vias']:>6}   {label}: {status}")
    gap = worst["cost"] - best["cost"]
    print(paint(f"\n  -> Among the orders that work, total cost differs by up to {gap} ({gap / best['cost']:.0%}).", fg=214))

    start_order = bad[0]["order"] if bad else tuple(names)
    print(paint("\n  [Simplified rip-up and reroute] starting from an order that fails:", fg=221, bold=True))
    order = list(start_order)
    for it in range(1, 8):
        r = route_all(order, "astar")
        od = "->".join(order)
        if not r["failed"]:
            print(f"   round {it}: order {od}  {paint('OK, all connected', fg=46)}  (cost {r['cost']}, vias {r['vias']})")
            break
        f = r["failed"][0]
        print(f"   round {it}: order {od}  {paint('net ' + f + ' is blocked', fg=196)}"
              f" -> tear up everything, move {f} to the front, route again")
        order.remove(f)
        order.insert(0, f)
    print("  (Real tools rip up only the wires in the way and negotiate congestion, e.g. PathFinder.)")

    # ---- D. Dijkstra vs A*
    order = best["order"]
    ra = route_all(order, "astar")
    rd = route_all(order, "dijkstra")
    print(banner(f"D. Dijkstra vs A*  (order {'->'.join(order)})"))
    print(f"  {'net':<5}{'pins':>5}{'A* cost':>10}{'A* nodes':>10}{'Dij cost':>10}{'Dij nodes':>10}{'saved':>8}")
    pins_n = dict(NETS)
    for n in order:
        _, ca, ea = ra["per_net"][n]
        _, cd, ed = rd["per_net"][n]
        sv = f"{1 - ea / ed:.0%}" if ed else "-"
        print(f"  {paint(n, fg=NET_COLOR[n], bold=True):<5}{len(pins_n[n]):>5}{ca:>10}{ea:>10}{cd:>10}{ed:>10}{sv:>8}")
    print(f"  {'total':<5}{'':>5}{ra['cost']:>10}{ra['expanded']:>10}{rd['cost']:>10}{rd['expanded']:>10}"
          f"{1 - ra['expanded'] / rd['expanded']:>8.0%}")
    print(paint("  -> Every net gets the same minimum cost (the A* heuristic is admissible) but A* expands "
                "far fewer nodes.", fg=214))

    # ---- E. result
    print(banner(f"E. Best routing result (order {'->'.join(ra['order'])}): "
                 f"cost {ra['cost']}, wire length {ra['wirelength']}, vias {ra['vias']}"))
    print(paint("  M1 (horizontal preferred)  -  ◉ = via, letters = pins", fg=221))
    print(render_layer(ra, 0))
    print(paint("\n  M2 (vertical preferred; passes over ▒▒ macros but not through ▓▓ walls)", fg=221))
    print(render_layer(ra, 1))

    print("\n  Details per net:")
    for n in ra["order"]:
        ok_, c, e = ra["per_net"][n]
        es = ra["edges"][n]
        v = sum(1 for ed in es if len({p[0] for p in ed}) == 2)
        print(f"    {paint(n, fg=16, bg=NET_COLOR[n], bold=True)}  wire {len(es) - v:>3}  vias {v}  cost {c:>3}  "
              f"{'connected' if ok_ else 'BLOCKED'}  pins {pins_n[n]}")

    # ---- F. other methods
    print(banner("F. Other routing methods used in real IC design (see README)"))
    for k, v in [
        ("Lee / maze router", "BFS wave, shortest on one layer, O(W*H) memory (part A here)"),
        ("Hadlock", "improved Lee: counts detours instead of distance, narrower wave"),
        ("A* router", "adds a heuristic, part D here"),
        ("Line probe (Mikami-Tabuchi, Hightower)", "probes along straight lines: little memory, not always shortest"),
        ("Channel routing (left-edge)", "track assignment inside a regular channel"),
        ("Rip-up and reroute / PathFinder", "tear up congested wires, negotiate congestion"),
        ("Steiner tree", "minimum total wire for multi-pin nets (here: Prim-like growth)"),
        ("Global + detailed routing", "plan regions first, then route exact wires inside them"),
    ]:
        print(f"  * {paint(k, fg=51)}: {v}")


if __name__ == "__main__":
    main()