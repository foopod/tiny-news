import json
from ulid import ULID
from datetime import datetime
import os

def process_zuzu():
    # Load JSON data from a file
    with open('raw_takuzu.json', 'r') as file:
        data = json.load(file)

    supported = [8]
    puzzles = []

    for cols in supported:
        puzzle_list = data.get(f"{cols}")
        print(f"{cols}")
        print(puzzle_list)
        for puzzle in puzzle_list:
            puzzle = puzzle.split("::")[2]
            task = []
            offset = 0
            for i in range(cols):
                row = []
                for j in range(cols):
                    value = puzzle[i+j*cols]
                    row.append(value if value != '.' else 'x')
                task.append(row)
            
            data = {
                'size': cols,
                'task': task
            }
            puzzle_json = {
                'puzzle_type': 'takuzu',
                'data': data
            }
            with open(f"zuzu/{cols}-{str(ULID.from_datetime(datetime.now()))}.json", 'w') as file:
                file.write(json.dumps(puzzle_json))

def process_zuzu_puzzles():
    current_date = datetime.now()
    unused = os.listdir('zuzu')
    while(len(unused) > 0):
        next_date = None
        while (not next_date):
            if(current_date.weekday() == 0): # Monday
                next_date = current_date
            current_date += timedelta(days=1)