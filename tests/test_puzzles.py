import unittest
import sys
import os
from unittest.mock import patch, Mock, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from puzzles import get_random_puzzle, print_puzzle
from http_utils import get_cached_json


class TestPuzzleFunctionality(unittest.TestCase):

    @patch('puzzles.get_cached_json')
    @patch('puzzles.random.choice')
    def test_get_random_puzzle_success(self, mock_choice, mock_cached_json):
        # Mock puzzle type selection
        mock_choice.return_value = 'sudoku'

        # Mock successful puzzle response
        mock_cached_json.return_value = {
            "task": "123456789" * 9,  # Simple sudoku string
            "difficulty": "easy"
        }

        result = get_random_puzzle()

        self.assertEqual(result['puzzle_type'], 'sudoku')
        self.assertIn('data', result)
        self.assertEqual(result['data']['task'], "123456789" * 9)
        mock_cached_json.assert_called_once()

    @patch('puzzles.get_cached_json')
    @patch('puzzles.random.choice')
    def test_get_random_puzzle_anagram(self, mock_choice, mock_cached_json):
        # Test anagram puzzle type
        mock_choice.return_value = 'anagram'

        mock_cached_json.return_value = {
            "task": "NEWSPAPER",
            "words": ["NEWS", "PAPER", "WRAP", "PEAR", "NEAR"],
            "difficulty": "medium"
        }

        result = get_random_puzzle()

        self.assertEqual(result['puzzle_type'], 'anagram')
        self.assertEqual(result['data']['task'], "NEWSPAPER")
        self.assertEqual(len(result['data']['words']), 5)

    @patch('puzzles.get_cached_json')
    @patch('puzzles.random.choice')
    def test_get_random_puzzle_wordsearch(self, mock_choice, mock_cached_json):
        # Test wordsearch puzzle type
        mock_choice.return_value = 'wordsearch'

        mock_cached_json.return_value = {
            "grid": [
                ["A", "B", "C", "D"],
                ["E", "F", "G", "H"],
                ["I", "J", "K", "L"],
                ["M", "N", "O", "P"]
            ],
            "words": [
                {"word": "ABC", "start": [0, 0], "direction": "horizontal"},
                {"word": "AFKP", "start": [0, 0], "direction": "diagonal"}
            ]
        }

        result = get_random_puzzle()

        self.assertEqual(result['puzzle_type'], 'wordsearch')
        self.assertEqual(len(result['data']['grid']), 4)
        self.assertEqual(len(result['data']['words']), 2)

    @patch('puzzles.get_cached_json')
    @patch('puzzles.random.choice')
    def test_get_random_puzzle_api_failure(self, mock_choice, mock_cached_json):
        # Test when API returns error data
        mock_choice.return_value = 'sudoku'

        mock_cached_json.return_value = {
            "error": "Failed to fetch data: API unavailable"
        }

        result = get_random_puzzle()

        self.assertEqual(result['puzzle_type'], 'sudoku')
        self.assertIn('error', result['data'])

    def test_print_puzzle_anagram(self):
        # Test printing anagram puzzle with mocked printer
        mock_printer = Mock()

        puzzle_dict = {
            "puzzle_type": "anagram",
            "data": {
                "task": "TESTING",
                "words": ["TEST", "STING", "SET", "GET"]
            }
        }

        print_puzzle(puzzle_dict, mock_printer)

        # Verify printer methods were called
        mock_printer.textln.assert_called()
        mock_printer.set.assert_called()

        # Check that the task was printed
        calls = [call[0][0] for call in mock_printer.textln.call_args_list if call[0]]
        task_printed = any("Goal: 4 words" in str(call) for call in calls)
        longest_printed = any("Longest: 5 letters" in str(call) for call in calls)

        self.assertTrue(task_printed)
        self.assertTrue(longest_printed)

    @patch('puzzles.render_sudoku')
    def test_print_puzzle_sudoku(self, mock_render):
        # Test printing sudoku puzzle
        mock_printer = Mock()

        puzzle_dict = {
            "puzzle_type": "sudoku",
            "data": {
                "task": "123456789" * 9
            }
        }

        print_puzzle(puzzle_dict, mock_printer)

        # Verify sudoku renderer was called
        mock_render.assert_called_once_with("123456789" * 9)

        # Verify image was printed
        mock_printer.image.assert_called_once_with('puzzle.png', impl='graphics', center=True)

    def test_print_puzzle_wordsearch(self):
        # Test printing wordsearch puzzle
        mock_printer = Mock()

        puzzle_dict = {
            "puzzle_type": "wordsearch",
            "data": {
                "grid": [
                    ["A", "B", "C"],
                    ["D", "E", "F"],
                    ["G", "H", "I"]
                ],
                "words": [
                    {"word": "ABC"},
                    {"word": "DEF"},
                    {"word": "GHI"}
                ]
            }
        }

        print_puzzle(puzzle_dict, mock_printer)

        # Verify printer methods were called
        mock_printer.textln.assert_called()

        # Check that words were printed
        calls = [call[0][0] for call in mock_printer.textln.call_args_list if call[0]]
        words_printed = any("ABC, DEF, GHI" in str(call) for call in calls)
        self.assertTrue(words_printed)

    def test_puzzle_api_integration(self):
        # Test integration by mocking at the import level
        with patch('puzzles.get_cached_json') as mock_cached_json:
            mock_cached_json.return_value = {
                "task": "INTEGRATION",
                "words": ["INTER", "RATE", "TIGER", "TEAR"],
                "difficulty": "hard"
            }

            # Test getting random puzzle (which uses cached JSON internally)
            result = get_random_puzzle()

            self.assertEqual(result["puzzle_type"] in ["sudoku", "wordsearch", "anagram"], True)
            self.assertEqual(result["data"]["task"], "INTEGRATION")
            self.assertEqual(len(result["data"]["words"]), 4)
            self.assertEqual(mock_cached_json.call_count, 1)


if __name__ == '__main__':
    unittest.main()