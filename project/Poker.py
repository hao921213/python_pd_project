from enum import Enum

class Suit(Enum):
    HEARTS = "Hearts"
    SPADES = "Spades"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"

class Number(Enum):
    ACE = ("Ace", 14)
    TWO = ("2", 2)
    THREE = ("3", 3)
    FOUR = ("4", 4)
    FIVE = ("5", 5)
    SIX = ("6", 6)
    SEVEN = ("7", 7)
    EIGHT = ("8", 8)
    NINE = ("9", 9)
    TEN = ("10", 10)
    JACK = ("Jack", 11)
    QUEEN = ("Queen", 12)
    KING = ("King", 13)

    def __init__(self, rank, value):
        self.rank = rank
        self._value_ = value 

    @property
    def value(self):
        return self._value_
