# Homework 10: Derivatives and Integrals with Numbers

> This README is the write-up and process document for the assignment. The program and this document were produced with the help of Claude AI, then run, checked against exact answers, and corrected where the first version was wrong.

Name: 洪偉升
Department: 資訊工程學系
Student ID: 111310523
Class: Introduction to Algorithms

---

## 1. The assignment

Write programs that compute derivatives and integrals **numerically** (with
arithmetic on numbers, not with algebra):

1. numerical derivative and integral of a **one-variable** function
2. **Monte Carlo** integral of a one-variable function
3. numerical **gradient** (n-variable derivative) and **hypervolume** (n-variable integral)
4. **Monte Carlo** integral of an n-variable function
5. a function `integral(f, low, high)` that uses a **Riemann sum** for n variables
   (n = length of `low` and `high`), tried in **1, 2, 5 and 100 dimensions**
   with `f(x) = x1^2 + ... + xn^2`, then done again with Monte Carlo

Files:

| File | Purpose |
|---|---|
| `numeric_calculus.py` | all five parts, one file, nothing to install |
| `output.txt` | the full output of `python numeric_calculus.py` |

Run it with `python numeric_calculus.py` (a few seconds to under half a minute,
depending on the computer). All random numbers come from a seeded generator, so
every number in the output is the same on every run; only the `seconds` columns
change.

### Setup for part 5

As given in the assignment, `low = 0` and `high = 1` in every dimension, so the
box is the unit hypercube `[0, 1]^n`. The exact answer is known: each term
`xi^2` integrates to 1/3, so the integral is **n/3**. That makes it possible to
check every result.

## 2. The ideas in plain words

- **Derivative = slope.** Estimate it from two points close to each other.
- **Integral = area (volume, hypervolume).** Cut the region into many small
  pieces, estimate the height of f on each, add up height x size.
- **Riemann sum / grid:** the pieces form a regular grid.
- **Monte Carlo:** instead of a regular grid, throw random points into the
  region, average f over them and multiply by the size of the region.
- **Hypervolume** is the n-dimensional version of area: the integral of f over a
  box in n dimensions. With f = 1 inside a shape and 0 outside, it is the volume
  of that shape.

## 3. Part 1: one variable (`derivative`, `integral_1d`)

### Derivative
The **central difference** uses both sides of x:

```
f'(x) ~ ( f(x+h) - f(x-h) ) / (2h)
```

Two kinds of error compete. The *formula* error shrinks as `h` gets smaller
(like `h^2` for the central difference, like `h` for the one-sided "forward"
difference). The *rounding* error of the computer grows as `h` gets smaller,
because two almost equal numbers are subtracted and the result is divided by a
tiny number (it grows like `eps/h`, where eps = 2.2e-16 is the precision of a
double). The best `h` is where they meet, around `eps^(1/3)` ~ 6e-6. The table
in the output shows it for sin at x = 1: the central error reaches 1.1e-11 at
h = 1e-5, and gets worse for smaller h. The default `h = 1e-5` was chosen from this.

### Integral
`integral_1d(f, a, b, n, rule)` cuts [a, b] into n slices. Four rules:

| Rule | Each slice is replaced by | Error shrinks like |
|---|---|---|
| `left` | a rectangle as tall as f at the left edge (a Riemann sum) | 1/n |
| `mid` | a rectangle as tall as f in the middle (a Riemann sum) | 1/n^2 |
| `trapezoid` | a slanted top through both edges | 1/n^2 |
| `simpson` | a parabola through both edges and the middle | 1/n^4 |

The output measures this on the integral of e^x from 0 to 1 (exact e - 1):
making the slices 10 times more numerous divides the error by 10 (left), 100
(mid, trapezoid) and about 10,000 (Simpson). With 1000 slices Simpson reaches an
error near 1e-14.

*Why not sin on [0, pi]?* My first test used it, and the left rule seemed to be
order 2. That is a coincidence: sin is 0 at both ends, which makes the left sum
identical to the trapezoid sum. e^x has different ends, so each rule shows its
true order.

## 4. Part 2: one variable, Monte Carlo (`mc_integral_1d`)

```
integral ~ (b - a) * average of f at N random points of [a, b]
```

It also returns the **standard error**, the typical size of its own error,
computed from how spread out the sampled values are (`(b-a) * std(f) / sqrt(N)`),
so no exact answer is needed to know how reliable the estimate is.

The error follows the **1/sqrt(N) law**: 100 times more points give only 10
times less error. In the output the column "std error x sqrt(N)" is constant
(about 0.49, which is the spread of e^x on [0, 1]). The actual error is random,
so it wobbles around the std error, but it is typically that size.

