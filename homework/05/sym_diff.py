# Problem 2: symbolic differentiation, sym_diff(expr).
#
# Expressions are written as nested tuples in prefix form, e.g.
#   x^2 + 3x   ->  ('+', ('**', 'x', 2), ('*', 3, 'x'))
# A bare number is a constant, a bare string is a variable name.
#
# sym_diff just applies the standard differentiation rules recursively --
# sum rule, product rule, power rule, chain rule for sin/cos/exp/ln.

def sym_diff(expr, var='x'):
    if isinstance(expr, (int, float)):
        return 0
    if isinstance(expr, str):
        return 1 if expr == var else 0

    op, *args = expr

    if op == '+':
        a, b = args
        return ('+', sym_diff(a, var), sym_diff(b, var))

    if op == '-':
        if len(args) == 1:
            return ('-', sym_diff(args[0], var))
        a, b = args
        return ('-', sym_diff(a, var), sym_diff(b, var))

    if op == '*':
        a, b = args
        # product rule: (a*b)' = a'b + ab'
        return ('+', ('*', sym_diff(a, var), b), ('*', a, sym_diff(b, var)))

    if op == '/':
        a, b = args
        # quotient rule: (a/b)' = (a'b - ab') / b^2
        top = ('-', ('*', sym_diff(a, var), b), ('*', a, sym_diff(b, var)))
        return ('/', top, ('**', b, 2))

    if op == '**':
        base, power = args
        # only handling constant exponents here (covers the usual cases)
        return ('*', ('*', power, ('**', base, power - 1)), sym_diff(base, var))

    if op == 'sin':
        return ('*', ('cos', args[0]), sym_diff(args[0], var))

    if op == 'cos':
        return ('*', ('*', -1, ('sin', args[0])), sym_diff(args[0], var))

    if op == 'exp':
        return ('*', ('exp', args[0]), sym_diff(args[0], var))

    if op == 'ln':
        return ('/', sym_diff(args[0], var), args[0])

    raise ValueError(f'unsupported operator: {op}')


# A derivative straight out of the rules above is full of +0, *1, *0 junk --
# this just cleans that up so the result is readable.
def simplify(expr):
    if isinstance(expr, (int, float, str)):
        return expr

    op = expr[0]
    args = [simplify(a) for a in expr[1:]]

    if op == '+':
        a, b = args
        if a == 0:
            return b
        if b == 0:
            return a
        return ('+', a, b)

    if op == '-':
        if len(args) == 1:
            return 0 if args[0] == 0 else ('-', args[0])
        a, b = args
        if b == 0:
            return a
        return ('-', a, b)

    if op == '*':
        a, b = args
        if a == 0 or b == 0:
            return 0
        if a == 1:
            return b
        if b == 1:
            return a
        return ('*', a, b)

    if op == '/':
        a, b = args
        if a == 0:
            return 0
        if b == 1:
            return a
        return ('/', a, b)

    if op == '**':
        base, power = args
        if power == 0:
            return 1
        if power == 1:
            return base
        return ('**', base, power)

    return (op, *args)


def to_string(expr):
    if isinstance(expr, (int, float, str)):
        return str(expr)

    op, *args = expr
    if op in ('sin', 'cos', 'exp', 'ln'):
        return f'{op}({to_string(args[0])})'
    if op == '**':
        return f'{to_string(args[0])}^{to_string(args[1])}'
    if op == '-' and len(args) == 1:
        return f'-{to_string(args[0])}'

    a, b = args
    return f'({to_string(a)} {op} {to_string(b)})'


# Upgrade: don't just trust the algebra -- evaluate the original expression
# and the derivative at an actual number, and check the symbolic derivative
# against a numerical one (central difference). If they disagree, something
# in sym_diff is wrong.
import math


def evaluate(expr, values):
    if isinstance(expr, (int, float)):
        return expr
    if isinstance(expr, str):
        return values[expr]

    op, *args = expr
    if op == '+':
        return evaluate(args[0], values) + evaluate(args[1], values)
    if op == '-':
        if len(args) == 1:
            return -evaluate(args[0], values)
        return evaluate(args[0], values) - evaluate(args[1], values)
    if op == '*':
        return evaluate(args[0], values) * evaluate(args[1], values)
    if op == '/':
        return evaluate(args[0], values) / evaluate(args[1], values)
    if op == '**':
        return evaluate(args[0], values) ** evaluate(args[1], values)
    if op == 'sin':
        return math.sin(evaluate(args[0], values))
    if op == 'cos':
        return math.cos(evaluate(args[0], values))
    if op == 'exp':
        return math.exp(evaluate(args[0], values))
    if op == 'ln':
        return math.log(evaluate(args[0], values))
    raise ValueError(f'unsupported operator: {op}')


def numerical_derivative(expr, var, x, h=1e-6):
    plus = evaluate(expr, {var: x + h})
    minus = evaluate(expr, {var: x - h})
    return (plus - minus) / (2 * h)


if __name__ == '__main__':
    tests = [
        ('**', 'x', 2),                                   # x^2
        ('+', ('**', 'x', 2), ('*', 3, 'x')),              # x^2 + 3x
        ('*', 'x', ('sin', 'x')),                          # x * sin(x)
        ('**', 'x', 3),                                    # x^3
        ('/', 1, 'x'),                                     # 1/x
        ('exp', ('**', 'x', 2)),                           # exp(x^2)
    ]

    check_at = 1.7  # some arbitrary point where everything above is defined

    for expr in tests:
        d = simplify(sym_diff(expr))
        symbolic_value = evaluate(d, {'x': check_at})
        numeric_value = numerical_derivative(expr, 'x', check_at)
        ok = abs(symbolic_value - numeric_value) < 1e-4

        print(f'd/dx [{to_string(expr)}]  =  {to_string(d)}')
        print(f'    at x={check_at}: symbolic={symbolic_value:.6f}  '
              f'numeric={numeric_value:.6f}  {"OK" if ok else "MISMATCH"}')