# Homework 8: The Traveling Salesman Problem with Five Optimization Methods

> This README is the write-up and process document for the assignment. The program and this document were produced with the help of Claude AI, then run, checked and measured as described in the text.

Name: 洪偉升
Department: 資訊工程學系
Student ID: 111310523
Class: Introduction to Algorithms

## 1. The assignment

Week 8 (optimization algorithms): solve the **Traveling Salesman Problem**
(TSP) with each of these five methods:

1. improvement method (改良法)
2. hill climbing (爬山演算法)
3. simulated annealing (模擬退火法)
4. gradient descent (梯度下降法)
5. greedy algorithm (貪婪演算法)

Files:

| File | Purpose |
|---|---|
| `tsp.py` | the five methods, an exact reference solver, and the experiments |
| `output.txt` | the full output of `python tsp.py` |
| `tsp_tours.png` | picture of the tours found for the 12-city instance (needs matplotlib; see section 8) |

Run it with `python tsp.py` (pure Python, no packages needed; the picture is
only drawn if matplotlib happens to be installed).

## 2. The problem

There are `n` cities. A salesman must visit **every city exactly once** and
return to the start. Find the **shortest such round trip**.

- A *tour* is an ordering of the cities, e.g. `[0, 8, 7, 3, ...]`; the last
  city connects back to the first.
- Its *length* is the sum of the distances between consecutive cities.
- Cities here are random points in the unit square, distance is the straight
  line (Euclidean) distance.
- There are `(n-1)!/2` different tours, so trying them all is hopeless for
  large `n` (for 20 cities it is about 6 * 10^16). That is why heuristics are
  used: they give a *good* tour quickly, but with no guarantee of the best.

All five methods are optimization methods in the same sense: they search for
the tour with the smallest length.

## 3. The common building block: the 2-opt move

Three of the methods (improvement, hill climbing, annealing) change a tour with
the same small move, **2-opt**: pick two positions `i < k` and **reverse the
part of the tour between them**.

```
before:  ... a [b ... c] d ...        after:  ... a [c ... b] d ...
```

Only two edges change: `a-b` and `c-d` are replaced by `a-c` and `b-d`. So the
change in length can be computed in constant time without recomputing the
whole tour:

```
delta = D[a][c] + D[b][d] - D[a][b] - D[c][d]      (delta < 0 means shorter)
```

This is `two_opt_delta` in the code. Reversing a section also never creates an
invalid tour, so every neighbour of a tour is again a valid tour.

## 4. The five methods

### 4.1 Greedy (`greedy`)
**Principle:** start at city 0; always walk to the **nearest city not visited
yet**; at the end return to the start.

**Cost:** `O(n^2)` (n steps, each scanning up to n cities).

**Properties:** extremely fast and deterministic, but short-sighted. Early
choices look good, yet the last cities that are left over can force very long
edges. It never looks back and never fixes a mistake.

### 4.2 Improvement method (`improve`)
**Principle:** take any existing tour and **improve it systematically**. Here:
look at *every* possible 2-opt move, apply the one that shortens the tour the
most, and repeat. Stop when no move shortens the tour any more.

**Cost:** one round scans all pairs `(i, k)`, so `O(n^2)` per round. The number
of rounds has no neat formula, but the method always terminates, because every
round makes the tour strictly shorter and there are only finitely many tours.

**Properties:** deterministic for a given starting tour. It ends in a *local
optimum*: a tour that no single 2-opt move can improve. That is often good but
is not necessarily the global best.

*Interpretation note:* the assignment does not define "改良法" in detail. I
read it as this iterative-improvement (local search) idea. It could also be
started from the greedy tour instead of a random one (a sensible variant that is
not tested here); the program uses the same random start for methods 1, 2
and 3 to keep the comparison fair.

### 4.3 Hill climbing (`hill_climb`)
**Principle:** pick **one random** 2-opt move; if it makes the tour shorter,
keep it, otherwise throw it away. Repeat a fixed number of times (20,000).