In one dimension Monte Carlo loses clearly: Simpson with 1000 slices has an
error near 1e-14, Monte Carlo with a million points about 5e-4. Its advantage
only appears when the dimension grows.

## 5. Part 3: n variables, gradient and hypervolume

### Gradient (`gradient`)
The gradient is the list of partial derivatives. Each is a central difference
along one axis, so it costs **2n evaluations of f**, which is cheap in any
dimension. Checks:

- `f(x,y,z) = x*y*z + sin(x)` at (0.7, -1.2, 2.5): the numerical gradient equals
  the exact one to all printed digits.
- `f = x1^2 + ... + x100^2` in 100 dimensions: the gradient is `2x`; the largest
  error over the 100 components is 2.5e-10, from only 200 evaluations.

### Hypervolume (`integral`)
`integral(f, low, high, steps)` is the grid method of part 5 (section 7). Here
it computes the **volume of the unit ball** with f = 1 inside and 0 outside:

| dim | grid | boxes | grid result | exact |
|---|---|---|---|---|
| 2 | 400^2 | 160,000 | 3.14190 | 3.14159 |
| 3 | 60^3 | 216,000 | 4.18904 | 4.18879 |
| 4 | 20^4 | 160,000 | 4.96480 | 4.93480 |

(The exact volume is `pi^(n/2) / Gamma(n/2 + 1)`.) A grid is only roughly right
along a curved edge, because boxes cut by the edge are counted whole or not at
all. More importantly, the number of boxes is `k^n`, so the same ball in 10
dimensions with just 10 slices per side would need 10,000,000,000 boxes.

## 6. Part 4: n variables, Monte Carlo (`mc_integral`)

Same idea as part 2, in a box:

```
integral ~ (volume of the box) * average of f at N random points of the box
```

- Integral of `x^2+y^2+z^2` over the unit cube with 200,000 points:
  0.99936 +- 0.00115 (exact 1).
- Volume of the unit ball, 1,000,000 random points in the cube `[-1, 1]^n`:

| dim | MC estimate | +- std error | exact |
|---|---|---|---|
| 2 | 3.13904 | 0.00164 | 3.14159 |
| 3 | 4.19034 | 0.00400 | 4.18879 |
| 5 | 5.28186 | 0.01188 | 5.26379 |
| 10 | 2.56205 | 0.05116 | 2.55016 |

Every estimate is within two standard errors of the exact value. In 10
dimensions only 2,502 of the million points land inside the ball (about 1 in
400, since the ball is a tiny part of the cube), so that estimate is noisier
(std error about 2% of the answer). That is the weak spot of Monte Carlo: rare
events need many points. It still works where a grid cannot even be built.

## 7. Part 5: `integral(f, low, high)` with a Riemann sum

```python
# simplified: the real function also supports rule='left' (f at the lowest corner of each box)
def integral(f, low, high, steps=10, rule='mid', max_points=50_000_000):
    n = len(low)                                   # the number of variables
    widths = [(hi - lo) / steps for lo, hi in zip(low, high)]
    axes = [[lo + (i + 0.5) * w for i in range(steps)] for lo, w in zip(low, widths)]
    total = 0.0
    for point in itertools.product(*axes):         # every small box of the grid
        total += f(point)
    return total * math.prod(widths)               # f times the volume of one small box
```

Every side of the box is cut into `steps` slices, so the box is cut into
`steps^n` small boxes; f is evaluated once in the middle of each and multiplied
by the volume of one small box. `f` receives the point as a tuple of n numbers,
so the same function handles any dimension:
`integral(lambda x: sum(v*v for v in x), [0, 0], [1, 1])`.
`max_points` makes the function raise `TooManyPoints` instead of starting a grid
that would never finish.

### 7.1 Results, f = x1^2 + ... + xn^2 on [0,1]^n

| dim | steps | boxes | result | exact n/3 | error |
|---|---|---|---|---|---|
| 1 | 1000 | 1,000 | 0.33333325 | 0.333333 | -8.33e-08 |
| 2 | 1000 | 1,000,000 | 0.66666650 | 0.666667 | -1.67e-07 |
| 5 | 20 | 3,200,000 | 1.66562500 | 1.666667 | -1.04e-03 |
| 100 | (impossible) | 2^100 ~ 1.3e30 even with 2 steps | refused | 33.3333 | |

