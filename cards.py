# project_folder/cards.py

from treys import Deck

class Player:
    def __init__(self):
        self.cards = []

class Flop:
    def __init__(self):
        self.cards = []

    def generate_flop(self, deck):
        self.cards = deck.draw(3)
