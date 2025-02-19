# project_folder/helpers.py

from treys import Card
import os

def pretty_print_cards(cards):
    """
    Convert treys card integers to readable strings.

    :param cards: list of treys card integers
    :return: list of strings
    """
    return [Card.int_to_pretty_str(card) for card in cards]

def card_to_image_path(card):
    """
    Convert treys card integer to image file path.

    :param card: treys card integer
    :return: string path to card image
    """
    card_str = Card.int_to_pretty_str(card).strip('[]')  # e.g., 'Ah'
    suit_map = {'♠': 's', '♥': 'h', '♦': 'd', '♣': 'c'}
    rank = card_str[0]
    suit_symbol = card_str[1]
    suit = suit_map.get(suit_symbol, 'x')  # 'x' for unknown suits
    image_name = f"{rank}{suit}.png"
    return os.path.join('graphics', 'cards', image_name)


def get_all_card_strings():
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suits = ['h', 'd', 'c', 's']
    return [r + s for r in ranks for s in suits]