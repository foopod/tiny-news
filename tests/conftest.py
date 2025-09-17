import sys
from unittest.mock import Mock, MagicMock
import pytest

# Mock cairo-dependent modules globally for all tests
cairo_mocks = {
    'cairosvg': Mock(),
    'cairocffi': Mock(),
    'chess': Mock(),
    'crossword': Mock(),
    'sudoku': Mock(),
    'wordwheel': Mock(),
}

# Apply mocks before any imports
for module_name, mock_obj in cairo_mocks.items():
    sys.modules[module_name] = mock_obj

# Mock the render functions that would be called
render_chess = Mock()
render_sudoku = Mock()
render_crossword = Mock()
draw_wordwheel = Mock()

sys.modules['chess'].render_chess = render_chess
sys.modules['sudoku'].render_sudoku = render_sudoku
sys.modules['crossword'].render_crossword = render_crossword
sys.modules['wordwheel'].draw_wordwheel = draw_wordwheel