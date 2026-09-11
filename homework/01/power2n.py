import time
import sys
import multiprocessing as mp

sys.setrecursionlimit(10000)


# ===== Method 1: direct exponentiation =====
def power2n_v1(n):
    return 2 ** n


# ===== Method 2a: recursion, f(n) = f(n-1) + f(n-1) =====
def power2n_v2a(n):
    if n == 0:
        return 1
    return power2n_v2a(n - 1) + power2n_v2a(n - 1)


# ===== Method 2b: recursion, f(n) = 2 * f(n-1) =====
def power2n_v2b(n):
    if n == 0:
        return 1
    return 2 * power2n_v2b(n - 1)


# ===== Method 3: recursion + lookup table (memoization) =====
_table = {0: 1}


def power2n_v3(n):
    if n in _table:
        return _table[n]
    result = 2 * power2n_v3(n - 1)
    _table[n] = result
    return result


# ===== Main program: testing =====
# Uses a separate process (instead of signal.alarm, which does not exist on
# Windows) so a runaway recursive call can be forcibly killed after a
# timeout, on any OS.
def _worker(func, n, queue):
    result = func(n)
    queue.put(result)


def run_with_timeout(func, arg, timeout_sec=5):
    queue = mp.Queue()
    proc = mp.Process(target=_worker, args=(func, arg, queue))
    start = time.perf_counter()
    proc.start()
    proc.join(timeout_sec)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        return None, None

    elapsed = time.perf_counter() - start
    if not queue.empty():
        return queue.get(), elapsed
    return None, None


if __name__ == "__main__":
    n = 100

    methods = [
        ("Method 1  (2**n)", power2n_v1),
        ("Method 2a (f(n-1)+f(n-1))", power2n_v2a),
        ("Method 2b (2*f(n-1))", power2n_v2b),
        ("Method 3  (recursion+table)", power2n_v3),
    ]

    print(f"Testing n = {n}\n")
    print(f"{'Method':<30}{'Result':<12}{'Time (sec)':<15}")
    print("-" * 57)

    for name, func in methods:
        if func is power2n_v3:
            _table.clear()
            _table[0] = 1

        result, elapsed = run_with_timeout(func, n, timeout_sec=5)

        if result is None:
            print(f"{name:<30}{'TIMEOUT':<12}{'>5 sec (never finishes)':<15}")
        else:
            digits = len(str(result))
            print(f"{name:<30}{str(digits)+' digits':<12}{elapsed:<15.8f}")

    print("\nCorrectness check (method 1 as baseline):")
    print("Method 2b matches method 1:", power2n_v2b(n) == power2n_v1(n))
    print("Method 3  matches method 1:", power2n_v3(n) == power2n_v1(n))