# Circle Packing Around a Keep-Out Zone

Find a packing of exactly 32 circles inside the unit square, avoiding a circular
keep-out zone, whose radii sum to at least **2.80**. Save it to `/app/packing.json`.

## Requirements

Write `/app/packing.json` as a JSON list of exactly 32 circles. Each circle is a
list of three numbers `[x, y, r]`: the center `(x, y)` and the radius `r`.

```json
[[0.1, 0.1, 0.1], [0.3, 0.1, 0.1], ...]
```

The keep-out zone is the disk centered at `(0.37, 0.58)` with radius `0.15`.

The packing is accepted if all of the following hold:

1. There are exactly 32 circles, and every `x`, `y`, and `r` is a finite number.
2. Every radius is positive: `r > 0`.
3. Every circle lies inside the unit square `[0, 1] x [0, 1]`:
   `x - r >= 0`, `x + r <= 1`, `y - r >= 0`, and `y + r <= 1`.
4. No circle overlaps the keep-out zone: the distance from its center to
   `(0.37, 0.58)` is at least `r + 0.15`. Circles may touch the zone.
5. No two circles overlap: for every pair, the distance between the centers is at
   least the sum of the two radii. Circles may touch.
6. The sum of the 32 radii is at least 2.80.

Conditions 3, 4, and 5 are checked with an absolute tolerance of `1e-9`. Condition 6
has no tolerance. The circles may have different radii.

## Environment

- Python 3.12 with `numpy` and `scipy` is installed.
- `python /app/check_packing.py` checks `/app/packing.json` against the rules above
  and prints the sum of radii and the first rule that fails, if any. Pass a
  different path as an argument to check another file.

## Time limit

You have 15 minutes. Only the contents of `/app/packing.json` at the end are
graded, so save a valid packing early and overwrite it whenever you find a better one.
