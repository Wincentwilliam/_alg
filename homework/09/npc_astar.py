#!/usr/bin/env python3
"""
Homework 9 (4/5): An NPC that searches for the player, solved with A*.

Scenario: a game map has walls, grass, forest and swamp. An NPC (👹) hunts a
player (🧑) who runs away. Every tick the NPC re-plans an A* path to the
player's current position and walks one step along it.

A* in one line:  f(n) = g(n) + h(n)
  g(n) = real cost from the start to n (grass 1, forest 2, swamp 5; diagonal x sqrt2)
  h(n) = estimated cost from n to the goal (octile distance, never overestimates)
  -> always finds the cheapest path, and expands far fewer nodes than Dijkstra.

Features:
  * 8-direction movement, no cutting through wall corners
  * terrain costs, so the cheapest path is not always the shortest one
  * a chase simulation with re-planning at every tick
  * A* vs Dijkstra vs Greedy best-first on the same query

Usage:  python npc_astar.py              # snapshots
        python npc_astar.py --animate    # animation
"""
import argparse
import heapq
import math
import os
import sys
import time

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
    line = "=" * 70
    return "\n" + paint(line, fg=39) + "\n" + paint("  " + title, fg=51, bold=True) + "\n" + paint(line, fg=39)


# ------------------------------------------------------------------ map
W, H = 34, 17
COST = {".": 1.0, ",": 2.0, "~": 5.0}   # grass / forest / swamp ('#' = wall)
SQRT2 = math.sqrt(2)


def build_map():
    g = [["."] * W for _ in range(H)]

    def rect(x1, y1, x2, y2, ch):
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                g[y][x] = ch

    rect(0, 0, W - 1, 0, "#"); rect(0, H - 1, W - 1, H - 1, "#")
    rect(0, 0, 0, H - 1, "#"); rect(W - 1, 0, W - 1, H - 1, "#")
    rect(3, 11, 7, 15, ",")        # south-west forest
    rect(28, 2, 32, 6, ",")        # north-east forest
    rect(11, 9, 21, 13, "~")       # big central swamp (shortcut but expensive)
    rect(9, 2, 10, 9, "#")         # long wall on the left
    rect(9, 12, 10, 15, "#")       # lower-left wall (gap at rows 10-11)
    rect(14, 4, 14, 7, "#")        # central vertical wall
    rect(14, 4, 23, 5, "#")        # central horizontal wall
    rect(26, 9, 27, 15, "#")       # right wall
    rect(18, 7, 19, 7, "#")
    return g


GRID = build_map()


def passable(x, y):
    return 0 <= x < W and 0 <= y < H and GRID[y][x] != "#"


# ------------------------------------------------------------------ search
def octile(a, b):
    """Admissible heuristic (the cheapest terrain costs 1, so this never overestimates)."""
    dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
    return (dx + dy) + (SQRT2 - 2) * min(dx, dy)


def neighbors(p):
    x, y = p
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if not passable(nx, ny):
                continue
            if dx != 0 and dy != 0:   # diagonal move: both side squares must be free
                if not (passable(x + dx, y) and passable(x, y + dy)):
                    continue
            step = SQRT2 if (dx and dy) else 1.0
            yield (nx, ny), step * COST[GRID[ny][nx]]


def search(start, goal, mode="astar"):
    """
    mode 'astar'    : f = g + h
         'dijkstra' : f = g          (h = 0)
         'greedy'   : f = h          (fast, but not guaranteed optimal)
    Returns dict: path, cost, expanded (nodes expanded), closed (expanded set).
    """
    def f_of(g, p):
        h = octile(p, goal)
        return {"astar": g + h, "dijkstra": g, "greedy": h}[mode]

    open_heap = [(f_of(0, start), 0, start)]
    g_score = {start: 0.0}
    parent = {start: None}
    closed = set()
    counter = 0                     # tie-breaker so tuples never compare positions
    while open_heap:
        _, _, cur = heapq.heappop(open_heap)
        if cur in closed:
            continue
        closed.add(cur)
        if cur == goal:
            break
        for nb, c in neighbors(cur):
            ng = g_score[cur] + c
            if ng < g_score.get(nb, float("inf")):
                g_score[nb] = ng
                parent[nb] = cur
                counter += 1
                heapq.heappush(open_heap, (f_of(ng, nb), counter, nb))
    if goal not in parent:
        return {"path": [], "cost": float("inf"), "expanded": len(closed), "closed": closed}
    path, cur = [], goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return {"path": path[::-1], "cost": g_score[goal], "expanded": len(closed), "closed": closed}


