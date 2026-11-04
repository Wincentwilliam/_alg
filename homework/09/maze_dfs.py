#!/usr/bin/env python3
"""
Homework 9 (1/5): The mouse-in-a-maze problem, solved with DFS.

A mouse starts at the top-left corner and must find the cheese at the
bottom-right corner. DFS is implemented with an explicit stack (no recursion),
so a big maze can never cause a RecursionError.

What the program does:
  1. Generates a random maze (fixed seed, so it is repeatable) with the
     recursive-backtracker algorithm, then knocks out a few extra walls so the
     maze has loops. Loops are what make DFS return a non-shortest path.
  2. Runs DFS and records the visit order, the number of backtracks and the
     maximum stack size.
  3. Runs BFS on the same maze and compares the path lengths.

Usage:
  python maze_dfs.py                  # snapshots of the search
  python maze_dfs.py --animate        # animated search
  python maze_dfs.py --seed 3 --width 41 --height 19
"""
import argparse
import os
import random
import sys
import time
from collections import deque

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.system("")  # lets Windows terminals understand ANSI colors

USE_COLOR = not os.environ.get("NO_COLOR") and (
    sys.stdout.isatty() or os.environ.get("FORCE_COLOR")
)


def paint(text, fg=None, bg=None, bold=False):
    """Color helper (256-color ANSI). Does nothing when color is off."""
    if not USE_COLOR:
        return text
    codes = ""
    if bold:
        codes += "\033[1m"
    if fg is not None:
        codes += f"\033[38;5;{fg}m"
    if bg is not None:
        codes += f"\033[48;5;{bg}m"
    return f"{codes}{text}\033[0m"


# Direction order: up, right, down, left (the order DFS prefers to try)
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
DIR_NAME = {(0, -1): "U", (1, 0): "R", (0, 1): "D", (-1, 0): "L"}


