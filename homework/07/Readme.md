# Homework 7: Dynamic Programming and Text Algorithms -- `diff` via LCS

> This README is the write-up and process document for the assignment. The program and this document were produced with the help of Claude AI, then run and checked as described in section 7.

Name: 洪偉升
Department: 資訊工程學系
Student ID: 111310523
Class: Introduction to Algorithms

## 1. The assignment

Pick a text-type problem and solve it **with dynamic programming** and
**without dynamic programming**, then explain the principle of both,
their complexity, and compare them.

Chosen problem: **`diff` -- comparing two files and listing what was
removed and what was added**, solved through the **Longest Common
Subsequence (LCS)**.

Files:

| File | Purpose |
|---|---|
| `lcs_diff.py` | naive recursion, top-down DP, bottom-up DP, the diff itself, a benchmark and a self-check |
| `output.txt` | the full output of `python lcs_diff.py` |

Run it with:

```
python lcs_diff.py                 # demo: LCS example, program diff, benchmark, self-check
python lcs_diff.py old.txt new.txt # diff two text files of your own
```

## 2. The problem

Given two sequences of lines (or characters) `a` (old) and `b` (new),
find the **longest sequence that appears in both in the same order**
(not necessarily next to each other). Example:

```
a = AGGTAB
b = GXTXAYB      LCS = GTAB   (length 4)
```

For `diff`, the lines are the "characters". Lines that belong to the LCS
are unchanged; every other line of `a` is a deletion (`-`) and every
other line of `b` is an addition (`+`). The longer the LCS, the smaller
the diff, so finding the LCS is exactly finding the smallest set of
changes that turns `a` into `b` (when only insertions and deletions are
allowed).

## 3. The recurrence

Let `L(i, j)` be the LCS length of the suffixes `a[i:]` and `b[j:]`:

```
L(i, j) = 0                              if i or j is at the end
L(i, j) = 1 + L(i+1, j+1)                if a[i] == b[j]
L(i, j) = max(L(i+1, j), L(i, j+1))      otherwise
```

If the first elements match, they can be taken for free. If not, one of
the two must be skipped, and we try both. The answer is `L(0, 0)`.

## 4. Without dynamic programming: plain recursion (`lcs_naive`)

The recurrence is written directly as a recursive function:

```python
def go(i, j):
    if i == len(a) or j == len(b):
        return 0
    if a[i] == b[j]:
        return 1 + go(i + 1, j + 1)
    return max(go(i + 1, j), go(i, j + 1))
```

**Why it is slow:** when the characters differ, the function branches
into two calls, and those branches keep reaching the *same* `(i, j)`
pairs again through different paths. For instance `(i+1, j+1)` is
reached both from `(i+1, j)` and from `(i, j+1)`. The same sub-problem
is solved again and again, and the number of calls grows exponentially.

## 5. With dynamic programming

Two properties make DP applicable:

1. **Optimal substructure**: the answer for `(i, j)` is built from the
   answers of smaller sub-problems.
2. **Overlapping sub-problems**: there are only `(m+1)(n+1)` different
   `(i, j)` pairs, but plain recursion visits them exponentially many
   times.

DP simply makes sure each sub-problem is **solved once and remembered**.

### Top-down DP: memoization (`lcs_memo`)
The same recursion, plus a dictionary. Before computing `(i, j)` it
looks in the table; after computing, it stores the answer. This is the
"recursion + lookup table" idea.

### Bottom-up DP: filling a table (`lcs_table`, `lcs_dp`)
No recursion at all. A table `dp[i][j]` is filled from the end of both
sequences towards the start, so every cell it needs is already computed:

```python
for i in range(m - 1, -1, -1):
    for j in range(n - 1, -1, -1):
        if a[i] == b[j]:
            dp[i][j] = 1 + dp[i + 1][j + 1]
        else:
            dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
```

### Recovering the actual diff (`diff`, `lcs_string`)
The table holds lengths only. To get the real LCS (and therefore the
diff), walk from `dp[0][0]`: if the two current lines are equal, keep
them and move diagonally; otherwise move towards the neighbour with the
bigger value, emitting a deletion (move in `a`) or an addition (move in
`b`). The walk takes `O(m + n)` steps.

## 6. Complexity and comparison

`m` and `n` are the lengths of the two inputs.

| Method | Time | Extra space | Notes |
|---|---|---|---|
| Plain recursion | exponential; in the worst case (no common element) exactly `2*C(m+n, m) - 1` calls, which grows like `2^(m+n)` | `O(m+n)` recursion depth | simplest to write, unusable beyond tiny inputs |
| Top-down DP (memo) | `O(m*n)` | `O(m*n)` table + `O(m+n)` recursion depth | still recursive, so very long inputs hit Python's recursion limit |
| Bottom-up DP | `O(m*n)` | `O(m*n)` table | no recursion, fastest in practice |
| Walk back for the diff | `O(m+n)` | `O(m+n)` result | needs the full table |

