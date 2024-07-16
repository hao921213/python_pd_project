import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from PIL import Image, ImageTk
from Player import Player
from Gamelogic import GameLogic
import os

from face_recognition import initialize_db, recognize_faces, capture_faces, train_model, save_model_to_db, get_user_info, clear_data

class LoginApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")
        self.players_info = [] 
        self.create_widgets()
        initialize_db()  

    def create_widgets(self):
        self.label = ttk.Label(self.root, text="依序登入玩家1到玩家4", font=('Helvetica', 14))
        self.label.pack(pady=20)
        self.login_button = ttk.Button(self.root, text="開始人臉辨識", command=self.face_login)
        self.login_button.pack(pady=20)

    def face_login(self):
        if len(self.players_info) < 4:
            user_id = recognize_faces()
            if user_id:
                user_info = get_user_info(user_id)
                if user_info:
                    self.players_info.append(user_info)
                    messagebox.showinfo("Login Success", f"玩家{len(self.players_info)}登入成功：{user_info[0]}")
                    if len(self.players_info) == 4:
                        self.start_game()
                else:
                    messagebox.showerror("Error", "未存在此用戶")
            else:
                messagebox.showerror("Error", "未偵測到人臉")
        else:
            self.start_game()

    def start_game(self):
        self.root.destroy()
        app = MainApp(self.players_info)
        app.run()


