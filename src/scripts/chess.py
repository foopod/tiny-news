import pandas as pd
import json

def convert_puzzles():
    df = pd.read_csv('~/Downloads/hardest200.csv')
    current_date = datetime.now()
    
    # Check if required columns exist
    # Iterate over rows
    for index, row in df.iterrows():
        fen = row['FEN']
        moves = row['Moves']
        print(f"  FEN: {fen}")
        print(f"  Moves: {moves}")

        is_friday = False
        while (not is_friday):
            current_date += timedelta(days=1)
            if(current_date.weekday() == 4): # Wednesday
                is_friday = True

        board = chess.Board(fen=fen)

        # apply last move
        next_move = moves.split(' ')[0]
        board.push(chess.Move.from_uci(next_move))

        # save new board
        
        
        new_file_name = current_date.strftime("%Y-%m-%d")
        json_data = {"puzzle_type": "chess", "data": {"task": board.fen()}}
        
        with open(f"puzzles/{new_file_name}.json", 'w') as file:
            file.write(json.dumps(json_data))