# ------------------------------------------------------------------ drawing
def render(npc, player, path=(), closed=()):
    path_set, closed_set = set(path), set(closed)
    lines = []
    for y in range(H):
        s = ""
        for x in range(W):
            p = (x, y)
            ch = GRID[y][x]
            if p == npc:
                s += "👹"
                continue
            if p == player:
                s += "🧑"
                continue
            if ch == "#":
                s += paint("▓▓", fg=244, bg=238)
                continue
            base_bg = {".": 22, ",": 28, "~": 24}[ch]
            if p in closed_set:
                base_bg = {".": 58, ",": 64, "~": 60}[ch]     # expanded by the search -> yellowish
            if p in path_set:
                s += paint("••", fg=226, bg=base_bg, bold=True)
            elif ch == ",":
                s += paint("♣♣", fg=34 if p not in closed_set else 70, bg=base_bg)
            elif ch == "~":
                s += paint("≈≈", fg=117, bg=base_bg)
            elif p in closed_set:
                s += paint("  " if USE_COLOR else "░░", bg=base_bg)
            else:
                s += paint("  " if USE_COLOR else ". ", bg=base_bg)
        lines.append(s)
    return "\n".join(lines)


def legend():
    return ("  legend: " + paint("  ", bg=22) + "grass(1)  " + paint("♣♣", fg=34, bg=28) + "forest(2)  "
            + paint("≈≈", fg=117, bg=24) + "swamp(5)  " + paint("▓▓", fg=244, bg=238) + "wall  "
            + paint("••", fg=226, bold=True) + "A* path  " + paint("  ", bg=58) + "expanded cells  "
            + "👹 NPC  🧑 player")


# ------------------------------------------------------------------ simulation
SAFE_SPOTS = [(1, 1), (1, 15), (8, 15), (12, 1), (25, 1), (32, 1), (32, 15), (32, 8), (25, 15), (13, 8), (24, 8)]


def pick_escape(player, npc):
    """
    Player AI: among a few safe spots choose the one with the best
    (NPC cost - 1.5 * player cost). Both costs are computed with A* too.
    """
    best, best_score = None, -1e9
    for spot in SAFE_SPOTS:
        if spot == player or not passable(*spot):
            continue
        d_npc = search(npc, spot, "astar")["cost"]
        d_me = search(player, spot, "astar")["cost"]
        score = d_npc - 1.5 * d_me
        if score > best_score:
            best, best_score = spot, score
    return best


def simulate(npc0, player0, player_period=2, catch_dist=1, max_ticks=300):
    """
    The NPC moves 1 step per tick; the player moves 1 step every player_period ticks.
    The player picks a new escape spot every 6 steps (or when it arrives).
    """
    npc, player = npc0, player0
    player_path, steps_since_pick = [], 99
    frames, stats = [], {"replans": 0, "expanded": 0, "expanded_dij": 0}
    for tick in range(max_ticks):
        if tick % player_period == 0:
            if not player_path or steps_since_pick >= 6:
                target = pick_escape(player, npc)
                player_path = search(player, target, "astar")["path"][1:]
                steps_since_pick = 0
            if player_path:
                player = player_path.pop(0)
                steps_since_pick += 1
        r = search(npc, player, "astar")             # NPC re-plans every tick
        stats["replans"] += 1
        stats["expanded"] += r["expanded"]
        stats["expanded_dij"] += search(npc, player, "dijkstra")["expanded"]
        frames.append({"tick": tick, "npc": npc, "player": player, "path": r["path"],
                       "closed": r["closed"], "cost": r["cost"], "expanded": r["expanded"]})
        if max(abs(npc[0] - player[0]), abs(npc[1] - player[1])) <= catch_dist:
            return frames, stats, True
        if len(r["path"]) >= 2:
            npc = r["path"][1]
    return frames, stats, False


