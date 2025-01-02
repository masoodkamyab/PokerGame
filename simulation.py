import random


def simulate_win_probability(hero_cards, community_cards, deck,
                             num_opponents=7, n_simulations=10000):
    """
    Returns the approximate probability of 'hero_cards' winning against
    `num_opponents` in a Monte Carlo simulation, given partial community cards.

    :param hero_cards: list of exactly 2 card strings (e.g. ['As', 'Kd'])
    :param community_cards: list of already-known community cards (0 to 5)
    :param deck: full 52-card deck (or leftover deck) as a list
    :param num_opponents: how many opponents (7 for an 8-player total)
    :param n_simulations: how many random deals to run
    :return: float in [0, 1] for estimated win probability
    """
    import copy
    from rules import evaluate_hand, compare_hands  # Adjust if needed

    # Known cards = hero + known community
    known_cards = set(hero_cards + community_cards)

    # The "available" deck for simulation is everything in `deck`
    # that isn't in known_cards
    available_deck = [card for card in deck if card not in known_cards]

    hero_win_count = 0

    for _ in range(n_simulations):
        # Shuffle the available deck for random dealing
        random.shuffle(available_deck)

        # 1) Deal 2 cards to each opponent
        opponents_hands = []
        idx = 0
        for _ in range(num_opponents):
            opponents_hands.append([available_deck[idx], available_deck[idx + 1]])
            idx += 2

        # 2) Figure out how many community cards still need to be dealt
        cards_needed = 5 - len(community_cards)  # 0..5
        # if the board is already fully known (river), cards_needed=0
        board = community_cards + available_deck[idx: idx + cards_needed]
        idx += cards_needed

        # Evaluate hero’s best 5-card combination
        hero_hand_value = evaluate_hand(hero_cards + board)

        # Evaluate each opponent
        hero_best = True
        for opp in opponents_hands:
            opp_hand_value = evaluate_hand(opp + board)
            # compare_hands(...) can return 1 for hero win, -1 for opp win, 0 tie
            result = compare_hands(hero_cards + board, opp + board)
            if result == -1:
                # Opponent has a strictly better hand; hero loses
                hero_best = False
                break
            elif result == 0:
                # A tie occurs – some like to treat this as partial credit,
                # but commonly we'll consider it "not a hero win".
                hero_best = False
                break

        if hero_best:
            hero_win_count += 1

    return hero_win_count / n_simulations
