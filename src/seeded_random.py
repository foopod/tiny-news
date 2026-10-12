"""Helpers for puzzles picked or generated from a date.

Only rng.random() is used because it is the only part of the random module
guaranteed to produce the same sequence across Python versions, so a date's
puzzle never changes after an upgrade.
"""


def rand_below(rng, n):
    return int(rng.random() * n)


def shuffle(rng, items):
    # Fisher-Yates using only rng.random()
    for i in range(len(items) - 1, 0, -1):
        j = rand_below(rng, i + 1)
        items[i], items[j] = items[j], items[i]
