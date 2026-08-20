#!/usr/bin/env python3
"""
Erdos-Straus conjecture explorer.

The conjecture states that for every integer n >= 2 there exist positive
integers x, y, z such that:

    4/n = 1/x + 1/y + 1/z

This program verifies the conjecture up to a given bound, and can print
one solution for each n.
"""

_factor_cache = {}


def factorize(num: int) -> dict:
    """Trial division factorization: returns {prime: exponent}."""
    factors = {}

    if num % 2 == 0:
        cnt = 0
        while num % 2 == 0:
            num //= 2
            cnt += 1
        factors[2] = cnt

    d = 3
    while d * d <= num:
        if num % d == 0:
            cnt = 0
            while num % d == 0:
                num //= d
                cnt += 1
            factors[d] = cnt
        d += 2

    if num > 1:
        factors[num] = factors.get(num, 0) + 1

    return factors


def factorize_cached(num: int) -> dict:
    """Cached version of factorize."""
    if num not in _factor_cache:
        _factor_cache[num] = factorize(num)
    return _factor_cache[num]


def iter_divisors(factors: dict, exponent_multiplier: int = 1):
    """Yield all divisors of the number described by factors.

    The exponent_multiplier is useful when we need divisors of a square.
    """
    items = [(p, e * exponent_multiplier) for p, e in factors.items()]

    def generate(index, current):
        if index == len(items):
            yield current
            return

        prime, exp = items[index]
        power = 1
        for _ in range(exp + 1):
            yield from generate(index + 1, current * power)
            power *= prime

    yield from generate(0, 1)


def is_solution(n: int, triple) -> bool:
    """Check whether 4/n = 1/x + 1/y + 1/z exactly."""
    x, y, z = triple
    return 4 * x * y * z == n * (x * y + y * z + z * x)


def solve(n: int):
    """
    Return a positive integer triple (x, y, z) satisfying

        4/n = 1/x + 1/y + 1/z

    or None if no solution is found.
    """
    if n < 2:
        return None

    # Known congruence shortcuts.
    if n % 2 == 0:
        return (n // 2, n, n)

    if n % 3 == 0:
        k = n // 3
        return (2 * k, 2 * k, n)

    if n % 3 == 2:
        k = (n - 2) // 3
        return tuple(sorted((n, k + 1, n * (k + 1))))

    # Remaining case: n ≡ 1 (mod 6). Use a divisor search.
    factors_n = factorize_cached(n)

    # In a sorted solution x <= y <= z, x must satisfy n/4 < x <= 3n/4.
    lo = n // 4 + 1
    hi = (3 * n) // 4

    for x in range(lo, hi + 1):
        A = 4 * x - n
        if A <= 0:
            continue

        # Factor B = n * x.
        factors_B = factors_n.copy()
        for p, e in factorize_cached(x).items():
            factors_B[p] = factors_B.get(p, 0) + e

        B = n * x
        B2 = B * B

        # For fixed x:
        #    1/y + 1/z = A/B
        # is equivalent to:
        #    (A*y - B)(A*z - B) = B^2
        for d in iter_divisors(factors_B, exponent_multiplier=2):
            if (d + B) % A != 0:
                continue

            e = B2 // d
            if (e + B) % A != 0:
                continue

            y = (d + B) // A
            z = (e + B) // A

            if y >= x and z >= y:
                return (x, y, z)

    return None


def verify_conjecture(limit: int, verbose: bool = False) -> bool:
    """Check the conjecture for all n from 2 through limit."""
    for n in range(2, limit + 1):
        sol = solve(n)

        if sol is None:
            print(f"Counterexample found: n={n}")
            return False

        if not is_solution(n, sol):
            print(f"Internal error for n={n}: {sol}")
            return False

        if verbose:
            x, y, z = sol
            print(f"n={n:4d}: 4/{n} = 1/{x} + 1/{y} + 1/{z}")

    print(f"Verified for all n from 2 to {limit}.")
    return True


if __name__ == "__main__":
    import sys

    limit = 100
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [limit]")
            sys.exit(1)

    verify_conjecture(limit, verbose=(limit <= 200))
