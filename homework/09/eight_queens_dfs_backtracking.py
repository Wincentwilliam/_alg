#!/usr/bin/env python3
"""
Homework 9 (3/5): The eight queens problem, solved with DFS + backtracking.

Place 8 queens on an 8x8 board so that no two share a row, column or diagonal.

Modelling:
  search tree : level r decides the column of the queen in row r, so the
                "same row" conflict can never happen.
  pruning     : three sets give an O(1) conflict check
                cols = used columns, d1 = used (r - c) diagonals,
                d2 = used (r + c) diagonals
  DFS         : place a queen, go to the next row; if no square is free,
                backtrack (undo the last queen and try its next column).

What is printed:
  1. the first search steps (place / undo) and the deepest dead end
  2. the first solution
  3. all 92 solutions grouped by symmetry into 12 fundamental solutions
  4. a table for N = 4..10 (solutions, DFS nodes, time)

Usage:  python eight_queens.py         # N = 8
        python eight_queens.py -n 6    # other board sizes
"""
import argparse
import os
import sys
import time
from math import comb

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
    line = "=" * 66
    return "\n" + paint(line, fg=39) + "\n" + paint("  " + title, fg=51, bold=True) + "\n" + paint(line, fg=39)


# ------------------------------------------------------------------ DFS + backtracking
def solve(n, record_trace=False):
    """
    Returns a dict:
      solutions   : all solutions; solution[r] = column of the queen in row r
      nodes       : number of successful placements (DFS nodes)
      first_nodes : nodes expanded when the first solution was found
      trace       : events before the first solution (if record_trace)
      deepest     : the deepest dead end before the first solution
    """
    cols, d1, d2 = set(), set(), set()
    board = [-1] * n
    sols = []
    st = {"nodes": 0, "first": None, "trace": [], "deepest": (-1, None)}

    def dfs(r):
        if r == n:                       # all queens placed -> a solution
            sols.append(tuple(board))
            if st["first"] is None:
                st["first"] = st["nodes"]
            return
        placed_any = False
        for c in range(n):
            if c in cols or (r - c) in d1 or (r + c) in d2:
                continue                  # pruning: this square is attacked
            placed_any = True
            board[r] = c                  # choose
            cols.add(c); d1.add(r - c); d2.add(r + c)
            st["nodes"] += 1
            if record_trace and st["first"] is None:
                st["trace"].append(("place", r, c))
            dfs(r + 1)
            cols.discard(c); d1.discard(r - c); d2.discard(r + c)   # un-choose
            board[r] = -1
            if record_trace and st["first"] is None:
                st["trace"].append(("undo", r, c))
        if not placed_any and st["first"] is None and r > st["deepest"][0]:
            st["deepest"] = (r, board[:])   # no free square in row r = dead end
            if record_trace:
                st["trace"].append(("dead", r, -1))

    dfs(0)
    return {"solutions": sols, "nodes": st["nodes"], "first_nodes": st["first"],
            "trace": st["trace"], "deepest": st["deepest"]}


# ------------------------------------------------------------------ symmetry
def to_solution(pos, n):
    arr = [0] * n
    for r, c in pos:
        arr[r] = c
    return tuple(arr)


def symmetries(sol):
    """The 8 symmetric variants (4 rotations x optional mirror) of a solution."""
    n = len(sol)
    cur = [(r, c) for r, c in enumerate(sol)]
    variants = set()
    for _ in range(4):
        cur = [(c, n - 1 - r) for r, c in cur]                          # rotate 90 degrees
        variants.add(to_solution(cur, n))
        variants.add(to_solution([(r, n - 1 - c) for r, c in cur], n))  # mirror
    return variants


def fundamental(solutions):
    """Group solutions into symmetry classes: {representative: all members}."""
    seen, groups = set(), {}
    for s in solutions:
        if s in seen:
            continue
        cls = symmetries(s)
        groups[min(cls)] = sorted(cls)
        seen |= cls
    return groups


# ------------------------------------------------------------------ drawing
def board_lines(sol, n, show_attacks=False, mini=False):
    """sol[r] = column of the queen in row r, or -1 if the row is still empty."""
    lines = []
    attacked = set()
    if show_attacks:
        for r, c in enumerate(sol):
            if c >= 0:
                for rr in range(n):
                    for cc in range(n):
                        if rr == r or cc == c or abs(rr - r) == abs(cc - c):
                            attacked.add((rr, cc))
    for r in range(n):
        row = "" if mini else paint(f"{r + 1:>2} ", fg=244)
        for c in range(n):
            light = (r + c) % 2 == 0
            bg = 252 if light else 66
            if (r, c) in attacked and sol[r] != c:
                bg = 217 if light else 131       # attacked squares turn red
            if sol[r] == c:
                row += paint("Q ", fg=16 if light else 231, bg=bg, bold=True)
            else:
                row += paint("  " if USE_COLOR else ". ", bg=bg)
        lines.append(row)
    if not mini:
        lines.append("   " + " ".join(chr(ord("a") + c) for c in range(n)))
    return lines


