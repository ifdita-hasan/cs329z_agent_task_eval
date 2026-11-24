"""Check a circle packing against the task rules.

Usage: python /app/check_packing.py [path]     (default: /app/packing.json)
"""

import json
import math
import sys

N_CIRCLES = 32
TARGET = 2.80
KEEPOUT_X, KEEPOUT_Y, KEEPOUT_R = 0.37, 0.58, 0.15
TOL = 1e-9


def evaluate(path):
    """Return (accepted, sum_of_radii_or_None, message)."""
    try:
        with open(path) as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, None, f"{path} does not exist"
    except (OSError, ValueError) as exc:
        return False, None, f"{path} is not valid JSON: {exc}"

    if not isinstance(data, list) or len(data) != N_CIRCLES:
        return False, None, f"expected a JSON list of exactly {N_CIRCLES} circles"

    circles = []
    for i, item in enumerate(data):
        if not isinstance(item, list) or len(item) != 3:
            return False, None, f"circle {i} is not a list [x, y, r]"
        for value in item:
            is_number = isinstance(value, (int, float)) and not isinstance(value, bool)
            if not is_number or not math.isfinite(value):
                return False, None, f"circle {i} contains a value that is not a finite number"
        circles.append(tuple(float(value) for value in item))

    total = math.fsum(r for _, _, r in circles)

    for i, (x, y, r) in enumerate(circles):
        if r <= 0:
            return False, total, f"circle {i} has a non-positive radius"
        if x - r < -TOL or x + r > 1 + TOL or y - r < -TOL or y + r > 1 + TOL:
            return False, total, f"circle {i} is not inside the unit square"
        if math.hypot(x - KEEPOUT_X, y - KEEPOUT_Y) < r + KEEPOUT_R - TOL:
            return False, total, f"circle {i} overlaps the keep-out zone"

    for i in range(N_CIRCLES):
        xi, yi, ri = circles[i]
        for j in range(i + 1, N_CIRCLES):
            xj, yj, rj = circles[j]
            if math.hypot(xi - xj, yi - yj) < ri + rj - TOL:
                return False, total, f"circles {i} and {j} overlap"

    if total < TARGET:
        return False, total, f"valid packing, but the sum of radii is below the target {TARGET}"
    return True, total, "valid packing that reaches the target"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "/app/packing.json"
    accepted, total, message = evaluate(path)
    if total is not None:
        print(f"sum of radii: {total:.9f} (target {TARGET})")
    print(("ACCEPTED: " if accepted else "REJECTED: ") + message)
    return 0 if accepted else 1


if __name__ == "__main__":
    sys.exit(main())
