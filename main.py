import sys, os, random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QDialog, QFormLayout, QSpinBox, QComboBox, QScrollArea,
    QGridLayout, QCheckBox
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
from treys import Evaluator, Deck, Card
from cards import Player, Flop
from helpers import card_to_image_path, get_all_card_strings
from probability import calculate_win_probability

# --- CardImageSelectionDialog with improved selection UI ---
class CardImageSelectionDialog(QDialog):
    def __init__(self, title, prompt, num_cards, available_cards, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.num_cards = num_cards
        self.available_cards = self.sort_cards_by_suit(available_cards)
        self.selected_cards = []
        self.init_ui(prompt)

    def sort_cards_by_suit(self, cards):
        suit_order = {'h': 0, 'd': 1, 'c': 2, 's': 3}
        rank_order = {r: i for i, r in enumerate("23456789TJQKA", start=2)}
        return sorted(cards, key=lambda x: (suit_order.get(x[-1], 99), rank_order.get(x[0], 99)))

    def init_ui(self, prompt):
        main_layout = QVBoxLayout()
        prompt_lbl = QLabel(prompt)
        main_layout.addWidget(prompt_lbl)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.grid = QGridLayout()
        container.setLayout(self.grid)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.buttons = {}
        col = 0
        row = 0
        for card in self.available_cards:
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setFixedSize(40, 60)
            btn.setIcon(QIcon(os.path.join("graphics", "cards", f"{card}.png")))
            btn.setIconSize(btn.size())
            # Set stylesheet to show a yellow border when checked
            btn.setStyleSheet("""
                QPushButton { border: 2px solid transparent; }
                QPushButton:checked { border: 400px solid lightblue; }
            """)
            btn.clicked.connect(self.update_selection)
            self.buttons[card] = btn
            self.grid.addWidget(btn, row, col)
            col += 1
            if col >= 13:
                col = 0
                row += 1
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("Select")
        self.select_btn.clicked.connect(self.accept_selection)
        self.select_btn.setEnabled(False)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def update_selection(self):
        self.selected_cards = [card for card, btn in self.buttons.items() if btn.isChecked()]
        self.select_btn.setEnabled(len(self.selected_cards) == self.num_cards)

    def accept_selection(self):
        if len(self.selected_cards) != self.num_cards:
            QMessageBox.warning(self, "Selection Error", f"Select exactly {self.num_cards} card(s).")
            return
        self.accept()

    def get_selected_cards(self):
        return self.selected_cards

# --- End CardImageSelectionDialog ---

class StartupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Setup")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        self.numPlayersSpin = QSpinBox()
        self.numPlayersSpin.setMinimum(2)
        self.numPlayersSpin.setMaximum(10)
        self.numPlayersSpin.setValue(8)
        layout.addRow("Number of Players:", self.numPlayersSpin)
        self.cardModeCombo = QComboBox()
        self.cardModeCombo.addItems(["Random", "Manual"])
        layout.addRow("Card Mode:", self.cardModeCombo)
        self.startButton = QPushButton("Start Game")
        self.startButton.clicked.connect(self.accept)
        layout.addRow(self.startButton)
        self.setLayout(layout)

    def getValues(self):
        num_players = self.numPlayersSpin.value()
        manual = (self.cardModeCombo.currentText() == "Manual")
        return num_players, manual

class PokerUI(QWidget):
    def __init__(self, num_players=8, manual_mode=False):
        super().__init__()
        self.num_players = num_players
        self.manual_mode = manual_mode
        self.current_step = 0  # 0: hero, 1: flop, 2: turn, 3: river
        self.used_cards = set()  # track already selected card strings
        self.setWindowTitle("Poker Win Probability Calculator")
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet("background-color: #35654d")
        self.deck = Deck()
        self.evaluator = Evaluator()
        self.num_opponents = self.num_players - 1
        self.players = [Player() for _ in range(self.num_players)]
        self.flop = Flop()
        self.turn = []
        self.river = []
        self.init_ui()
        self.update_available_cards_display()
        if self.manual_mode:
            self.setup_manual_mode()
        else:
            self.deal_initial()

    def init_ui(self):
        main_layout = QVBoxLayout()
        # Top bar with Change Setup button
        top_layout = QHBoxLayout()
        self.config_label = QLabel(f"Players: {self.num_players} | Mode: {'Manual' if self.manual_mode else 'Random'}")
        self.config_label.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")
        top_layout.addWidget(self.config_label)
        self.change_setup_btn = QPushButton("Change Setup")
        self.change_setup_btn.setStyleSheet("background-color: #8c001a; color: white;")
        self.change_setup_btn.clicked.connect(self.change_setup)
        top_layout.addWidget(self.change_setup_btn)
        main_layout.addLayout(top_layout)
        # Hero Hand display
        hero_layout = QHBoxLayout()
        hero_label = QLabel("Hero Hand:")
        hero_label.setStyleSheet("font-weight: bold; font-size: 20px; color: white;")
        hero_layout.addWidget(hero_label)
        self.hero_card_labels = [QLabel(), QLabel()]
        for label in self.hero_card_labels:
            label.setFixedSize(100, 145)
            label.setScaledContents(True)
            hero_layout.addWidget(label)
        main_layout.addLayout(hero_layout)
        # Community Cards display
        community_layout = QHBoxLayout()
        community_label = QLabel("Community Cards:")
        community_label.setStyleSheet("font-weight: bold; font-size: 20px; color: white;")
        community_layout.addWidget(community_label)
        self.community_card_labels = []
        for _ in range(5):
            label = QLabel()
            label.setFixedSize(100, 145)
            label.setScaledContents(True)
            label.setStyleSheet("border: 1px solid black;")
            placeholder = QPixmap("graphics/cards/back.png")
            if placeholder.isNull():
                label.setStyleSheet("border: 1px solid black; background-color: gray;")
            else:
                label.setPixmap(placeholder)
            self.community_card_labels.append(label)
            community_layout.addWidget(label)
        main_layout.addLayout(community_layout)
        # Opponents folded control (as checkboxes)
        fold_layout = QHBoxLayout()
        fold_label = QLabel("Folded Opponents:")
        fold_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        fold_layout.addWidget(fold_label)
        self.fold_checkboxes = []
        # Create a checkbox for each opponent (players 2..num_players)
        for i in range(2, self.num_players+1):
            cb = QCheckBox(f"Player {i}")
            cb.setStyleSheet("color: white;")
            cb.stateChanged.connect(self.calculate_and_display_probabilities)
            self.fold_checkboxes.append(cb)
            fold_layout.addWidget(cb)
        main_layout.addLayout(fold_layout)
        # Probabilities display
        prob_layout = QVBoxLayout()
        self.preflop_label = QLabel("Pre-Flop Win Probability: N/A")
        self.preflop_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        self.postflop_label = QLabel("Post-Flop Win Probability: N/A")
        self.postflop_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        self.after_turn_label = QLabel("After Turn Win Probability: N/A")
        self.after_turn_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        self.after_river_label = QLabel("After River Win Probability: N/A")
        self.after_river_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        prob_layout.addWidget(self.preflop_label)
        prob_layout.addWidget(self.postflop_label)
        prob_layout.addWidget(self.after_turn_label)
        prob_layout.addWidget(self.after_river_label)
        main_layout.addLayout(prob_layout)
        # Buttons layout for random mode
        self.button_layout = QHBoxLayout()
        self.deal_flop_btn = QPushButton("Deal Flop")
        self.deal_flop_btn.setStyleSheet("background-color: #005f64")
        self.deal_flop_btn.clicked.connect(self.deal_flop)
        self.deal_turn_btn = QPushButton("Deal Turn")
        self.deal_turn_btn.setStyleSheet("background-color: #005f64")
        self.deal_turn_btn.clicked.connect(self.deal_turn)
        self.deal_river_btn = QPushButton("Deal River")
        self.deal_river_btn.setStyleSheet("background-color: #005f64")
        self.deal_river_btn.clicked.connect(self.deal_river)
        self.reset_btn = QPushButton("Reset Game")
        self.reset_btn.setStyleSheet("background-color: #5a0a21")
        self.reset_btn.clicked.connect(self.reset_game)
        self.button_layout.addWidget(self.deal_flop_btn)
        self.button_layout.addWidget(self.deal_turn_btn)
        self.button_layout.addWidget(self.deal_river_btn)
        self.button_layout.addWidget(self.reset_btn)
        main_layout.addLayout(self.button_layout)
        # Next Step button for manual mode
        self.next_step_btn = QPushButton("Next Step")
        self.next_step_btn.setStyleSheet("background-color: #007f3f")
        self.next_step_btn.clicked.connect(self.manual_next_step)
        self.next_step_btn.hide()
        main_layout.addWidget(self.next_step_btn)
        # Available Cards widget (visible in both modes)
        self.available_cards_area = QScrollArea()
        self.available_cards_area.setWidgetResizable(True)
        self.available_cards_widget = QWidget()
        self.available_cards_layout = QGridLayout()
        self.available_cards_widget.setLayout(self.available_cards_layout)
        self.available_cards_area.setWidget(self.available_cards_widget)
        main_layout.addWidget(QLabel("Available Cards:"))
        main_layout.addWidget(self.available_cards_area)
        self.setLayout(main_layout)

    def change_setup(self):
        dlg = StartupDialog()
        if dlg.exec_() == QDialog.Accepted:
            num_players, manual_mode = dlg.getValues()
            self.num_players = num_players
            self.manual_mode = manual_mode
            self.num_opponents = self.num_players - 1
            self.config_label.setText(f"Players: {self.num_players} | Mode: {'Manual' if self.manual_mode else 'Random'}")
            # Rebuild opponent fold checkboxes
            for cb in self.fold_checkboxes:
                cb.setParent(None)
            self.fold_checkboxes = []
            for i in range(2, self.num_players+1):
                cb = QCheckBox(f"Player {i}")
                cb.setStyleSheet("color: white;")
                cb.stateChanged.connect(self.calculate_and_display_probabilities)
                self.fold_checkboxes.append(cb)
            self.reset_game()

    def update_available_cards_display(self):
        for i in reversed(range(self.available_cards_layout.count())):
            widget = self.available_cards_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        if self.manual_mode:
            all_cards = get_all_card_strings()
            available = [card for card in all_cards if card not in self.used_cards]
        else:
            available = [Card.int_to_pretty_str(c).strip("[]") for c in self.deck.cards]
        suit_order = {'h': 0, 'd': 1, 'c': 2, 's': 3}
        rank_order = {r: i for i, r in enumerate("23456789TJQKA", start=2)}
        available = sorted(available, key=lambda x: (suit_order.get(x[-1], 99), rank_order.get(x[0], 99)))
        col = 0
        row = 0
        for card_str in available:
            lbl = QLabel()
            lbl.setFixedSize(40, 60)
            lbl.setScaledContents(True)
            pixmap = QPixmap(os.path.join("graphics", "cards", f"{card_str}.png"))
            if pixmap.isNull():
                pixmap = QPixmap("graphics/cards/back.png")
            lbl.setPixmap(pixmap)
            self.available_cards_layout.addWidget(lbl, row, col)
            col += 1
            if col >= 13:
                col = 0
                row += 1

    def setup_manual_mode(self):
        self.deal_flop_btn.hide()
        self.deal_turn_btn.hide()
        self.deal_river_btn.hide()
        self.next_step_btn.show()
        self.used_cards = set()
        self.current_step = 0
        self.manual_next_step()
        self.update_available_cards_display()

    def manual_next_step(self):
        all_cards = get_all_card_strings()
        available = [card for card in all_cards if card not in self.used_cards]
        if self.current_step == 0:
            dlg = CardImageSelectionDialog("Select Hero Hand", "Select 2 cards for Hero Hand:", 2, available, self)
            if dlg.exec_() == QDialog.Accepted:
                selected = dlg.get_selected_cards()
                try:
                    hero_cards = [Card.new(card) for card in selected]
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Card conversion error: {str(e)}")
                    return
                self.players[0].cards = hero_cards
                self.used_cards.update(selected)
                self.update_card_labels(self.hero_card_labels, hero_cards)
                effective_opponents = self.num_opponents - self.fold_count()
                prob = calculate_win_probability(hero_cards, [], effective_opponents, self.evaluator, num_simulations=10000)
                self.preflop_label.setText(f"Pre-Flop Win Probability: {prob:.4f}")
                self.current_step = 1
                self.update_available_cards_display()
        elif self.current_step == 1:
            dlg = CardImageSelectionDialog("Select Flop Cards", "Select 3 cards for the Flop:", 3, available, self)
            if dlg.exec_() == QDialog.Accepted:
                selected = dlg.get_selected_cards()
                try:
                    flop_cards = [Card.new(card) for card in selected]
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Card conversion error: {str(e)}")
                    return
                self.flop.cards = flop_cards
                self.used_cards.update(selected)
                self.update_card_labels(self.community_card_labels, flop_cards, start=0)
                hero_cards = self.players[0].cards
                effective_opponents = self.num_opponents - self.fold_count()
                prob = calculate_win_probability(hero_cards, flop_cards, effective_opponents, self.evaluator, num_simulations=10000)
                self.postflop_label.setText(f"Post-Flop Win Probability: {prob:.4f}")
                self.current_step = 2
                self.update_available_cards_display()
        elif self.current_step == 2:
            dlg = CardImageSelectionDialog("Select Turn Card", "Select 1 card for the Turn:", 1, available, self)
            if dlg.exec_() == QDialog.Accepted:
                selected = dlg.get_selected_cards()
                try:
                    turn_card = Card.new(selected[0])
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Card conversion error: {str(e)}")
                    return
                self.turn = [turn_card]
                self.used_cards.update(selected)
                self.update_card_labels(self.community_card_labels, self.turn, start=3)
                hero_cards = self.players[0].cards
                community = self.flop.cards + self.turn
                effective_opponents = self.num_opponents - self.fold_count()
                prob = calculate_win_probability(hero_cards, community, effective_opponents, self.evaluator, num_simulations=10000)
                self.after_turn_label.setText(f"After Turn Win Probability: {prob:.4f}")
                self.current_step = 3
                self.update_available_cards_display()
        elif self.current_step == 3:
            dlg = CardImageSelectionDialog("Select River Card", "Select 1 card for the River:", 1, available, self)
            if dlg.exec_() == QDialog.Accepted:
                selected = dlg.get_selected_cards()
                try:
                    river_card = Card.new(selected[0])
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Card conversion error: {str(e)}")
                    return
                self.river = [river_card]
                self.used_cards.update(selected)
                self.update_card_labels(self.community_card_labels, self.river, start=4)
                hero_cards = self.players[0].cards
                community = self.flop.cards + self.turn + self.river
                effective_opponents = self.num_opponents - self.fold_count()
                prob = calculate_win_probability(hero_cards, community, effective_opponents, self.evaluator, num_simulations=10000)
                self.after_river_label.setText(f"After River Win Probability: {prob:.4f}")
                self.current_step = 4
                self.next_step_btn.setEnabled(False)
                QMessageBox.information(self, "Manual Mode Complete", "Manual input complete.")
                self.update_available_cards_display()

    def fold_count(self):
        return sum(1 for cb in self.fold_checkboxes if cb.isChecked())

    # --- Random mode functions ---
    def deal_initial(self):
        hero = self.players[0]
        hero.cards = self.deck.draw(2)
        self.update_card_labels(self.hero_card_labels, hero.cards)
        self.calculate_and_display_probabilities()
        self.update_available_cards_display()

    def deal_flop(self):
        if self.flop.cards:
            QMessageBox.warning(self, "Warning", "Flop already dealt!")
            return
        self.flop.generate_flop(self.deck)
        self.update_card_labels(self.community_card_labels, self.flop.cards, start=0)
        self.calculate_and_display_probabilities()
        self.update_available_cards_display()

    def deal_turn(self):
        if not self.flop.cards:
            QMessageBox.warning(self, "Warning", "Deal the flop first!")
            return
        if self.turn:
            QMessageBox.warning(self, "Warning", "Turn already dealt!")
            return
        self.turn = self.deck.draw(1)
        self.update_card_labels(self.community_card_labels, self.turn, start=3)
        self.calculate_and_display_probabilities()
        self.update_available_cards_display()

    def deal_river(self):
        if not self.turn:
            QMessageBox.warning(self, "Warning", "Deal the turn first!")
            return
        if self.river:
            QMessageBox.warning(self, "Warning", "River already dealt!")
            return
        self.river = self.deck.draw(1)
        self.update_card_labels(self.community_card_labels, self.river, start=4)
        self.calculate_and_display_probabilities()
        self.update_available_cards_display()
    # --- End Random mode functions ---

    def reset_game(self):
        self.deck = Deck()
        self.evaluator = Evaluator()
        self.players = [Player() for _ in range(self.num_players)]
        self.flop = Flop()
        self.turn = []
        self.river = []
        self.current_step = 0
        self.used_cards = set()
        for cb in self.fold_checkboxes:
            cb.setChecked(False)
        self.clear_card_labels()
        if self.manual_mode:
            self.next_step_btn.setEnabled(True)
            self.manual_next_step()
        else:
            self.deal_initial()
        self.update_available_cards_display()

    def update_card_labels(self, labels, cards, start=0):
        for i, card in enumerate(cards):
            if start + i < len(labels):
                pixmap = QPixmap(card_to_image_path(card))
                if pixmap.isNull():
                    pixmap = QPixmap("graphics/cards/back.png")
                labels[start + i].setPixmap(pixmap)

    def clear_card_labels(self):
        for label in self.hero_card_labels:
            label.clear()
        for label in self.community_card_labels:
            placeholder = QPixmap("graphics/cards/back.png")
            label.setPixmap(placeholder)

    def calculate_and_display_probabilities(self):
        hero = self.players[0]
        hero_cards = hero.cards
        community_cards = self.flop.cards + self.turn + self.river
        effective_opponents = self.num_opponents - self.fold_count()
        if effective_opponents < 0:
            effective_opponents = 0
        if not self.flop.cards and not self.turn and not self.river:
            preflop_prob = calculate_win_probability(hero_cards, [], effective_opponents, self.evaluator, num_simulations=10000)
            self.preflop_label.setText(f"Pre-Flop Win Probability: {preflop_prob:.4f}")
            self.postflop_label.setText("Post-Flop Win Probability: N/A")
            self.after_turn_label.setText("After Turn Win Probability: N/A")
            self.after_river_label.setText("After River Win Probability: N/A")
            return
        if len(self.flop.cards) >= 3 and not self.turn and not self.river:
            postflop_prob = calculate_win_probability(hero_cards, self.flop.cards, effective_opponents, self.evaluator, num_simulations=10000)
            self.postflop_label.setText(f"Post-Flop Win Probability: {postflop_prob:.4f}")
            self.after_turn_label.setText("After Turn Win Probability: N/A")
            self.after_river_label.setText("After River Win Probability: N/A")
            return
        if len(self.flop.cards) >= 3 and len(self.turn) == 1 and not self.river:
            community_after_turn = self.flop.cards + self.turn
            after_turn_prob = calculate_win_probability(hero_cards, community_after_turn, effective_opponents, self.evaluator, num_simulations=10000)
            self.after_turn_label.setText(f"After Turn Win Probability: {after_turn_prob:.4f}")
            self.after_river_label.setText("After River Win Probability: N/A")
            return
        if len(self.flop.cards) >= 3 and len(self.turn) == 1 and len(self.river) == 1:
            community_full = self.flop.cards + self.turn + self.river
            after_river_prob = calculate_win_probability(hero_cards, community_full, effective_opponents, self.evaluator, num_simulations=10000)
            self.after_river_label.setText(f"After River Win Probability: {after_river_prob:.4f}")
            return

class PokerApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        startup = StartupDialog()
        if startup.exec_() == QDialog.Accepted:
            num_players, manual_mode = startup.getValues()
            self.window = PokerUI(num_players=num_players, manual_mode=manual_mode)
            self.window.show()
            sys.exit(self.app.exec_())

if __name__ == "__main__":
    PokerApp()
