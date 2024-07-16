import random
from Card import Card
from Poker import Suit, Number

class Deck:
    def __init__(self):
        self.cards = []
        self.initialize_deck()

    def initialize_deck(self):
        for suit in Suit:
            for number in Number:
                self.cards.append(Card(suit, number))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        if self.cards:
            return self.cards.pop(0)  
        else:
            raise Exception("No cards left in the deck")

