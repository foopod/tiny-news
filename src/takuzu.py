"""Date-seeded takuzu (binary puzzle) generator.

The same date always produces the same puzzle. Only rng.random() is used for
randomness because it is the only part of the random module guaranteed to
produce the same sequence across Python versions.

Puzzles are generated in two steps:
  1. Build a random full solution grid, row by row, with backtracking
     (restarting if a search attempt takes too long).
  2. Visit every cell once in a shuffled order and blank it, rolling the
     removal back if the deduction solver can no longer complete the grid.

The solver only uses single-line deductions (pairs, sandwiches and completed
counts), so every puzzle can be solved without guessing and has exactly one
solution.
"""
import copy
import itertools
import random
from functools import lru_cache

SIZES = [6, 8, 10]
EMPTY = 'x'
# rows placed per solution attempt before restarting
RESTART_BUDGET = 50


def _rand_below(rng, n):
    return int(rng.random() * n)


def _shuffle(rng, items):
    # Fisher-Yates using only rng.random() so results are stable across Python versions
    for i in range(len(items) - 1, 0, -1):
        j = _rand_below(rng, i + 1)
        items[i], items[j] = items[j], items[i]


def _line_ok(line, n):
    """True if a (partial) line has no triples and no more than n/2 of either symbol."""
    if line.count(0) > n // 2 or line.count(1) > n // 2:
        return False
    for i in range(n - 2):
        if line[i] is not None and line[i] == line[i + 1] == line[i + 2]:
            return False
    return True


@lru_cache(maxsize=None)
def _valid_rows(n):
    return [row for row in itertools.product((0, 1), repeat=n) if _line_ok(row, n)]


def _columns_ok(grid, n):
    """Check the columns of a partially built grid after appending its last row."""
    k = len(grid) - 1
    for c in range(n):
        ones = sum(row[c] for row in grid)
        if ones > n // 2 or (k + 1 - ones) > n // 2:
            return False
        if k >= 2 and grid[k - 2][c] == grid[k - 1][c] == grid[k][c]:
            return False
    return True


def _solution(n, rng):
    """Build a random valid full grid: balanced, no triples, unique rows and columns.

    Unlucky early rows can lead to a very long search, so each attempt gets a
    small budget and the search restarts (with fresh random choices) when it
    runs out.
    """
    while True:
        grid = _try_solution(n, rng, budget=RESTART_BUDGET)
        if grid:
            return grid


def _try_solution(n, rng, budget):
    rows = _valid_rows(n)
    grid = []
    steps = 0

    def fill():
        nonlocal steps
        if len(grid) == n:
            return len(set(zip(*grid))) == n
        steps += 1
        if steps > budget:
            return False
        candidates = list(rows)
        _shuffle(rng, candidates)
        for row in candidates:
            if row in grid:
                continue
            grid.append(row)
            if _columns_ok(grid, n) and fill():
                return True
            grid.pop()
        return False

    if fill():
        return [list(row) for row in grid]
    return None


def _lines(n):
    rows = [[(r, c) for c in range(n)] for r in range(n)]
    cols = [[(r, c) for r in range(n)] for c in range(n)]
    return rows + cols


def solve(puzzle, n):
    """Apply single-line deductions until nothing changes.

    For each empty cell, if placing a symbol would break the balance or
    no-triples rule in its row or column, the cell must hold the other
    symbol. Returns the completed grid, or None if deductions alone can't
    finish it.
    """
    grid = [row[:] for row in puzzle]
    lines = _lines(n)
    changed = True
    while changed:
        changed = False
        for cells in lines:
            values = [grid[r][c] for r, c in cells]
            for i, value in enumerate(values):
                if value is not None:
                    continue
                for v in (0, 1):
                    values[i] = v
                    if not _line_ok(values, n):
                        values[i] = 1 - v
                        r, c = cells[i]
                        grid[r][c] = 1 - v
                        changed = True
                        break
                    values[i] = None
    if any(v is None for row in grid for v in row):
        return None
    return grid


def _dig(solution, n, rng):
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(n) for c in range(n)]
    _shuffle(rng, cells)
    for r, c in cells:
        puzzle[r][c] = None
        if solve(puzzle, n) is None:
            puzzle[r][c] = solution[r][c]
    return puzzle


def size_for_date(date):
    # rotate through the sizes week by week
    return SIZES[(date.toordinal() // 7) % len(SIZES)]


# generated puzzles kept in memory, keyed by (date, size)
_cache = {}


def generate_takuzu(date, size=None):
    n = size or size_for_date(date)
    key = (date, n)
    if key not in _cache:
        _cache[key] = _generate(date, n)
    return copy.deepcopy(_cache[key])


def _generate(date, n):
    rng = random.Random(f"takuzu-{date.isoformat()}")
    solution = _solution(n, rng)
    puzzle = _dig(solution, n, rng)
    task = [[EMPTY if v is None else str(v) for v in row] for row in puzzle]
    return {
        'puzzle_type': 'takuzu',
        'data': {
            'size': n,
            'task': task
        }
    }