**The numbers are not just close, they are exactly what the maths predicts.**
For this f the midpoint rule is off by exactly `n/(12*steps^2)`, so the result
must be `n * (1/3 - 1/(12*steps^2))`. The program checks that its results match
this formula to 9 digits in 1, 2 and 5 dimensions.

**100 dimensions cannot be done with a grid.** Even 2 slices per side gives
2^100 ~ 1.3e30 boxes. At the speed measured in the 5-D run (about 3 million
evaluations per second) that is of the order of 10^16 years, so the program
refuses and prints this estimate instead. The only grid it can afford is a
single box (`steps=1`), which evaluates f at the centre and gives 25.0 instead
of 33.33: 25% off, with no way to improve it.

### Why: the curse of dimensionality

The cost is `steps^n`, and the accuracy per dimension only improves like
`1/steps^2`. To divide the error by 10 the midpoint grid needs about `sqrt(10)`
times more slices per side, i.e. `10^(n/2)` times more boxes: a factor of about
316 in 5 dimensions and 10^50 in 100. The table in the output shows the number
of boxes for 10 steps: 10^5 in 5-D (a fraction of a second), 10^10 in 10-D
(about an hour), 10^20 in 20-D (about a million years), 10^100 in 100-D.

### 7.2 The same with Monte Carlo (100,000 random points)

| dim | estimate | +- std error | exact n/3 | std err / exact |
|---|---|---|---|---|
| 1 | 0.33342 | 0.00094 | 0.33333 | 0.283% |
| 2 | 0.66541 | 0.00134 | 0.66667 | 0.200% |
| 5 | 1.66690 | 0.00210 | 1.66667 | 0.126% |
| 100 | 33.32002 | 0.00941 | 33.33333 | 0.028% |

The same *number* of points (100,000) handles all four dimensions. 100
dimensions only cost more time per point (each point has 100 numbers instead of
1: about a second in total), and the result is 0.04% off, where the Riemann sum
could not even start. The last column is the error to *expect* relative to the
answer; it *falls* as the dimension grows, because the answer grows like n while
the spread of f grows only like sqrt(n). The second table in the output shows
the 100-D error improving with more points (std error 0.26, 0.091, 0.029, 0.0095
for 100, 1,000, 10,000, 100,000 points): the 1/sqrt(N) law again.

## 8. Riemann sum vs Monte Carlo

| | Riemann sum (grid) | Monte Carlo |
|---|---|---|
| Evaluations of f | `steps^n`, explodes with n | `N`, you choose it |
| Error | ~ 1/steps^2 per dimension (smooth f) | ~ 1/sqrt(N) in **any** dimension |
| Best for | 1 to 3 dimensions, smooth f | many dimensions, rough f, shapes (indicator functions) |
| Weak spot | the curse of dimensionality | slow 1/sqrt(N) convergence; rare events need many points |
| Error information | needs smoothness to be accurate | reports its own standard error |

In one dimension the grid (especially Simpson) is far better; in 100 dimensions
only Monte Carlo is possible. The crossover is the lesson of part 5.

## 9. Actual output