**Cost:** `O(1)` to evaluate a move, `O(n)` to apply an accepted one.

**Difference to the improvement method:** the improvement method inspects *all*
neighbours and picks the best; hill climbing tries *one random* neighbour at a
time. Hill climbing is cheaper per step but wanders more, and may stop before
it reaches the local optimum if the step budget is small.

**Weakness:** it only ever goes *downhill* in length, so it gets **stuck in
local optima** and cannot escape them.

### 4.4 Simulated annealing (`anneal`)
**Principle:** exactly the same random 2-opt moves as hill climbing, with one
change: a move that makes the tour **longer by `delta`** is still accepted with
probability

```
exp(-delta / T)
```

`T` is the "temperature". It starts high (almost anything is accepted, so the
search roams widely) and is multiplied by a constant slightly below 1 at every
step until it is almost zero (then it behaves like hill climbing). Accepting
occasional worse tours is what lets it climb *out of* local optima. The best
tour ever seen is remembered and returned.

**Cost:** `O(1)` per evaluated move, `steps` moves in total (20,000 by
default, `T` going from 0.5 to 0.001).

**Properties:** random, so different seeds give different results; quality
depends on the cooling schedule and the number of steps (see section 7).

### 4.5 Gradient descent (`gradient_descent`)
**Problem:** gradient descent needs a *continuous* function to differentiate,
but a tour is an ordering, which is discrete. The classic way out is the
**elastic net** (Durbin and Willshaw, 1987).

**Principle:** place a closed **ring of `m = 3n` points** `y_j` (a rubber band)
near the middle of the cities. Define an energy that is small when the ring
passes close to every city and is short and smooth:

```
E = -alpha*K * sum_i ln( sum_j exp(-|x_i - y_j|^2 / (2 K^2)) )   +   beta/2 * sum_j |y_(j+1) - y_j|^2
      (cities pull the ring towards themselves)                      (the ring resists stretching)
```

`x_i` are the cities. The ring points are moved downhill on `E`: each step
adds `K * (-dE/dy_j)` to `y_j`, which is the update implemented in the code,

```
y_j  +=  alpha * sum_i w_ij * (x_i - y_j)  +  beta * K * (y_(j+1) - 2 y_j + y_(j-1))
```

where `w_ij` says how strongly city `i` pulls ring point `j` (a softmax of the
distances). So this is gradient descent with learning rate `K`. `K` is the
"width" of each city's attraction: it starts at 0.2 and shrinks by 3% every 10
steps down to 0.01 (about 990 steps). At first the pull is wide and the ring
only finds the rough shape; as `K` shrinks each city captures its own part of
the ring. **Finally each city is read off at its nearest ring point, and the
cities are sorted by the position of that ring point to get the tour.**

**Cost:** each step compares `n` cities with `m = 3n` ring points, so `O(n^2)`
per step and `O(n^2)` times about 990 steps in total. It is by far the
slowest of the five here (section 6).

**Properties:** it is a genuine gradient method, but only an *indirect* way
of solving TSP, with several hand-chosen parameters (`alpha`, `beta`, the `K`
schedule). Nothing guarantees the final reading is a good tour, though in the
experiments it was.

### 4.6 Reference answer: Held-Karp dynamic programming (`held_karp`)
Not one of the five required methods. To judge how good the heuristics are, the
program also computes the **exact optimum** with the Held-Karp dynamic
programming algorithm (the same idea as last week: remember the best path for
every subset of cities visited so far). It takes `O(n^2 * 2^n)` time and
`O(n * 2^n)` memory, so it works for about 12 to 15 cities and no further.
That is why section A and B use 12 cities, and section C (40 cities) can only
compare the methods with each other.

## 5. Validity checks

