# project_folder/rules.py

from collections import defaultdict

RANK_ORDER = {'2': 2, '3': 3, '4':4, '5':5, '6':6, '7':7, '8':8,
              '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}

def evaluate_hand(hand):
    ranks = sorted([RANK_ORDER[card[0]] for card in hand], reverse=True)
    suits = [card[1] for card in hand]
    rank_counts = defaultdict(int)
    for rank in ranks:
        rank_counts[rank] += 1
    counts = sorted(rank_counts.values(), reverse=True)
    unique_ranks = sorted(rank_counts.keys(), reverse=True)

    is_flush = len(set(suits)) == 1
    is_straight = False
    if len(unique_ranks) >= 5:
        for i in range(len(unique_ranks) - 4):
            window = unique_ranks[i:i+5]
            if window[0] - window[4] == 4:
                is_straight = True
                high_card = window[0]
                break
    # Special case: Ace to Five straight
    if not is_straight and set([14, 2, 3, 4, 5]).issubset(set(ranks)):
        is_straight = True
        high_card = 5

    if is_straight and is_flush:
        return (8, high_card)  # Straight Flush
    elif counts[0] == 4:
        four_kind = unique_ranks[counts.index(4)]
        kicker = max([rank for rank in ranks if rank != four_kind])
        return (7, four_kind, kicker)  # Four of a Kind
    elif counts[0] == 3 and counts[1] >= 2:
        three_kind = unique_ranks[counts.index(3)]
        pair = unique_ranks[counts.index(2)]
        return (6, three_kind, pair)  # Full House
    elif is_flush:
        return (5, ranks[:5])  # Flush
    elif is_straight:
        return (4, high_card)  # Straight
    elif counts[0] == 3:
        three_kind = unique_ranks[counts.index(3)]
        kickers = sorted([rank for rank in ranks if rank != three_kind], reverse=True)[:2]
        return (3, three_kind, kickers)  # Three of a Kind
    elif counts[0] == 2 and counts[1] == 2:
        high_pair = unique_ranks[counts.index(2)]
        low_pair = unique_ranks[counts.index(2, counts.index(2)+1)]
        kicker = max([rank for rank in ranks if rank != high_pair and rank != low_pair])
        return (2, high_pair, low_pair, kicker)  # Two Pair
    elif counts[0] == 2:
        pair = unique_ranks[counts.index(2)]
        kickers = sorted([rank for rank in ranks if rank != pair], reverse=True)[:3]
        return (1, pair, kickers)  # One Pair
    else:
        return (0, ranks[:5])  # High Card

def compare_hands(hand1, hand2):
    eval1 = evaluate_hand(hand1)
    eval2 = evaluate_hand(hand2)
    if eval1 > eval2:
        return 1
    elif eval1 < eval2:
        return -1
    else:
        return 0

def hand_rank_description(rank_tuple):
    descriptions = {
        8: "Straight Flush",
        7: "Four of a Kind",
        6: "Full House",
        5: "Flush",
        4: "Straight",
        3: "Three of a Kind",
        2: "Two Pair",
        1: "One Pair",
        0: "High Card"
    }
    return descriptions.get(rank_tuple[0], "Unknown")
