import copy
import tkinter as tk

class CircularBuffer():
	def __init__(self):
		pass

class GameFrame(tk.Frame):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game

		self.main_frame = tk.Frame(self, height=210, width=250, bg="orange")
		self.main_frame.grid(row=0, column=0, sticky="nsew", padx=(5,0), pady=(5,0))
		self.main_frame.grid_propagate(False)

		self.options_frame = tk.Frame(self, bg="red")
		self.options_frame.grid(row=1, column=0, sticky="nsew", padx=(5,0), pady=(5,0))
		tk.Button(self.options_frame, text="Reset played", command=self.reset).grid(row=0, column=0)
		tk.Button(self.options_frame, text="Revive all", command=self.revive_all).grid(row=0, column=1)
		tk.Button(self.options_frame, text="Next Game", command=parent.next_stage).grid(row=0, column=2, padx=(45,0))

		self.player_buttons = dict()
		self.delete_buttons = dict()
		for i, (player_idx, player_name) in enumerate(self.game.players.items()):
			self.player_buttons[player_idx] = tk.Button(self.main_frame, text=player_name, command=lambda player_idx=player_idx: self.played_player(player_idx))
			self.delete_buttons[player_idx] = tk.Button(self.main_frame, text="X", bg="red", command=lambda player_idx=player_idx: self.delete_player(player_idx))

		tk.Label(self.main_frame, text="POSSIBLE OPPONENTS", bg="#99ff99").grid(row=0, column=0, columnspan=2, sticky="nsew")
		tk.Label(self.main_frame, text="LAST PLAYED", bg="#99ff99").grid(row=0, column=2, columnspan=2, sticky="nsew", padx=(5,0))

		self.update_info()

	def played_player(self, player_idx):
		self.game.played(player_idx)

		self.update_info()

	def delete_player(self, player_idx):
		self.game.player_died(player_idx)
		self.player_buttons[player_idx].grid_forget()
		self.delete_buttons[player_idx].grid_forget()
		
		self.update_info()

	def reset(self):
		self.game.reset()
		self.update_info()

	def revive_all(self):
		self.game.revive_all()
		self.update_info()

	def update_info(self):
		for _, button in self.player_buttons.items():
			button.grid_forget()

		for _, button in self.delete_buttons.items():
			button.grid_forget()

		for i, opponent in enumerate(self.game.get_possible_opponents()):
			self.player_buttons[opponent].grid(row=i+1, column=0, sticky="nsew")
			self.player_buttons[opponent]["state"] = tk.NORMAL
			self.delete_buttons[opponent].grid(row=i+1, column=1)

		for i, opponent in enumerate(self.game.get_played_opponents()):
			self.player_buttons[opponent].grid(row=i+1, column=2, sticky="nsew", padx=(5,0))
			self.player_buttons[opponent]["state"] = tk.DISABLED
			self.delete_buttons[opponent].grid(row=i+1, column=3, padx=(5,0))

class GameLogic:
	def __init__(self, players):
		self.players = dict()
		for i, player in enumerate(players):
			self.players[i] = player

		self.players_backup = copy.copy(self.players)

		self.played_against = list()
		self.played_start_idx = -1

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
		if remaining_players <= 1:
			self.reset()
			return

		# How many players are kept in the played buffer
		#   depending on how many players are remaining.
		PLAYED_LOGIC = {
			7: 4, 6: 4, 5: 3, 
			4: 2, 3: 2, 2: 1
		}

		self.played_start_idx += 1
		if self.played_start_idx > PLAYED_LOGIC[remaining_players]-1:
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

		self.playerList = playerList
		self.stringVars = list()

		self.setup_frame()

	def setup_frame(self):
		tk.Label(self, text="Enter player names:", bg="#99ff99").grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(3,5))

		for i in range(7):
			tk.Label(self, text="Player {}:".format(i+1)).grid(row=i+1, column=0, padx=3, pady=3)
			self.stringVars.append(tk.StringVar(self))
			tk.Entry(self, textvariable=self.stringVars[-1]).grid(row=i+1, column=1, pady=3)

		tk.Button(self, text="Start Game", command=self.start_game).grid(row=8, column=1)

	def start_game(self):
		for i in range(7):
			self.playerList.append(self.stringVars[i].get())

		self.master.next_stage()


class Game(tk.Tk):
	def __init__(self):
		super().__init__()

		self.grid_columnconfigure(0, weight=1)

		self.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=0)

		self.geometry("260x250")
		self.minsize(260, 250)
		self.title("TFT Scouter Assistent")

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
		playerSelection = PlayerSelectionFrame(self, self.players)
		playerSelection.grid(row=0, column=0, sticky="nsew")

	def start_main_game(self):
		gameLogic = GameLogic(self.players)
		gameFrame = GameFrame(self, gameLogic)
		gameFrame.grid(row=0, column=0, sticky="nsew")


def main():

	game = Game()
	game.mainloop()


if __name__ == "__main__":
	main()