Every tour returned by every method is checked to be a permutation of all the
cities (each city exactly once) before it is reported; the program would stop
with an error otherwise. For the 12-city instances the exact answer from
Held-Karp is used as the yardstick, and the program asserts that no heuristic
returns a tour shorter than it (that would mean a bug); the assertion held
for every run.

## 6. Actual output

```
== A. one instance, 12 cities (exact optimum known) ==
method               length      gap to optimal   seconds
---------------------------------------------------------
greedy               3.6824                1.5%     0.000
improvement          3.6267                0.0%     0.000
hill climbing        3.6267                0.0%     0.053
annealing            3.6267                0.0%     0.037
gradient descent     3.6267                0.0%     0.193
optimal (DP)         3.6267                0.0%     0.020
  greedy            [0, 8, 7, 3, 2, 1, 5, 11, 9, 6, 4, 10]
  improvement       [7, 8, 0, 10, 4, 6, 9, 1, 11, 5, 2, 3]
  hill climbing     [7, 3, 2, 5, 11, 1, 9, 6, 4, 10, 0, 8]
  annealing         [7, 3, 2, 5, 11, 1, 9, 6, 4, 10, 0, 8]
  gradient descent  [5, 2, 3, 7, 8, 0, 10, 4, 6, 9, 1, 11]
  optimal (DP)      [0, 8, 7, 3, 2, 5, 11, 1, 9, 6, 4, 10]
picture saved to tsp_tours.png

== B. average over 10 random instances, 12 cities each ==
method              avg gap  worst gap  optimal found  avg seconds
------------------------------------------------------------------
greedy                14.6%      34.9%        0/10           0.000
improvement            0.0%       0.4%        9/10           0.000
hill climbing          1.0%       3.4%        6/10           0.040
annealing              0.0%       0.0%       10/10           0.048
gradient descent       0.0%       0.4%        9/10           0.189

== C. one bigger instance, 40 cities (no exact answer) ==
method               length   gap to best found   seconds
---------------------------------------------------------
greedy               6.4166               16.6%     0.000
improvement          5.5412                0.7%     0.005
hill climbing        5.9439                8.0%     0.041
annealing            5.5816                1.4%     0.058
gradient descent     5.6296                2.3%     2.121
annealing 100k       5.5051                0.0%     0.338

== D. annealing: effect of the number of steps (same 40 cities, 5 runs each) ==
   steps  shortest     mean  longest  seconds each
--------------------------------------------------
   20000    5.4741   5.6429   5.9463         0.050
  100000    5.4423   5.4701   5.4993         0.237
  400000    5.4423   5.4537   5.4993         1.125
(improvement / 2-opt from the same start: 5.5412)
```

The `seconds` columns depend on the computer and change slightly on every run;
the lengths do not, because all random generators use fixed seeds.

### Reading the results

**A. One 12-city instance.** Greedy is 1.5% above the optimum; the other four
methods found a tour of exactly the optimal length 3.6267. The tours are the
same cycle written from different starting cities (and sometimes in the
opposite direction), which is why the lists look different. The picture
`tsp_tours.png` shows it: greedy takes a different path around the cluster on
the right, the others coincide with the optimal tour.

**B. Average over 10 random instances.**
- **Greedy** is clearly the worst: 14.6% above optimal on average, up to 34.9%,
  and never optimal. It is also the fastest.
- **Improvement** reached the optimum on 9 of 10 instances and was 0.4% off on
  the other (average gap under 0.1%, which prints as 0.0%).
- **Hill climbing** is noticeably weaker: optimal on 6 of 10, up to 3.4% off.
  This is the local-optimum trap, since it can never accept a worse tour.
- **Simulated annealing** found the optimum on **all 10** instances. The only
  difference to hill climbing is that it sometimes accepts a worse tour.
- **Gradient descent (elastic net)** was optimal on 9 of 10, 0.4% off on the
  other, but about 4 times slower than annealing even for 12 cities.