def side_by_side(blocks, gap="   "):
    h = max(len(b) for b in blocks)
    return "\n".join(gap.join(b[i] if i < len(b) else " " * 16 for b in blocks) for i in range(h))


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description="N queens (DFS + backtracking)")
    ap.add_argument("-n", type=int, default=8, help="board size, default 8")
    ap.add_argument("--trace", type=int, default=28, help="how many search events to show")
    a = ap.parse_args()
    n = a.n

    print(banner(f"{n} QUEENS  x  DFS + backtracking"))
    print(f"  Brute force: choose {n} squares of {n * n} = C({n * n},{n}) = {comb(n * n, n):,} boards.")
    print(f"  One queen per row: {n}^{n} = {n ** n:,} boards - still a lot.")
    print("  DFS + pruning: drop a whole subtree as soon as there is a conflict.")

    t0 = time.perf_counter()
    res = solve(n, record_trace=True)
    dt = (time.perf_counter() - t0) * 1000
    sols = res["solutions"]

    print(banner("1. Search trace (place / undo / dead end), indentation = depth"))
    label = {"place": paint("place Q", fg=46), "undo": paint("undo   ", fg=208), "dead": paint("DEAD END", fg=196)}
    for kind, r, c in res["trace"][: a.trace]:
        where = f"row {r + 1}" + (f", column {chr(97 + c)}" if c >= 0 else "")
        print(f"  {'  ' * r}{label[kind]} {where}")
    rest = len(res["trace"]) - a.trace
    if rest > 0:
        print(paint(f"  ... {rest} more events until the first solution ...", fg=244))
    print(f"\n  DFS made {res['first_nodes']} placements before it found the first solution.")

    depth, partial = res["deepest"]
    if partial:
        print(paint(f"\n  Deepest dead end before the first solution (row {depth + 1} has no free square; "
                    "red = attacked):", fg=214))
        print("\n".join(board_lines(partial, n, show_attacks=True)))

    first = sols[0]
    print(banner("2. The first solution (first one DFS finds: top row, leftmost column first)"))
    print("\n".join(board_lines(first, n)))
    print("  positions (row->column): " + "  ".join(f"{r + 1}->{chr(97 + c)}" for r, c in enumerate(first)))
    print("  as an array  solution[r] =", list(first))

    print(banner(f"3. All solutions: {len(sols)} found, {res['nodes']:,} DFS nodes, {dt:.2f} ms"))
    groups = fundamental(sols)
    print(f"  Grouped by rotation / mirror symmetry -> {len(groups)} fundamental solutions")
    sizes = {}
    for rep, cls in groups.items():
        sizes[len(cls)] = sizes.get(len(cls), 0) + 1
    parts = [f"{v} classes x {k} variants" for k, v in sorted(sizes.items(), reverse=True)]
    check = " + ".join(f"{k}*{v}" for k, v in sorted(sizes.items(), reverse=True))
    print(f"  Made of: {', '.join(parts)}   (check: {check} = {sum(k * v for k, v in sizes.items())})\n")

    reps = sorted(groups)
    per_row = 4 if n <= 8 else 3
    for i in range(0, len(reps), per_row):
        chunk = reps[i: i + per_row]
        blocks = []
        for j, rep in enumerate(chunk, i + 1):
            title = paint(f"#{j:<2} x{len(groups[rep])} variants".ljust(2 * n), fg=221)
            blocks.append([title] + board_lines(rep, n, mini=True))
        print(side_by_side(blocks))
        print()

    print(banner("4. Scaling: more queens -> many more solutions, search grows fast"))
    print(f"  {'N':>3} | {'solutions':>9} | {'fundamental':>11} | {'DFS nodes':>10} | {'N^N':>16} | {'ms':>7}")
    print("  " + "-" * 3 + "-+-" + "-" * 9 + "-+-" + "-" * 11 + "-+-" + "-" * 10 + "-+-" + "-" * 16 + "-+-" + "-" * 7)
    for k in range(4, 11):
        t0 = time.perf_counter()
        r = solve(k)
        ms = (time.perf_counter() - t0) * 1000
        f = len(fundamental(r["solutions"]))
        mark = "  <-" if k == n else ""
        print(f"  {k:>3} | {len(r['solutions']):>9} | {f:>11} | {r['nodes']:>10,} | {k ** k:>16,} | {ms:>7.1f}{mark}")

    print(f"\n  Key point: for N={n} DFS expands only {res['nodes']:,} nodes, far less than "
          f"{n}^{n} = {n ** n:,}. That is the power of pruning.")


if __name__ == "__main__":
    main()