# Homework 4 (Week 4): Iterative Methods

> This README was written by Claude AI to explain both parts of the assignment, the code, and the actual output.

Name: 洪偉升
Department: 資訊工程學系
Student ID: 111310523
Class: Introduction to Algorithms

## Assignment overview

This homework has two parts:

1. **Write a program that solves a self-chosen problem using an
   iterative method**, following the style of the reference file
   [`iterative3.py`](https://github.com/ccc115a/alg/blob/main/02-方法/03-迭代法/01a-equation/iterative3.py).
2. **Read and understand** the reference file
   [`iter_framework.py`](https://github.com/ccc115a/alg/blob/main/02-方法/03-迭代法/05-framework/iter_framework.py),
   then **write documentation** explaining how it works.

Files in this submission:
- `iterative_sqrt.py` — Part 1
- `README.md` (this file) — explanation for both parts

---

## Part 1: `iterative_sqrt.py`

### The problem chosen

The reference file `iterative3.py` solves `x² = 3` (i.e. finds `√3`)
using three different **fixed-point iteration** formulas, run side by
side, to show that some formulas converge and some don't.

For this homework, the self-chosen problem is a generalization of that
same idea: **finding the square root of any number `N`** (not just 3),
using the same three-formula comparison technique, plus:
- letting the user type in **any number they want** and see the result
  immediately
- a summary table comparing the same three formulas across several
  different numbers at once
- tracking the numerical error against Python's own `math.sqrt()` as a
  ground truth

### What is fixed-point iteration?

To find `√N`, the equation `x² = N` is rearranged into the form
`x = g(x)`, where `g` is some formula built from `x` and `N`. Starting
from a guess, repeatedly applying `g` (i.e. `x = g(x)`, over and over)
will, for a *good* choice of `g`, make `x` get closer and closer to the
true answer. This is called a **fixed point**, because once you plug in
the true answer, applying `g` again gives back the same value.

Not every rearrangement of the equation converges, which is exactly
what this program demonstrates using three different formulas:

| Formula | Definition | Behavior |
|---|---|---|
| Formula 1 | `x = N / x` | **Never converges** — it just bounces back and forth between two values forever |
| Formula 2 | `x = x − (1/2N)·(x² − N)` | **Converges, but slowly** |
| Formula 3 | `x = ½·(x + N/x)` | **Converges very fast** — this is Newton's method (also known as the Babylonian method) applied to square roots |

### How the code works

```python
def find_sqrt(N, iterations=15, show_table=True):
    true_value = math.sqrt(N)

    g1 = lambda x: N / x
    g2 = lambda x: x - 1 / (2 * N) * (x * x - N)
    g3 = lambda x: 1 / 2 * (x + N / x)

    x1 = x2 = x3 = 1.0

    for i in range(iterations):
        x1, x2, x3 = g1(x1), g2(x2), g3(x3)
        ...  # print each step

    return x1, x2, x3, true_value
```

- `find_sqrt(N, ...)` wraps the whole process into a reusable function,
  so it can be run for **any** `N`, any number of times.
- All three formulas start from the same initial guess (`x = 1.0`) and
  are updated together in the same loop, exactly like the reference
  `iterative3.py`.
- `show_table=True` prints every iteration step; `show_table=False` is
  used for the summary table so it only prints the final results.

The `if __name__ == "__main__":` block has two parts:

**Part A — interactive input:**
```python
user_input = input("Enter a number to find its square root (or press Enter to skip): ")
if user_input:
    N = float(user_input)
    find_sqrt(N)
```
This lets the person running the program type in **any number** and
immediately see the full iteration table for that specific number.

**Part B — summary table across several numbers:**
```python
for N in [2, 5, 10, 25, 50, 100]:
    x1, x2, x3, true_value = find_sqrt(N, iterations=15, show_table=False)
    print(...)
```
This runs the same three formulas across six different numbers, so the
convergence pattern can be compared side by side.

### Actual output

**Example: user enters `7`**
```
Enter a number to find its square root (or press Enter to skip): 7
Finding sqrt(7.0) = 2.645751 using 3 iteration formulas
 i        x1 (N/x)    x2 (grad step)     x3 (Newton)
-------------------------------------------------------
 0        7.000000          1.428571        4.000000
 1        1.000000          1.782799        2.875000
 2        7.000000          2.055772        2.654891
 3        1.000000          2.253901        2.645767
 4        7.000000          2.391039        2.645751
 5        1.000000          2.482677        2.645751
 6        7.000000          2.542414        2.645751
 7        1.000000          2.580709        2.645751
 8        7.000000          2.604990        2.645751
 9        1.000000          2.620278        2.645751
10        7.000000          2.629860        2.645751
11        1.000000          2.635848        2.645751
12        7.000000          2.639584        2.645751
13        1.000000          2.641912        2.645751
14        7.000000          2.643362        2.645751

--- Final results after 15 iterations ---
True value          : 2.645751
Formula 1 (x1)      : 7.000000   | error = 4.354249
Formula 2 (x2)      : 2.643362   | error = 0.002389
Formula 3 (x3)      : 2.645751   | error = 0.000000
```

**Summary table across several numbers:**
```
================ Summary across several numbers ================
     N    sqrt(N) true      Formula1      Formula2      Formula3
-----------------------------------------------------------------
     2        1.414214      2.000000      1.414214      1.414214
     5        2.236068      5.000000      2.235768      2.236068
    10        3.162278     10.000000      3.149116      3.162278
    25        5.000000     25.000000      4.742925      5.000000
    50        7.071068     50.000000      5.992650      7.071068
   100       10.000000    100.000000      6.997355     10.000000
```

### Reading the results

- **Formula 1** always ends up bouncing between `N` and `1` — it never
  gets any closer to the true answer, no matter which `N` is tested.
  This is because its derivative at the fixed point has magnitude
  greater than 1, which mathematically guarantees divergence for fixed-
  point iteration.
- **Formula 2** always converges, but it takes many more iterations to
  get close (notice how far off it still is from the true value after
  only 15 steps for larger `N`, like `100`).
- **Formula 3** converges to the correct answer (to 6 decimal places)
  within just 4-5 iterations for every single `N` tested. This
  quadratic convergence rate is the hallmark of Newton's method.

### How to run

```
python iterative_sqrt.py
```
Type any number when prompted, or press Enter to skip straight to the
summary table.

---

## Part 2: Documentation for `iter_framework.py`

### What this file is about

`iter_framework.py` demonstrates a very important idea: **almost every
iterative algorithm in numerical computing, linear algebra, and machine
learning shares the exact same underlying skeleton.**

That skeleton is:

```
state = initial_state
repeat:
    next_state = do_one_step(state)
    if converged(state, next_state):
        stop
    state = next_state
```

Instead of writing this loop over and over for every algorithm (Newton's
method, Gauss-Seidel, PageRank, K-Means, etc.), this file writes the loop
**once**, as a generic, reusable framework — and then plugs in 9 different
classic algorithms as just two small functions each: a **transition
function** and a **convergence check**.

This is an example of the **Template Method design pattern**: the
overall algorithm structure (the loop) is fixed, but the specific
behavior at each step is customizable.

### The core framework: `generic_iterator`

```python
def generic_iterator(transition_func, is_converged, initial_state, max_iter=1000):
    state = initial_state
    for iteration in range(max_iter):
        next_state = transition_func(state)
        if is_converged(state, next_state, iteration):
            return next_state, iteration + 1
        state = next_state
    print("[warning] reached max iterations without full convergence")
    return state, max_iter
```

| Parameter | Meaning |
|---|---|
| `transition_func` | A function `g(state) -> next_state`. Defines **one step** of whatever algorithm is being run. |
| `is_converged` | A function `(old_state, new_state, iteration) -> bool`. Decides **when to stop**. |
| `initial_state` | The starting point — can be a number, a vector, a matrix, or a tuple. |
| `max_iter` | A safety limit in case the algorithm never converges. |

**Return value**: the final state, and how many iterations it actually took.

### Why this design is powerful

Because `state` can be *anything*, and `transition_func` / `is_converged`
can contain *any* logic, this one loop can represent completely
different algorithms just by changing what gets passed in. The loop
itself never needs to be rewritten once it works.

### How each classic algorithm fits into the framework

| Demo function | Represents | State | Transition | Converged when |
|---|---|---|---|---|
| `demo_fixed_point()` | 2D fixed-point iteration | a 2D vector | linear combination update | vector barely changes |
| `demo_newton()` | Newton's method, solving `x² − 4 = 0` | a number | `x - f(x)/f'(x)` | value stabilizes — same idea as Formula 3 in Part 1 |
| `demo_gauss_seidel()` | Linear system solver | a vector `x` | update each component using latest neighbors | largest change is tiny |
| `demo_power_iteration()` | Dominant eigenvector | a vector `v` | `v_new = A·v`, normalized | direction stops changing |
| `demo_qr_algorithm()` | All eigenvalues of a matrix | a matrix `A` | QR-decompose, then multiply factors in reverse | matrix becomes near-diagonal |
| `demo_rk4()` | ODE solver (Runge-Kutta 4th order) | `(t, y)` | one RK4 step forward | `t` reaches the target end time |
| `demo_pagerank()` | Web page ranking | a vector `r` | `r_new = G·r` (Google matrix) | ranking vector stabilizes — same technique as Power Iteration |
| `demo_kmeans()` | K-Means clustering | cluster centroids | E-step (assign points) + M-step (recompute centroids) | centroids stop moving |
| `demo_em_two_coin()` | Expectation-Maximization | `(theta_A, theta_B)` | E-step (weighted counts) + M-step (update estimates) | both probabilities stop changing |

### The big takeaway

Even though Newton's method, PageRank, K-Means, and solving differential
equations look like completely unrelated topics, **they all boil down to
the exact same pattern**:

> Start somewhere → repeatedly apply an update rule → stop once the
> result stops changing meaningfully.

By separating "how one step works" (`transition_func`) from "when to
stop" (`is_converged`) and from "how to loop" (`generic_iterator`),
this file shows that a single ~10-line function can be reused across
numerical analysis, linear algebra, differential equations, and machine
learning — instead of writing a new, slightly different loop from
scratch every single time.

### Connection between Part 1 and Part 2

Part 1 (`iterative_sqrt.py`) manually writes out a loop with 3 different
formulas tried side by side. `iter_framework.py` shows the *next step*
in abstraction: instead of hardcoding the loop for one specific problem,
the loop itself becomes reusable, and any new iterative method —
including the sqrt-finding formulas from Part 1 — can be plugged in
simply by writing a `transition` function and a `converged` function,
without touching the loop at all.

For example, Formula 3 from Part 1 (`x = ½(x + N/x)`) could be rewritten
using this framework as:

```python
transition = lambda x: 0.5 * (x + N / x)
converged  = lambda old, new, i: abs(new - old) < 1e-9
result, iters = generic_iterator(transition, converged, initial_state=1.0)
```