```
==============================================================================
PART 1   one variable: numerical derivative and integral
==============================================================================

Derivative of sin(x) at x = 1   (exact value cos(1) = 0.540302305868)
         h     forward diff       error     central diff       error
  ----------------------------------------------------------------
     1e-01     0.4973637525    4.29e-02     0.5394022522    9.00e-04
     1e-02     0.5360859810    4.22e-03     0.5402933009    9.00e-06
     1e-03     0.5398814804    4.21e-04     0.5403022158    9.01e-08
     1e-04     0.5402602314    4.21e-05     0.5403023050    9.00e-10
     1e-05     0.5402980985    4.21e-06     0.5403023059    1.11e-11
     1e-06     0.5403018851    4.21e-07     0.5403023059    2.77e-11
     1e-07     0.5403022640    4.18e-08     0.5403023057    1.94e-10
     1e-08     0.5403023029    2.97e-09     0.5403023084    2.58e-09
     1e-09     0.5403023584    5.25e-08     0.5403023029    2.97e-09
     1e-10     0.5403022474    5.85e-08     0.5403022474    5.85e-08
     1e-11     0.5403011372    1.17e-06     0.5403011372    1.17e-06
     1e-12     0.5403455461    4.32e-05     0.5402900349    1.23e-05
  The forward error shrinks like h and the central error like h^2, until rounding noise takes
  over: for the central difference below h = 1e-5, for the forward one below about 1e-8, making
  h smaller makes things WORSE. Smallest central error here: 1.1e-11 at h = 1e-05.
  (The default h = 1e-5 is a safe choice.)

Integral of e^x from 0 to 1   (exact value e - 1 = 1.718281828459)
   slices           left            mid      trapezoid        simpson      <- absolute error
  --------------------------------------------------------------------
       10       8.45e-02       7.16e-04       1.43e-03       9.53e-07
      100       8.58e-03       7.16e-06       1.43e-05       9.55e-11
     1000       8.59e-04       7.16e-08       1.43e-07       9.77e-15
  Error divided by this when the slices grow 10x (the "order" of the rule):
    left               10x   -> about 10^1
    mid               100x   -> about 10^2
    trapezoid         100x   -> about 10^2
    simpson          9771x   -> about 10^4
  left: error ~ 1/n.  mid and trapezoid: ~ 1/n^2.  Simpson: ~ 1/n^4.
  (sin on [0, pi] would hide the first line: sin is 0 at both ends, which makes the left
  sum equal the trapezoid sum. e^x has different ends, so every rule shows its true order.)

==============================================================================
PART 2   one variable: Monte Carlo integral
==============================================================================

Same integral, e^x from 0 to 1 (exact e - 1 = 1.718282), with random points:
    samples    estimate   abs error   std error  std err*sqrt(N)
  --------------------------------------------------------------
        100     1.76890     0.05062     0.04515           0.4515
      1,000     1.71139     0.00689     0.01533           0.4847
     10,000     1.70500     0.01328     0.00489           0.4892
    100,000     1.71738     0.00090     0.00155           0.4915
  1,000,000     1.71775     0.00053     0.00049           0.4917
  The std error falls like 1/sqrt(N): 100x more points buy only 10x less error (the last column,
  std error * sqrt(N), is constant: it is the spread of f). The actual error is random, so it
  wobbles around the std error from row to row, but it is typically that size.
  The std error is the program's own estimate of its error, computed from the spread of the
  samples, so it needs no exact answer.
  Compared with part 1: Simpson with 1000 slices has error 1e-14; Monte Carlo with
  a million points has about 5e-4. In ONE dimension it cannot compete. Its strength only
  shows when the dimension grows (parts 4 and 5).

==============================================================================
PART 3   n variables: gradient and hypervolume
==============================================================================

Gradient of f(x,y,z) = x*y*z + sin(x) at (0.7, -1.2, 2.5):
  numerical : [-2.23515781, 1.75, -0.84]
  exact     : [-2.23515781, 1.75, -0.84]

Gradient of f(x) = x1^2+...+x100^2 in 100 dimensions (exact gradient is 2x):
  largest error over the 100 components: 2.5e-10.  It took only 200 evaluations of f.
  A derivative costs 2n evaluations, so it stays cheap in any dimension. The integral does not (below).

Hypervolume = the integral of f over a box. With f = 1 on the inside of a shape and 0
outside, it is the shape's volume. Volume of the unit ball with a grid of small boxes:
   dim     grid     boxes   grid result     exact     error
  ----------------------------------------------------------
     2   400^2   160,000       3.14190   3.14159   0.00031
     3    60^3   216,000       4.18904   4.18879   0.00025
     4    20^4   160,000       4.96480   4.93480   0.03000
  A grid hugging a curved edge is only roughly right (the edge cuts boxes in half); and
  the number of boxes is k^n. The same ball in 10 dimensions with just 10 slices per side
  would already need 10^10 = 10,000,000,000 boxes.

==============================================================================
PART 4   n variables: Monte Carlo integral (hypervolume)
==============================================================================

Integral of x^2+y^2+z^2 over the unit cube, 200,000 random points: 0.99936 +- 0.00115   (exact 1)

Volume of the unit ball (random points in the cube [-1,1]^n, 1,000,000 points each):
   dim   MC estimate  +- std error     exact     error  points that hit
  ----------------------------------------------------------------------
     2       3.13904       0.00164   3.14159  -0.00255          784,761
     3       4.19034       0.00400   4.18879   0.00155          523,792
     5       5.28186       0.01188   5.26379   0.01807          165,058
    10       2.56205       0.05116   2.55016   0.01188            2,502
  In 10 dimensions only about 1 point in 400 lands inside the ball, so the estimate is noisier:
  its std error is about 2% of the answer. Monte Carlo still works where a grid cannot be built.

==============================================================================
PART 5   integral(f, low, high) for n variables
==============================================================================

f(x) = x1^2 + ... + xn^2 over the box [0,1]^n  (low = 0 and high = 1 in every dimension).
Exact answer: n/3, because each term integrates to 1/3.

--- 5.1  Riemann sum (midpoint rule) ---
   dim  steps           boxes        result   exact n/3       error   seconds
  -----------------------------------------------------------------------------
     1   1000           1,000    0.33333325    0.333333   -8.33e-08      0.00
     2   1000       1,000,000    0.66666650    0.666667   -1.67e-07      0.27
     5     20       3,200,000    1.66562500    1.666667   -1.04e-03      1.08
  For this f the midpoint rule is off by exactly -n/(12*steps^2), and the results match that
  formula to 9 digits, so the program does what the maths says.

  100 dimensions:
  steps=2 (just TWO slices per side) -> 1.27e+30 grid points: refused. At the speed measured in the 5-D run
  (2,964,975 evaluations per second) that is about 1.4e+16 years of computing.
  The only grid that can be afforded is steps=1 (a single box, f at its centre): 25.0000  vs exact 33.3333  -> 25% off, and no way to refine it.

  Why: the number of boxes is steps^n.
     dim     boxes with 10 steps        time at that speed
  --------------------------------------------------------
       1                      10                 3.4e-06 s
       2                     100                 3.4e-05 s
       5                 100,000                   0.034 s
      10                   1e+10                0.039 days
      20                   1e+20             1.1e+06 years
     100                  1e+100             1.1e+86 years

--- 5.2  Monte Carlo (100,000 random points each) ---
  The error of Monte Carlo shrinks like 1/sqrt(N) in EVERY dimension. What changes with n is only
  how spread out f is: here the spread grows like sqrt(n) while the answer grows like n, so the
  relative error even gets smaller in higher dimensions.
   dim    estimate  +- std error   exact n/3   abs error  rel error  std err/exact  seconds
  -----------------------------------------------------------------------------------------
     1     0.33342       0.00094     0.33333     0.00008     0.025%         0.283%     0.06
     2     0.66541       0.00134     0.66667     0.00125     0.188%         0.200%     0.07
     5     1.66690       0.00210     1.66667     0.00023     0.014%         0.126%     0.11
   100    33.32002       0.00941    33.33333     0.01331     0.040%         0.028%     1.15
  "rel error" is what happened in this one run; "std err/exact" is the size of error to EXPECT, and it
  does fall with the dimension (the single runs wobble around it).
  The same number of points (100,000) handles 100 dimensions: 1.2 s (each point just has 100 numbers
  instead of 1) and 0.04% off, where the Riemann sum could not even start.

  How the 100-D estimate improves with more points (exact 33.33333):
      points    estimate   abs error   std error
  ----------------------------------------------
         100     33.3654      0.0320      0.2636
       1,000     33.3740      0.0407      0.0914
      10,000     33.3383      0.0050      0.0293
     100,000     33.3378      0.0044      0.0095

  Riemann sum vs Monte Carlo, in short:
    cost         Riemann: steps^n evaluations (explodes)     Monte Carlo: N evaluations, you choose
    error        Riemann: ~ 1/steps^2, great in 1-3 dims      Monte Carlo: ~ 1/sqrt(N), any dimension
    error info   Riemann: needs smoothness to be accurate     Monte Carlo: reports its own std error

==============================================================================
SELF-CHECK: 27 of 27 comparisons with exact values passed
==============================================================================
```

