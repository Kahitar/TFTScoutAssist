TFT Scout Assist
================

A small python tkinter app for the game Teamfight Tactics from Riot Games to help track who the next possible opponents are.

## Installation

1. Download this script by clicking "Clone or Download" -> "Download ZIP" on the right above the file list.
2. Unzip to a folder you like.
3. Install python using the Microsoft Store (Windows 10): [Link](https://www.microsoft.com/store/productId/9NJ46SX7X90P)
	- I didn't test this App on Apple OS and have no idea if it works there and how to install python. If you have success using it there, feel free to tell me how and I'll add instructions here.

## Usage

### Game setup:
1. In the first screen enter the names (or any identifier you want, like a shorthand for the name) of your 7 opponents. 
2. Click `Start Game`.

### Game controls:
- The `left column` will alway contain the opponents you can possibly play against next. The `right column` contains the players you last played against (in the correct order).
- Click on a player's button in the left column to mark this player as the last opponent you played against. The player button will move to the right column.
- If a player is eliminated, press the red cross button next to it's name. The button of that player will be removed.
- Click `Reset played` to move all not eliminated opponents back to the left column.
- Click `Revive all` to bring back all buttons of opponents that you previously marked as eliminated. *This will also move all buttons back to the left column!*
- Click `New Game` to delete all players and return to the first screen where you can enter the opponent's names for the next game.
- The checkbutton `Always on top` toggles whether the window should always be on top of every other window or not.
