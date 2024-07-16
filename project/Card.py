from Poker import Suit, Number
from PIL import Image
import os

class Card:
    def __init__(self, suit, number):
        if not isinstance(suit, Suit) or not isinstance(number, Number):
            raise TypeError("suit must be an instance of Suit and number must be an instance of Number")
        self.suit = suit
        self.number = number

    def get_suit(self):
        return self.suit  

    def get_number(self):
        return self.number  

    def __str__(self):
        return f"{self.number.rank} of {self.suit.value}"

    def __repr__(self):
        return self.__str__()

    def get_card_image(self, size=(40, 60)):
        image_name = f"{self.number.rank.lower()}_of_{self.suit.value.lower()}.png"
        image_path = os.path.join(os.path.dirname(__file__), "Card_image", image_name)
        if os.path.exists(image_path):
            image = Image.open(image_path)
            image = image.resize(size, Image.LANCZOS)
            return image
        else:
            raise FileNotFoundError(f"Image file not found: {image_path}")
