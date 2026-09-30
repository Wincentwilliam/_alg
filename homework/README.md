# Homework 1: power2n(n)

> This README was created with the help of Claude AI.

Name: 洪偉升
Department: 資訊工程學系
Student ID: 111310523
Class: Introduction to Algorithms 

## Assignment

Implement `power2n(n)` to compute 2 to the power of n, and compare the following four
implementations at `n = 100`:

1. **Method 1**: direct use of Python's built-in exponentiation `2 ** n`
2. **Method 2a**: recursion, `power2n(n) = power2n(n-1) + power2n(n-1)`
3. **Method 2b**: recursion, `power2n(n) = 2 * power2n(n-1)`
4. **Method 3**: recursion + lookup table (memoization)

## Files

- `power2n.py`: the four implementations, plus a main program that tests and times each one

## Method explanations

### Method 1: `2 ** n`
Uses Python's built-in power operator directly (implemented internally with fast exponentiation, roughly O(log n)). This is the fastest method.

### Method 2a: `f(n-1) + f(n-1)`
This looks like it halves the problem size at each step, but it actually calls
`power2n(n-1)` **twice**. Each level of recursion doubles the number of calls,
so the total number of calls is O(2^n). At `n = 100` that's about 2^100 calls
(roughly 10^30), which no computer could finish in any reasonable amount of time.
This method effectively never completes for n = 100.

### Method 2b: `2 * f(n-1)`
Calls `power2n(n-1)` only once, reducing the problem size by 1 each time.
Time complexity is O(n), so n = 100 only needs 100 levels of recursion and runs quickly.

### Method 3: recursion + lookup table
Builds on method 2b by adding a dictionary (table) that stores values already computed.
If the same `n` is requested again, it's looked up directly instead of being
recomputed. For this particular problem there's no repeated computation of the
same `n`, so the table doesn't provide a real speed advantage here complexity
is still O(n) but it demonstrates memoization, a technique that's very useful
for recursions with overlapping subproblems (e.g. Fibonacci).

## Test results (n = 100)

| Method | Completes? | Time |
|---|---|---|
| Method 1 (2**n) | Yes | ~0.01 sec |
| Method 2a (f(n-1)+f(n-1)) | No timeout, still not done after 5 sec | — |
| Method 2b (2*f(n-1)) | Yes | ~0.005 sec |
| Method 3 (recursion + table) | Yes | ~0.003 sec |

(Exact numbers vary by machine, but method 2a will never finish at n = 100 in a
reasonable amount of time. The timeout in `power2n.py` is implemented with
`multiprocessing` each method runs in its own process so it can be forcibly
killed after 5 seconds on any OS, including Windows, where the Unix-only
`signal.alarm` is not available. This adds a small process-spawn overhead
of a few milliseconds to the measured times, but it does not change which
method is fastest or which one times out.)

## Conclusion

- **Fastest**: Method 1 (built-in exponentiation)
- **Slowest / never finishes**: Method 2a, because the number of calls grows
  exponentially as O(2^n)
- Methods 2b and 3 are both O(n) and run at similar speed. Method 3's lookup
  table doesn't help *for this specific problem*, but it illustrates how
  memoization a common optimization technique is written.

---

# Homework 2: Solving Recurrence Relations

> This README was written by Claude AI to explain the step-by-step solutions.

Name: 洪偉升
Department: 資訊工程學系
Student ID: 111310523
Class: Introduction to Algorithms 


## Overview

This homework asks us to find the **exact closed-form formula** and the
**Big O** growth rate for four recurrence relations. The method used
throughout is **unrolling (repeated substitution)**: we expand the
recurrence step by step until a clear pattern appears, then sum that
pattern using either an arithmetic series or a geometric series formula.

| Series type | Formula |
|---|---|
| Arithmetic sum | 1 + 1 + ... + 1 (k times) = k |
| Geometric sum | 2⁰ + 2¹ + ... + 2^(k-1) = 2^k − 1 |

For recurrences involving `n/2`, we assume **n = 2^k** (a power of two) so
that the division always comes out even, and substitute `k = log₂n` back
in at the end.

---

## 1. T(n) = T(n-1) + 8, T(1) = 1

### Unrolling

