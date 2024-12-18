# Poker Game Simulator

This repository contains a Python-based poker game simulation designed to evaluate poker hands, compare them, and simulate basic game functionality. It consists of modular code divided into files for card management, poker rules, and the main game logic. The project is beginner-friendly and serves as a foundation for building a complete poker game.

## Features

- Full deck simulation with 52 standard playing cards.
- Randomized card drawing for players and the flop.
- Hand evaluation based on standard poker rules.
- Comparison of poker hands to determine the winner.
- Modular code structure for easy expansion.
- **Probability calculation** for estimating the chance of winning in any game state.

---

## Installation

### Prerequisites

- Python 3.8 or higher
- `pygame` library for card animations and graphics (optional)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/poker-game-simulator.git
   cd poker-game-simulator
   ```

2. Install dependencies:
   ```bash
   pip install pygame
   ```

---

## Files and Structure

### **1. card_manager.py**
- Manages the deck, card drawing, and player hands.
- Key Classes and Functions:
  - `draw_random_cards(num_cards)`: Draws random cards from the deck.
  - `Card`: Represents a single card with attributes for rank and suit.
  - `Player`: Represents a player and their drawn cards.
  - `Flop`: Simulates the three flop cards drawn during the game.

### **2. poker_rules.py**
- Implements hand evaluation logic and rules for poker.
- Key Functions:
  - `evaluate_hand(cards)`: Determines the rank of a poker hand.
  - `compare_hands(hand1, hand2)`: Compares two hands to determine the winner.
  - `hand_rank_description(rank)`: Returns a textual description of a hand rank.
  - `calculate_probability(state)`: Estimates the probability of winning for a given game state.

### **3. main.py**
- Entry point for the poker game simulation.
- Handles the game flow, including:
  - Initializing players.
  - Drawing cards for players and the flop.
  - Evaluating hands and declaring the winner.
  - Calculating and displaying the probability of winning.

---

## Usage

1. Run the main script to start the game simulation:
   ```bash
   python main.py
   ```

2. Example output:
   ```
   Player 1 Hand: ['8♠', 'K♥']
   Player 2 Hand: ['5♣', 'Q♦']
   Flop: ['3♦', '7♥', '9♠']
   Player 1 wins with High Card (King).
   Probability of Player 1 Winning: 62.5%
   ```

---

## How It Works

1. A deck of 52 cards is initialized.
2. Two players are dealt two random cards each.
3. Three flop cards are revealed.
4. Each player's hand is evaluated based on poker hand rankings.
5. The probability of winning for each player is calculated based on remaining cards and potential hands.
6. The winner is determined by comparing hand ranks.

---

## Future Improvements

- Add support for additional game stages (Turn and River).
- Implement betting mechanics and player actions (fold, call, raise).
- Create a graphical user interface (GUI) for a more interactive experience.
- Enhance hand evaluation logic to support multi-player games.
- Integrate advanced probability calculations for multi-player scenarios.

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes and push to your fork.
4. Submit a pull request with a description of your changes.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments

Special thanks to the contributors who helped build this project. For any questions or suggestions, feel free to open an issue or contact the repository owner.

