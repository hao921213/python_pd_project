from PIL import Image

class Player:
    def __init__(self, name, initial_chips):
        self.name = name
        self.hand = []
        self._is_in_game = True  
        self._has_acted = False 
        self.current_bet = 0
        self.chips = initial_chips
        self.is_all_in = False
        self.avatar = None

    def receive_card(self, card):
        self.hand.append(card)
    
    def get_hand(self):
        return self.hand.copy()

    def fold(self):
        self._is_in_game = False
        self.hand.clear()

    def set_all_in(self):
        self.is_all_in = True

    def all_in(self):
        if self.chips > 0:
            self.current_bet += self.chips
            self.chips = 0
            self.is_all_in = True
            self._has_acted = True

    @property
    def is_in_game(self):
        return self._is_in_game  

    @property
    def has_acted(self):
        return self._has_acted

    def set_has_acted(self, has_acted):
        self._has_acted = has_acted

    def get_avatar(self):
        return self.avatar

    def set_avatar(self, avatar_path):
        self.avatar = Image.open(avatar_path)

    def get_current_bet(self):
        return self.current_bet

    def update_bet(self, amount):
        self.current_bet += amount
        self.adjust_chips(amount)

    def clear_bet(self):
        self.current_bet = 0

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def adjust_chips(self, amount):
        self.chips -= amount

    def get_chips(self):
        return self.chips

    def set_chips(self, value):
        self.chips = value

    def reset_player(self):
        self.hand.clear()
        self._is_in_game = True  
        self._has_acted = False 
        self.current_bet = 0
        self.is_all_in = False
