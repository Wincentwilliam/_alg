# Homework 10: derivatives and integrals computed with numbers, not with algebra.
#
#   1. one variable : numerical derivative and integral
#   2. one variable : Monte Carlo integral
#   3. n variables  : numerical gradient and hypervolume (integral over a box)
#   4. n variables  : Monte Carlo integral
#   5. integral(f, low, high) with a Riemann sum for n variables, tried in 1, 2, 5
#      and 100 dimensions, then done again with Monte Carlo
#
# Pure Python, no packages needed. Every random number comes from a seeded
# generator, so the numbers printed are the same on every run (only the timings change).

import itertools
import math
import random
import sys
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


# ============================================================ 1. one variable
def derivative(f, x, h=1e-5):
    """Central difference: the slope through the points on both sides of x."""
    return (f(x + h) - f(x - h)) / (2 * h)


def forward_difference(f, x, h=1e-5):
    """The simpler, less accurate one-sided slope. Only used for comparison."""
    return (f(x + h) - f(x)) / h


def integral_1d(f, a, b, n=1000, rule='simpson'):
    """
    Area under f on [a, b] cut into n slices.
      left      : a rectangle as tall as f at the left edge of each slice (a Riemann sum)
      mid       : a rectangle as tall as f in the middle of each slice (a Riemann sum)
      trapezoid : a slanted top joining f at both edges
      simpson   : a parabola through the two edges and the middle (n must be even)
    """
    h = (b - a) / n
    if rule == 'left':
        return h * sum(f(a + i * h) for i in range(n))
    if rule == 'mid':
        return h * sum(f(a + (i + 0.5) * h) for i in range(n))
    if rule == 'trapezoid':
        return h * (0.5 * f(a) + sum(f(a + i * h) for i in range(1, n)) + 0.5 * f(b))
    if rule == 'simpson':
        if n % 2:
            raise ValueError('Simpson needs an even number of slices')
        odd = sum(f(a + i * h) for i in range(1, n, 2))
        even = sum(f(a + i * h) for i in range(2, n, 2))
        return h / 3 * (f(a) + 4 * odd + 2 * even + f(b))
    raise ValueError(f'unknown rule {rule!r}')


# ============================================================ 2. one variable, Monte Carlo
def mc_integral_1d(f, a, b, samples, rng):
    """
    Average f at random points of [a, b], times the length of the interval.
    Also returns the standard error, the typical size of the error of this estimate.
    """
    total = total_sq = 0.0
    for _ in range(samples):
        v = f(a + (b - a) * rng.random())
        total += v
        total_sq += v * v
    mean = total / samples
    var = max(total_sq / samples - mean * mean, 0.0) * samples / (samples - 1)
    return (b - a) * mean, (b - a) * math.sqrt(var / samples)


# ============================================================ 3. n variables
def gradient(f, x, h=1e-5):
    """Vector of partial derivatives: a central difference along each axis. Costs 2n evaluations."""
    grad = []
    for i in range(len(x)):
        up, down = list(x), list(x)
        up[i] += h
        down[i] -= h
        grad.append((f(up) - f(down)) / (2 * h))
    return grad


class TooManyPoints(Exception):
    """Raised instead of starting a grid that would never finish."""

    def __init__(self, points):
        super().__init__(f'{points:.3g} grid points')
        self.points = points


def integral(f, low, high, steps=10, rule='mid', max_points=50_000_000):
    """
    Riemann sum over the box low[0]..high[0] x ... x low[n-1]..high[n-1]; n = len(low).
    Every side is cut into `steps` slices, so the box is cut into steps**n small
    boxes. f is evaluated once per small box (at its middle, or at its lowest
    corner with rule='left') and multiplied by the volume of that small box.
    f receives the point as a tuple of n numbers.
    """
    n = len(low)
    if len(high) != n:
        raise ValueError('low and high must have the same length')
    points = steps ** n
    if points > max_points:
        raise TooManyPoints(points)
    widths = [(hi - lo) / steps for lo, hi in zip(low, high)]
    shift = 0.5 if rule == 'mid' else 0.0
    axes = [[lo + (i + shift) * w for i in range(steps)] for lo, w in zip(low, widths)]
    total = 0.0
    for point in itertools.product(*axes):
        total += f(point)
    return total * math.prod(widths)


