import unittest
import sys
import os
import random
import importlib.util
from datetime import date, timedelta
from unittest.mock import Mock, patch

# Add src to path for imports
SRC = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, SRC)

import wordwheel_generator
from wordwheel_generator import generate_wordwheel, load_words, word_for_date
from puzzles import puzzle_for_date, print_puzzle

WEDNESDAY = date(2026, 10, 14)


def wednesdays(count, start=WEDNESDAY):
    return [start + timedelta(weeks=i) for i in range(count)]


def cycle_start(cycle, words):
    # cycles begin at week numbers that are multiples of the word count; +2 moves Monday to Wednesday
    return date.fromordinal(cycle * len(words) * 7 + 1) + timedelta(days=2)


def load_real_wordwheel():
    # conftest replaces the wordwheel module with a mock, so load the real one directly
    spec = importlib.util.spec_from_file_location("wordwheel_real", os.path.join(SRC, "wordwheel.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestWordList(unittest.TestCase):

    def test_words_are_usable(self):
        words = load_words()
        self.assertGreater(len(words), 100)
        self.assertEqual(len(words), len(set(words)), "words should be unique")
        for word in words:
            self.assertTrue(word.isalpha() and word.islower(), word)
            # the wheel's radius is len(word) * 18, so longer words don't fit on the paper
            self.assertTrue(6 <= len(word) <= 12, word)


class TestWordwheelGenerator(unittest.TestCase):

    def test_same_date_same_puzzle(self):
        self.assertEqual(generate_wordwheel(WEDNESDAY), wordwheel_generator._generate(WEDNESDAY))

    def test_no_repeats_until_every_word_is_used(self):
        words = load_words()
        cycle = WEDNESDAY.toordinal() // 7 // len(words)
        dates = wednesdays(len(words), cycle_start(cycle, words))
        picked = [word_for_date(d, words) for d in dates]
        self.assertEqual(sorted(picked), sorted(words))

    def test_new_cycle_is_a_different_order(self):
        words = load_words()
        cycle = WEDNESDAY.toordinal() // 7 // len(words)
        first = [word_for_date(d, words) for d in wednesdays(len(words), cycle_start(cycle, words))]
        second = [word_for_date(d, words) for d in wednesdays(len(words), cycle_start(cycle + 1, words))]
        self.assertEqual(sorted(first), sorted(second))
        self.assertNotEqual(first, second)

    def test_layout_is_in_range(self):
        for d in wednesdays(50):
            data = generate_wordwheel(d)['data']
            self.assertIn(data['reverse'], (True, False))
            self.assertTrue(0 <= data['rotation'] < len(data['task']))

    def test_golden_puzzle(self):
        # Pinned so that a refactor or Python upgrade can't silently change past puzzles
        self.assertEqual(generate_wordwheel(WEDNESDAY), GOLDEN_PUZZLE)

    def test_puzzle_is_cached_per_date(self):
        d = date(2030, 1, 9)
        with patch('wordwheel_generator._generate', wraps=wordwheel_generator._generate) as mock_generate:
            first = generate_wordwheel(d)
            first['data']['task'] = 'mutated'
            second = generate_wordwheel(d)
            self.assertEqual(mock_generate.call_count, 1)
            self.assertNotEqual(second['data']['task'], 'mutated')

    def test_wednesday_is_generated_wordwheel(self):
        for d in wednesdays(3):
            self.assertEqual(puzzle_for_date(d), generate_wordwheel(d))

    @patch('puzzles.draw_wordwheel')
    def test_print_puzzle_passes_layout_to_renderer(self, mock_draw):
        printer = Mock()
        puzzle = generate_wordwheel(WEDNESDAY)
        print_puzzle(puzzle, printer)
        mock_draw.assert_called_once_with(
            puzzle['data']['task'], output_file="puzzle.png",
            reverse=puzzle['data']['reverse'], rotation=puzzle['data']['rotation'])
        printer.image.assert_called_once()


class TestWordwheelLayout(unittest.TestCase):

    def setUp(self):
        self.wordwheel = load_real_wordwheel()

    def test_blanks_the_top_scoring_letter(self):
        # z scores highest in "gazebo"
        self.assertEqual(self.wordwheel.shuffle("gazebo"), "ga ebo")

    def test_reverse_and_rotation(self):
        self.assertEqual(self.wordwheel.shuffle("gazebo", reverse=True), "obe ag")
        self.assertEqual(self.wordwheel.shuffle("gazebo", rotation=2), " eboga")
        self.assertEqual(self.wordwheel.shuffle("gazebo", reverse=True, rotation=1), "be ago")

    def test_does_not_reseed_global_random(self):
        random.seed(1234)
        state = random.getstate()
        self.wordwheel.shuffle("gazebo", reverse=True, rotation=3)
        self.assertEqual(random.getstate(), state)

    def test_every_word_renders(self):
        output = os.path.join(os.path.dirname(__file__), "wordwheel_test.png")
        self.addCleanup(lambda: os.path.exists(output) and os.remove(output))
        for word in load_words():
            self.wordwheel.draw_wordwheel(word, output_file=output, reverse=True, rotation=1)


GOLDEN_PUZZLE = {'puzzle_type': 'wordwheel', 'data': {'task': 'gorgeous', 'reverse': True, 'rotation': 1}}


if __name__ == '__main__':
    unittest.main()
