# Homework 6 (Week 6): A Lambda Calculus Interpreter That Shows Every Step

> This README is the process document for the assignment. The interpreter and this write-up were produced with the help of Claude AI (the assignment allows AI use as long as the process is shared), and then tested as described in section 7.

Name: 洪偉升
Department: 資訊工程學系
Student ID: 111310523
Class: Introduction to Algorithms

## 1. The assignment

Write an interpreter for the Lambda Calculus that:

1. **shows the complete computation process** (every reduction step, not
   just the final answer),
2. comes with **some Lambda Calculus programs as input**,
3. can be either a **named** or a **nameless** version.

Files:

| File | Purpose |
|---|---|
| `lambda_calc.py` | the interpreter |
| `examples.lc` | sample Lambda Calculus programs used as input |
| `output.txt` | the full output of running the interpreter on `examples.lc` |

## 2. Background: what is the Lambda Calculus?

A tiny language with only three kinds of terms:

| Term | Written | Meaning |
|---|---|---|
| Variable | `x` | a name |
| Abstraction | `\x. body` | an anonymous function with parameter `x` |
| Application | `f a` | call `f` with argument `a` (left-associative: `f a b` = `(f a) b`) |

There is one computation rule, **beta reduction**:

```
(\x. body) arg   ->   body  with every free x replaced by arg
```

Everything else (numbers, booleans, arithmetic, loops) is built out of
functions. For example the Church numeral `n` is "apply `f` n times":

```
0 = \f x. x          1 = \f x. f x          2 = \f x. f (f x)
TRUE = \t f. t       FALSE = \t f. f
```

## 3. Named vs. nameless

The assignment allows a "named" or a "nameless" version. I read this as
the two standard ways to represent variables:

- **Named**: variables keep their names (`\x. \y. x`). Easy to read, but
  substitution must avoid *variable capture* (renaming, called alpha
  conversion).
- **Nameless (de Bruijn indices)**: each variable is replaced by a number
  saying how many lambdas away its binder is (`\. \. 1`). No names, so no
  capture problem.

This interpreter does the computation in the **named** representation,
and additionally prints every final result in the **nameless** form, so
both are visible. (If the teacher meant something different by
"named/nameless", the core interpreter is still a complete, working
Lambda Calculus evaluator.)

Example: `\x. \y. x y` in nameless form is `\. \. 1 0`.

## 4. How the interpreter works

### Parsing
`tokenize` + a small recursive-descent `Parser` turn text into a tree of
three node types (`Var`, `Abs`, `App`). Supported syntax:

```
\x. body        or   λx. body       a function
\x y. body                          shorthand for \x. \y. body
f a b                               application, left-associative
NAME = expr                         a definition (macro)
3                                   a number literal, becomes a Church numeral
# comment
```

### Definitions (macros)
`NAME = expr` lines are stored, and every later use of `NAME` is replaced
by its definition before reduction starts. This is what lets programs
read like `PLUS 2 3` instead of a wall of lambdas. Names that are bound by
a lambda are never replaced (a parameter called `PLUS` shadows the macro).

### Substitution without capture
`subst(t, x, s)` replaces free occurrences of `x` in `t` by `s`. If going
under a lambda `\y.` would capture a free `y` of `s`, the binder is first
renamed (`y` becomes `y'`) and the interpreter prints a note such as
`alpha: renamed y to y' to avoid capture`.

### Evaluation strategy: normal order
`step` finds the **leftmost-outermost** redex and reduces it. Normal
order is guaranteed to find a normal form whenever one exists, which is
why `(\x y. x) a (omega)` style terms terminate.

### Showing the process
For each step the interpreter prints the whole term with the redex that is
about to be reduced wrapped in `[[ ]]`, then the term after the step:

```
    2. [[(\y. a) b]]
       => a
```

At the end it prints the number of beta steps, the result in named form,
the result in nameless form, and, if the result is a Church numeral or a
boolean, what it means.

### Non-terminating programs
Some terms never reach a normal form, e.g. omega = `(\x. x x) (\x. x x)`.
The interpreter remembers every term it has seen; if a term repeats, it
stops and says so (there is also a step limit as a safety net).

## 5. Running it

```
python lambda_calc.py               # runs the built-in sample programs (same as examples.lc)
python lambda_calc.py my_file.lc    # runs your own program file
python lambda_calc.py -i            # interactive: type terms and definitions
```

## 6. Sample programs and actual output

`examples.lc`:

```
# ---- basic terms (no definitions needed) ----
(\x. x) y
(\x y. x) a b
(\x. x x) (\x. x x)
(\x. \y. x y) y
# ---- definitions (named macros) ----
TRUE  = \t f. t
FALSE = \t f. f
NOT   = \b. b FALSE TRUE
AND   = \p q. p q p
SUCC  = \n f x. f (n f x)
PLUS  = \m n f x. m f (n f x)
MULT  = \m n f. m (n f)
NOT TRUE
AND TRUE FALSE
SUCC 2
PLUS 2 3
MULT 2 3
```

