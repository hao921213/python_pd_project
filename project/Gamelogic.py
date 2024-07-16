from Deck import Deck
from Player import Player
from CardVS import CardVS
from Card import Card
from Poker import Suit, Number

class GameLogic:
    def __init__(self, main_app):
        self.main_app = main_app
        self.deck = Deck()
        self.players = [Player("Player 1", 10000), Player("Player 2", 10000),
                        Player("Player 3", 10000), Player("Player 4", 10000)]
        self.current_bet = 0
        self.current_player_index = 0
        self.community_cards = []
        self.round = 0  # 0: Pre-flop, 1: Flop, 2: Turn, 3: River
        self.winner = None
        self.winner_score = -1
        self.pot = 0
        self.initialize_game()
    #初始化遊戲
    def initialize_game(self):
        self.deck.shuffle()
        self.current_bet = 0
        self.current_player_index = 0
        self.community_cards = []
        self.round = 0
        self.deal_cards()
    #發牌
    def deal_cards(self):
        for player in self.players:
            player.reset_player()
            player.receive_card(self.deck.deal_card())
            player.receive_card(self.deck.deal_card())
    #每一輪間更新
    def reset_for_next_round(self):
        self.deck = Deck()  
        self.deck.shuffle()
        self.community_cards.clear()
        self.round = 0
        self.current_bet = 0
        self.pot = 0
        for player in self.players:
            player.reset_player()
        self.deal_cards()
    

  
    #更新pot
    def update_pot(self, amount):
        self.pot += amount
    #行動
    def fold(self):
        self.players[self.current_player_index].fold()

    def check(self):
        if self.current_bet == 0:
            print(f"{self.players[self.current_player_index].get_name()} checks")
            self.players[self.current_player_index].set_has_acted(True)
        else:
            print(f"Check not allowed, current bet is: {self.current_bet}")

    def call(self):
        current_player = self.get_current_player()
        amount_to_call = self.current_bet - current_player.get_current_bet()
        self.update_pot(amount_to_call)
        if current_player.get_chips() >= amount_to_call:
            current_player.update_bet(amount_to_call)
            current_player.set_has_acted(True)
        else:
            print(f"{current_player.get_name()} does not have enough chips to call.")

    def raise_bet(self, raise_amount):
        current_player = self.get_current_player()
        new_total_bet = self.current_bet + raise_amount
        amount_to_raise = new_total_bet - current_player.get_current_bet()
        self.update_pot(amount_to_raise)
        if current_player.get_chips() >= amount_to_raise:
            current_player.update_bet(amount_to_raise)
            self.current_bet = new_total_bet
            current_player.set_has_acted(True)
        else:
            print("Not enough chips to raise.")

    def all_in(self):
        current_player = self.get_current_player()
        all_in_amount = current_player.get_chips()
        if all_in_amount > self.current_bet:
            current_player.update_bet(all_in_amount - current_player.get_current_bet())
            self.current_bet = all_in_amount
        else:
            current_player.update_bet(all_in_amount)
        current_player.set_all_in()
        current_player.set_has_acted(True)
    #發公牌
    def deal_community_cards(self, number_of_cards):
        for _ in range(number_of_cards):
            card = self.deck.deal_card()
            self.community_cards.append(card)
            print(f"Community card dealt: {card}")
            self.main_app.add_community_card(card)

    def move_to_next_player(self):
        while True:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            if self.players[self.current_player_index].is_in_game:  
                break

        if self.is_betting_round_over():
            print("End of betting round")
            if self.has_all_in():
                self.deal_community_cards(5 - len(self.community_cards))
                self.round = 3
            else:
                self.proceed_to_next_stage()

    def has_all_in(self):
        return any(player.is_all_in for player in self.players)

    #每一回合移動
    def proceed_to_next_stage(self):
        if self.round == 0:  # Pre-flop
            self.round = 1
            self.deal_community_cards(3)  # 發三張flop牌
        elif self.round == 1:  # Flop
            self.round = 2
            self.deal_community_cards(1)  # 發turn牌
        elif self.round == 2:  # Turn
            self.round = 3
            self.deal_community_cards(1)  # 發river牌
        else:  # River
            self.determine_winner()
            self.round = 0  # 重置回合
            self.reset_for_next_round()  # 重置牌局
        self.current_bet = 0
        for player in self.players:
            player.clear_bet()
            player.set_has_acted(False)
        

    def determine_winner(self):
        card_vs = CardVS()
        self.winner = None
        self.winner_score = -1
        for player in self.players:
            if player.is_in_game:  
                score = card_vs.get_max_rank(player, self.community_cards)
                if self.winner is None or score > self.winner_score:
                    self.winner = player
                    self.winner_score = score
                elif score == self.winner_score:
                    result = card_vs.card_vs(self.winner, player, self.community_cards)
                    if result == 2:
                        self.winner = player

        if self.winner:
            print(f"{self.winner.get_name()} wins the game with a score of {self.winner_score}")
            self.main_app.display_winner(self.winner)
        else:
            print("It's a tie!")
            self.main_app.display_winner(None)
        self.reveal_all_hands()

        self.share_pot()
        self.check_end_game()

    def share_pot(self):
        if self.winner:
            self.winner.set_chips(self.winner.get_chips() + self.pot)
        else:
            in_game_players = [player for player in self.players if player.is_in_game]  # 使用属性访问语法
            split_pot = self.pot // len(in_game_players)
            for player in in_game_players:
                player.set_chips(player.get_chips() + split_pot)

    def is_betting_round_over(self):
        for player in self.players:
            if player.is_in_game and not player.has_acted:  
                return False
        for player in self.players:
            if player.is_in_game and player.get_current_bet() != self.current_bet and not player.is_all_in:
                return False
        return True

    def prepare_for_next_game(self):
        self.reset_for_next_round()
        self.main_app.reset_community_cards()

    def end_game(self):
        self.main_app.quit_game()

    def check_end_game(self):
        if self.is_end_game_condition_met():
            self.end_game()
        else:
            self.prepare_for_next_game()
            self.main_app.start_new_round()

    def is_end_game_condition_met(self):
        for player in self.players:
            if player.get_chips() <= 0:
                return True
        return False

    def get_current_player(self):
        return self.players[self.current_player_index]

    def get_current_bet(self):
        return self.current_bet

    def set_current_bet(self, new_bet):
        self.current_bet = new_bet

    def get_players(self):
        return self.players

    def get_current_player_index(self):
        return self.current_player_index

    def set_player_names_and_avatars(self, names, avatars):
        for i in range(len(self.players)):
            if i < len(names):
                self.players[i].set_name(names[i])
            if i < len(avatars):
                self.players[i].set_avatar(avatars[i])
    
    def reveal_all_hands(self):
        # 通知主界面更新顯示，讓所有玩家的手牌可見
        self.main_app.reveal_all_hands()