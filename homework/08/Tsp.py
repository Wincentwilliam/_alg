# Week 8: the Traveling Salesman Problem solved with five optimization methods.
#
#   1. improvement (改良法)     systematic 2-opt: always take the best fix until none is left
#   2. hill climbing (爬山)     random 2-opt move, keep it only if the tour got shorter
#   3. simulated annealing      same moves, but sometimes accept a worse tour (less and less often)
#   4. gradient descent         elastic net: a rubber ring pulled towards the cities by gradient steps
#   5. greedy (貪婪)            always walk to the nearest unvisited city
#
# For reference there is also an exact solver (Held-Karp, dynamic programming)
# that is only practical for about 15 cities or fewer.
#
# Pure Python, no third-party packages. A plot is saved only if matplotlib exists.

import math
import random
import sys
import time


# ----------------------------------------------------------- basics
def make_cities(n, seed):
    rng = random.Random(seed)
    return [(rng.random(), rng.random()) for _ in range(n)]


def dist_matrix(cities):
    return [[math.dist(a, b) for b in cities] for a in cities]


def tour_length(tour, D):
    n = len(tour)
    return sum(D[tour[i]][tour[(i + 1) % n]] for i in range(n))


def two_opt_delta(tour, D, i, k):
    """Change in length if tour[i..k] is reversed (needs 1 <= i < k <= n-1)."""
    n = len(tour)
    a, b = tour[i - 1], tour[i]
    c, d = tour[k], tour[(k + 1) % n]
    return D[a][c] + D[b][d] - D[a][b] - D[c][d]


# ----------------------------------------------------------- 5. greedy
def greedy(D, start=0):
    tour = [start]
    left = set(range(len(D))) - {start}
    while left:
        last = tour[-1]
        nxt = min(left, key=lambda c: D[last][c])
        tour.append(nxt)
        left.remove(nxt)
    return tour


# ----------------------------------------------------------- 1. improvement
def improve(tour, D):
    """Look at every possible 2-opt move, apply the best one, repeat."""
    tour = tour[:]
    n = len(tour)
    rounds = 0
    while True:
        best_delta, best_move = -1e-12, None
        for i in range(1, n - 1):
            for k in range(i + 1, n):
                delta = two_opt_delta(tour, D, i, k)
                if delta < best_delta:
                    best_delta, best_move = delta, (i, k)
        if best_move is None:
            return tour, rounds
        i, k = best_move
        tour[i:k + 1] = reversed(tour[i:k + 1])
        rounds += 1


# ----------------------------------------------------------- 2. hill climbing
def hill_climb(tour, D, rng, steps=20000):
    tour = tour[:]
    n = len(tour)
    for _ in range(steps):
        i, k = sorted(rng.sample(range(1, n), 2))
        if two_opt_delta(tour, D, i, k) < 0:
            tour[i:k + 1] = reversed(tour[i:k + 1])
    return tour


# ----------------------------------------------------------- 3. simulated annealing
def anneal(tour, D, rng, steps=20000, t_start=0.5, t_end=0.001):
    tour = tour[:]
    n = len(tour)
    cur = tour_length(tour, D)
    best, best_len = tour[:], cur
    cooling = (t_end / t_start) ** (1 / steps)
    t = t_start
    for _ in range(steps):
        i, k = sorted(rng.sample(range(1, n), 2))
        delta = two_opt_delta(tour, D, i, k)
        # a worse tour is accepted with probability exp(-delta / t)
        if delta < 0 or rng.random() < math.exp(-delta / t):
            tour[i:k + 1] = reversed(tour[i:k + 1])
            cur += delta
            if cur < best_len - 1e-12:
                best, best_len = tour[:], cur
        t *= cooling
    return best