If only the *length* of the LCS is needed, bottom-up DP can keep just
two rows (`O(min(m, n))` space), but recovering the diff needs the full
table (or a cleverer scheme such as Hirschberg's algorithm).

**Comparison in one sentence:** both approaches use the same recurrence
and give the same answer, but plain recursion recomputes the same
`(i, j)` states exponentially often, while DP computes each of the
`(m+1)(n+1)` states exactly once, turning exponential time into
polynomial time at the price of `O(m*n)` memory.

**What real `diff` does:** GNU `diff` uses Myers' algorithm, which runs
in `O(N*D)` time where `D` is the number of differences. When two files
are almost the same (small `D`) this is much faster than filling the
whole `m*n` table. The DP table solution here is the classical,
easy-to-understand version of the same problem.

## 7. Actual output

```
== LCS of two strings ==
a = AGGTAB, b = GXTXAYB
naive : (4, 1079)
memo  : (4, 68)
dp    : 4 -> GTAB

== diff of two versions of a small program ==
- def total(prices):
+ def total(prices, tax=0):
      result = 0
      for p in prices:
-         result = result + p
+         result += p
+     result = result * (1 + tax)
      return result
  
- print(total([1, 2, 3]))
+ print(total([1, 2, 3], 0.05))

== naive recursion vs dynamic programming ==
   n   naive calls  naive sec  memo calls  dp cells    dp sec
   4           139     0.0000          33        25  0.000010
   6         1,847     0.0007          73        49  0.000018
   8        25,739     0.0078         129        81  0.000029
  10       369,511     0.0964         201       121  0.000049
  12     5,408,311     0.7693         289       169  0.000042

DP alone on two random strings of length 1500: LCS = 982, 0.39 s (2,253,001 cells)

self-check (300 random pairs, diff reconstructs both files): passed
```

How to read it:

- **LCS example**: all three methods agree the LCS length is 4 and the
  DP walk recovers `GTAB`. The naive version needed 1079 calls for these
  two tiny strings, the memo version 68.
- **diff**: the two versions of the small program are compared line by
  line. Unchanged lines have two spaces, `-` marks a removed line and `+`
  an added line.
- **Benchmark**: the strings `AAAA...` and `CCCC...` share no character,
  which is the worst case for plain recursion. Each time `n` grows by 2
  the number of naive calls is multiplied by roughly 14 (about 3.8 per
  extra character), reaching 5.4 million calls for just `n = 12`. The
  memo version needs only a few hundred calls and the DP table has just
  `(n+1)^2` cells. The naive counts match the closed form
  `2*C(2n, n) - 1` exactly (for example n = 4: `2*70 - 1 = 139`).
  "memo calls" counts every function invocation, including the ones
  that only read the cache, which is why it can be a little larger
  than "dp cells" (the number of table entries). The time columns
  differ a little on every run and on every computer; the call counts
  and the LCS results never change.
- **Large input**: only the DP version can handle two strings of length
  1500 (2.25 million cells): it took about half a second on the machine
  used here (more or less on yours), while plain recursion would never
  finish. The result LCS = 982 was double-checked with a second,
  independently written DP.

## 8. How it was tested

- 300 random pairs of short strings: the naive, memo and DP lengths are
  all equal and equal to the length of the recovered LCS string.
- The diff of the demo files is **reconstructed in both directions**:
  keeping the unchanged and removed lines gives back the old file exactly,
  keeping the unchanged and added lines gives the new file exactly.
- The "self-check ... passed" line at the end of the output is this test.
- The `AGGTAB` / `GXTXAYB` example was also checked by brute force over
  every subsequence (LCS = `GTAB`, length 4), the number of lines kept by
  the diff (4) equals the LCS length of the two line lists and equals the
  number of matched lines found by Python's `difflib`.

## 9. Limitations

- Only the "line unchanged / removed / added" model is supported (no
  "line moved" or "line modified in place" detection).
- The full table is kept in memory, so two files of 100,000 lines each
  would need 10 billion cells; real tools use Myers or Hirschberg for that.
- If several LCSs exist, the one found depends on the tie-breaking rule
  in the walk back (`>=` prefers deleting first).

## 10. How this was made (process)

1. Read the assignment: pick a text problem, solve with and without DP,
   explain principle, complexity and comparison.
2. Chose `diff`/LCS because the DP structure is clear and the
   difference to plain recursion can be measured.
3. Wrote the three LCS versions and the diff walk with Claude AI.
4. First benchmark used random strings, but the naive call counts were
   irregular (n = 10 and n = 12 almost equal), because the count depends
   on the content. It was changed to the worst-case strings so the
   exponential growth is visible and repeatable.
5. Added the self-check (random cross-check and diff reconstruction),
   ran everything, and wrote this document from the real output.