### The constant function

```
> (\x y. x) a b
  start : (\x y. x) a b
    1. [[(\x y. x) a]] b
       => (\y. a) b
    2. [[(\y. a) b]]
       => a
  normal form reached after 2 beta step(s)
  result: a
```

### Omega: a program that never finishes

```
> (\x. x x) (\x. x x)
  start : (\x. x x) (\x. x x)
    1. [[(\x. x x) (\x. x x)]]
       => (\x. x x) (\x. x x)
  this term has appeared before, so reduction loops forever (no normal form)
```

### Variable capture handled by renaming

```
> (\x. \y. x y) y
  start : (\x y. x y) y
    1. [[(\x y. x y) y]]
        (alpha: renamed y to y' to avoid capture)
       => \y'. y y'
  normal form reached after 1 beta step(s)
  result: \y'. y y'
  nameless (de Bruijn): \. y 0
```

Without the renaming, the free `y` would be captured and the result would
wrongly be `\y. y y`. In the nameless form the difference is visible
immediately: the free `y` stays a name while the bound variable is `0`.

### Booleans: `NOT TRUE`

```
> NOT TRUE
  start : (\b. b (\t f. f) (\t f. t)) (\t f. t)
    1. [[(\b. b (\t f. f) (\t f. t)) (\t f. t)]]
       => (\t f. t) (\t f. f) (\t f. t)
    2. [[(\t f. t) (\t f. f)]] (\t f. t)
       => (\f t. \f. f) (\t f. t)
    3. [[(\f t. \f. f) (\t f. t)]]
       => \t f. f
  normal form reached after 3 beta step(s)
  result: \t f. f
  nameless (de Bruijn): \. \. 0
  meaning: FALSE
```

### Arithmetic: `PLUS 2 3`

```
> PLUS 2 3
  start : (\m n f x. m f (n f x)) (\f x. f (f x)) (\f x. f (f (f x)))
    1. [[(\m n f x. m f (n f x)) (\f x. f (f x))]] (\f x. f (f (f x)))
       => (\n f x. (\f x. f (f x)) f (n f x)) (\f x. f (f (f x)))
    2. [[(\n f x. (\f x. f (f x)) f (n f x)) (\f x. f (f (f x)))]]
       => \f x. (\f x. f (f x)) f ((\f x. f (f (f x))) f x)
    3. \f x. [[(\f x. f (f x)) f]] ((\f x. f (f (f x))) f x)
       => \f x. (\x. f (f x)) ((\f x. f (f (f x))) f x)
    4. \f x. [[(\x. f (f x)) ((\f x. f (f (f x))) f x)]]
       => \f x. f (f ((\f x. f (f (f x))) f x))
    5. \f x. f (f ([[(\f x. f (f (f x))) f]] x))
       => \f x. f (f ((\x. f (f (f x))) x))
    6. \f x. f (f [[(\x. f (f (f x))) x]])
       => \f x. f (f (f (f (f x))))
  normal form reached after 6 beta step(s)
  result: \f x. f (f (f (f (f x))))
  nameless (de Bruijn): \. \. 1 (1 (1 (1 (1 0))))
  meaning: Church numeral 5
```

Note that reductions can happen *inside* a lambda body (steps 3 to 6);
that is what "normal form" means: no redex is left anywhere.

The other programs give `SUCC 2` = 3 in 3 steps, `AND TRUE FALSE` =
FALSE in 4 steps and `MULT 2 3` = 6 in 7 steps (see `output.txt`).

## 7. How it was tested

- Every example above was run and the results checked by hand
  (`NOT TRUE` = FALSE, `SUCC 2` = 3, `PLUS 2 3` = 5, `MULT 2 3` = 6).
- An automatic cross-check ran `PLUS a b` and `MULT a b` for every
  `a, b` from 0 to 4 (50 cases) and compared the decoded Church numeral
  with Python's own `a + b` and `a * b`: 0 mismatches.
- The variable-capture case and the non-terminating case were checked
  separately, as shown above.

## 8. Limitations

- Only normal-order reduction is implemented (no call-by-value), and no
  eta reduction.
- Church numerals and booleans are recognised for the "meaning" line;
  other results are just printed as terms.
- Very long reductions are cut off by a step limit (200 by default).

## 9. How this was made (process)

1. Read the assignment and the reference topics (Lambda Calculus,
   functional programming, a Python implementation).
2. Decided the design: named terms with capture-avoiding substitution
   as the core, nameless (de Bruijn) output as a bonus.
3. Wrote the parser, the substitution/reduction engine and the step
   printer with Claude AI.
4. First run printed 200 identical lines for omega, so loop detection was
   added; the first version of `decode` reported the numeral 0 as FALSE,
   which are the same term, so the message was changed to mention both.
5. Added an interactive mode and ran the 50-case arithmetic cross-check.
6. Wrote this document.