# ----------------------------------------------------------- 4. gradient descent
def gradient_descent(cities, rng, alpha=0.2, beta=2.0, k_start=0.2, k_end=0.01):
    """
    Elastic net (Durbin & Willshaw). A closed ring of m points y_j is moved
    to minimise the energy
        E = -alpha*K * sum_i ln( sum_j exp(-|x_i - y_j|^2 / (2K^2)) )
            + beta/2 * sum_j |y_{j+1} - y_j|^2
    The first term pulls the ring towards every city x_i, the second one keeps
    the ring short and smooth. Each step moves y_j by K * (-dE/dy_j), which is
    plain gradient descent with learning rate K; K shrinks slowly, so the ring
    first finds the rough shape and then sticks to individual cities.
    Afterwards every city is read off at its nearest ring point.
    """
    n = len(cities)
    m = 3 * n
    cx = sum(x for x, _ in cities) / n
    cy = sum(y for _, y in cities) / n
    ring = [[cx + 0.1 * math.cos(2 * math.pi * j / m) + rng.uniform(-0.005, 0.005),
             cy + 0.1 * math.sin(2 * math.pi * j / m) + rng.uniform(-0.005, 0.005)]
            for j in range(m)]

    k, step = k_start, 0
    while k > k_end:
        pull = [[0.0, 0.0] for _ in range(m)]
        for px, py in cities:
            d2 = [(px - y[0]) ** 2 + (py - y[1]) ** 2 for y in ring]
            lowest = min(d2)                       # subtract it so exp() never underflows
            phi = [math.exp(-(d - lowest) / (2 * k * k)) for d in d2]
            total = sum(phi)
            for j in range(m):
                w = alpha * phi[j] / total
                pull[j][0] += w * (px - ring[j][0])
                pull[j][1] += w * (py - ring[j][1])

        new_ring = []
        for j in range(m):
            prev, nxt, cur = ring[j - 1], ring[(j + 1) % m], ring[j]
            new_ring.append([
                cur[0] + pull[j][0] + beta * k * (nxt[0] - 2 * cur[0] + prev[0]),
                cur[1] + pull[j][1] + beta * k * (nxt[1] - 2 * cur[1] + prev[1]),
            ])
        ring = new_ring

        step += 1
        if step % 10 == 0:
            k *= 0.97

    def nearest_ring_point(c):
        return min(range(m), key=lambda j: (c[0] - ring[j][0]) ** 2 + (c[1] - ring[j][1]) ** 2)

    return sorted(range(n), key=lambda i: nearest_ring_point(cities[i]))


# ----------------------------------------------------------- exact answer (reference)
def held_karp(D):
    n = len(D)
    INF = float('inf')
    dp = [[INF] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]
    dp[1][0] = 0.0
    for mask in range(1, 1 << n, 2):               # only masks that contain city 0
        for j in range(n):
            if dp[mask][j] == INF:
                continue
            for nxt in range(1, n):
                if mask >> nxt & 1:
                    continue
                cand = dp[mask][j] + D[j][nxt]
                m2 = mask | (1 << nxt)
                if cand < dp[m2][nxt]:
                    dp[m2][nxt] = cand
                    parent[m2][nxt] = j
    full = (1 << n) - 1
    last = min(range(1, n), key=lambda j: dp[full][j] + D[j][0])
    tour, mask = [], full
    while last != -1:
        tour.append(last)
        mask, last = mask ^ (1 << last), parent[mask][last]
    return tour[::-1]


# ----------------------------------------------------------- running everything
METHODS = ['greedy', 'improvement', 'hill climbing', 'annealing', 'gradient descent']


def solve_all(cities, seed):
    """Run the five methods on one instance. Returns {name: (tour, seconds)}."""
    D = dist_matrix(cities)
    n = len(cities)
    start = list(range(n))
    random.Random(seed).shuffle(start)             # same random start for 1, 2, 3

    results = {}

    def timed(name, fn):
        t = time.perf_counter()
        tour = fn()
        results[name] = (tour, time.perf_counter() - t)
        assert sorted(tour) == list(range(n)), f'{name} gave an invalid tour'

    timed('greedy', lambda: greedy(D))
    timed('improvement', lambda: improve(start, D)[0])
    timed('hill climbing', lambda: hill_climb(start, D, random.Random(seed + 1)))
    timed('annealing', lambda: anneal(start, D, random.Random(seed + 2)))
    timed('gradient descent', lambda: gradient_descent(cities, random.Random(seed + 3)))
    return D, results


