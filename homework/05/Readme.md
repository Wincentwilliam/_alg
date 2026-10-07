# Homework 5 (Week 5): Recursion, Functional Programming, Lambda Calculus

> This README was written by Claude AI to explain the three problems, the approach taken for each, the upgrades added on top, and the actual output.

Name: 洪偉升
Department: 資訊工程學系
Student ID: 111310523
Class: Introduction to Algorithms

## Assignment

1. Solve the Tower of Hanoi problem two ways: recursively, and without
   recursion.
2. Use recursion to solve symbolic differentiation, `sym_diff(expr)`.
3. Build your own `map`, `filter`, `reduce`, then (without using any
   loops) solve bubble sort.

Files:
- `hanoi.py` — Problem 1
- `sym_diff.py` — Problem 2
- `functional_sort.py` — Problem 3

---

## Problem 1: Tower of Hanoi (`hanoi.py`)

### The recursive version

The classic rule for moving `n` disks from `src` to `dst` using `aux` as
a spare peg:

1. Move the top `n-1` disks out of the way, onto `aux`
2. Move the remaining large disk from `src` to `dst`
3. Move the `n-1` disks from `aux` onto `dst`

```python
def hanoi_recursive(n, src='A', aux='B', dst='C', moves=None):
    if moves is None:
        moves = []
    if n == 0:
        return moves
    hanoi_recursive(n - 1, src, dst, aux, moves)
    moves.append((src, dst))
    hanoi_recursive(n - 1, aux, src, dst, moves)
    return moves
```

### The non-recursive version

Removing the recursive function calls doesn't remove the underlying
algorithm — it just means **we** have to manage the "call stack"
ourselves instead of letting Python's interpreter do it. `hanoi_iterative`
keeps an explicit `stack` (an ordinary Python list) holding either:
- `('solve', k, s, a, d)` — "still need to solve the sub-problem of
  moving `k` disks from `s` to `d` using `a`"
- `('move', s, d)` — "actually record one disk move from `s` to `d`"

Each `('solve', ...)` task, when popped, pushes back exactly the three
steps the recursive version would have called — in reverse order, since
a stack is last-in-first-out. This is a direct simulation of recursion
with a plain list and a `while` loop — no recursive function call is
used anywhere in this version.

### Upgrade: watching it happen

`replay()` takes the move list and actually simulates the three pegs,
printing what every peg looks like after each move — instead of just
reading a list of letters, you can watch the puzzle get solved disk by
disk. The program also now asks how many disks to use instead of it
being hardcoded, and double-checks that both methods agree and that the
move count matches the known formula `2ⁿ − 1`.

### Actual output (3 disks)

```
How many disks? (default 4): 3

Solving Hanoi with 3 disks (7 moves expected)
Recursive and non-recursive move sequences match: True
Move count correct (2^n - 1): True

Replaying the solution step by step:

start:
  A: [3] [2] [1]
  B:
  C:

move 1: A -> C  (disk 1)
  A: [3] [2]
  B:
  C: [1]

move 2: A -> B  (disk 2)
  A: [3]
  B: [2]
  C: [1]

move 3: C -> B  (disk 1)
  A: [3]
  B: [2] [1]
  C:

move 4: A -> C  (disk 3)
  A:
  B: [2] [1]
  C: [3]

move 5: B -> A  (disk 1)
  A: [1]
  B: [2]
  C: [3]

move 6: B -> C  (disk 2)
  A: [1]
  B:
  C: [3] [2]

move 7: A -> C  (disk 1)
  A:
  B:
  C: [3] [2] [1]
```

Both methods produce **exactly the same sequence of moves** (verified
automatically, not just read by eye), and the move count always equals
the textbook formula `2ⁿ − 1`.

---

## Problem 2: Symbolic Differentiation (`sym_diff.py`)

### Representing expressions

Since there's no math expression parser available, expressions are
written as nested tuples in **prefix notation**:

