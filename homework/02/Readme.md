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