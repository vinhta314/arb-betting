import itertools
import json
import logging

from fractions import Fraction
from fuzzywuzzy import process
from exceptions import ExtractionError

NAMES_PATH = '../config/names.json'


def load_json(path):
    with open(path, 'r') as file:
        return json.load(file)


def flatten(iterable):
    return list(itertools.chain.from_iterable(iterable))


def match_name(name, possible_names):
    best_match, match_percentage = process.extractOne(name.lower(), possible_names)

    if match_percentage >= 90:
        return best_match
    else:
        return None


def get_possible_names(event_type, sub_event=None, draw=False):
    strict_names = load_json(NAMES_PATH)

    if sub_event is not None:
        possible_names = strict_names[event_type][sub_event]
    else:
        possible_names = flatten(strict_names[event_type].values())

    if draw:
        possible_names.append('draw')

    return possible_names


def clean_names(names, event_type, sub_event=None, draw=False):
    """
    Extracted names from bookmakers can vary, so these are always matched to an strict dictionary of names in the
    config. Where names do not closely match, it is replace by a None type which indicates that event should be
    discarded.
    """
    possible_names = get_possible_names(event_type, sub_event, draw)

    return [match_name(name, possible_names) for name in names]


def separate_name_str(name_str, separator_str) -> list:
    name_pair = name_str.split(separator_str)

    if len(name_pair) == 2:
        return name_pair
    else:
        raise ExtractionError('name_str was not split into two names as expected')


def separate_concatenated_names(concatenated_names: [str], separator_str) -> [str]:
    """
    Certain names are extracted from bookmakers as concatenated pairs e.g. '<name1> and <name2>'. These need to be
    split into individual names for a given extract of concatenated names.

    ['<name1> and <name2>', '<name3> and <name4>', '<name5> and <name6>']
    --> [<name1>, <name2>, <name3>, <name4>, <name5>, <name6>]

    """
    name_pairs = [separate_name_str(concatenated_name, separator_str) for concatenated_name in concatenated_names]

    return flatten(name_pairs)


def insert_draw_placeholders(names: [str]) -> [str]:
    """
    Some events allow for draw as an outcome. For this project, the outcome of draw can be treated as another
    participant, so 'draw' placeholder names must be added to the list of extracted names.

    [<name1>, <name2>, <name3>, <name4>, <name5>, <name6>]
    --> [<name1>, 'draw', <name2>, <name3>, 'draw', <name4>, <name5>, 'draw', <name6>]

    """
    if len(names) % 2 != 0:
        raise ExtractionError('Odd number of names in extracted names')

    stop = int((3/2) * len(names) + 1)
    names_copy = names.copy()

    for i in range(1, stop, 3):
        names_copy.insert(i, 'draw')

    return names_copy


def group_elements(lst, n):
    """
    Given a list, divide the list into tuples grouped by n.
    e.g. lst = [1, 2, 3, 4, 5, 6, 7, 8], n = 2 --> [(1, 2), (3, 4), (5, 6), (7, 8)]
    """
    if len(lst) % n != 0:
        raise ExtractionError('Extracted elements list not divisible by expected integer n')

    i = 0
    res = []

    while i < len(lst):
        res.append(tuple(lst[i + j] for j in range(n)))
        i += n

    return res


def collection_valid(name_col, odds_col):
    for name, odds in zip(name_col, odds_col):
        if name is None or not isinstance(odds, float):
            logging.info(f'Invalid collections identified for names: {name_col} or odds: {odds_col}')
            return False
    return True


def decimal_odds(odds: str):
    try:
        fractional_odds = float(Fraction(odds))

        return 1 + fractional_odds
    except ValueError:
        return odds
