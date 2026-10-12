import unittest
import sys
import os
import time
from datetime import date, timedelta
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from takuzu import generate_takuzu, size_for_date, solve, SIZES
from puzzles import puzzle_for_date, puzzle_from_api

MONDAY = date(2026, 10, 12)
MONDAYS = [MONDAY + timedelta(weeks=i) for i in range(30)]


def to_grid(task):
    return [[None if v == 'x' else int(v) for v in row] for row in task]


def count_solutions(grid, n, limit=2):
    """Brute force solution counter, independent of the generator's solver."""
    for r in range(n):
        for c in range(n):
            if grid[r][c] is None:
                total = 0
                for v in (0, 1):
                    grid[r][c] = v
                    if partial_ok(grid, n):
                        total += count_solutions(grid, n, limit - total)
                    if total >= limit:
                        break
                grid[r][c] = None
                return total
    return 1 if is_valid_solution(grid, n) else 0


def partial_ok(grid, n):
    for line in grid + [list(col) for col in zip(*grid)]:
        if line.count(0) > n // 2 or line.count(1) > n // 2:
            return False
        for i in range(n - 2):
            if line[i] is not None and line[i] == line[i + 1] == line[i + 2]:
                return False
    return True


def is_valid_solution(grid, n):
    columns = [tuple(col) for col in zip(*grid)]
    return (partial_ok(grid, n)
            and len(set(tuple(row) for row in grid)) == n
            and len(set(columns)) == n)


class TestTakuzuGenerator(unittest.TestCase):

    def test_same_date_same_puzzle(self):
        self.assertEqual(generate_takuzu(MONDAY), generate_takuzu(MONDAY))

    def test_different_mondays_different_puzzles(self):
        tasks = [str(generate_takuzu(d)['data']['task']) for d in MONDAYS]
        self.assertEqual(len(set(tasks)), len(tasks))

    def test_sizes_rotate_weekly(self):
        sizes = [size_for_date(d) for d in MONDAYS[:len(SIZES)]]
        self.assertEqual(sorted(sizes), sorted(SIZES))
        for d in MONDAYS:
            self.assertEqual(generate_takuzu(d)['data']['size'], size_for_date(d))

    def test_puzzles_are_valid_unique_and_solvable_by_deduction(self):
        # brute force counting is slow for 10x10, so check a subset of dates
        for d in MONDAYS[:10]:
            for n in SIZES:
                puzzle = generate_takuzu(d, n)
                self.assertEqual(puzzle['puzzle_type'], 'takuzu')
                self.assertEqual(puzzle['data']['size'], n)
                grid = to_grid(puzzle['data']['task'])
                self.assertEqual(len(grid), n)
                self.assertTrue(all(len(row) == n for row in grid))

                solution = solve(grid, n)
                self.assertIsNotNone(solution, f"{d} {n}x{n} not solvable by deduction")
                self.assertTrue(is_valid_solution(solution, n))
                self.assertEqual(count_solutions([row[:] for row in grid], n), 1)

    def test_golden_puzzle(self):
        # Pinned so that a refactor or Python upgrade can't silently change past puzzles
        self.assertEqual(generate_takuzu(MONDAY)['data'], {
            'size': 8,
            'task': GOLDEN_TASK
        })

    def test_generation_is_fast(self):
        start = time.time()
        for d in MONDAYS[:10]:
            generate_takuzu(d, 10)
        self.assertLess((time.time() - start) / 10, 0.5)


class TestMondayPuzzle(unittest.TestCase):

    def test_monday_is_generated_takuzu(self):
        for d in MONDAYS[:3]:
            self.assertEqual(puzzle_for_date(d), generate_takuzu(d))

    def test_puzzle_from_api_prints_takuzu_on_monday(self):
        printer = Mock()
        puzzle_from_api(printer, MONDAY)

        text_calls = [call[0][0] for call in printer.textln.call_args_list if call[0]]
        self.assertTrue(any(str(t).startswith('|') for t in text_calls), "Takuzu grid should be printed")

    def test_missing_puzzle_does_not_raise(self):
        printer = Mock()
        puzzle_from_api(printer, date(2020, 1, 4))  # a Saturday with no puzzle file
        printer.textln.assert_not_called()


GOLDEN_TASK = [
    ['0', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
    ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
    ['1', 'x', '1', 'x', '0', '0', 'x', 'x'],
    ['1', 'x', 'x', '0', '0', 'x', 'x', 'x'],
    ['x', 'x', 'x', 'x', 'x', 'x', '1', 'x'],
    ['x', 'x', 'x', 'x', '0', 'x', '1', 'x'],
    ['0', 'x', 'x', 'x', 'x', 'x', 'x', '0'],
    ['x', 'x', '1', 'x', '1', 'x', '1', 'x'],
]


if __name__ == '__main__':
    unittest.main()
