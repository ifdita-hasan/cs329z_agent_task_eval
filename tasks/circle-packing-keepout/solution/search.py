"""Search that produced the oracle packing in solve.sh (kept for reference; solve.sh does not run it).

Method: iterated local search.
  1. Local optimizer: SLSQP maximizes the sum of radii subject to the containment,
     non-overlap and keep-out constraints, starting from a given layout.
  2. Start from the best of 30 random layouts.
  3. Repeatedly perturb the current packing (jitter all circles, or move a few circles to
     random places), re-run the local optimizer, and keep the result if it is better or
     only slightly worse.

Usage: python search.py [seconds] [seed] [output.json]
"""

import json
import sys
import time

import numpy as np
from scipy.optimize import minimize

N = 32
KEEPOUT_X, KEEPOUT_Y, KEEPOUT_R = 0.37, 0.58, 0.15
PAIRS = np.triu_indices(N, 1)


def local_opt(z0):
    """Maximize the sum of radii from the starting point z0 = [x..., y..., r...]."""
    i, j = PAIRS

    def constraints(z):
        x, y, r = z[:N], z[N:2 * N], z[2 * N:]
        dist = np.hypot(x[i] - x[j], y[i] - y[j])
        keepout = np.hypot(x - KEEPOUT_X, y - KEEPOUT_Y) - r - KEEPOUT_R
        return np.concatenate([dist - r[i] - r[j], keepout, x - r, 1 - x - r, y - r, 1 - y - r])

    result = minimize(
        lambda z: -z[2 * N:].sum(), z0, method="SLSQP",
        bounds=[(0, 1)] * (2 * N) + [(0, 0.5)] * N,
        constraints=[{"type": "ineq", "fun": constraints}],
        options={"maxiter": 400, "ftol": 1e-12},
    )
    z = result.x.copy()
    z[2 * N:] -= 1e-10  # shrink slightly so the packing is strictly valid
    return z


def score(z):
    """Sum of radii if the packing is valid, otherwise -1."""
    x, y, r = z[:N], z[N:2 * N], z[2 * N:]
    i, j = PAIRS
    inside = (r > 0).all() and (x - r >= 0).all() and (x + r <= 1).all() and (y - r >= 0).all() and (y + r <= 1).all()
    apart = (np.hypot(x[i] - x[j], y[i] - y[j]) >= r[i] + r[j]).all()
    clear = (np.hypot(x - KEEPOUT_X, y - KEEPOUT_Y) >= r + KEEPOUT_R).all()
    return float(r.sum()) if inside and apart and clear else -1.0


def perturb(z, rng):
    z = z.copy()
    if rng.integers(3) == 0:              # jitter every circle and shrink the radii
        z[:2 * N] += rng.normal(0, 0.03, 2 * N)
        z[2 * N:] *= 0.85
    else:                                 # move 1 to 3 circles to random places
        k = rng.integers(1, 4)
        idx = np.argsort(z[2 * N:])[:k] if rng.integers(2) == 0 else rng.choice(N, k, replace=False)
        z[idx] = rng.uniform(0.05, 0.95, k)
        z[N + idx] = rng.uniform(0.05, 0.95, k)
        z[2 * N + idx] = 0.01
        z[2 * N:] *= 0.95
    z[:2 * N] = np.clip(z[:2 * N], 0.01, 0.99)
    return z


def random_start(rng):
    return np.concatenate([rng.uniform(0.05, 0.95, 2 * N), rng.uniform(0.02, 0.12, N)])


def main():
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 120.0
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    out = sys.argv[3] if len(sys.argv) > 3 else "packing.json"
    rng = np.random.default_rng(seed)
    start = time.time()

    best, best_score = None, -1.0
    for _ in range(30):
        z = local_opt(random_start(rng))
        if score(z) > best_score:
            best, best_score = z, score(z)

    current, current_score = best, best_score
    while time.time() - start < seconds:
        z = local_opt(perturb(current, rng))
        s = score(z)
        if s > current_score - 0.002 * rng.random():
            current, current_score = z, s
        if s > best_score:
            best, best_score = z, s
            print(f"{time.time() - start:6.1f}s  sum of radii = {best_score:.6f}", flush=True)

    circles = [[float(best[k]), float(best[N + k]), float(best[2 * N + k])] for k in range(N)]
    with open(out, "w") as f:
        json.dump(circles, f, indent=1)
    print(f"saved {out} with sum of radii {best_score:.6f}")


if __name__ == "__main__":
    main()
