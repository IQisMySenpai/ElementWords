import json
import concurrent.futures

with open('elements.json', 'r') as element_file:
    elements = json.load(element_file)


def sanitise_words(input_words=None):
    """
    Sanitises a list of words with running the sanitise_word function as a multiprocess.
    :param input_words: A list of words.
    :return: The sanitised list of words with out the ones that couldn't be sanitised.
    """
    if input_words is None:
        return []

    input_length = len(input_words)
    print(f'\nSanitising {input_length} words...\n')

    # Start multiprocessing the words
    with concurrent.futures.ProcessPoolExecutor() as executor:
        output_words = executor.map(sanitise_word, input_words)

    print(f'\nFinished Sanitising {input_length} words!\n')

    # Removes all None and returns the list
    return list(filter(None, output_words))


def sanitise_word(word=''):
    """
    Sanitises a word.
    :param word: A word string.
    :return: The sanitised word, or None if it couldn't be sanitised.
    """
    print(f'Sanitising {word}')

    # Check for strings
    if type(word) is not str:
        return None

    # Sanitise for later use.
    word = word.replace("\n", "").lower().strip()

    # Filter out empty words, to save processing power on later steps
    if word == '':
        return None

    return word


def small_brain_filter(input_words=None):
    """
    Filters a list of words with the small_brain_algorithm function as a multiprocess.
    :param input_words: A list of words.
    :return: A list of lists, where each list contains the word and possible elements
    """
    if input_words is None:
        return []

    input_length = len(input_words)
    print(f'\nSmall Brain Filtering {input_length} words...\n')

    # Start multiprocessing the words
    with concurrent.futures.ProcessPoolExecutor() as executor:
        output_words = executor.map(small_brain_algorithm, input_words)

    print(f'\nFinished Small Brain Filtering {input_length} words!\n')

    # Removes all None and returns the list
    return list(filter(None, output_words))


def small_brain_algorithm(word=''):
    """
    Checks if all elements that are in a word have a char total longer or equal to the word
    :param word: A word string.
    :return: A list with where index 0 is the word and index 1 is all possible elements that are in the word.
    """
    print(f'Small Braining {word}')

    word_possible_elements = []
    word_possible_elements_len = 0

    # Checks each element if it is contained in the word.
    for element in elements:
        # If a element is in the word add the length to the total and append it to a list.
        if element in word:
            word_possible_elements_len += len(element)
            word_possible_elements.append(element)

    # If the total char of the elements is smaller than the word return None
    if len(word) > word_possible_elements_len:
        return None

    return [word, word_possible_elements]


def big_brain_filter(input_words=None):
    """
    Filters the output of the small_brain_filter with the big_brain_algorithm function as a multiprocess.
    :param input_words: The output of the small_brain_filter
    :return: A dict of lists, where each list contains all possibilities to write a word out of elements
    """
    if input_words is None:
        return []

    input_length = len(input_words)
    print(f'\nBig Brain Filtering {input_length} words...\n')

    # Start multiprocessing the words
    with concurrent.futures.ProcessPoolExecutor() as executor:
        output_words = executor.map(big_brain_algorithm, input_words)

    print(f'\nFinished Big Brain Filtering {input_length} words!\n')
    # Removes all None and returns the dict
    results = {}
    for d in list(filter(None, output_words)):
        results.update(d)
    return results


def big_brain_algorithm(word_list=None):
    """
    Checks if a word can be made out of the elements that are contained in it.
    :param word_list: A list with where index 0 is the word and index 1 is all possible elements that are in the word.
    :return: All possibilities to create the word out of elements.
    """
    if word_list is None:
        return None

    word = word_list[0]
    word_possible_elements = word_list[1]

    print(f'Big Braining {word}')

    # Create a list of length of the word
    element_positions = [[] for _ in range(len(word))]

    # Checks at which position(s) the element fits in the word
    for word_possible_element in word_possible_elements:
        # Find the first occurrence in a word
        pos = word.find(word_possible_element, 0)
        # Create a fail_safe just in case
        fail_safe = 0

        while fail_safe < 100:
            # Break if no new occurrence is found
            if pos < 0:
                break

            fail_safe += 1

            # Add to the list at the position of the position
            element_positions[pos].append(word_possible_element)

            # Check for a new occurrence later in the word
            pos = word.find(word_possible_element, pos + len(word_possible_element))

    # Run a recursive function to check the construction possibilities
    result = big_brain_recursive(len(word), element_positions, 0)
    if type(result) is list:
        result = {word: result}

    return result


def big_brain_recursive(word_len, element_positions, pos):
    results = []
    # Loop through each element at the current position
    for element in element_positions[pos]:
        # If element finishes the word add the word to results
        if pos + len(element) == word_len:
            results += [[element]]
            continue

        # A safety which should never be run. Checks if the element surpasses the len of the word
        # if pos + len(element) > word_len:
        #     continue

        # If there is no element at the next position, continue
        if len(element_positions[pos + len(element)]) < 1:
            continue

        # Check the next position
        result = big_brain_recursive(word_len, element_positions, pos + len(element))

        # If a result (list) is found add the current element to each result.
        if type(result) is list:
            for r in range(len(result)):
                result[r].insert(0, element)
            results += result

    # If a result(s) is found return it
    if len(results) > 0:
        return results

    # Else return None
    return None


if __name__ == '__main__':
    with open('words.txt', 'r') as word_file:
        words = word_file.readlines()
        word_file.close()

    big_dict = big_brain_filter(small_brain_filter(sanitise_words(words)))

    with open('output.txt', 'a') as output_file:
        keys = list(big_dict.keys())
        keys.sort()
        for key in keys:
            for option in big_dict[key]:
                indexes = []
                for elem in option:
                    indexes.append(str(elements.index(elem) + 1))
                output_file.write(f'{key} - {",".join(option)} - {" ".join(indexes)}\n')