def show_frame(fr, extra=""):
    head = paint(f" tick {fr['tick']:>3}", fg=51, bold=True) \
        + f"  NPC{fr['npc']}  player{fr['player']}  remaining A* cost {fr['cost']:.1f}  " \
          f"expanded {fr['expanded']} cells {extra}"
    return head + "\n" + render(fr["npc"], fr["player"], fr["path"], fr["closed"])


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description="NPC hunts the player (A*)")
    ap.add_argument("--animate", action="store_true")
    ap.add_argument("--delay", type=float, default=0.12)
    ap.add_argument("--every", type=int, default=8, help="snapshot mode: print one frame every N ticks")
    a = ap.parse_args()

    npc0, player0 = (2, 2), (30, 14)

    print(banner("NPC HUNTS THE PLAYER  x  A* search"))
    print(legend())
    print(f"\n  map {W}x{H}; NPC starts at {npc0}, player at {player0}; 8 directions, no corner cutting.")
    print(render(npc0, player0))

    print(banner("1. One query, three algorithms (NPC -> player's start position)"))
    results = {m: search(npc0, player0, m) for m in ("astar", "dijkstra", "greedy")}
    best = results["dijkstra"]["cost"]
    print(f"  {'algorithm':<12}{'path cost':>10}{'optimal?':>12}{'expanded':>10}{'path cells':>12}")
    for mode, label in (("astar", "A*"), ("dijkstra", "Dijkstra"), ("greedy", "Greedy BFS")):
        r = results[mode]
        opt = "yes" if abs(r["cost"] - best) < 1e-9 else f"no (+{r['cost'] - best:.1f})"
        print(f"  {label:<12}{r['cost']:>10.2f}{opt:>12}{r['expanded']:>10}{len(r['path']):>12}")
    save = 1 - results["astar"]["expanded"] / results["dijkstra"]["expanded"]
    print(paint(f"\n  -> A* and Dijkstra both find the cheapest path, but A* expands {save:.0%} fewer nodes. "
                "Greedy is fastest here but takes a much more expensive route.", fg=214))

    print(banner("2. What A* explores (yellowish = expanded cells, .. = chosen path)"))
    print(show_frame({"tick": 0, "npc": npc0, "player": player0, "path": results["astar"]["path"],
                      "closed": results["astar"]["closed"], "cost": results["astar"]["cost"],
                      "expanded": results["astar"]["expanded"]}))
    print()
    print(paint("  For comparison, Dijkstra has no heuristic and spreads out like a wave:", fg=244))
    print(render(npc0, player0, results["dijkstra"]["path"], results["dijkstra"]["closed"]))

    print(banner("3. Chase: the player runs away (also using A*), the NPC re-plans every tick"))
    frames, stats, caught = simulate(npc0, player0)

    if a.animate:
        sys.stdout.write("\033[2J")
        for fr in frames:
            sys.stdout.write("\033[H" + show_frame(fr) + "\n" + " " * 100 + "\n")
            sys.stdout.flush()
            time.sleep(a.delay)
    else:
        picks = list(range(0, len(frames), a.every))
        if (len(frames) - 1) not in picks:
            picks.append(len(frames) - 1)
        for i in picks:
            print()
            print(show_frame(frames[i], extra="<- caught!" if i == len(frames) - 1 and caught else ""))

    last = frames[-1]
    print(banner("Chase result and statistics"))
    if caught:
        print(paint(f"  The NPC caught the player at tick {last['tick']}!", fg=196, bold=True))
    else:
        print(paint("  The player escaped (max ticks reached).", fg=46, bold=True))
    print(f"  re-plans                 : {stats['replans']}")
    print(f"  A* nodes expanded (all)  : {stats['expanded']:,}  (avg {stats['expanded'] / stats['replans']:.0f} per plan)")
    print(f"  Dijkstra would expand    : {stats['expanded_dij']:,}  (avg {stats['expanded_dij'] / stats['replans']:.0f} per plan)")
    print(f"  A* saved                 : {1 - stats['expanded'] / stats['expanded_dij']:.0%} of the search work")
    print("\n  Key point: the closer h(n) is to the real cost, the fewer nodes A* expands;")
    print("  as long as h never overestimates, the path is still optimal.")


if __name__ == "__main__":
    main()