class MainApp:
    def __init__(self, players_info):
        self.root = tk.Tk()
        self.root.title("Poker Game")
        self.game_logic = GameLogic(self)
        self.players_info = players_info 
        self.player_card_visible = [False] * len(self.players_info)  
        self.create_widgets()
        self.initialize_game() 

    def initialize_game(self):
        self.player_card_visible[0] = True
        self.update_player_display()
        self.update_bet_and_pot_display()

    def create_widgets(self):
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 12), padding=10)
        style.configure('TLabel', font=('Helvetica', 14))
        self.player_frames = []
        self.player_labels = []
        self.player_hands = []
        self.player_chips_labels = []

        positions = [('nw', 0, 0), ('ne', 0, 2), ('sw', 2, 0), ('se', 2, 2)]
        for i, (pos, player_info) in enumerate(zip(positions, self.players_info)):
            frame = ttk.Frame(self.root, relief='groove')
            frame.grid(row=pos[1], column=pos[2], padx=10, pady=10, sticky=pos[0])
            name, chips = player_info
            label = ttk.Label(frame, text=f"{name}")
            label.pack()
            hand_frame = ttk.Frame(frame)
            hand_frame.pack()
            chips_label = ttk.Label(frame, text=f"Chips: {chips}")
            chips_label.pack()
            self.player_frames.append(frame)
            self.player_labels.append(label)
            self.player_hands.append(hand_frame)
            self.player_chips_labels.append(chips_label)

        self.community_frame = ttk.Frame(self.root)
        self.community_frame.grid(row=0, column=1, padx=10, pady=10)
        self.community_label = ttk.Label(self.community_frame, text="Community Cards:")
        self.community_label.pack()
        self.community_cards_frame = ttk.Frame(self.community_frame)
        self.community_cards_frame.pack()

        self.bet_label = ttk.Label(self.root, text="Current Bet: 0")
        self.bet_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.pot_label = ttk.Label(self.root, text="Pot: 0")
        self.pot_label.grid(row=1, column=2, padx=10, pady=10, sticky='e')

        self.action_frame = ttk.Frame(self.root)
        self.action_frame.grid(row=3, column=1, padx=10, pady=10)
        self.check_button = ttk.Button(self.action_frame, text="Check", command=self.check)
        self.check_button.pack(side=tk.LEFT)
        self.call_button = ttk.Button(self.action_frame, text="Call", command=self.call)
        self.call_button.pack(side=tk.LEFT)
        self.raise_button = ttk.Button(self.action_frame, text="Raise", command=self.show_raise_dialog)
        self.raise_button.pack(side=tk.LEFT)
        self.fold_button = ttk.Button(self.action_frame, text="Fold", command=self.fold)
        self.fold_button.pack(side=tk.LEFT)
        self.all_in_button = ttk.Button(self.action_frame, text="All-in", command=self.all_in)
        self.all_in_button.pack(side=tk.LEFT)
        self.next_button = ttk.Button(self.root, text="Next Player", command=self.next_player)
        self.next_button.grid(row=4, column=1, padx=10, pady=10)

        self.current_player_label = ttk.Label(self.root, text="輪到: 玩家", font=('Helvetica', 14))
        self.current_player_label.grid(row=1, column=1, padx=10, pady=10)

    def show_raise_dialog(self):
        raise_window = tk.Toplevel(self.root)
        raise_window.title("Select Raise Amount")
        raise_window.geometry("300x100")
        raise_slider = ttk.Scale(raise_window, from_=0, to=10000, orient='horizontal')
        raise_slider.pack(pady=20)
        confirm_button = ttk.Button(raise_window, text="Confirm Raise", command=lambda: self.confirm_raise(raise_slider, raise_window))
        confirm_button.pack()

    def add_community_card(self, card):
        img = ImageTk.PhotoImage(card.get_card_image().resize((100, 150)))
        lbl = tk.Label(self.community_cards_frame, image=img)
        lbl.image = img 
        lbl.pack(side=tk.LEFT)

    def reset_community_cards(self):
        for widget in self.community_cards_frame.winfo_children():
            widget.destroy()

    def get_community_cards_text(self):
        return " ".join([str(card) for card in self.game_logic.community_cards])

    def display_winner(self, winner):
        if winner:
            self.update_chips(winner)
            messagebox.showinfo("Game Over", f"The winner is {winner.get_name()} with {winner.get_chips()} chips.")
        else:
            messagebox.showinfo("Game Over", "It's a tie!")
        self.update_all_players_chips()  

    def update_chips(self, winner):
        conn = sqlite3.connect('poker_game.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE PlayerInfo SET chips = ? WHERE name = ?", (winner.get_chips(), winner.get_name()))
        conn.commit()
        conn.close()
        self.update_chips_display()

    def update_all_players_chips(self):
        conn = sqlite3.connect('poker_game.db')
        cursor = conn.cursor()
        for i, player in enumerate(self.game_logic.players):
            cursor.execute("UPDATE PlayerInfo SET chips = ? WHERE name = ?", (player.get_chips(), player.get_name()))
        conn.commit()
        conn.close()

    def update_chips_display(self):
        for i, (chips_label, player_info) in enumerate(zip(self.player_chips_labels, self.players_info)):
            chips_label.config(text=f"Chips: {self.game_logic.players[i].get_chips()}")

    def update_player_display(self):
        for i, (player_info, hand_frame, label) in enumerate(zip(self.players_info, self.player_hands, self.player_labels)):
            label.config(text=player_info[0]) 
            visible = self.player_card_visible[i]
            self.update_hand_display(hand_frame, self.game_logic.players[i].get_hand(), visible)
        self.update_chips_display()

    def update_hand_display(self, hand_frame, hand, visible):
        for widget in hand_frame.winfo_children():
            widget.destroy()

        cover_image_path = os.path.join(os.getcwd(), "cover_image.png")  

        if visible:
            for card in hand:
                img = ImageTk.PhotoImage(card.get_card_image().resize((100, 150)))
                lbl =tk.Label(hand_frame, image=img)
                lbl.image = img  
                lbl.pack(side=tk.LEFT)
        else:
            if os.path.exists("d:\python\project\cover_image.png"):  
                cover_img = Image.open("d:\python\project\cover_image.png").resize((100, 150))
                img = ImageTk.PhotoImage(cover_img)
                for _ in hand:
                    lbl = tk.Label(hand_frame, image=img)
                    lbl.image = img 
                    lbl.pack(side=tk.LEFT)
            else:
                print(f"Cover image not found at {cover_image_path}")  

    def check(self):
        self.game_logic.check()
        self.update_after_action()

    def call(self):
        self.game_logic.call()
        self.update_after_action()

    def raise_bet(self):
        self.show_raise_dialog()

    def confirm_raise(self, slider, window):
        raise_amount = int(slider.get())
        self.game_logic.raise_bet(raise_amount)
        self.update_after_action()
        window.destroy()

    def fold(self):
        self.game_logic.fold()
        self.update_after_action()

    def all_in(self):
        self.game_logic.all_in()
        self.update_after_action()

    def update_after_action(self):
        current_player_index = self.game_logic.current_player_index
        current_player_name = self.players_info[current_player_index][0]
        self.current_player_label.config(text=f"当前轮到: {current_player_name}")
        self.player_card_visible[current_player_index] = False
        self.update_player_display()
        self.update_bet_and_pot_display()

    def next_player(self):
        self.game_logic.move_to_next_player()
        current_player_index = self.game_logic.current_player_index
        self.player_card_visible = [False] * len(self.player_card_visible)  
        self.player_card_visible[current_player_index] = True  
        self.update_player_display()
        self.update_bet_and_pot_display()

    def reveal_all_hands(self):
        self.player_card_visible = [True] * len(self.player_card_visible)
        self.update_player_display()
        
    def update_bet_and_pot_display(self):
        self.bet_label.config(text=f"Current Bet: {self.game_logic.current_bet}")
        self.pot_label.config(text=f"Pot: {self.game_logic.pot}")

    def run(self):
        self.update_player_display()
        self.root.mainloop()

    def quit_game(self):
        self.root.quit()

    def start_new_round(self):
        self.game_logic.prepare_for_next_game()
        self.player_card_visible = [False] * len(self.player_card_visible)  
        self.update_player_display()


if __name__ == "__main__":
    if not os.path.exists('trainer'):
        os.makedirs('trainer')
    if not os.path.exists('face_data'):
        os.makedirs('face_data')
    login_app = LoginApp()
    login_app.root.mainloop()
