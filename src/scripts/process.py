import json
from datetime import datetime, timedelta
import os
import shutil
import random


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
        for index, puzzle in enumerate(puzzle_list):
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
            with open(f"zuzu/{cols}-{index}.json", 'w') as file:
                file.write(json.dumps(puzzle_json))

def process_zuzu_puzzles():
    current_date = datetime.now()
    unused = os.listdir('zuzu')
    while(len(unused) > 0):
        is_monday = False
        while (not is_monday):
            current_date += timedelta(days=1)
            if(current_date.weekday() == 0): # Monday
                is_monday = True
        
        new_file_name = current_date.strftime("%Y-%m-%d")
        file_to_copy = random.choice(unused)
        shutil.copyfile(f"zuzu/{file_to_copy}", f"puzzles/{new_file_name}.json")
        unused.remove(file_to_copy)

def process_wordwheels():
    words = ["abdominal", "abrasive", "abundance",
        "accident", "activate", "adjacent", "aircraft", "alligator", "ambition", "amphibian", "amusement",
        "analogy", "ancestral", "androgyny", "annotate", "accusation", "relevancy", "companion", "sedative",
        "marinate", "redirection", "perambulate", "benevolence", "complaint", "reschedule", "aneurism",
        "backstage", "badminton", "balcony", "beguiling", "blemish", "bribery", "brutalism", "chocolate",
        "cabinet", "cabaret", "caffeine", "cannibal", "capitalism", "cardiology", "cavernous", "circumvent",
        "collapse", "corduroy", "crucible", "cumulative", "dalmatian", "daydream", "debatable", "declassified",
        "denomination", "deprecation", "descendant", "dietitian", "digression", "dreadful", "dungeon",
        "eccentric", "editorial", "education", "egomania", "emphatic", "emporium", "endemic", "endorsement",
        "enhancement", "equation", "expiry", "familiar", "feminism", "fermented", "fierceness", "firmament",
        "flamboyant", "floatation", "florist", "fogginess", "foreboding", "fundamental", "galavant", 
        "galvanised", "gardener", "gazebo", "gelatinous", "glimmered", "glucose", "gorgeous", "governance",
        "haunting", "hairspray", "hallucinate", "heftiness", "herbalism", "hindrance", "historian",
        "identity", "idyllic", "ignorant", "illegitimate", "imbalance", "immersion", "incognito", "indicative",
        "keystone", "kidnapper", "kilolitre", "kindergarten", "lacerate", "language", "legislation", "levitate",
        "logistics", "lubricate", "maelstrom", "malcontent", "messenger", "modernise", "narcissist", 
        "nocturnal", "numerous", "obstinate", "olfactory", "organism", "palatable", "pantomime", "peppercorn",
        "quietness", "queried", "quaternion", "rancorous", "reciprocal", "repeatedly", "salacious", 
        "scientific", "sentinel", "sinusoid"]
    print(len(words))
    current_date = datetime.now()
    while(len(words) > 0):
        is_wednesday = False
        while (not is_wednesday):
            current_date += timedelta(days=1)
            if(current_date.weekday() == 2): # Wednesday
                is_wednesday = True
        
        new_file_name = current_date.strftime("%Y-%m-%d")
        word_used = random.choice(words)
        json_data = {"puzzle_type": "wordwheel", "data": {"task": word_used}}
        
        with open(f"puzzles/{new_file_name}.json", 'w') as file:
            file.write(json.dumps(json_data))
        words.remove(word_used)


def process_puzzles():
    # load puzzles from csv
    puzzles = []
    
    for p in puzzles:
        # load board
        board = chess.Board(fen=p)

        # apply last move
        next_move = 'd4e6'
        board.push(chess.Move.from_uci(next_move))

        # save new board
        board.fen()

# render_chess(board.fen(), 'puzzle.png')

def load_puzzles():
    import dask.dataframe as dd

    df = dd.read_csv('~/Downloads/matein1.csv')


    filtered_df = df[df['FEN'].str.contains(' b ')]

    hardest = filtered_df.nlargest(200, 'Rating')

    hardest.to_csv('~/Downloads/hardest200.csv', single_file=True, index=False)