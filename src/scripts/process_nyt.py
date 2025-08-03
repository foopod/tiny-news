import json
from datetime import datetime, timedelta
import random


with open('scripts/nyt_crosswords_jan_jul_2025_2025-08-02.json', 'r') as file:
    data = json.load(file)

    output = []
    for i, puzzle in enumerate(data):
        if len(puzzle['data']['body'][0]['cells']) != 25:
            continue
        empties = []
        labels = []
        for index, cell in enumerate(puzzle['data']['body'][0]['cells']):
            if cell.get('answer', None) is None:
                empties.append(index)
            if cell.get('label', None):
                labels.append((index, cell.get('label')))
        
        
        across = []
        down = []
        for clue in puzzle['data']['body'][0]['clues']:
            c = {
                'label': clue['label'],
                'text': clue['text'][0]["plain"]
            }
            if clue['direction'] == 'Across':
                across.append(c)
            else:
                down.append(c)

        width = puzzle['data']['body'][0]['dimensions']['width']
        height = puzzle['data']['body'][0]['dimensions']['height']

        output_puzzle = {
            'width': width,
            'height': height,
            'empties': empties,
            'labels': labels,
            'clues': {'across': across, 'down': down}
        }
        output.append(output_puzzle)

    current_date = datetime.now()
    while(len(output) > 0):
        is_tuesday = False
        while (not is_tuesday):
            current_date += timedelta(days=1)
            if(current_date.weekday() == 1): # Wednesday
                is_tuesday = True
        
        new_file_name = current_date.strftime("%Y-%m-%d")
        puzzle = random.choice(output)
        json_data = {"puzzle_type": "crossword", "data": puzzle}
        
        with open(f"test/{new_file_name}.json", 'w') as file:
            file.write(json.dumps(json_data))
        output.remove(puzzle)