import pygame
import random
import os


def draw_random_cards(num_cards):
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suits = ['♠', '♥', '♣', '♦']
    deck = [f'{rank}{suit}' for rank in ranks for suit in suits]

    if num_cards > len(deck):
        raise ValueError('Cannot draw more cards than are in the deck.')

    return random.sample(deck, num_cards)


class Card:
    def __init__(self, input_rank, input_suit):
        self.animation_start_time = pygame.time.get_ticks()
        self.animation_complete = False
        self.data = {"value": input_rank, "suit": input_suit}
        self.id = f"{self.data['value']}{self.data['suit']}"
        self.img = f"graphics/cards/{self.id}.png"

        if not os.path.exists(self.img):
            raise FileNotFoundError(f"Card image not found: {self.img}")

        self.card_rotation_angle = random.uniform(-3, 3)
        self.card_img = pygame.image.load(self.img)
        self.card_img = pygame.transform.scale(self.card_img,
                                               (self.card_img.get_width() * 4, self.card_img.get_height() * 4))
        self.card_rot = pygame.transform.rotate(self.card_img, self.card_rotation_angle)
        self.card_bounding_rect = self.card_rot.get_bounding_rect()
        self.card_surf = pygame.Surface(self.card_bounding_rect.size, pygame.SRCALPHA)


class Player:
    def __init__(self):
        self.cards = []

    def draw_cards(self, deck, num_cards=2):
        self.cards = draw_random_cards(num_cards)


class Flop:
    def __init__(self):
        self.cards = []

    def generate_flop(self, deck):
        self.cards = draw_random_cards(3)