def report_single(n, seed, with_optimum, long_anneal_steps=None):
    cities = make_cities(n, seed)
    D, results = solve_all(cities, seed)

    if long_anneal_steps:                          # same start, same method, just a bigger budget
        start = list(range(n))
        random.Random(seed).shuffle(start)
        t = time.perf_counter()
        tour = anneal(start, D, random.Random(seed + 2), steps=long_anneal_steps)
        results[f'annealing {long_anneal_steps // 1000}k'] = (tour, time.perf_counter() - t)

    best_known = None
    if with_optimum:
        t = time.perf_counter()
        opt = held_karp(D)
        results['optimal (DP)'] = (opt, time.perf_counter() - t)
        best_known = tour_length(opt, D)
    else:
        best_known = min(tour_length(t, D) for t, _ in results.values())

    label = 'gap to optimal' if with_optimum else 'gap to best found'
    print(f'{"method":<18}{"length":>9}{label:>20}{"seconds":>10}')
    print('-' * 57)
    for name, (tour, secs) in results.items():
        length = tour_length(tour, D)
        if with_optimum:
            assert length >= best_known - 1e-9, f'{name} beat the exact optimum: bug'
        gap = 100 * (length - best_known) / best_known
        print(f'{name:<18}{length:>9.4f}{gap:>19.1f}%{secs:>10.3f}')
    return cities, results, D


def report_average(n, seeds):
    gaps = {m: [] for m in METHODS}
    secs = {m: 0.0 for m in METHODS}
    for seed in seeds:
        cities = make_cities(n, seed)
        D, results = solve_all(cities, seed)
        opt_len = tour_length(held_karp(D), D)
        for m in METHODS:
            tour, s = results[m]
            assert tour_length(tour, D) >= opt_len - 1e-9, f'{m} beat the exact optimum: bug'
            gaps[m].append(100 * (tour_length(tour, D) - opt_len) / opt_len)
            secs[m] += s

    print(f'{"method":<18}{"avg gap":>9}{"worst gap":>11}{"optimal found":>15}{"avg seconds":>13}')
    print('-' * 66)
    for m in METHODS:
        g = gaps[m]
        hits = sum(1 for x in g if x < 1e-9)
        print(f'{m:<18}{sum(g) / len(g):>8.1f}%{max(g):>10.1f}%{hits:>9}/{len(g):<5}{secs[m] / len(seeds):>13.3f}')


def report_anneal_budget(n, seed, budgets, repeats=5):
    """Annealing is random, so run it several times for each step budget."""
    cities = make_cities(n, seed)
    D = dist_matrix(cities)
    start = list(range(n))
    random.Random(seed).shuffle(start)

    print(f'{"steps":>8}{"shortest":>10}{"mean":>9}{"longest":>9}{"seconds each":>14}')
    print('-' * 50)
    for steps in budgets:
        t = time.perf_counter()
        lengths = [tour_length(anneal(start, D, random.Random(100 + r), steps=steps), D)
                   for r in range(repeats)]
        each = (time.perf_counter() - t) / repeats
        print(f'{steps:>8}{min(lengths):>10.4f}{sum(lengths) / repeats:>9.4f}'
              f'{max(lengths):>9.4f}{each:>14.3f}')
    two_opt = tour_length(improve(start, D)[0], D)
    print(f'(improvement / 2-opt from the same start: {two_opt:.4f})')


def try_plot(cities, results, path):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('(matplotlib not installed, skipping the picture)')
        return
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    D = dist_matrix(cities)
    for ax, (name, (tour, _)) in zip(axes.flat, results.items()):
        pts = [cities[i] for i in tour] + [cities[tour[0]]]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], '-o', markersize=4)
        ax.plot(*cities[tour[0]], 'rs')
        ax.set_title(f'{name}: {tour_length(tour, D):.3f}')
        ax.set_aspect('equal')
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    print(f'picture saved to {path}')


if __name__ == '__main__':
    print('== A. one instance, 12 cities (exact optimum known) ==')
    cities, results, D = report_single(12, seed=1, with_optimum=True)
    for name, (tour, _) in results.items():
        print(f'  {name:<18}{tour}')
    try_plot(cities, results, 'tsp_tours.png')

    print('\n== B. average over 10 random instances, 12 cities each ==')
    report_average(12, seeds=range(1, 11))

    print('\n== C. one bigger instance, 40 cities (no exact answer) ==')
    report_single(40, seed=5, with_optimum=False, long_anneal_steps=100000)

    print('\n== D. annealing: effect of the number of steps (same 40 cities, 5 runs each) ==')
    report_anneal_budget(40, seed=5, budgets=(20000, 100000, 400000))