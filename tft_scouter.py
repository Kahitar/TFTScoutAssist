import copy
import tkinter as tk
from tkinter import messagebox

class GameFrame(tk.Frame):
	def __init__(self, master, gameLogic):
		super().__init__(master, bg="orange", height=225, width=280)

		self.gameLogic = gameLogic
		self.active = True

		self.label_inactive = tk.Label(self, text="3 players left, everyone can play everyone", bg="#ff5555", width=36)
		self.label_possible = tk.Label(self, text="Possible opponents", bg="#99ff99", width=18)
		self.label_played = tk.Label(self, text="Last played", bg="#99ff99", width=18)

		self.player_buttons = dict()
		self.delete_buttons = dict()

		self.reset()

	def reset(self):
		self.forget_buttons()
		
		for i, (player_idx, player_name) in enumerate(self.gameLogic.players.items()):
			self.player_buttons[player_idx] = tk.Button(self, text=player_name, command=lambda player_idx=player_idx: self.played_player(player_idx))
			self.delete_buttons[player_idx] = tk.Button(self, text="X", bg="red", command=lambda player_idx=player_idx: self.delete_player(player_idx))

		self.set_active()

		self.update_played()

	def played_player(self, player_idx):
		self.gameLogic.played(player_idx)

		self.update_played()

	def delete_player(self, player_idx):
		self.gameLogic.player_died(player_idx)
		self.player_buttons[player_idx].grid_forget()
		self.delete_buttons[player_idx].grid_forget()
		
		self.update_played()

	def set_active(self):
		self.label_inactive.grid_forget()

		self.label_possible.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(5,0), pady=(5,5))
		self.label_played.grid(row=0, column=2, columnspan=2, sticky="nsew", padx=(5,5), pady=(5,5))
		self.active = True
	
	def set_inactive(self):
		self.label_possible.grid_forget()
		self.label_played.grid_forget()

		self.label_inactive.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=(5,0), pady=(5,5))
		self.active = False

	def update_played(self):
		self.forget_buttons()

		button_states = tk.NORMAL
		if len(self.gameLogic.players) <= 2:
			button_states = tk.DISABLED
			if self.active:
				self.set_inactive()
		elif not self.active:
			self.set_active()

		for i, opponent in enumerate(self.gameLogic.get_possible_opponents()):
			self.player_buttons[opponent].grid(row=i+1, column=0, sticky="nsew", padx=(10,0), pady=(0,1))
			self.player_buttons[opponent]["state"] = button_states
			self.delete_buttons[opponent].grid(row=i+1, column=1)
			self.delete_buttons[opponent]["state"] = button_states

		for i, opponent in enumerate(self.gameLogic.get_played_opponents()):
			self.player_buttons[opponent].grid(row=i+1, column=2, sticky="nsew", padx=(10,0), pady=(0,1))
			self.player_buttons[opponent]["state"] = tk.DISABLED
			self.delete_buttons[opponent].grid(row=i+1, column=3, padx=(5,0))

	def forget_buttons(self):
		for _, button in self.player_buttons.items():
			button.grid_forget()

		for _, button in self.delete_buttons.items():
			button.grid_forget()

class OptionsFrame(tk.Frame):
	def __init__(self, parent, gameLogic, gameFrame):
		super().__init__(parent, bg="orange")
		
		self.gameLogic = gameLogic
		self.gameFrame = gameFrame
		self.parent = parent

		self.grid_rowconfigure(0,weight=0)
		self.grid_rowconfigure(1,weight=1)
		self.grid_rowconfigure(2,weight=0)
		self.grid_rowconfigure(3,weight=0)
		tk.Label(self, text="Options", bg="#99ff99", width=5).grid(row=0, column=0, sticky="new", padx=5, pady=5)
		tk.Checkbutton(self, text="Always on top", variable=parent.always_on_top).grid(row=1, column=0, sticky="new", padx=5, pady=0)
		self.reset_button = tk.Button(self, text="Reset played", command=self.reset)
		self.reset_button.grid(row=2, column=0, sticky="nsew", padx=5, pady=(5,0))
		self.revive_button = tk.Button(self, text="Revive all", command=self.revive_all)
		self.revive_button.grid(row=3, column=0, sticky="nsew", padx=5, pady=(5,0))
		self.next_game_button = tk.Button(self, text="New Game", command=self.end_game, bg="#ff5555")
		self.next_game_button.grid(row=4, column=0, sticky="nsew", padx=5, pady=5)

	def disable_game_buttons(self):
		self.reset_button["state"] = tk.DISABLED
		self.revive_button["state"] = tk.DISABLED
		self.next_game_button["state"] = tk.DISABLED

	def enable_game_buttons(self):
		self.reset_button["state"] = tk.NORMAL
		self.revive_button["state"] = tk.NORMAL
		self.next_game_button["state"] = tk.NORMAL

	def reset(self):
		self.gameLogic.reset()
		self.gameFrame.update_played()

	def revive_all(self):
		self.gameLogic.revive_all()
		self.gameFrame.update_played()

	def end_game(self):
		if messagebox.askokcancel("Start new game?", " Are you sure you want to start a new game? \nAll the player names will be deleted."):
			self.parent.next_stage()

