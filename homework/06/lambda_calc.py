# Lambda Calculus interpreter that prints every reduction step.
#
# Main version: "named" terms (variables keep their names, so we need
# capture-avoiding substitution). As a bonus, every result is also shown
# in the "nameless" de Bruijn form.
#
# Syntax:   \x. body     (or λx. body)       \x y. body  =  \x. \y. body
#           f a b        application, left-associative
#           NAME = expr  definition (macro), expanded before reduction
#           3            a number literal = Church numeral
#           # ...        comment
#
# Strategy: normal order (always reduce the leftmost-outermost redex),
# which finds a normal form whenever one exists.

import re
import sys
from dataclasses import dataclass


# ---------------------------------------------------------------- terms
@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Abs:
    param: str
    body: object


@dataclass(frozen=True)
class App:
    fn: object
    arg: object


# --------------------------------------------------------------- parser
TOKEN = re.compile(r'\s*(?:(λ|\\)|(\.)|(\()|(\))|(\d+)|([A-Za-z_][A-Za-z0-9_\']*))')


def tokenize(text):
    tokens, pos = [], 0
    text = text.strip()
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            raise SyntaxError(f'unexpected character {text[pos]!r} in: {text}')
        kind = m.lastindex
        tokens.append(('lam', 'λ') if kind == 1 else
                      ('dot', '.') if kind == 2 else
                      ('lp', '(') if kind == 3 else
                      ('rp', ')') if kind == 4 else
                      ('num', m.group(5)) if kind == 5 else
                      ('id', m.group(6)))
        pos = m.end()
    return tokens


def church(n):
    body = Var('x')
    for _ in range(n):
        body = App(Var('f'), body)
    return Abs('f', Abs('x', body))


class Parser:
    def __init__(self, tokens):
        self.toks, self.i = tokens, 0

    def peek(self):
        return self.toks[self.i][0] if self.i < len(self.toks) else None

    def take(self, kind):
        if self.peek() != kind:
            raise SyntaxError(f'expected {kind}, got {self.peek()}')
        self.i += 1
        return self.toks[self.i - 1][1]

    def expr(self):
        if self.peek() == 'lam':
            return self.lam()
        terms = []
        while self.peek() in ('id', 'num', 'lp', 'lam'):
            if self.peek() == 'lam':        # a lambda swallows everything to its right
                terms.append(self.lam())
                break
            terms.append(self.atom())
        if not terms:
            raise SyntaxError('empty expression')
        result = terms[0]
        for t in terms[1:]:
            result = App(result, t)
        return result

    def lam(self):
        self.take('lam')
        params = []
        while self.peek() == 'id':
            params.append(self.take('id'))
        if not params:
            raise SyntaxError('lambda needs at least one parameter')
        self.take('dot')
        body = self.expr()
        for p in reversed(params):
            body = Abs(p, body)
        return body

    def atom(self):
        kind = self.peek()
        if kind == 'id':
            return Var(self.take('id'))
        if kind == 'num':
            return church(int(self.take('num')))
        self.take('lp')
        inner = self.expr()
        self.take('rp')
        return inner


def parse(text):
    p = Parser(tokenize(text))
    t = p.expr()
    if p.i != len(p.toks):
        raise SyntaxError(f'leftover tokens in: {text}')
    return t


# ------------------------------------------------------ printing (named)
def show(t, mark=None):
    """Named form. `mark` is a sub-term (by identity) to wrap in [[ ]]."""
    s = _show(t, mark)
    return s


def _show(t, mark):
    text = _show_plain(t, mark)
    return f'[[{text}]]' if t is mark else text


def _show_plain(t, mark):
    if isinstance(t, Var):
        return t.name
    if isinstance(t, Abs):
        params, body = [t.param], t.body
        while isinstance(body, Abs) and body is not mark and body.param not in params:
            params.append(body.param)
            body = body.body
        return '\\' + ' '.join(params) + '. ' + _show(body, mark)
    left = _show(t.fn, mark)
    if isinstance(t.fn, Abs) and t.fn is not mark:
        left = f'({left})'
    right = _show(t.arg, mark)
    if isinstance(t.arg, (App, Abs)) and t.arg is not mark:
        right = f'({right})'
    return f'{left} {right}'


# ------------------------------------------- printing (nameless / de Bruijn)
def nameless(t, ctx=()):
    if isinstance(t, Var):
        return str(ctx.index(t.name)) if t.name in ctx else t.name
    if isinstance(t, Abs):
        return '\\. ' + nameless(t.body, (t.param,) + ctx)
    left = nameless(t.fn, ctx)
    if isinstance(t.fn, Abs):
        left = f'({left})'
    right = nameless(t.arg, ctx)
    if isinstance(t.arg, (App, Abs)):
        right = f'({right})'
    return f'{left} {right}'


