# Problem 3: build our own map / filter / reduce, then use them (and pure
# recursion -- no for/while anywhere) to implement bubble sort.

import random


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


# One bubble-sort pass, done with my_reduce instead of a loop: we fold over
# the list carrying "everything placed so far" and "the value still being
# bubbled along", swapping whenever the carried value is out of order with
# the next one. `should_swap` is injectable so the same pass can sort
# ascending or descending.
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


# Upgrade: a stress test. Instead of trusting one hand-picked example,
# throw a few hundred random lists at bubble_sort and check every single
# one against Python's built-in sorted(). Written recursively, same as
# everything else in this file -- still no for/while anywhere.
def random_list(rng, size):
    if size == 0:
        return []
    return [rng.randint(-50, 50)] + random_list(rng, size - 1)


def stress_test(trials=300, max_len=12, seed=42):
    rng = random.Random(seed)

    def run(trial, failures):
        if trial == trials:
            return failures
        sample = random_list(rng, rng.randint(0, max_len))
        got = bubble_sort(sample)
        expected = sorted(sample)
        next_failures = failures + [(sample, got, expected)] if got != expected else failures
        return run(trial + 1, next_failures)

    return trials, run(0, [])


if __name__ == '__main__':
    nums = [5, 1, 4, 2, 8, 0, 9, 3]

    print('my_map   :', my_map(lambda x: x * x, nums))
    print('my_filter:', my_filter(lambda x: x % 2 == 0, nums))
    print('my_reduce:', my_reduce(lambda a, b: a + b, nums, 0))

    print()
    print('unsorted  :', nums)
    print('ascending :', bubble_sort(nums))
    print('descending:', bubble_sort(nums, descending=True))

    print()
    trials, failures = stress_test()
    print(f'Stress test: {trials} random lists compared against sorted()')
    if failures:
        print(f'  {len(failures)} FAILED, e.g. {failures[0]}')
    else:
        print('  all passed')