class GameLogic:
	# How many players are kept in the played buffer
	#   depending on how many players are remaining.
	PLAYED_LOGIC = { # remaining : played buffer
		7: 4, 6: 3, 5: 2, 
		4: 2, 3: 1, 2: 0
	}

	def __init__(self):
		self.players = dict()
		self.reset()

	def new_game(self, players):
		self.players = dict()
		for i, player in enumerate(players):
			self.players[i] = player
		self.players_backup = copy.copy(self.players)
		
		self.reset()

	def reset(self):
		self.played_against = list()
		self.played_start_idx = -1

	def revive_all(self):
		self.players = copy.copy(self.players_backup)
		self.reset()

	def played(self, player_idx):
		if player_idx in self.played_against:
			print("Error: This matchup should have been impossible. Ignoring entry...")
			return
		
		remaining_players = len(self.players)
		if remaining_players <= 2:
			self.reset()
			return

		self.played_start_idx += 1
		if self.played_start_idx > self.PLAYED_LOGIC[remaining_players]-1:
			self.played_start_idx = 0
		
		if self.played_start_idx + 1 > len(self.played_against):
			self.played_against.append(player_idx)
		else:
			self.played_against[self.played_start_idx] = player_idx

	def player_died(self, player_idx):
		self.reset()

		for idx, player in self.players.items():
			if idx == player_idx:
				del self.players[idx]
				break

	def get_played_opponents(self):
		ret = list()
		len_ = len(self.played_against)
		for i in range(len_):
			next_idx = self.played_start_idx - i
			if next_idx < 0:
				next_idx += len_
			ret.append(self.played_against[next_idx])
		return ret

	def get_possible_opponents(self):
		possible_opponents = [player_idx for player_idx in self.players.keys() if player_idx not in self.played_against]
		return possible_opponents


class PlayerSelectionFrame(tk.Frame):
	def __init__(self, master, playerList):
		super().__init__(master, bg="orange")

		self.grid_columnconfigure(0, weight=0)
		self.grid_columnconfigure(1, weight=1)
		self.grid_columnconfigure(2, weight=0)

		self.playerList = playerList
		self.stringVars = list()

		self.setup_frame()

	def setup_frame(self):
		tk.Label(self, text="Enter opponent names", bg="#99ff99").grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(5,0), pady=(5,2))

		for i in range(7):
			tk.Label(self, text="Player {}:".format(i+1)).grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
			self.stringVars.append(tk.StringVar(self))
			tk.Entry(self, textvariable=self.stringVars[-1]).grid(row=i+1, column=1, pady=3, sticky="nsew")

		tk.Button(self, text="Start Game", command=self.start_game).grid(row=i+1, column=2, padx=5, sticky="e")

	def start_game(self):
		for i in range(7):
			self.playerList.append(self.stringVars[i].get())

		self.master.next_stage()


class Game(tk.Tk):
	def __init__(self):
		super().__init__()

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		self.minsize(408, 235)
		self.title("TFT Scouter Assistent")

		self.always_on_top = tk.BooleanVar()
		self.always_on_top.set(True)
		self.always_on_top.trace_add('write', lambda x, y, z: self.set_always_on_top(self.always_on_top.get()))
		self.set_always_on_top(self.always_on_top.get())

		self.gameLogic = GameLogic()
		self.gameFrame = GameFrame(self, self.gameLogic)
		self.options_frame = OptionsFrame(self, self.gameLogic, self.gameFrame)
		self.options_frame.grid(row=0, column=1, sticky="nsew", padx=(5,5), pady=5)

		self.stage = 0
		self.next_stage()

	def next_stage(self):
		if self.stage == 0:
			self.start_player_selection_frame()
			self.stage += 1
		elif self.stage == 1:
			print("Players: ", self.players)
			self.start_main_game()
			self.stage = 0

	def start_player_selection_frame(self):
		self.players = list()
		self.playerSelection = PlayerSelectionFrame(self, self.players)
		self.playerSelection.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=5)

		self.options_frame.disable_game_buttons()

	def start_main_game(self):
		self.playerSelection.grid_forget()
		self.gameLogic.new_game(self.players)
		self.gameFrame.reset()
		self.gameFrame.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=5)
		self.gameFrame.grid_propagate(False)

		self.options_frame.enable_game_buttons()

	def set_always_on_top(self, is_always_on_top):
		self.wm_attributes("-topmost", is_always_on_top)


def main():

	game = Game()
	game.mainloop()


if __name__ == "__main__":
	main()