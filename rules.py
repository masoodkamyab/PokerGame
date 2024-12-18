from collections import Counter


def evaluate_hand(cards):
    """
    Evaluate the rank of a poker hand.

    :param cards: List of cards in hand (e.g., ['2♠', '3♠', '4♠', '5♠', '6♠']).
    :return: Tuple (rank, highest_card), where rank is a numeric value for the hand.
    """
    ranks = '23456789TJQKA'
    suits = [card[-1] for card in cards]
    values = sorted([ranks.index(card[0]) for card in cards], reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight = len(set(values)) == 5 and values[0] - values[-1] == 4
    counts = Counter(values).most_common()

    if is_straight and is_flush:
        return (9, values[0])  # Straight Flush
    elif counts[0][1] == 4:
        return (8, counts[0][0])  # Four of a Kind
    elif counts[0][1] == 3 and counts[1][1] == 2:
        return (7, counts[0][0])  # Full House
    elif is_flush:
        return (6, values)  # Flush
    elif is_straight:
        return (5, values[0])  # Straight
    elif counts[0][1] == 3:
        return (4, counts[0][0])  # Three of a Kind
    elif counts[0][1] == 2 and counts[1][1] == 2:
        return (3, (counts[0][0], counts[1][0]))  # Two Pair
    elif counts[0][1] == 2:
        return (2, counts[0][0])  # One Pair
    else:
        return (1, values)  # High Card


def compare_hands(hand1, hand2):
    """
    Compare two poker hands and determine the winner.

    :param hand1: List of cards in the first hand.
    :param hand2: List of cards in the second hand.
    :return: 1 if hand1 wins, -1 if hand2 wins, 0 if tie.
    """
    rank1, value1 = evaluate_hand(hand1)
    rank2, value2 = evaluate_hand(hand2)

    if rank1 > rank2:
        return 1
    elif rank1 < rank2:
        return -1
    else:  # Same rank, compare values
        if value1 > value2:
            return 1
        elif value1 < value2:
            return -1
        else:
            return 0


def hand_rank_description(rank):
    """
    Get the textual description of a hand rank.

    :param rank: Numeric rank of the hand.
    :return: String description of the rank.
    """
    descriptions = {
        9: "Straight Flush",
        8: "Four of a Kind",
        7: "Full House",
        6: "Flush",
        5: "Straight",
        4: "Three of a Kind",
        3: "Two Pair",
        2: "One Pair",
        1: "High Card",
    }
    return descriptions.get(rank, "Unknown")