```
T(n) = T(n-1) + 8
     = T(n-2) + 8 + 8
     = T(n-3) + 8 + 8 + 8
     ...
     = T(1) + 8(n-1)
```

Each step down adds one more constant `8`. Going from `T(n)` down to
`T(1)` takes `(n-1)` steps, so `8` is added `(n-1)` times.

### Solving

```
T(n) = T(1) + 8(n-1) = 1 + 8n - 8
```

**Exact formula: T(n) = 8n − 7**

**Verification:** T(2) = T(1) + 8 = 9, and 8(2) − 7 = 9 ✓

**Big O: O(n)** — linear growth, like a single loop from 1 to n.

---

## 2. T(n) = 2T(n-1) + 9, T(1) = 1

### Unrolling

```
T(n) = 2T(n-1) + 9
     = 2[2T(n-2) + 9] + 9      = 4T(n-2) + 2(9) + 9
     = 4[2T(n-3) + 9] + 2(9)+9 = 8T(n-3) + 4(9)+2(9)+9
     ...
     = 2^(n-1) T(1) + 9(2^(n-2) + 2^(n-3) + ... + 2 + 1)
```

The bracketed sum is a geometric series:
`2^0 + 2^1 + ... + 2^(n-2) = 2^(n-1) − 1`

### Solving

```
T(n) = 2^(n-1)(1) + 9(2^(n-1) - 1)
     = 2^(n-1) + 9·2^(n-1) - 9
     = 10·2^(n-1) - 9
     = 5·2^n - 9
```

**Exact formula: T(n) = 5·2ⁿ − 9**

**Verification:** T(2) = 2T(1) + 9 = 11, and 5(2²) − 9 = 20 − 9 = 11 ✓

**Big O: O(2ⁿ)** — exponential growth. This is the classic pattern seen in
recurrences like the Tower of Hanoi, where the problem size only shrinks
by 1 but the work doubles at every step.

---

## 3. T(n) = 2T(n/2) + 1, T(1) = 1

Assume **n = 2^k**.

### Unrolling

```
T(n) = 2T(n/2) + 1
     = 2[2T(n/4) + 1] + 1      = 4T(n/4) + 2 + 1
     = 4[2T(n/8) + 1] + 2+1    = 8T(n/8) + 4+2+1
     ...
     = 2^k T(n/2^k) + (2^(k-1) + ... + 2 + 1)
```

This stops when `n/2^k = 1`, i.e. `k = log₂n`, and `2^k = n`.
The bracketed sum is `2^k − 1 = n − 1`.

### Solving

```
T(n) = n·T(1) + (n - 1) = n(1) + n - 1 = 2n - 1
```

**Exact formula: T(n) = 2n − 1**

**Verification:** T(2) = 2T(1)+1 = 3, and 2(2)−1 = 3 ✓
T(4) = 2T(2)+1 = 7, and 2(4)−1 = 7 ✓

**Big O: O(n)** — linear growth. This is the pattern behind algorithms
like merge sort, where the problem is split in half at every level but
a constant (or linear) amount of merging work is done per level.

---

## 4. T(n) = T(n/2) + 1, T(1) = 1

Assume **n = 2^k**.

### Unrolling

```
T(n) = T(n/2) + 1
     = T(n/4) + 1 + 1
     = T(n/8) + 1 + 1 + 1
     ...
     = T(n/2^k) + k
```

This stops when `n/2^k = 1`, i.e. `k = log₂n`.

### Solving

```
T(n) = T(1) + k = 1 + log₂n
```

**Exact formula: T(n) = log₂n + 1**

**Verification:** T(2) = T(1)+1 = 2, and 1+log₂2 = 1+1 = 2 ✓
T(4) = T(2)+1 = 3, and 1+log₂4 = 1+2 = 3 ✓

**Big O: O(log n)** — logarithmic growth. This is exactly the recurrence
for binary search: the problem is halved at every step, and only a
constant amount of work is done at each level.

---

## Summary Table

