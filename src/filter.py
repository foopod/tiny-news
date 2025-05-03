from puzzle import scrabble_scores

def is_suitable(word):
    if len(word) < 6:
        return False

    if len(word) > 12:
        return False
    
    if not word.isalpha():
        return False

    if get_scrabble_score(word) > 20:
        return False

    # Example check: only alphabetic and 4+ letters long
    return word.isalpha() and len(word) >= 4

def get_scrabble_score(word):
    score = 0
    for letter in word:
        score+= scrabble_scores.get(letter)

    return score

def filter_words(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            word = line.strip()
            if is_suitable(word):
                outfile.write(word + '\n')

# Example usage
filter_words('data/english.txt', 'data/dictionary.txt')