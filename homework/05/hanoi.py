# Problem 1: Tower of Hanoi, solved two ways -- recursive and non-recursive.
#
# Classic rule: to move n disks from `src` to `dst` using `aux` as a spare peg,
# first move the top n-1 disks out of the way, move the big disk, then move
# the n-1 disks back on top of it.


def hanoi_recursive(n, src='A', aux='B', dst='C', moves=None):
    if moves is None:
        moves = []
    if n == 0:
        return moves

    hanoi_recursive(n - 1, src, dst, aux, moves)
    moves.append((src, dst))
    hanoi_recursive(n - 1, aux, src, dst, moves)

    return moves


# Non-recursive version: same algorithm, but we keep our own explicit stack
# instead of letting Python's call stack do it for us. Each item pushed is
# either "do this move" or "solve this smaller sub-problem", mirroring
# exactly what the recursive calls above would have done -- we just manage
# the call stack by hand with a list and a while loop.
def hanoi_iterative(n, src='A', aux='B', dst='C'):
    moves = []
    stack = [('solve', n, src, aux, dst)]

    while stack:
        task = stack.pop()

        if task[0] == 'move':
            _, frm, to = task
            moves.append((frm, to))
            continue

        _, k, s, a, d = task
        if k == 0:
            continue

        # push in reverse order so they get popped in the right sequence:
        # solve(k-1, s, d, a) -> move(s, d) -> solve(k-1, a, s, d)
        stack.append(('solve', k - 1, a, s, d))
        stack.append(('move', s, d))
        stack.append(('solve', k - 1, s, d, a))

    return moves


# Upgrade: replay a move sequence and show what the three pegs look like
# after every single move, so you can actually watch the puzzle get solved
# instead of just reading a list of letters.
def print_towers(pegs, n):
    width = n * 2 + 1
    for peg in ('A', 'B', 'C'):
        disks = pegs[peg]
        row = ''.join(f'[{d}]'.center(4) for d in disks)
        print(f'  {peg}: {row}')
    print()


def replay(moves, n):
    pegs = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
    print('start:')
    print_towers(pegs, n)

    for step, (frm, to) in enumerate(moves, 1):
        disk = pegs[frm].pop()
        pegs[to].append(disk)
        print(f'move {step}: {frm} -> {to}  (disk {disk})')
        print_towers(pegs, n)


if __name__ == '__main__':
    raw = input('How many disks? (default 4): ').strip()
    n = int(raw) if raw else 4

    rec = hanoi_recursive(n)
    it = hanoi_iterative(n)

    print(f'\nSolving Hanoi with {n} disks ({2**n - 1} moves expected)')
    print('Recursive and non-recursive move sequences match:', rec == it)
    print('Move count correct (2^n - 1):', len(rec) == 2 ** n - 1)

    print(f'\nReplaying the solution step by step:\n')
    replay(rec, n)