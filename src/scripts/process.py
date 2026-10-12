import json
from datetime import datetime, timedelta
import random


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