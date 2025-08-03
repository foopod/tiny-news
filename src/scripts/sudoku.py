import json
from datetime import datetime, timedelta

def process_sudoku():
    with open(f"SUPER160.txt", 'r') as file:
        current_date = datetime.now()
        for line in file:
            line = line.strip()
        
            puzzle = {"puzzle_type": "sudoku", "data": {"task": line}}


            is_tuesday = False
            while (not is_tuesday):
                current_date += timedelta(days=1)
                if(current_date.weekday() == 1): # Tuesday
                    is_tuesday = True

            new_file_name = current_date.strftime("%Y-%m-%d")
            
            with open(f"test/{new_file_name}.json", 'w') as file:
                file.write(json.dumps(puzzle))