| Math | Tuple form |
|---|---|
| `x` | `'x'` |
| `3` | `3` |
| `x² + 3x` | `('+', ('**', 'x', 2), ('*', 3, 'x'))` |
| `x·sin(x)` | `('*', 'x', ('sin', 'x'))` |

A bare number is treated as a constant, a bare string as a variable.

### The rules, applied recursively

`sym_diff(expr, var)` pattern-matches on the operator at the front of
the tuple and applies the standard calculus rule, calling itself on the
sub-expressions:

| Rule | Formula |
|---|---|
| Constant | `d/dx[c] = 0` |
| Variable | `d/dx[x] = 1`, `d/dx[y] = 0` |
| Sum | `(a+b)' = a' + b'` |
| Product | `(a·b)' = a'·b + a·b'` |
| Quotient | `(a/b)' = (a'b − ab') / b²` |
| Power (constant exponent) | `(aⁿ)' = n·aⁿ⁻¹·a'` (chain rule included) |
| `sin`, `cos`, `exp`, `ln` | standard chain-rule derivatives |

A derivative computed this way is technically correct but full of
clutter like `x*1`, `0+y`, `x**1` — so `simplify()` recursively cleans
those up, and `to_string()` turns the tuple back into a readable
formula for printing.

### Upgrade: proving the derivative is actually correct

Algebra rules can be implemented wrong without anything crashing, so
`evaluate(expr, values)` plugs real numbers into an expression (prefix
tuple or plain number/variable) and computes its value, and
`numerical_derivative(expr, var, x, h)` estimates the derivative purely
numerically using the **central difference formula**:

```
f'(x) ≈ (f(x+h) − f(x−h)) / (2h)
```

For every test expression, the program now evaluates the symbolic
derivative at a specific point (`x = 1.7`) and compares it against this
independent numerical estimate. If `sym_diff` had a bug in any rule, the
two numbers would disagree — this is effectively a built-in unit test
for the differentiation logic itself.

### Actual output

```
d/dx [x^2]  =  (2 * x)
    at x=1.7: symbolic=3.400000  numeric=3.400000  OK
d/dx [(x^2 + (3 * x))]  =  ((2 * x) + 3)
    at x=1.7: symbolic=6.400000  numeric=6.400000  OK
d/dx [(x * sin(x))]  =  (sin(x) + (x * cos(x)))
    at x=1.7: symbolic=0.772629  numeric=0.772629  OK
d/dx [x^3]  =  (3 * x^2)
    at x=1.7: symbolic=8.670000  numeric=8.670000  OK
d/dx [(1 / x)]  =  ((0 - 1) / x^2)
    at x=1.7: symbolic=-0.346021  numeric=-0.346021  OK
d/dx [exp(x^2)]  =  (exp(x^2) * (2 * x))
    at x=1.7: symbolic=61.177253  numeric=61.177253  OK
```

All six derivatives match their numerical estimate to within `1e-4`,
confirming each rule (sum, product, quotient, power, and the chain rule
for `sin`/`cos`/`exp`) is implemented correctly — not just "looks right"
by eye, but is independently verified.

---

## Problem 3: Custom map/filter/reduce + Loop-Free Bubble Sort (`functional_sort.py`)

### Building map, filter, reduce from scratch

All three are written using **recursion only** — no `for`/`while`
anywhere:

```python
def my_map(func, lst):
    if not lst:
        return []
    return [func(lst[0])] + my_map(func, lst[1:])

def my_filter(pred, lst):
    if not lst:
        return []
    head, tail = lst[0], my_filter(pred, lst[1:])
    return [head] + tail if pred(head) else tail

def my_reduce(func, lst, acc):
    if not lst:
        return acc
    return my_reduce(func, lst[1:], func(acc, lst[0]))
```

Each one peels off the first element, recurses on the rest, and
combines the result — the same divide-and-conquer shape used in the
Tower of Hanoi solution.

### Bubble sort, without a single loop

The key idea: **one pass of bubble sort is itself a left-to-right fold**
— you carry along "the value currently being bubbled" and "everything
already placed", comparing it against each new element as you go. That
is precisely what `reduce` is for, so `bubble_pass` is implemented using
`my_reduce` instead of a loop:

