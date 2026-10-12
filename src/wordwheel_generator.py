"""Date-seeded wordwheel puzzles.

Words are picked from data/wordwheel_words.txt in a shuffled order, so every
word is used once before any repeats. When the list is exhausted, a new
shuffled order starts. The same date always gives the same word and layout.

Changing the word list changes which word every date gets, past and future.
"""
import copy
import os
import random

from seeded_random import rand_below, shuffle

WORDS_FILE = os.path.join(os.path.dirname(__file__), "data", "wordwheel_words.txt")

# generated puzzles kept in memory, keyed by date
_cache = {}


def load_words():
    with open(WORDS_FILE) as f:
        return [line.strip() for line in f if line.strip()]


def word_for_date(date, words):
    # one slot per week, so consecutive Wednesdays get consecutive slots
    week = date.toordinal() // 7
    cycle, position = divmod(week, len(words))
    order = list(range(len(words)))
    shuffle(random.Random(f"wordwheel-cycle-{cycle}"), order)
    return words[order[position]]


def generate_wordwheel(date):
    if date not in _cache:
        _cache[date] = _generate(date)
    return copy.deepcopy(_cache[date])


def _generate(date):
    word = word_for_date(date, load_words())
    rng = random.Random(f"wordwheel-{date.isoformat()}")
    return {
        'puzzle_type': 'wordwheel',
        'data': {
            'task': word,
            'reverse': rng.random() < 0.5,
            'rotation': rand_below(rng, len(word))
        }
    }
