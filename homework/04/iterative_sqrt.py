import math

def find_sqrt(N, iterations=15, show_table=True):
    """
    Find sqrt(N) using 3 different fixed-point iteration formulas.
    Returns the final value from each formula.
    """
    true_value = math.sqrt(N)

    # Three different ways to rewrite "x^2 = N" as a fixed-point form x = g(x):

    # Formula 1: x = N / x   (direct rearrangement of x*x = N)
    g1 = lambda x: N / x

    # Formula 2: x = x - (1/(2N)) * (x^2 - N)   (a gradient-style correction step)
    g2 = lambda x: x - 1 / (2 * N) * (x * x - N)

    # Formula 3: x = 1/2 * (x + N/x)   (Newton's method / Babylonian method)
    g3 = lambda x: 1 / 2 * (x + N / x)

    x1 = x2 = x3 = 1.0   # all three start from the same initial guess

    if show_table:
        print(f"\nFinding sqrt({N}) = {true_value:.6f} using 3 iteration formulas")
        print(f"{'i':>2}  {'x1 (N/x)':>14}  {'x2 (grad step)':>16}  {'x3 (Newton)':>14}")
        print("-" * 55)

    for i in range(iterations):
        x1, x2, x3 = g1(x1), g2(x2), g3(x3)
        if show_table:
            print(f"{i:>2}  {x1:>14.6f}  {x2:>16.6f}  {x3:>14.6f}")

    if show_table:
        print(f"\n--- Final results after {iterations} iterations ---")
        print(f"True value          : {true_value:.6f}")
        print(f"Formula 1 (x1)      : {x1:.6f}   | error = {abs(x1 - true_value):.6f}")
        print(f"Formula 2 (x2)      : {x2:.6f}   | error = {abs(x2 - true_value):.6f}")
        print(f"Formula 3 (x3)      : {x3:.6f}   | error = {abs(x3 - true_value):.6f}")

    return x1, x2, x3, true_value


if __name__ == "__main__":

    try:
        user_input = input("Enter a number to find its square root (or press Enter to skip): ").strip()
    except EOFError:
        user_input = ""

    if user_input:
        N = float(user_input)
        find_sqrt(N)

    print("\n\n================ Summary across several numbers ================")
    print(f"{'N':>6}  {'sqrt(N) true':>14}  {'Formula1':>12}  {'Formula2':>12}  {'Formula3':>12}")
    print("-" * 65)

    for N in [2, 5, 10, 25, 50, 100]:
        x1, x2, x3, true_value = find_sqrt(N, iterations=15, show_table=False)
        print(f"{N:>6}  {true_value:>14.6f}  {x1:>12.6f}  {x2:>12.6f}  {x3:>12.6f}")

    print("\nNote: Formula 1 never converges (it just oscillates between two values)")
    print("Formula 2 converges but slowly.")
    print("Formula 3 (Newton's method) converges to the correct answer fastest for every N.")