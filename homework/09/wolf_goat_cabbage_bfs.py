#!/usr/bin/env python3
"""
Homework 9 (2/5): Wolf, goat and cabbage river crossing, solved with BFS.

A farmer must carry a wolf, a goat and a cabbage from the left bank to the
right bank. The boat holds the farmer plus at most one item. If the farmer is
not present, the wolf eats the goat and the goat eats the cabbage.
What is the smallest number of crossings?

Modelling:
  state  = (farmer, wolf, goat, cabbage), each 0 = left bank, 1 = right bank
           -> 2^4 = 16 states, of which 10 are legal (nobody gets eaten)
  action = the farmer crosses alone, or with one item on his own bank
  start  = (0,0,0,0) = LLLL        goal = (1,1,1,1) = RRRR

Why BFS?  Every crossing costs 1, and BFS expands the state graph layer by
layer, so the first time it reaches the goal is a shortest solution. This
program also stores ALL shortest parents, so it can list every shortest
solution, not just one.

Usage:  python wolf_goat_cabbage.py
"""
import os
import sys
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


NAMES = ["farmer", "wolf", "goat", "cabbage"]
EMOJI = ["👨", "🐺", "🐐", "🥬"]
START, GOAL = (0, 0, 0, 0), (1, 1, 1, 1)


# ------------------------------------------------------------------ model
def is_valid(s):
    f, w, g, c = s
    if w == g != f:   # wolf and goat alone together
        return False
    if g == c != f:   # goat and cabbage alone together
        return False
    return True


def neighbors(s):
    """Returns [(next_state, index_of_carried_item_or_None)]."""
    f = s[0]
    res = []
    ns = list(s)
    ns[0] = 1 - f
    res.append((tuple(ns), None))                 # farmer crosses alone
    for i in (1, 2, 3):                           # carry wolf / goat / cabbage
        if s[i] == f:                             # item must be on the farmer's bank
            ns = list(s)
            ns[0] = 1 - f
            ns[i] = 1 - f
            res.append((tuple(ns), i))
    return [(n, i) for n, i in res if is_valid(n)]


def tag(s):
    """Short form: L/R per object, e.g. RLRL = farmer R, wolf L, goat R, cabbage L."""
    return "".join("LR"[v] for v in s)


# ------------------------------------------------------------------ BFS
def bfs_all_shortest(start):
    """BFS that keeps every parent on a shortest path to each state."""
    dist = {start: 0}
    parents = {start: []}
    layers = [[start]]
    q = deque([start])
    expanded = 0
    while q:
        u = q.popleft()
        expanded += 1
        for v, item in neighbors(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                parents[v] = [(u, item)]
                q.append(v)
                while len(layers) <= dist[v]:
                    layers.append([])
                layers[dist[v]].append(v)
            elif dist[v] == dist[u] + 1:
                parents[v].append((u, item))   # another equally short way in
    return dist, parents, layers, expanded


def enumerate_paths(parents, start, goal):
    """Walk back from goal through all parents -> every shortest path."""
    results = []

    def back(node, acc):
        if node == start:
            results.append([(start, None)] + acc[::-1])
            return
        for p, item in parents[node]:
            back(p, acc + [(node, item)])

    back(goal, [])
    return results


# ------------------------------------------------------------------ drawing
def scene(s):
    left = [EMOJI[i] if s[i] == 0 else "  " for i in range(4)]
    right = [EMOJI[i] if s[i] == 1 else "  " for i in range(4)]
    boat_l = "🛶" if s[0] == 0 else "  "
    boat_r = "🛶" if s[0] == 1 else "  "
    river = paint("~~~~~~~~~~", fg=39)
    return f"[{' '.join(left)}] {boat_l}{river}{boat_r} [{' '.join(right)}]"


def banner(title):
    line = "=" * 66
    return "\n" + paint(line, fg=39) + "\n" + paint("  " + title, fg=51, bold=True) + "\n" + paint(line, fg=39)


def describe(prev, item):
    direction = "left -> right" if prev[0] == 0 else "right -> left"
    if item is None:
        return f"farmer crosses alone ({direction})"
    return f"farmer carries the {NAMES[item]} {EMOJI[item]} ({direction})"


def print_solution(idx, path):
    print(banner(f"Solution #{idx}: {len(path) - 1} crossings"))
    print(f"  start  {scene(path[0][0])}")
    for step, ((prev, _), (cur, item)) in enumerate(zip(path, path[1:]), 1):
        print()
        print(paint(f"  move {step}: {describe(prev, item)}", fg=221))
        print(f"         {scene(cur)}    {paint(tag(cur), fg=244)}")
    print(paint("\n  Everyone arrived safely on the right bank!", fg=46, bold=True))


# ------------------------------------------------------------------ main
def main():
    print(banner("WOLF, GOAT AND CABBAGE  x  BFS (breadth-first search)"))
    print("  Rules: the boat carries the farmer + at most one item;")
    print("         alone together, the wolf eats the goat and the goat eats the cabbage.")
    print("  State = (farmer, wolf, goat, cabbage);  L = left bank, R = right bank\n")

    all_states = [(a, b, c, d) for a in (0, 1) for b in (0, 1) for c in (0, 1) for d in (0, 1)]
    valid = [s for s in all_states if is_valid(s)]
    invalid = [s for s in all_states if not is_valid(s)]
    print(f"  Total states 2^4 = {len(all_states)}: {len(valid)} legal, {len(invalid)} illegal.")
    print("  Illegal states (somebody gets eaten):")
    for s in invalid:
        f, w, g, c = s
        why = []
        if w == g != f:
            why.append("wolf eats goat")
        if g == c != f:
            why.append("goat eats cabbage")
        print(f"    {paint(tag(s), fg=196)}  {' + '.join(why)}")

    dist, parents, layers, expanded = bfs_all_shortest(START)
    print(banner("BFS layers (layer k = k crossings from the start)"))
    for k, layer in enumerate(layers):
        bar = "  ".join(paint(tag(s), fg=51 if s != GOAL else 46, bold=(s == GOAL)) for s in layer)
        print(f"  layer {k} ({len(layer)} state{'s' if len(layer) != 1 else ''}): {bar}")
    print(f"\n  BFS expanded {expanded} nodes; reachable legal states = {len(dist)} / {len(valid)}")

    print(banner("State-space graph (edge = one legal crossing)"))
    for s in sorted(dist, key=lambda x: dist[x]):
        outs = [tag(v) for v, _ in neighbors(s)]
        print(f"  [{dist[s]}] {tag(s)} --> {', '.join(outs)}")

    paths = enumerate_paths(parents, START, GOAL)
    print(banner(f"RESULT: minimum = {dist[GOAL]} crossings, {len(paths)} different shortest solutions"))
    for i, p in enumerate(paths, 1):
        print_solution(i, p)

    if len(paths) == 2:
        print(banner("What the two solutions have in common"))
        print("  Both take the goat first and bring it back on move 4 (the trick of the puzzle).")
        print("  They differ only in the order of wolf and cabbage, which never hurt each other.")


if __name__ == "__main__":
    main()