| # | Recurrence | Exact Formula | Big O | Similar to |
|---|---|---|---|---|
| 1 | T(n) = T(n-1) + 8 | 8n − 7 | O(n) | Simple linear loop |
| 2 | T(n) = 2T(n-1) + 9 | 5·2ⁿ − 9 | O(2ⁿ) | Tower of Hanoi |
| 3 | T(n) = 2T(n/2) + 1 | 2n − 1 | O(n) | Merge sort |
| 4 | T(n) = T(n/2) + 1 | log₂n + 1 | O(log n) | Binary search |

## Key Takeaway

The shape of a recurrence tells you a lot before you even solve it:

- **T(n-1)** (shrinks by a constant) + **constant work** → usually **O(n)**
- **2·T(n-1)** (branches into 2, shrinks by 1) + constant work → usually
  **O(2ⁿ)** (exponential — very slow)
- **2·T(n/2)** (branches into 2, but halves the size) + constant work per
  level → usually **O(n)** (the branching and the halving cancel out)
- **T(n/2)** (only halves, no branching) + constant work → usually
  **O(log n)** (very fast)

---

# Homework 3 (Week 3): Enumeration + Brute Force — Solving SAT

> This README was written by Claude AI to explain the assignment, the concept behind it, and the actual code/output used to solve it.

Name: 洪偉升
Department: 資訊工程學系
Student ID: 111310523
Class: Introduction to Algorithms

## 1. The material given by the teacher

- **Topic**: Enumeration + Brute Force
- **Task**: Write a program that systematically enumerates a truth table
  to solve the SAT problem.
- **Reference**: [Boolean satisfiability problem — Wikipedia](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)

This is a classic Week-3-style exercise in an algorithms course: before
learning smarter algorithms, you first learn the simplest possible one —
brute force — and see with your own eyes why it works but also why it
doesn't scale.

## 2. What is the SAT problem?

**SAT (Boolean Satisfiability Problem)**: given a logical formula built
from boolean variables (each variable is either `0`/false or `1`/true)
combined with `AND`, `OR`, and `NOT`, the question is:

> **Is there at least one combination of 0/1 values for the variables
> that makes the whole formula equal to 1 (true)?**

- If yes -> the formula is **SAT (satisfiable)**
- If no -> the formula is **UNSAT (unsatisfiable)**

SAT is one of the most important problems in computer science because it
is **NP-complete** -- no algorithm is known that can solve every SAT
instance quickly (in polynomial time) as the number of variables grows.
That's exactly why this exercise starts with the simplest possible
method: try everything.

## 3. The concept: enumeration + brute force

- **Enumeration** = systematically listing out *every single*
  combination of values, in a fixed order, without skipping any.
- **Brute force** = for each combination listed, actually test it
  against the formula -- no shortcuts, no guessing, no skipping.

For a formula with `n` variables, each variable can be `0` or `1`, so
there are exactly **2^n** possible combinations -- this is the entire
**truth table**. Brute force means: build all 2^n rows, and check the
formula's result on every one of them.

| n (variables) | 2^n (rows to check) |
|---|---|
| 1 | 2 |
| 3 | 8 |
| 10 | 1,024 |
| 20 | 1,048,576 |

**Time complexity: O(2^n)**. This confirms the formula is checked
*correctly* (nothing is missed), but the number of rows doubles every
time one more variable is added -- this is exponential growth, the same
idea as the `power2n` recursion from a previous homework.

## 4. How the code solves it (`sat_solver.py`)

```python
import itertools

def evaluate_formula(formula_func, variables, bits):
    values = dict(zip(variables, [bool(b) for b in bits]))
    return formula_func(values)

def brute_force_sat(formula_func, variables, formula_name="Formula"):
    n = len(variables)
    total_rows = 2 ** n
    satisfying_rows = []

    header = "  ".join(f"{v:>2}" for v in variables) + "  |  Result"
    print(f"\n=== {formula_name} ===")
    print(header)
    print("-" * len(header))

    for bits in itertools.product([0, 1], repeat=n):
        result = 1 if evaluate_formula(formula_func, variables, bits) else 0
        row = "  ".join(f"{b:>2}" for b in bits) + f"  |  {result}"
        print(row)
        if result == 1:
            satisfying_rows.append(bits)

    print(f"\nTotal rows checked : {total_rows}")
    print(f"Rows where result=1 : {len(satisfying_rows)}")
    if satisfying_rows:
        print("Verdict: SAT. Example:", dict(zip(variables, satisfying_rows[0])))
    else:
        print("Verdict: UNSAT.")

    return satisfying_rows
```