# ============================================================ 4. n variables, Monte Carlo
def mc_integral(f, low, high, samples, rng):
    """
    Monte Carlo over the same box: average f at random points of the box and
    multiply by the volume of the box. Returns (estimate, standard error).
    """
    spans = [hi - lo for lo, hi in zip(low, high)]
    volume = math.prod(spans)
    total = total_sq = 0.0
    for _ in range(samples):
        v = f([lo + s * rng.random() for lo, s in zip(low, spans)])
        total += v
        total_sq += v * v
    mean = total / samples
    var = max(total_sq / samples - mean * mean, 0.0) * samples / (samples - 1)
    return volume * mean, volume * math.sqrt(var / samples)


# ============================================================ test functions
def sum_of_squares(x):
    return sum(v * v for v in x)


def inside_unit_ball(x):
    """1 inside the unit ball, 0 outside. Its integral is the ball's hypervolume."""
    return 1.0 if sum(v * v for v in x) <= 1.0 else 0.0


def unit_ball_volume(n):
    return math.pi ** (n / 2) / math.gamma(n / 2 + 1)


def fmt_big(x):
    return f'{x:.3g}' if x >= 1e6 else f'{x:,.0f}'


CHECKS = []                                   # every comparison with an exact value ends up here


def check(name, ok):
    CHECKS.append((name, ok))


