# Week 7: dynamic programming on text -- the diff problem via LCS.
#
# diff compares two texts and reports which lines were removed/added. The
# core of it is the Longest Common Subsequence (LCS): lines that are part
# of the LCS stay unchanged, everything else is a deletion or an addition.
#
# Three ways to compute the LCS:
#   lcs_naive : plain recursion, no memory            (NOT dynamic programming)
#   lcs_memo  : same recursion + a lookup table        (top-down DP)
#   lcs_dp    : fill a table row by row, no recursion  (bottom-up DP)

import random
import sys
import time


# ------------------------------------------------ 1. naive recursion
def lcs_naive(a, b):
    """Returns (length of LCS, number of recursive calls made)."""
    calls = 0

    def go(i, j):                      # LCS of a[i:] and b[j:]
        nonlocal calls
        calls += 1
        if i == len(a) or j == len(b):
            return 0
        if a[i] == b[j]:
            return 1 + go(i + 1, j + 1)
        return max(go(i + 1, j), go(i, j + 1))

    return go(0, 0), calls


# ------------------------------------------------ 2. top-down DP (memo)
def lcs_memo(a, b):
    """Same recursion, but every (i, j) is solved only once."""
    calls = 0
    cache = {}

    def go(i, j):
        nonlocal calls
        calls += 1
        if i == len(a) or j == len(b):
            return 0
        if (i, j) not in cache:
            if a[i] == b[j]:
                cache[(i, j)] = 1 + go(i + 1, j + 1)
            else:
                cache[(i, j)] = max(go(i + 1, j), go(i, j + 1))
        return cache[(i, j)]

    return go(0, 0), calls


# ------------------------------------------------ 3. bottom-up DP
def lcs_table(a, b):
    """dp[i][j] = LCS length of a[i:] and b[j:], filled from the end."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if a[i] == b[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    return dp


def lcs_dp(a, b):
    return lcs_table(a, b)[0][0]


def lcs_string(a, b):
    """Walk the table from the top-left to recover one actual LCS."""
    dp = lcs_table(a, b)
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            out.append(a[i])
            i, j = i + 1, j + 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            i += 1
        else:
            j += 1
    return out


# ------------------------------------------------ diff built on the table
def diff(old, new):
    """List of ('keep'|'del'|'add', line) turning `old` into `new`."""
    dp = lcs_table(old, new)
    i = j = 0
    ops = []
    while i < len(old) and j < len(new):
        if old[i] == new[j]:
            ops.append(('keep', old[i]))
            i, j = i + 1, j + 1
        elif dp[i + 1][j] >= dp[i][j + 1]:
            ops.append(('del', old[i]))
            i += 1
        else:
            ops.append(('add', new[j]))
            j += 1
    ops += [('del', line) for line in old[i:]]
    ops += [('add', line) for line in new[j:]]
    return ops


def print_diff(ops):
    mark = {'keep': '  ', 'del': '- ', 'add': '+ '}
    for kind, line in ops:
        print(mark[kind] + line)


# ------------------------------------------------ demo / benchmark
OLD = """def total(prices):
    result = 0
    for p in prices:
        result = result + p
    return result

print(total([1, 2, 3]))""".splitlines()

NEW = """def total(prices, tax=0):
    result = 0
    for p in prices:
        result += p
    result = result * (1 + tax)
    return result

print(total([1, 2, 3], 0.05))""".splitlines()


def benchmark():
    rng = random.Random(7)
    print(f"{'n':>4} {'naive calls':>13} {'naive sec':>10} {'memo calls':>11} "
          f"{'dp cells':>9} {'dp sec':>9}")
    # worst case for the naive version: no character in common, so every
    # branch of the recursion has to be explored
    for n in (4, 6, 8, 10, 12):
        a, b = 'A' * n, 'C' * n

        t = time.perf_counter()
        len1, calls1 = lcs_naive(a, b)
        t_naive = time.perf_counter() - t

        len2, calls2 = lcs_memo(a, b)

        t = time.perf_counter()
        len3 = lcs_dp(a, b)
        t_dp = time.perf_counter() - t

        assert len1 == len2 == len3
        print(f'{n:>4} {calls1:>13,} {t_naive:>10.4f} {calls2:>11,} '
              f'{(n + 1) ** 2:>9,} {t_dp:>9.6f}')

    # only the DP version can handle big inputs
    n = 1500
    a = ''.join(rng.choice('ACGT') for _ in range(n))
    b = ''.join(rng.choice('ACGT') for _ in range(n))
    t = time.perf_counter()
    length = lcs_dp(a, b)
    print(f'\nDP alone on two random strings of length {n}: '
          f'LCS = {length}, {time.perf_counter() - t:.2f} s '
          f'({(n + 1) ** 2:,} cells)')


def self_check():
    rng = random.Random(1)
    for _ in range(300):
        a = ''.join(rng.choice('ab') for _ in range(rng.randint(0, 8)))
        b = ''.join(rng.choice('ab') for _ in range(rng.randint(0, 8)))
        n1, _ = lcs_naive(a, b)
        n2, _ = lcs_memo(a, b)
        assert n1 == n2 == lcs_dp(a, b) == len(lcs_string(a, b))

    ops = diff(OLD, NEW)
    assert [l for k, l in ops if k != 'add'] == OLD
    assert [l for k, l in ops if k != 'del'] == NEW
    return True


if __name__ == '__main__':
    if len(sys.argv) == 3:                       # python lcs_diff.py old.txt new.txt
        with open(sys.argv[1], encoding='utf-8') as f1, \
                open(sys.argv[2], encoding='utf-8') as f2:
            print_diff(diff(f1.read().splitlines(), f2.read().splitlines()))
        sys.exit()

    print('== LCS of two strings ==')
    a, b = 'AGGTAB', 'GXTXAYB'
    print(f'a = {a}, b = {b}')
    print('naive :', lcs_naive(a, b))
    print('memo  :', lcs_memo(a, b))
    print('dp    :', lcs_dp(a, b), '->', ''.join(lcs_string(a, b)))

    print('\n== diff of two versions of a small program ==')
    print_diff(diff(OLD, NEW))

    print('\n== naive recursion vs dynamic programming ==')
    benchmark()

    print('\nself-check (300 random pairs, diff reconstructs both files):',
          'passed' if self_check() else 'FAILED')