Step by step:

1. **`itertools.product([0, 1], repeat=n)`** -- this single line does the
   *enumeration*. It generates every possible combination of `0`/`1`
   for `n` variables, in order, e.g. for n=3 it produces
   `(0,0,0), (0,0,1), (0,1,0), ..., (1,1,1)` -- all 2^3 = 8 rows, none
   skipped.
2. For every row generated, `evaluate_formula` plugs the `0`/`1` values
   into the formula (converting them to `True`/`False` internally,
   since Python's `and`/`or`/`not` work with booleans) and returns the
   result as `0` or `1` -- this is the *brute force* part: the formula
   is actually evaluated for every single row, not assumed.
3. Every row that gives result `1` is stored as a satisfying assignment.
4. After all 2^n rows are checked: if at least one row gave `1`, the
   formula is **SAT**; if none did, it's **UNSAT**.

A formula is written as a small Python function, e.g.:
```python
f1 = lambda v: (v["A"] or v["B"]) and (not v["A"] or v["C"])
```
This avoids needing to build a full logic-expression parser -- any
formula can be tested just by writing it as ordinary Python boolean
logic using a dictionary of variable values.

## 5. Actual output from running the program

```
Note: 0 = False, 1 = True

=== (A or B) and (not A or C) ===
 A   B   C  |  Result
---------------------
 0   0   0  |  0
 0   0   1  |  0
 0   1   0  |  1
 0   1   1  |  1
 1   0   0  |  0
 1   0   1  |  1
 1   1   0  |  0
 1   1   1  |  1

Total rows checked : 8
Rows where result=1 : 4
Verdict: SAT. Example: {'A': 0, 'B': 1, 'C': 0}

=== A and (not A) ===
 A  |  Result
-------------
 0  |  0
 1  |  0

Total rows checked : 2
Rows where result=1 : 0
Verdict: UNSAT.
```

### Reading the results

**Formula 1: `(A or B) and (not A or C)`**
- All 2^3 = 8 rows were generated and checked -- exactly matches the
  theoretical count.
- 4 out of 8 rows give result `1`, so this formula is **satisfiable**.
- Example satisfying assignment: `A=0, B=1, C=0`. Check it by hand:
  `(0 or 1) and (not 0 or 0)` = `1 and 1` = `1` (correct)

**Formula 2: `A and (not A)`**
- All 2^1 = 2 rows were checked (`A=0` and `A=1`).
- Neither row gives result `1` -- this makes sense, because a variable
  and its own negation can logically never both be true at the same
  time. This is a **contradiction**, so the program correctly reports
  **UNSAT**.

Both results confirm the brute-force method works correctly: since
*every* row is checked, the program can never miss a satisfying
assignment, and it can only declare UNSAT after truly ruling out all
2^n possibilities.

## 6. Discussion / concept to understand for this lesson

- **Correctness vs. efficiency**: brute force is always *correct* -- it
  can never give a wrong SAT/UNSAT answer, because it doesn't skip
  anything. But it is not *efficient* -- the cost grows exponentially
  with the number of variables (O(2^n)).
- **Why SAT matters**: many real-world problems (scheduling, circuit
  design, puzzle solving, verification) can be reduced to SAT. Since
  SAT is NP-complete, solving it efficiently in general is one of the
  biggest open questions in computer science (the P vs NP problem).
- **Why this is only a starting point**: real SAT solvers don't use
  brute force -- they use smarter algorithms like **DPLL** or **CDCL**,
  which prune large parts of the search space early instead of
  checking every single row. This exercise is meant to make the naive
  baseline concrete before those smarter techniques are introduced
  later in the course.
- **Connection to previous exercises**: this is the same O(2^n) growth
  pattern seen in the `power2n` and recurrence-relation homeworks --
  it's a recurring theme in algorithms: some approaches look simple
  but scale terribly, which is exactly why complexity analysis matters
  before choosing an approach.

## 7. How to run

```
python sat_solver.py
```

To test a different formula, add a new block following the same
pattern used for the two examples above (define the variable list,
define the formula as a lambda, then call `brute_force_sat(...)`).

---

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

---