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

#Sprite upscaler
SPRITESCALE = 2.5

#Game & tilemap dimensions
TILESIZE = 30  # dimensions of each square tile in terms of displacement 
HEIGHT = 20    # number of tiles in y 
WIDTH = 30     # number of tiles in x
MINSEEDS = 50  # Voronoi map generation seeds
MAXSEEDS = 50

#Genetic algorithm constants
GENE_POOL_SIZE = 15

#Neural network constants
INPUT_COUNT = 11
NEURONS_PER_LAYER = 4
NUM_HIDDEN_LAYERS = 1
OUTPUT_NEURONS = 3

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
DIRT = float32(0.1)
GRASS = float32(2.5)
WOOD = float32(0.2)
TIGERCOLOUR = float32(-20.25)
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