# ============================================================ main
if __name__ == '__main__':
    rng = random.Random(2026)

    # ------------------------------------------------ part 1
    print('=' * 78)
    print('PART 1   one variable: numerical derivative and integral')
    print('=' * 78)

    print('\nDerivative of sin(x) at x = 1   (exact value cos(1) = %.12f)' % math.cos(1))
    print(f'  {"h":>8}{"forward diff":>17}{"error":>12}{"central diff":>17}{"error":>12}')
    print('  ' + '-' * 64)
    best = None
    for k in range(1, 13):
        h = 10.0 ** -k
        fwd, cen = forward_difference(math.sin, 1, h), derivative(math.sin, 1, h)
        e_f, e_c = abs(fwd - math.cos(1)), abs(cen - math.cos(1))
        best = min(best, (e_c, h)) if best else (e_c, h)
        print(f'  {h:>8.0e}{fwd:>17.10f}{e_f:>12.2e}{cen:>17.10f}{e_c:>12.2e}')
    print(f'  The forward error shrinks like h and the central error like h^2, until rounding noise takes')
    print(f'  over: for the central difference below h = 1e-5, for the forward one below about 1e-8, making')
    print(f'  h smaller makes things WORSE. Smallest central error here: {best[0]:.1e} at h = {best[1]:.0e}.')
    print(f'  (The default h = 1e-5 is a safe choice.)')
    check('central difference of sin at 1', abs(derivative(math.sin, 1) - math.cos(1)) < 1e-9)

    exact_int = math.e - 1
    print('\nIntegral of e^x from 0 to 1   (exact value e - 1 = %.12f)' % exact_int)
    rules = ['left', 'mid', 'trapezoid', 'simpson']
    print(f'  {"slices":>7}' + ''.join(f'{r:>15}' for r in rules) + '      <- absolute error')
    print('  ' + '-' * 68)
    errors = {}
    for n in (10, 100, 1000):
        row = []
        for r in rules:
            errors[(r, n)] = abs(integral_1d(math.exp, 0, 1, n, r) - exact_int)
            row.append(errors[(r, n)])
        print(f'  {n:>7}' + ''.join(f'{e:>15.2e}' for e in row))
    print('  Error divided by this when the slices grow 10x (the "order" of the rule):')
    for r in rules:
        ratio = errors[(r, 100)] / errors[(r, 1000)]
        print(f'    {r:<10} {ratio:>10.0f}x   -> about 10^{math.log10(ratio):.0f}')
    print('  left: error ~ 1/n.  mid and trapezoid: ~ 1/n^2.  Simpson: ~ 1/n^4.')
    print('  (sin on [0, pi] would hide the first line: sin is 0 at both ends, which makes the left')
    print('  sum equal the trapezoid sum. e^x has different ends, so every rule shows its true order.)')
    check('left rule has order 1', 8 < errors[('left', 100)] / errors[('left', 1000)] < 12)
    check('Simpson on e^x', errors[('simpson', 1000)] < 1e-10)
    check('mid on e^x', errors[('mid', 1000)] < 1e-5)

    # ------------------------------------------------ part 2
    print('\n' + '=' * 78)
    print('PART 2   one variable: Monte Carlo integral')
    print('=' * 78)
    print('\nSame integral, e^x from 0 to 1 (exact e - 1 = %.6f), with random points:' % exact_int)
    print(f'  {"samples":>9}{"estimate":>12}{"abs error":>12}{"std error":>12}{"std err*sqrt(N)":>17}')
    print('  ' + '-' * 62)
    for n in (100, 1_000, 10_000, 100_000, 1_000_000):
        est, se = mc_integral_1d(math.exp, 0, 1, n, rng)
        err = abs(est - exact_int)
        print(f'  {n:>9,}{est:>12.5f}{err:>12.5f}{se:>12.5f}{se * math.sqrt(n):>17.4f}')
        check(f'MC 1-D, {n} samples within 4 std errors', err <= 4 * se)
    print('  The std error falls like 1/sqrt(N): 100x more points buy only 10x less error (the last column,')
    print('  std error * sqrt(N), is constant: it is the spread of f). The actual error is random, so it')
    print('  wobbles around the std error from row to row, but it is typically that size.')
    print('  The std error is the program\'s own estimate of its error, computed from the spread of the')
    print('  samples, so it needs no exact answer.')
    print(f'  Compared with part 1: Simpson with 1000 slices has error {errors[("simpson", 1000)]:.0e}; Monte Carlo with')
    print('  a million points has about 1e-3. In ONE dimension it cannot compete. Its strength only')
    print('  shows when the dimension grows (parts 4 and 5).')

    # ------------------------------------------------ part 3
    print('\n' + '=' * 78)
    print('PART 3   n variables: gradient and hypervolume')
    print('=' * 78)

    f3 = lambda p: p[0] * p[1] * p[2] + math.sin(p[0])
    exact3 = lambda p: [p[1] * p[2] + math.cos(p[0]), p[0] * p[2], p[0] * p[1]]
    pt = [0.7, -1.2, 2.5]
    g, ge = gradient(f3, pt), exact3(pt)
    print('\nGradient of f(x,y,z) = x*y*z + sin(x) at (0.7, -1.2, 2.5):')
    print(f'  numerical : {[round(v, 8) for v in g]}')
    print(f'  exact     : {[round(v, 8) for v in ge]}')
    check('gradient 3-D', max(abs(a - b) for a, b in zip(g, ge)) < 1e-6)

    n = 100
    pt = [i / n for i in range(1, n + 1)]
    g = gradient(sum_of_squares, pt)
    worst = max(abs(g[i] - 2 * pt[i]) for i in range(n))
    print(f'\nGradient of f(x) = x1^2+...+x{n}^2 in {n} dimensions (exact gradient is 2x):')
    print(f'  largest error over the {n} components: {worst:.1e}.  It took only {2 * n} evaluations of f.')
    print('  A derivative costs 2n evaluations, so it stays cheap in any dimension. The integral does not (below).')
    check('gradient 100-D', worst < 1e-6)

    print('\nHypervolume = the integral of f over a box. With f = 1 on the inside of a shape and 0')
    print('outside, it is the shape\'s volume. Volume of the unit ball with a grid of small boxes:')
    print(f'  {"dim":>4}{"grid":>9}{"boxes":>10}{"grid result":>14}{"exact":>10}{"error":>10}')
    print('  ' + '-' * 58)
    for dim, k in ((2, 400), (3, 60), (4, 20)):
        res = integral(inside_unit_ball, [-1] * dim, [1] * dim, steps=k)
        ex = unit_ball_volume(dim)
        print(f'  {dim:>4}{k:>6}^{dim}{k ** dim:>10,}{res:>14.5f}{ex:>10.5f}{res - ex:>10.5f}')
        check(f'ball volume grid {dim}-D', abs(res - ex) / ex < 0.03)
    print('  A grid hugging a curved edge is only roughly right (the edge cuts boxes in half); and')
    print('  the number of boxes is k^n. The same ball in 10 dimensions with just 10 slices per side')
    print(f'  would already need 10^10 = {10 ** 10:,} boxes.')

    # ------------------------------------------------ part 4
    print('\n' + '=' * 78)
    print('PART 4   n variables: Monte Carlo integral (hypervolume)')
    print('=' * 78)

    est, se = mc_integral(sum_of_squares, [0, 0, 0], [1, 1, 1], 200_000, rng)
    print(f'\nIntegral of x^2+y^2+z^2 over the unit cube, 200,000 random points: '
          f'{est:.5f} +- {se:.5f}   (exact 1)')
    check('MC 3-D sum of squares', abs(est - 1) <= 4 * se)

    print('\nVolume of the unit ball (random points in the cube [-1,1]^n, 1,000,000 points each):')
    print(f'  {"dim":>4}{"MC estimate":>14}{"+- std error":>14}{"exact":>10}{"error":>10}{"points that hit":>17}')
    print('  ' + '-' * 70)
    for dim in (2, 3, 5, 10):
        t = time.perf_counter()
        est, se = mc_integral(inside_unit_ball, [-1] * dim, [1] * dim, 1_000_000, rng)
        ex = unit_ball_volume(dim)
        hits = round(est / 2 ** dim * 1_000_000)
        print(f'  {dim:>4}{est:>14.5f}{se:>14.5f}{ex:>10.5f}{est - ex:>10.5f}{hits:>17,}')
        check(f'MC ball {dim}-D within 4 std errors', abs(est - ex) <= 4 * se)
    print('  In 10 dimensions only about 1 point in 400 lands inside the ball, so the estimate is noisier:')
    print('  its std error is about 2% of the answer. Monte Carlo still works where a grid cannot be built.')

    # ------------------------------------------------ part 5
    print('\n' + '=' * 78)
    print('PART 5   integral(f, low, high) for n variables')
    print('=' * 78)
    print('\nf(x) = x1^2 + ... + xn^2 over the box [0,1]^n  (low = 0 and high = 1 in every dimension).')
    print('Exact answer: n/3, because each term integrates to 1/3.')

    print('\n--- 5.1  Riemann sum (midpoint rule) ---')
    print(f'  {"dim":>4}{"steps":>7}{"boxes":>16}{"result":>14}{"exact n/3":>12}{"error":>12}{"seconds":>10}')
    print('  ' + '-' * 77)
    speed = None
    for dim, steps in ((1, 1000), (2, 1000), (5, 20)):
        t = time.perf_counter()
        res = integral(sum_of_squares, [0] * dim, [1] * dim, steps=steps)
        secs = time.perf_counter() - t
        if dim == 5:
            speed = steps ** dim / secs
        predicted = dim * (1 / 3 - 1 / (12 * steps ** 2))
        check(f'Riemann {dim}-D equals its predicted value', abs(res - predicted) < 1e-9)
        print(f'  {dim:>4}{steps:>7}{steps ** dim:>16,}{res:>14.8f}{dim / 3:>12.6f}{res - dim / 3:>12.2e}{secs:>10.2f}')
    print('  For this f the midpoint rule is off by exactly -n/(12*steps^2), and the results match that')
    print('  formula to 9 digits, so the program does what the maths says.')

    dim = 100
    print(f'\n  {dim} dimensions:')
    try:
        integral(sum_of_squares, [0] * dim, [1] * dim, steps=2)
    except TooManyPoints as e:
        years = e.points / speed / (365.25 * 24 * 3600)
        print(f'  steps=2 (just TWO slices per side) -> {e}: refused. At the speed measured in the 5-D run')
        print(f'  ({speed:,.0f} evaluations per second) that is about {years:.1e} years of computing.')
    one = integral(sum_of_squares, [0] * dim, [1] * dim, steps=1)
    print(f'  The only grid that can be afforded is steps=1 (a single box, f at its centre): '
          f'{one:.4f}  vs exact {dim / 3:.4f}  -> {abs(one - dim / 3) / (dim / 3):.0%} off, and no way to refine it.')
    check('Riemann 100-D one box = 25', abs(one - 25) < 1e-9)

    print('\n  Why: the number of boxes is steps^n.')
    print(f'  {"dim":>6}{"boxes with 10 steps":>24}{"time at that speed":>26}')
    print('  ' + '-' * 56)
    for d in (1, 2, 5, 10, 20, 100):
        boxes = 10 ** d
        secs = boxes / speed
        if secs < 60:
            when = f'{secs:.2g} s'
        elif secs < 3600 * 24 * 365:
            when = f'{secs / 86400:.3g} days'
        else:
            when = f'{secs / (365.25 * 86400):.2g} years'
        print(f'  {d:>6}{fmt_big(boxes):>24}{when:>26}')

    print('\n--- 5.2  Monte Carlo (100,000 random points each) ---')
    print('  The error of Monte Carlo shrinks like 1/sqrt(N) in EVERY dimension. What changes with n is only')
    print('  how spread out f is: here the spread grows like sqrt(n) while the answer grows like n, so the')
    print('  relative error even gets smaller in higher dimensions.')
    print(f'  {"dim":>4}{"estimate":>12}{"+- std error":>14}{"exact n/3":>12}{"abs error":>12}{"rel error":>11}{"std err/exact":>15}{"seconds":>9}')
    print('  ' + '-' * 89)
    mc_rows = {}
    for dim in (1, 2, 5, 100):
        t = time.perf_counter()
        est, se = mc_integral(sum_of_squares, [0] * dim, [1] * dim, 100_000, rng)
        secs = time.perf_counter() - t
        ex = dim / 3
        mc_rows[dim] = (secs, abs(est - ex) / ex)
        check(f'MC {dim}-D within 4 std errors', abs(est - ex) <= 4 * se)
        print(f'  {dim:>4}{est:>12.5f}{se:>14.5f}{ex:>12.5f}{abs(est - ex):>12.5f}{abs(est - ex) / ex:>11.3%}{se / ex:>15.3%}{secs:>9.2f}')
    print('  "rel error" is what happened in this one run; "std err/exact" is the size of error to EXPECT, and it')
    print('  does fall with the dimension (the single runs wobble around it).')
    print(f'  The same 100,000 points handle 100 dimensions: {mc_rows[100][0]:.1f} s (each point just has 100 numbers')
    print(f'  instead of 1) and {mc_rows[100][1]:.2%} off, where the Riemann sum could not even start.')

    print('\n  How the 100-D estimate improves with more points (exact 33.33333):')
    print(f'  {"points":>10}{"estimate":>12}{"abs error":>12}{"std error":>12}')
    print('  ' + '-' * 46)
    for n in (100, 1_000, 10_000, 100_000):
        est, se = mc_integral(sum_of_squares, [0] * 100, [1] * 100, n, rng)
        print(f'  {n:>10,}{est:>12.4f}{abs(est - 100 / 3):>12.4f}{se:>12.4f}')

    print('\n  Riemann sum vs Monte Carlo, in short:')
    print('    cost         Riemann: steps^n evaluations (explodes)     Monte Carlo: N evaluations, you choose')
    print('    error        Riemann: ~ 1/steps^2, great in 1-3 dims      Monte Carlo: ~ 1/sqrt(N), any dimension')
    print('    error info   Riemann: needs smoothness to be accurate     Monte Carlo: reports its own std error')

    # ------------------------------------------------ summary
    failed = [name for name, ok in CHECKS if not ok]
    print('\n' + '=' * 78)
    print(f'SELF-CHECK: {len(CHECKS) - len(failed)} of {len(CHECKS)} comparisons with exact values passed'
          + ('' if not failed else f'   FAILED: {failed}'))
    print('=' * 78)