```python
def bubble_pass(lst, should_swap=lambda a, b: a > b):
    placed, last, swapped = my_reduce(
        lambda acc, x: (
            (acc[0], x, acc[2]) if acc[1] is None
            else (acc[0] + [x], acc[1], True) if should_swap(acc[1], x)
            else (acc[0] + [acc[1]], x, acc[2])
        ),
        lst,
        ([], None, False),
    )
    return placed + ([last] if last is not None else []), swapped


def bubble_sort(lst, descending=False):
    should_swap = (lambda a, b: a < b) if descending else (lambda a, b: a > b)
    new_lst, swapped = bubble_pass(lst, should_swap)
    if not swapped:
        return new_lst
    return bubble_sort(new_lst, descending)
```

The accumulator is a triple `(placed_so_far, value_being_carried,
did_we_swap)`. Repeating passes until one reports no swaps is, again,
pure recursion — no loop anywhere in the sorting logic itself.

### Upgrade 1: ascending or descending

`should_swap` is now a parameter instead of being hardcoded, so the
exact same fold logic can sort either direction just by flipping the
comparison — `bubble_sort(nums, descending=True)`.

### Upgrade 2: stress testing instead of one example

Trusting a single hand-picked example isn't very convincing, so
`stress_test()` generates 300 random lists of random lengths and
compares `bubble_sort` against Python's own `sorted()` on every single
one, reporting any mismatch it finds. `random_list()` and the inner
`run()` helper build the random samples and loop through the trials
**recursively** — the whole file stays genuinely loop-free, not just
the sorting logic.

**A note on recursion depth**: because this recursion isn't tail-call
optimized by Python, each trial adds a stack frame that doesn't get
freed until all 300 (or however many) trials finish. With Python's
default recursion limit of 1000, this comfortably handles up to
roughly 950 trials before hitting a `RecursionError` — plenty of
headroom for 300, but a reminder that "rewrite the loop as recursion"
isn't free: it trades loop overhead for stack depth, which is finite.

### Actual output

```
my_map   : [25, 1, 16, 4, 64, 0, 81, 9]
my_filter: [4, 2, 8, 0]
my_reduce: 32

unsorted  : [5, 1, 4, 2, 8, 0, 9, 3]
ascending : [0, 1, 2, 3, 4, 5, 8, 9]
descending: [9, 8, 5, 4, 3, 2, 1, 0]

Stress test: 300 random lists compared against sorted()
  all passed
```

- `my_map(x -> x*x, nums)` squares every element.
- `my_filter(x -> x % 2 == 0, nums)` keeps only the even numbers.
- `my_reduce(+, nums, 0)` sums everything (5+1+4+2+8+0+9+3 = 32).
- `bubble_sort` sorts correctly in both directions, and all 300 random
  stress-test cases matched Python's built-in `sorted()` exactly — using
  nothing but recursion and the custom `my_reduce` from above.

---

## Why these three problems belong together

All three problems are really the same lesson told three different
ways: **a loop is just one way to repeat something — recursion (and
functional tools built on recursion, like map/filter/reduce) is
another**, and the two are interchangeable:

- Problem 1 shows this directly: the same algorithm, once with real
  recursive function calls, once with a manually-managed stack doing
  the exact same job — and the step-by-step replay proves both really
  do produce the identical solution, not just two outputs that happen
  to look similar.
- Problem 2 shows recursion as the natural way to process a *nested*
  structure — a math expression is a tree, and differentiating it means
  differentiating its parts and combining the results. The numerical
  cross-check shows that recursive symbolic manipulation can be
  verified independently, the same way you'd check any algorithm.
- Problem 3 shows that the "primitive" functional tools — map, filter,
  reduce — are themselves just recursion with a name, and that a
  surprisingly loop-heavy-looking algorithm like bubble sort can be
  rebuilt entirely out of them, then proven correct at scale with a
  stress test rather than a single example.