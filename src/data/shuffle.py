import random

def shuffle_words(input_file, output_file):
    # Read words from input file
    with open(input_file, 'r') as f:
        words = f.read().splitlines()

    # Shuffle the list
    random.shuffle(words)

    # Write the shuffled list to the output file
    with open(output_file, 'w') as f:
        for word in words:
            f.write(word + '\n')

# Example usage
shuffle_words('dictionary.txt', 'shuffled_words.txt')
