import unittest
import sys
import os
from unittest.mock import patch, Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import app
import tiny_news


def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)


def mock_printer():
    printer = Mock()
    printer.textln = Mock()
    return printer


def printed_lines(printer):
    return [str(call.args[0]) for call in printer.textln.call_args_list if call.args]


class TestKioskLoop(unittest.TestCase):
    """Runs the real main loop on SDL's dummy display with a scripted event queue."""

    def run_main(self, event_batches, flip_side_effect=None):
        batches = iter(event_batches + [[key(pygame.K_k)]])
        with patch('app.setup_logging'), \
                patch('app.pygame.event.get', side_effect=lambda: next(batches)), \
                patch('app.pygame.event.clear') as mock_clear, \
                patch('app.pygame.display.flip', side_effect=flip_side_effect), \
                self.assertRaises(SystemExit):
            app.main()
        return mock_clear

    def test_failing_print_does_not_stop_the_loop(self):
        failing = Mock(side_effect=RuntimeError("printer unplugged"), __name__="print_newsletter")
        with patch('app.print_newsletter', failing), self.assertLogs('app', 'ERROR'):
            self.run_main([[key(pygame.K_SPACE)], [key(pygame.K_SPACE)]])
        # the loop survived the first failure and handled the second key press too
        self.assertEqual(failing.call_count, 2)

    def test_drawing_error_does_not_stop_the_loop(self):
        flips = iter([RuntimeError("display glitch")])
        def flip():
            error = next(flips, None)
            if error:
                raise error
        newsletter = Mock(__name__="print_newsletter")
        with patch('app.print_newsletter', newsletter), self.assertLogs('app', 'ERROR'):
            self.run_main([[], [key(pygame.K_SPACE)]], flip_side_effect=flip)
        newsletter.assert_called_once()

    def test_key_presses_queued_during_a_print_are_dropped(self):
        newsletter = Mock(__name__="print_newsletter")
        with patch('app.print_newsletter', newsletter):
            mock_clear = self.run_main([[key(pygame.K_SPACE), key(pygame.K_SPACE), key(pygame.K_SPACE)]])
        newsletter.assert_called_once()
        mock_clear.assert_called_with(pygame.KEYDOWN)


class TestRunSafely(unittest.TestCase):

    def test_success(self):
        self.assertTrue(app.run_safely(Mock(__name__="ok")))

    def test_failure_is_logged_not_raised(self):
        with self.assertLogs('app', 'ERROR') as logs:
            self.assertFalse(app.run_safely(Mock(side_effect=OSError("USB"), __name__="print_weather_only")))
        self.assertIn("print_weather_only", logs.output[0])

    def test_key_mapping(self):
        self.assertIs(app.action_for_key(pygame.K_w), tiny_news.print_weather_only)
        self.assertIs(app.action_for_key(pygame.K_p), tiny_news.print_puzzle_only)
        self.assertIs(app.action_for_key(pygame.K_ESCAPE), tiny_news.print_rick_roll)
        self.assertIs(app.action_for_key(pygame.K_SPACE), tiny_news.print_newsletter)


class TestPrinterHandling(unittest.TestCase):

    def setUp(self):
        self.printer = mock_printer()
        patcher = patch('tiny_news.Usb', return_value=self.printer)
        self.mock_usb = patcher.start()
        self.addCleanup(patcher.stop)

    def test_printer_closed_when_printing_fails(self):
        self.printer.qr.side_effect = OSError("USB disconnected")
        with self.assertRaises(OSError):
            tiny_news.print_rick_roll()
        self.printer.close.assert_called_once()

    def test_unplugged_printer_raises_and_still_closes(self):
        # python-escpos connects on first write, so a missing printer fails there
        self.printer.textln.side_effect = OSError("Device not found")
        self.printer.text.side_effect = OSError("Device not found")
        self.printer.set.side_effect = OSError("Device not found")
        self.printer.print_and_feed.side_effect = OSError("Device not found")
        with self.assertRaises(OSError), self.assertLogs('tiny_news', 'ERROR'):
            tiny_news.print_newsletter()
        self.printer.close.assert_called_once()

    @patch('tiny_news.print_weather')
    @patch('tiny_news.puzzle_from_api')
    @patch('tiny_news.print_news', side_effect=KeyError('description'))
    def test_failed_section_does_not_stop_the_newsletter(self, mock_news, mock_puzzle, mock_weather):
        with self.assertLogs('tiny_news', 'ERROR') as logs:
            tiny_news.print_newsletter()

        self.assertIn("News", logs.output[0])
        lines = printed_lines(self.printer)
        self.assertIn("News unavailable today, sorry!", lines)
        mock_weather.assert_called_once()
        mock_puzzle.assert_called_once()
        self.assertIn('https://github.com/foopod/tiny-news', lines)
        self.printer.cut.assert_called_once()
        self.printer.close.assert_called_once()

    @patch('tiny_news.puzzle_from_api', side_effect=KeyError('puzzle_type'))
    def test_puzzle_only_failure_is_contained(self, mock_puzzle):
        with self.assertLogs('tiny_news', 'ERROR'):
            tiny_news.print_puzzle_only()
        self.assertIn("Puzzle unavailable today, sorry!", printed_lines(self.printer))
        self.printer.cut.assert_called_once()
        self.printer.close.assert_called_once()

    @patch('tiny_news.get_weather', side_effect=ValueError("bad data"))
    def test_weather_only_failure_is_contained(self, mock_weather):
        with self.assertLogs('tiny_news', 'ERROR'):
            tiny_news.print_weather_only()
        self.assertIn("Weather unavailable today, sorry!", printed_lines(self.printer))
        self.printer.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
