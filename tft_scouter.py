import tkinter as tk

class GameFrame(tk.Frame):
	def __init__(self, parent, game):
		super().__init__(parent)
		
		self.game = game

		self.info_frame = tk.Frame(self)
		self.info_frame.grid(row=0, column=1)

		self.options_frame = tk.Frame(self)
		self.options_frame.grid(row=1, column=0, columnspan=2)
		tk.Button(self.options_frame, text="Reset", command=self.reset).grid(row=0, column=0)

		self.player_buttons = dict()
		self.delete_buttons = dict()
		for i, (player_idx, player_name) in enumerate(self.game.players.items()):
			self.player_buttons[player_idx] = tk.Button(self.info_frame, text=player_name, command=lambda player_idx=player_idx: self.played_player(player_idx))
			self.delete_buttons[player_idx] = tk.Button(self.info_frame, text="X", command=lambda player_idx=player_idx: self.delete_player(player_idx))

		self.played_row_offset = 10
		tk.Label(self.info_frame, text="POSSIBLE OPPONENTS:").grid(row=0, column=0, columnspan=2)
		tk.Label(self.info_frame, text="PLAYED OPPONENTS:").grid(row=self.played_row_offset, column=0, columnspan=2)

		self.update_info()

	def played_player(self, player_idx):
		self.game.played(player_idx)

		self.update_info()

	def delete_player(self, player_idx):
		self.game.player_died(player_idx)

		self.player_buttons[player_idx].grid_forget()
		del self.player_buttons[player_idx]

		self.delete_buttons[player_idx].grid_forget()
		del self.delete_buttons[player_idx]
		
		self.update_info()

	def reset(self):
		self.game.reset()

		self.update_info()

	def update_info(self):
		for _, button in self.player_buttons.items():
			button.grid_forget()

		for _, button in self.delete_buttons.items():
			button.grid_forget()

		for i, opponent in enumerate(self.game.get_possible_opponents()):
			self.player_buttons[opponent].grid(row=i+1, column=0, sticky="nsew")
			self.delete_buttons[opponent].grid(row=i+1, column=1)

		for i, opponent in enumerate(self.game.get_played_opponents()):
			row_idx = self.played_row_offset + 1 + i
			self.player_buttons[opponent].grid(row=row_idx, column=0, sticky="nsew")
			self.delete_buttons[opponent].grid(row=row_idx, column=1)

class Game:
	def __init__(self):
		self.players = list()
		self.get_players()

		self.played_against = list()
		self.played_start_idx = -1

	def get_players(self):
		print("Enter identifier for other players:")
		self.players = dict()
		for i in range(7):
			self.players[i] = input("{}: ".format(i+1))

		# self.players = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g"}

	def reset(self):
		self.played_against = list()
		self.played_start_idx = -1

	def played(self, player_idx):
		print("PLAYED AGAINST: ", self.players[player_idx])

		if player_idx in self.played_against:
			print("Error: This matchup should have been impossible. Ignoring entry...")
			# TODO: Reset instead???
			return

		remaining_players = len(self.players)
		self.played_start_idx += 1
		if self.played_start_idx > remaining_players-4:
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
		print("PLAYED: ", self.played_against)
		return self.played_against

	def get_possible_opponents(self):
		possible_opponents = [player_idx for player_idx in self.players.keys() if player_idx not in self.played_against]
		print("POSSIBLE: ", possible_opponents)
		return possible_opponents

def main():

	game = Game()

	root = tk.Tk()
	gameFrame = GameFrame(root, game)
	gameFrame.grid(row=0, column=0)

	root.mainloop()


if __name__ == "__main__":
	main()