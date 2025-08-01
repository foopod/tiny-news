from datetime import datetime
import os
import requests
import random
import json
import textwrap

from util import center_pad, print_heading
from puzzle import draw
from chess_puzzle import render_chess
from sudoku import render_sudoku

puzzlemap = {
    'sudoku': 'https://shadify.yurace.pro/api/sudoku/generator',
    'wordsearch': 'https://shadify.yurace.pro/api/wordsearch/generator',
    'anagram': 'https://shadify.yurace.pro/api/anagram/generator'
}
description_map = {
    'sudoku': 'Fill free cells with numbers from 1 to 9 so that in each row, each column and each small 3 by 3 square each digit occurs only once.',
    'takuzu': 'Each column and each row must be unique. Each row and each column must have an equal number of x and o. No more than two x or o in a line.',
    'wordsearch': 'The aim of the puzzle is to find and mark all the words hidden in the grid. The words can be placed horizontally, vertically or diagonally.',
    'anagram': 'Create as many words as you can using only the letters in the word below.',
    'chess': 'Standard chess rules apply. Black has just had their turn, can white find a way to checkmate in just a single move?',
    'wordwheel': 'Place a letter into the blank space in such a way that it completes the word. The word can start in any position and could go in either direction.'
}
takuzu_map = {
    '0': "o",
    '1': "x"
}

def get_random_puzzle():
    options = ['sudoku', 'wordsearch', 'anagram']
    puzzle_type = random.choice(options)
    puzzle_type = 'anagram'
    
    params = {}
    # TODO add params based on puzzle type
    response = requests.get(puzzlemap[puzzle_type], params=params)
    data = response.json()
    return {
        'puzzle_type': puzzle_type,
        'data': data
    }

def print_puzzle(puzzle_dict, printer):
    puzzle_type = puzzle_dict["puzzle_type"]
    puzzle_data = puzzle_dict["data"]
    
    

    if puzzle_type != 'custom':
        desc = description_map[puzzle_type]
        print_heading(printer, f"Puzzle - {puzzle_type.capitalize()}")
    else:
        desc = puzzle_data["description"]
        print_heading(printer, f"Puzzle - {puzzle_data["type"].capitalize()}")
        
    lines = textwrap.wrap(desc, 48)
    for line in lines :
        printer.textln(line)

    if puzzle_type == 'anagram':
        printer.set(custom_size=True, height=2, width=2)
        printer.print_and_feed(1)
        printer.text(center_pad(puzzle_data["task"], 24))
        printer.print_and_feed(2)
        printer.set(custom_size=False, height=1, width=1)
        printer.textln(f"Goal: {len(puzzle_data["words"])} words")
        printer.textln(f"Longest: {len(max(puzzle_data["words"], key=len))} letters")
    elif puzzle_type == 'sudoku':
        render_sudoku(puzzle_data["task"])
        printer.image('puzzle.png', impl='graphics', center=True)
    elif puzzle_type == 'custom':
        printer.image(puzzle_data["task"], impl='graphics', center=True)
        lines = textwrap.wrap(puzzle_data["more_info"], 48)
        for line in lines :
            printer.textln(line)
    elif puzzle_type == 'chess':
        render_chess(puzzle_data["task"])
        printer.image('puzzle.png', impl='graphics', center=True)
    elif puzzle_type == 'wordwheel':
        draw(puzzle_data["task"], output_file="puzzle.png")
        printer.image('puzzle.png', impl='graphics', center=True)
    elif puzzle_type == 'takuzu':
        takuzu_data = []
        for row in puzzle_data["task"]:
            takuzu_data.append([takuzu_map[i] if i != 'x' else ' ' for i in row])
        print_grid(printer, takuzu_data)
    elif puzzle_type == 'wordsearch':
        print_grid(printer, puzzle_data["grid"])
        printer.print_and_feed(1)
        lines = textwrap.wrap(', '.join([w["word"] for w in puzzle_data["words"]]), 48)
        for line in lines :
            printer.textln(line)


def print_grid(printer, grid_dict):
    printer.set(custom_size=True, height=2, width=2, underline=True, align='center')
    printer.textln(f" {' '.join([f"{c if c else " "}" for c in " "*len(grid_dict)])} ")
    for row in grid_dict:
        line = f"|{'|'.join([f"{c if c else " "}" for c in row])}|"
        printer.textln(line)
    printer.set(custom_size=False, height=1, width=1, underline=False, align='left')

def puzzle_from_api(printer):
    now = datetime.today()
    date_format = "%Y-%m-%d"
    d = now.strftime(date_format)
    # d="2025-05-14"
    filepath = f"puzzles/{d}.json"
    puzzle_dict = {}
    
    if os.path.isfile(filepath):
        # already exists
        with open(filepath, 'r') as f:
            puzzle_dict = json.load(f)
    else:
        puzzle_dict = get_random_puzzle()
        with open(filepath, 'w') as f:
            f.writelines(json.dumps(puzzle_dict))

    print_puzzle(puzzle_dict, printer)

if __name__ == "__main__":
    from escpos.printer import Usb
    p = Usb(0x04b8, 0x0e28, 0)
    puzzle_from_api(p)