# ------------------------------------------------------- core reduction
def free_vars(t):
    if isinstance(t, Var):
        return {t.name}
    if isinstance(t, Abs):
        return free_vars(t.body) - {t.param}
    return free_vars(t.fn) | free_vars(t.arg)


def fresh(name, avoid):
    while name in avoid:
        name += "'"
    return name


def subst(t, x, s, log):
    """Replace free occurrences of x in t by s, avoiding variable capture."""
    if isinstance(t, Var):
        return s if t.name == x else t
    if isinstance(t, App):
        return App(subst(t.fn, x, s, log), subst(t.arg, x, s, log))
    if t.param == x:                       # x is shadowed, nothing to do
        return t
    if t.param in free_vars(s):            # would capture -> rename first (alpha)
        new = fresh(t.param, free_vars(s) | free_vars(t.body) | {x})
        log.append(f'alpha: renamed {t.param} to {new} to avoid capture')
        renamed = subst(t.body, t.param, Var(new), log)
        return Abs(new, subst(renamed, x, s, log))
    return Abs(t.param, subst(t.body, x, s, log))


def step(t, log):
    """One normal-order beta step. Returns (new_term, redex) or None."""
    if isinstance(t, App):
        if isinstance(t.fn, Abs):
            return subst(t.fn.body, t.fn.param, t.arg, log), t
        r = step(t.fn, log)
        if r:
            return App(r[0], t.arg), r[1]
        r = step(t.arg, log)
        if r:
            return App(t.fn, r[0]), r[1]
    elif isinstance(t, Abs):
        r = step(t.body, log)
        if r:
            return Abs(t.param, r[0]), r[1]
    return None


def expand(t, defs, bound=frozenset()):
    """Replace defined names (that are not shadowed) by their definitions."""
    if isinstance(t, Var):
        return defs[t.name] if t.name in defs and t.name not in bound else t
    if isinstance(t, Abs):
        return Abs(t.param, expand(t.body, defs, bound | {t.param}))
    return App(expand(t.fn, defs, bound), expand(t.arg, defs, bound))


# ------------------------------------------------- recognising results
def decode(t):
    """If t looks like a Church numeral or boolean, say so."""
    if isinstance(t, Abs) and isinstance(t.body, Abs):
        a, b, body = t.param, t.body.param, t.body.body
        if a != b:
            if body == Var(a):
                return 'TRUE'
            if body == Var(b):
                return 'FALSE (the same term is also Church numeral 0)'
            n = 0
            while isinstance(body, App) and body.fn == Var(a):
                n, body = n + 1, body.arg
            if body == Var(b):
                return f'Church numeral {n}'
    return None


# --------------------------------------------------------- run a program
def evaluate(term, max_steps=200, show_nameless=True):
    print(f'  start : {show(term)}')
    seen = {term}
    for n in range(1, max_steps + 1):
        log = []
        r = step(term, log)
        if r is None:
            print(f'  normal form reached after {n - 1} beta step(s)')
            print(f'  result: {show(term)}')
            if show_nameless:
                print(f'  nameless (de Bruijn): {nameless(term)}')
            meaning = decode(term)
            if meaning:
                print(f'  meaning: {meaning}')
            return term
        new, redex = r
        print(f'  {n:>3}. {show(term, redex)}')
        for note in log:
            print(f'        ({note})')
        print(f'       => {show(new)}')
        if new in seen:
            print('  this term has appeared before, so reduction loops forever (no normal form)')
            return new
        seen.add(new)
        term = new
    print(f'  stopped: no normal form within {max_steps} steps (probably diverges)')
    return term


def run_program(text, max_steps=200, defs=None):
    defs = {} if defs is None else defs
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.split('#')[0].strip()
        if not line:
            if raw.strip().startswith('#'):
                print(f'\n{raw.strip()}')
            continue
        try:
            if '=' in line:
                name, rhs = (s.strip() for s in line.split('=', 1))
                defs[name] = expand(parse(rhs), defs)
                print(f'\ndefine {name} = {show(defs[name])}')
            else:
                print(f'\n> {line}')
                evaluate(expand(parse(line), defs), max_steps)
        except SyntaxError as e:
            print(f'  line {lineno}: syntax error: {e}')


def repl():
    print('Lambda Calculus REPL. Type a term, or NAME = term to define. Ctrl+C / empty line to quit.')
    defs = {}
    while True:
        try:
            line = input('lc> ').strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break
        run_program(line, defs=defs)


# Built-in sample programs, so the script works even without examples.lc.
DEFAULT_PROGRAM = r"""
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
"""


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg in ('-i', '--interactive'):
        repl()
    elif arg is None:
        run_program(DEFAULT_PROGRAM)
    else:
        try:
            with open(arg, encoding='utf-8') as f:
                run_program(f.read())
        except FileNotFoundError:
            print(f'file not found: {arg}')