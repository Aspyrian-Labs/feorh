"""
Name: feorh_main.py 
Authors: Oliver Giles & Max Potter
Date: July 2017
Description:
    - Use pygame to create a simplistic model of a tiger hunting deer
    - Randomly generate a tile-based map 
    - Populate the map with tigers and deer
    - Tigers and deer have neural network 'brains' that control their actions
"""
import constants as const
import feorh as f

def main():
	#Initialise a simulation: create map, spawn creatures, set up counters, etc.
	game = f.Feorh()

	#Update the game whilst run conditions are met
	while game.running():
		game.update()

	#Clean up
	game.quit_game()

main()
