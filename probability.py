# project_folder/probability.py

from treys import Evaluator, Deck
import random

def calculate_win_probability(hero_cards, community_cards, num_opponents, evaluator, num_simulations=10000):
    """
    Calculate win probability for the hero using Monte Carlo simulation.

    :param hero_cards: list of hero's hole cards (treys integers)
    :param community_cards: list of community cards (treys integers)
    :param num_opponents: number of opponents
    :param evaluator: treys Evaluator instance
    :param num_simulations: number of Monte Carlo simulations
    :return: win probability as float between 0 and 1
    """
    wins = 0
    ties = 0

    # Initialize deck and remove known cards
    full_deck = Deck()
    known_cards = set(hero_cards + community_cards)
    remaining_deck = [card for card in full_deck.cards if card not in known_cards]

    for _ in range(num_simulations):
        simulation_deck = remaining_deck.copy()
        random.shuffle(simulation_deck)

        # Deal opponents' hole cards
        opponents_hands = []
        try:
            for _ in range(num_opponents):
                opp_hand = [simulation_deck.pop(), simulation_deck.pop()]
                opponents_hands.append(opp_hand)
        except IndexError:
            break  # Not enough cards to continue

        # Deal remaining community cards
        remaining_community = 5 - len(community_cards)
        simulated_community = community_cards.copy()
        if remaining_community > 0:
            simulated_community += [simulation_deck.pop() for _ in range(remaining_community)]

        # Evaluate hero's hand
        hero_score = evaluator.evaluate(simulated_community, hero_cards)

        # Evaluate opponents' hands
        opponent_scores = [evaluator.evaluate(simulated_community, opp) for opp in opponents_hands]

        # Determine if hero wins
        if all(hero_score < opp_score for opp_score in opponent_scores):
            wins += 1
        elif any(hero_score == opp_score for opp_score in opponent_scores):
            ties += 1
        # else: hero loses, do nothing

    win_probability = (wins + ties / (num_opponents + 1)) / num_simulations
    return win_probability
