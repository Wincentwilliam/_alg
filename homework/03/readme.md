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