**C. One 40-city instance.** There is no exact answer here, so the table
compares each method with the best tour found. Greedy is 16.6% worse, hill
climbing 8.0% worse, gradient descent 2.3%, and the 20,000-step annealing 1.4%
(improvement 0.7%). Gradient descent needs about 2 seconds, much more than all
the others, as predicted by its `O(n^2)` cost per step. The last row shows
annealing given 100,000 steps: it found the best tour of all (5.5051).

**D. Why annealing lost to improvement in C.** With 20,000 steps on 40 cities
annealing is under-budgeted: over 5 runs its tours ranged from 5.47 to 5.95
(mean 5.64), so a single run can land anywhere. With 100,000 steps the mean is
5.47 with a narrow spread, better than 2-opt's 5.54, and with 400,000 steps it
is 5.45. So the weakness in C was the step budget, not the method; more steps
(slower cooling) mean better and more reliable tours, at more time.

## 7. Comparison of the five methods

| | Greedy | Improvement (2-opt) | Hill climbing | Simulated annealing | Gradient descent (elastic net) |
|---|---|---|---|---|---|
| Idea | nearest unvisited city | apply the best 2-opt move until none helps | try a random 2-opt move, keep if shorter | random 2-opt move, accept worse ones with prob. `exp(-delta/T)` | move a rubber ring downhill on an energy |
| Cost | `O(n^2)` | `O(n^2)` per round | `O(1)` per move | `O(1)` per move | `O(n^2)` per step, ~990 steps |
| Random? | no | no (given a start) | yes | yes | almost no (tiny noise at the start) |
| Can escape local optima? | no (no search) | no | no | **yes** | partly (large `K` at the start) |
| Result quality here | worst | very good | middle | best (with enough steps) | very good |
| Speed here | fastest | very fast | fast | fast | slowest |
| Needs tuning | nothing | nothing | step count | `T` range, cooling, steps | `alpha`, `beta`, `K` schedule |

**Summary:** the more a method is willing to *look around* (improvement,
annealing) the better the tour; greedy is fast but its tours are 15% or more
above the optimum. The extra trick of annealing, occasionally accepting a worse
tour, is exactly what separates it from hill climbing, and in the 12-city
averages that trick takes the result from "optimal 6/10 times" to "optimal
10/10 times". Gradient descent shows that TSP can also be attacked with a
continuous method, but it is the slowest and the least natural fit.

## 8. Notes and limitations

- Only random instances with fixed seeds were tested (10 small ones plus one
  with 40 cities), so the percentages are indicative, not general laws.
- Heuristic results depend on parameters (steps, `T` schedule, `alpha`, `beta`,
  `K`). They were set once to reasonable values and only lightly tried; the one
  deliberate experiment is section D.
- "Improvement" and "gradient descent" are my interpretation of the assignment
  (see sections 4.2 and 4.5).
- Times come from one machine and differ on others.
- `tsp_tours.png` is written only when matplotlib can be imported. Without it
  the program prints a note and continues, so the rest of the output is
  unaffected.

## 9. How this was made (process)

1. Read the assignment: five optimization methods, one problem (TSP).
2. Decided on shared building blocks (distance matrix, tour length, the 2-opt
   move with an `O(1)` length change) so that methods 1, 2 and 3 use the same
   neighbourhood and differ only in *how they decide*.
3. Wrote the five methods with Claude AI. Gradient descent needed a
   continuous version of TSP, so the elastic net was used, including a
   numerical-stability fix (subtracting the smallest distance before `exp`).
4. Added the exact Held-Karp solver to have a true yardstick, and a validity
   check on every tour.
5. First results showed annealing losing to 2-opt on 40 cities. Instead of
   assuming a reason, the number of steps was varied over several seeds; the
   result is section D, and a longer annealing row was added to section C.
6. Ran everything, saved `output.txt`, checked the picture, and wrote this
   document from the real output.