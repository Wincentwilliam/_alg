import itertools


def evaluate_formula(formula_func, variables, bits):
    """
    bits : tuple of 0/1, e.g. (0, 1, 1) for A=0, B=1, C=1
    Convert 0/1 -> True/False just for evaluating the formula,
    but we display everything to the user as 0/1.
    """
    values = dict(zip(variables, [bool(b) for b in bits]))
    return formula_func(values)


def brute_force_sat(formula_func, variables, formula_name="Formula"):
    """
    Solve SAT by enumerating the whole truth table using 0/1.

    For n variables there are 2^n rows. We try every single row
    (brute force) and check if the formula gives 1 (true).
    """
    n = len(variables)
    total_rows = 2 ** n
    satisfying_rows = []

    header = "  ".join(f"{v:>2}" for v in variables) + "  |  Result"
    print(f"\n=== {formula_name} ===")
    print(header)
    print("-" * len(header))

    for bits in itertools.product([0, 1], repeat=n):
        result = 1 if evaluate_formula(formula_func, variables, bits) else 0
        row = "  ".join(f"{b:>2}" for b in bits) + f"  |  {result}"
        print(row)
        if result == 1:
            satisfying_rows.append(bits)

    print(f"\nTotal rows checked : {total_rows}")
    print(f"Rows where result=1 : {len(satisfying_rows)}")
    if satisfying_rows:
        print("Verdict: SAT. Example:", dict(zip(variables, satisfying_rows[0])))
    else:
        print("Verdict: UNSAT.")

    return satisfying_rows


if __name__ == "__main__":
    print("Note: 0 = False, 1 = True")

    # Example 1: SAT
    vars1 = ["A", "B", "C"]
    f1 = lambda v: (v["A"] or v["B"]) and (not v["A"] or v["C"])
    brute_force_sat(f1, vars1, "(A or B) and (not A or C)")

    # Example 2: UNSAT
    vars2 = ["A"]
    f2 = lambda v: v["A"] and not v["A"]
    brute_force_sat(f2, vars2, "A and (not A)")