import json
from datetime import datetime, timedelta
import random

def process_sudoku():
    with open(f"scripts/sudoku17.txt", 'r') as file:
        all_lines = file.readlines()

    current_date = datetime.now()
    lines = random.sample(all_lines, 300)
    for line in lines:
        line = line.strip()
    
        puzzle = {"puzzle_type": "sudoku", "data": {"task": line}}


        is_thursay = False
        while (not is_thursay):
            current_date += timedelta(days=1)
            if(current_date.weekday() == 1): # Thusday
                is_thursay = True

        new_file_name = current_date.strftime("%Y-%m-%d")
        
        with open(f"test/{new_file_name}.json", 'w') as file:
            file.write(json.dumps(puzzle))

process_sudoku()