The `seconds` columns depend on the computer. Everything else is identical on
every run.

## 10. Checks, corrections and limitations

**Checks.** The program ends with a self-check: 27 comparisons of a result with
an exact value (known derivatives, exact integrals, the ball volume formula, the
predicted grid error `n*(1/3 - 1/(12*steps^2))`). For Monte Carlo the check is
"within 4 standard errors". All 27 pass.

**Corrections made while building it.** Three explanations in the first
version were wrong or sloppy and were fixed after reading the output:

1. The left rule looked like order 2 on sin over [0, pi] because of the
   coincidence described in section 3; the test integral was changed to e^x on [0, 1].
2. It claimed "error x sqrt(N) stays constant" for Monte Carlo, but that
   column wobbles because the error is random; the constant quantity is
   "std error x sqrt(N)", which is what the table now shows.
3. It said the Monte Carlo error does not depend on the dimension; the
   *rate* 1/sqrt(N) does not, but the spread of f does (and here grows with n).
   The new "std err / exact" column shows the effect.

**Limitations.**
- The Riemann sum uses the same number of slices in every dimension and only
  the midpoint and left rules.
- The 100-D Riemann time is an extrapolation from the measured speed, not a
  measurement; it is only meant to show the order of magnitude.
- Timings come from one machine and differ on others. Pure Python was used on
  purpose, so nothing has to be installed; NumPy would be much faster.