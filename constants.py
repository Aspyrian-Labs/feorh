"""
Name: constants.py 
Authors: Oliver Giles & Max Potter
Date: July 2017
Description:
    - Stores the various parameters of the game
"""
from numpy import float32

#Meta properties
MAX_EPOCH = 100

#Flags
RUN_DIAGNOSTICS = True

#Starting framerate
START_FPS = 10

#Game & tilemap dimensions
TILESIZE = 30 
HEIGHT = 20
WIDTH = 30
MINSEEDS = 50
MAXSEEDS = 50

#Genetic algorithm constants
GENE_POOL_SIZE = 15

#Neural network constants
INPUT_COUNT = 15
NEURONS_PER_LAYER = 4
NUM_HIDDEN_LAYERS = 1
OUTPUT_NEURONS = 2

#Creature constants
TIGER_EAT_ENERGY = 50
DEER_EAT_ENERGY = 3
TIGERPOP = 5
DEERPOP = 10

#Constants for colours
ORANGE = (242, 68, 56)
YELLOW = (255,193,8)
BROWN = (120, 84, 72)
GREEN = (76, 173, 80)
WHITE = (255, 255, 255)

#Constants for tiles
WALL = float32(10.25)
DIRT = float32(0.375)
GRASS = float32(0.5)
WOOD = float32(0.625)
TIGERCOLOUR = float32(0.875)
DEERCOLOUR = float32(-10.25)

#Colour to tile conversion
colours = {
            DIRT : WHITE,
            GRASS : GREEN,
            WOOD : BROWN,
            DEERCOLOUR : YELLOW,
            TIGERCOLOUR : ORANGE
          }

tileNames = {
	WALL : '#',
	DIRT : 'd',
	GRASS : 'g',
	WOOD : 'w',
	TIGERCOLOUR : 'T',
	DEERCOLOUR : 'D'
}
