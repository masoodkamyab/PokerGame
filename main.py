import pygame
import random
from cards import Card, Player, Flop, draw_random_cards
from rules import evaluate_hand, compare_hands, hand_rank_description

# Initialize Pygame
pygame.init()

# Set up game screen
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Poker Game")

# Create players
player1 = Player()
player2 = Player()

# Draw cards for both players
deck = draw_random_cards(52)  # Full deck
player1.draw_cards(deck, num_cards=2)
player2.draw_cards(deck, num_cards=2)

# Create a flop
flop = Flop()
flop.generate_flop(deck)

# Print the player's hands and flop
print("Player 1 Hand:", player1.cards)
print("Player 2 Hand:", player2.cards)
print("Flop:", flop.cards)

# Evaluate the hands
player1_hand = player1.cards + flop.cards
player2_hand = player2.cards + flop.cards

player1_rank, player1_value = evaluate_hand(player1_hand)
player2_rank, player2_value = evaluate_hand(player2_hand)

# Compare the hands
result = compare_hands(player1_hand, player2_hand)

if result == 1:
    print(f"Player 1 wins with a {hand_rank_description(player1_rank)}!")
elif result == -1:
    print(f"Player 2 wins with a {hand_rank_description(player2_rank)}!")
else:
    print("It's a tie!")