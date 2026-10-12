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