# ------------------------------------------------------------------ maze
def generate_maze(w, h, seed, loops):
    """1 = wall, 0 = open. w and h must be odd."""
    rnd = random.Random(seed)
    g = [[1] * w for _ in range(h)]
    g[1][1] = 0
    stack = [(1, 1)]
    while stack:  # recursive backtracker (itself a DFS)
        x, y = stack[-1]
        nb = []
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            nx, ny = x + dx, y + dy
            if 0 < nx < w - 1 and 0 < ny < h - 1 and g[ny][nx] == 1:
                nb.append((dx, dy))
        if nb:
            dx, dy = rnd.choice(nb)
            g[y + dy // 2][x + dx // 2] = 0
            g[y + dy][x + dx] = 0
            stack.append((x + dx, y + dy))
        else:
            stack.pop()

    # knock out some walls -> several routes exist (loops)
    cand = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if g[y][x] == 1:
                horiz = g[y][x - 1] == 0 and g[y][x + 1] == 0 and g[y - 1][x] == 1 and g[y + 1][x] == 1
                vert = g[y - 1][x] == 0 and g[y + 1][x] == 0 and g[y][x - 1] == 1 and g[y][x + 1] == 1
                if horiz or vert:
                    cand.append((x, y))
    rnd.shuffle(cand)
    for x, y in cand[:loops]:
        g[y][x] = 0
    return g


# ------------------------------------------------------------------ search
def build_path(parent, goal):
    if goal not in parent:
        return []
    path, cur = [], goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return path[::-1]


def dfs(grid, start, goal):
    """
    DFS with an explicit stack.
    Returns: order (visit order), parent, path, backtracks, max_stack, trace.
    """
    stack = [(start, None)]
    parent, order, trace = {}, [], []
    backtracks, max_stack, last = 0, 1, None
    while stack:
        cur, par = stack.pop()
        if cur in parent:  # already visited
            continue
        parent[cur] = par
        if last is not None and par != last:
            backtracks += 1  # the previous cell was a dead end; we jumped back
        last = cur
        order.append(cur)
        if cur == goal:
            break
        x, y = cur
        pushed = 0
        # reversed(): push "up" last so it is popped first (up, right, down, left)
        for dx, dy in reversed(DIRS):
            n = (x + dx, y + dy)
            if grid[n[1]][n[0]] == 0 and n not in parent:
                stack.append((n, cur))
                pushed += 1
        if pushed != 1 and len(trace) < 10:  # record only junctions and dead ends
            trace.append((len(order), cur, pushed, len(stack)))
        max_stack = max(max_stack, len(stack))
    return {"order": order, "parent": parent, "path": build_path(parent, goal),
            "backtracks": backtracks, "max_stack": max_stack, "trace": trace}


def bfs(grid, start, goal):
    """BFS on the same maze, for comparison (always finds a shortest path)."""
    q = deque([start])
    parent = {start: None}
    order = []
    while q:
        cur = q.popleft()
        order.append(cur)
        if cur == goal:
            break
        x, y = cur
        for dx, dy in DIRS:
            n = (x + dx, y + dy)
            if grid[n[1]][n[0]] == 0 and n not in parent:
                parent[n] = cur
                q.append(n)
    return {"order": order, "parent": parent, "path": build_path(parent, goal)}


# ------------------------------------------------------------------ drawing
def render(grid, visited, path, mouse, cheese, start):
    out = []
    for y, row in enumerate(grid):
        s = ""
        for x, v in enumerate(row):
            p = (x, y)
            if p == mouse:
                s += "🐭"
            elif p == cheese:
                s += "🧀"
            elif p == start:
                s += "🚩"
            elif v == 1:
                s += paint("██", fg=60)
            elif p in path:
                s += paint("••", fg=226, bold=True)
            elif p in visited:
                s += paint("░░", fg=37)
            else:
                s += "  "
        out.append(s)
    return "\n".join(out)


def banner(title):
    line = "=" * 62
    return "\n" + paint(line, fg=39) + "\n" + paint("  " + title, fg=51, bold=True) + "\n" + paint(line, fg=39)


def animate(grid, order, start, goal, delay):
    visited = set()
    sys.stdout.write("\033[2J")
    for i, p in enumerate(order, 1):
        visited.add(p)
        head = paint(f" DFS searching... visited {i}/{len(order)} cells", fg=51)
        sys.stdout.write("\033[H" + head + "\n" + render(grid, visited, set(), p, goal, start) + "\n")
        sys.stdout.flush()
        time.sleep(delay)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description="Mouse in a maze (DFS)")
    ap.add_argument("--seed", type=int, default=7, help="random seed of the maze")
    ap.add_argument("--width", type=int, default=31, help="maze width (odd)")
    ap.add_argument("--height", type=int, default=15, help="maze height (odd)")
    ap.add_argument("--loops", type=int, default=14, help="extra walls removed (creates loops)")
    ap.add_argument("--animate", action="store_true", help="play an animation")
    ap.add_argument("--delay", type=float, default=0.03, help="seconds per cell in the animation")
    a = ap.parse_args()

    w, h = a.width | 1, a.height | 1
    grid = generate_maze(w, h, a.seed, a.loops)
    start, goal = (1, 1), (w - 2, h - 2)

    print(banner("MOUSE IN A MAZE  x  DFS (depth-first search)"))
    print(f"  maze size {w}x{h}, seed={a.seed}, extra loops={a.loops}")
    print(f"  start {start}  ->  goal {goal}\n")
    print(render(grid, set(), set(), start, goal, start))

    r = dfs(grid, start, goal)
    order = r["order"]

    print(banner("How the DFS stack behaves: first junctions / dead ends"))
    for step, cell, pushed, size in r["trace"]:
        kind = "JUNCTION " if pushed >= 2 else "DEAD END "
        note = f"pushed {pushed} new neighbours" if pushed else "nothing to push -> next pop jumps back"
        print(f"  cell #{step:>3} {cell!s:<8} {kind} {note}, stack now holds {size:>2}")
    print("  (every new cell pushes its unvisited neighbours; pop always takes the newest one)")

    if a.animate:
        animate(grid, order, start, goal, a.delay)
        print()
    else:
        for pct in (0.15, 0.5):
            k = max(1, int(len(order) * pct))
            print(banner(f"Snapshot: DFS at {int(pct * 100)}% of its search ({k}/{len(order)} cells)"))
            print(render(grid, set(order[:k]), set(), order[k - 1], goal, start))

    path = r["path"]
    print(banner("DFS found the cheese!  (.. = final path, shaded = visited but not on the path)"))
    print(render(grid, set(order), set(path), start, goal, start))

    b = bfs(grid, start, goal)
    print(banner("Statistics and DFS vs BFS"))
    print(f"  DFS cells visited     : {len(order)}")
    print(f"  DFS backtracks        : {r['backtracks']}   (times it jumped back after a dead end)")
    print(f"  DFS max stack size    : {r['max_stack']}")
    print(f"  DFS path length       : {len(path) - 1} steps")
    print(f"  BFS cells visited     : {len(b['order'])}")
    print(f"  BFS shortest path     : {len(b['path']) - 1} steps")
    extra = len(path) - len(b["path"])
    if extra > 0:
        print(paint(f"  -> DFS path is {extra} steps longer than the shortest path "
                    f"({extra / (len(b['path']) - 1):.0%}): DFS finds A path, not THE shortest.", fg=214))
    else:
        print(paint("  -> On this maze DFS happens to be shortest (try another --seed).", fg=214))

    moves = "".join(DIR_NAME[(x2 - x1, y2 - y1)] for (x1, y1), (x2, y2) in zip(path, path[1:]))
    print("\n  DFS path as moves (U/R/D/L):")
    print("  " + moves)


if __name__ == "__main__":
    main()