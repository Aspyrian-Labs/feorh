"""
Name: creatures.py 
Author: Oliver Giles & Max Potter
Date: June 2017
Description:
	- Contains class definitions for the animals of the game
"""

import pygame
from pygame.locals import *
from random import randint, choice, uniform
import minds as m
import math
from time import time
import genetic_algorithm as ga
from sys import getrefcount
import constants as const
from mapfuncs import outOfBounds

#Lists of objects
tigerList = pygame.sprite.Group()
deerList = pygame.sprite.Group()

deerSpeed = 2
fitnesses = []
wallDeaths = []
newBreeders = []
epoch = 1
idNumber = 0
wall = const.WALL
deerColour = const.DEERCOLOUR
tigerColour = const.TIGERCOLOUR
turnSpeed = 0.2

def load_png(name):
    image = pygame.image.load(name)
    if image.get_alpha is None:
        image = image.convert()
    else:
        image = image.convert_alpha()
    return image, image.get_rect()

class Creature(pygame.sprite.Sprite):
    """
    Generic creature class.
    Tigers hunt deer, deer eat grass. 
    All creatures lose energy over time and die it if hits zero.
    Handles sprite initialisation, vision and movement.
    All creatures have a Mind object (see minds.py).
    """

    def __init__(self, position, ctype, DNA = '', beastMode=False):
        pygame.sprite.Sprite.__init__(self)
        self.ctype = ctype
        self.name = self.get_name()
        self.angle  = uniform(0, 2*math.pi)
        #Handle creature type senstive parameters
        if ctype == 'tiger':
            if not beastMode:
                self.image, self.rect = load_png('tiger.png')
            else:
                self.image, self.rect = load_png('tigerGod.png')
            self.add(tigerList)
            self.baseSpeed = 6
            self.topSpeed = 10
            self.energy = 300
            self.maxEnergy = 300
            self.drainRate = 1
            self.birthsecond = time()
            self.age = 0.0
            self.killCount = 0
            self.id = get_id()
        elif ctype == 'deer':
            self.image, self.rect = load_png('deer.png')
            self.add(deerList)
            self.baseSpeed = deerSpeed
            self.topSpeed = deerSpeed*1.5
            self.energy = 200
            self.maxEnergy = 200
            self.drainRate = 2
            #self.birthsecond = time()
            self.age = 0.0
            self.id = get_id()
            self.deathByTiger = False

        #Scale sprites
        self.size = self.image.get_size()
        # create a 2x bigger image than self.image
        self.image = pygame.transform.scale(self.image, (int(self.size[0]*const.SPRITESCALE), int(self.size[1]*const.SPRITESCALE)))
        self.baseImage = self.image

        #Set up display information
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()  
        self.rect = self.image.get_rect(topleft=(position[0], position[1]))
        
        #Movement
        self.speed = self.baseSpeed
        self.dx = 0
        self.dy = 0
        self.tiles = [] #blank list to store all visited tiles

        #Set up default vision (5x5 grid, all seeing 'off map')
        # self.vision = [[wall for column in range(5)] for row in range(5
        self.vision = []

        #Create blank DNA and attach a Mind object to our creature
        self.DNA = DNA
        child = False if len(self.DNA) > 0 else True #children will have non-blank DNA strings
        self.weights, self.DNA = m.get_weights(firstGeneration = child, DNA = DNA)

    def update(self):
        #Deplete energy and check if still alive!
        self.energy -= self.drainRate
        if self.energy <= 0:
            self.die()

        self.age += 1
        if self.ctype == "deer":
            if self.age >= 1500:
                self.die()

        #Feed vision into neural network and retrieve button presses
        actions = m.think(self.weights, self.vision, self.rect.x, self.rect.y, self.angle)

        #Use output of NN (see minds.py) to determine movement 
        for action in actions: 
            #Speed up: action[0] = K_SPACE
            # if int(round(action[0])) == 1:
            #     self.speed = self.topSpeed
            # else:
            #     self.speed = self.baseSpeed

            left, right, stop = False, False, False
            self.dx, self.dy = 0, 0 #Reset speed

            #Establish 'buttons pressed': 
            if int(round(action[0])) == 1:
                left = True
            if int(round(action[1])) == 1:
                right = True
            if int(round(action[2])) == 1:
                stop = True

            if left and not right:
                tempTurnRate = -turnSpeed
            elif right and not left:
                tempTurnRate = turnSpeed
            else:
                tempTurnRate = 0
            if stop:
                tempSpeed = 0
            else:
                tempSpeed = self.speed
        
        #Update direction and displacement 
        self.angle += tempTurnRate
        self.angle = self.angle % (2.0 * math.pi) # angle is in radians: clamp it between 0 and 2pi
        # if self.angle * 180/math.pi >= 360:
        #     self.angle -= 360 / (180/math.pi)
        # elif self.angle * 180/math.pi < 0:
        #     self.angle -= 360 / (180/math.pi)

        direction = (math.cos(self.angle), -math.sin(self.angle)) # displacement origin is top left corner
        displacement = tuple(coord * tempSpeed for coord in direction)
        self.rect.x += displacement[0]
        self.rect.y += displacement[1]
        angleInDeg = self.angle * 180/math.pi
        self.image = pygame.transform.rotate(self.baseImage, angleInDeg % 360) 
        
        pygame.event.pump()

    def get_name(self):
        return choice(list(open('names.txt')))

    def get_vision(self, i, j, tilemap, height, width, centreTile):
        """
        Takes tilemap and indicies, grabs 5x5 section of tilemap centred on (i,j),
        sets vision equal to a list of length 5: 4 directions and the centre point.
        The elements of the final vision list are the most common tile type in the 
        quadrant they represent, with deer/tiger trumping all other tiles.
        """
        #Set up 5x5 array, every element is -1 (which will indicate 'seeing off map')
        chunk = [[wall for column in range(5)] for row in range(5)]

        for idx in range(5):
            for jdx in range(5):
                #Find tilemap index we want to look at
                tmidx = i - 2 + idx
                tmjdx = j - 2 + jdx

                #Skip changing vision list if index is out of tilemap bounds
                if tmidx < 0 or tmjdx < 0 or tmidx > height - 1 or tmjdx < 0 or tmjdx > width - 1:
                    continue

                chunk[idx][jdx] = tilemap[i - 2 + idx][j - 2 + jdx]

        #Collect 6 tiles in each direction
        left = [chunk[1][0],chunk[2][0],chunk[3][0],chunk[1][1],chunk[2][1],chunk[3][1]]
        right = [chunk[1][3],chunk[2][3],chunk[3][3],chunk[1][4],chunk[2][4],chunk[3][4]]
        up = [chunk[0][1],chunk[0][2],chunk[0][3],chunk[1][1],chunk[1][2],chunk[1][3]]
        down = [chunk[3][1],chunk[3][2],chunk[3][3],chunk[4][1],chunk[4][2],chunk[4][3]]

        directions = [up,down,left,right]
        visionTemp = []
        for direction in directions:
            if deerColour in direction and self.ctype == 'tiger':
                visionTemp.append(deerColour)
            elif tigerColour in direction and self.ctype == 'deer':
                visionTemp.append(tigerColour)
            else:
                visionTemp.append(max(set(direction), key=direction.count)) #find most common tile 
        visionTemp.append(centreTile) #stop the tiger seeing itself in the centre square

        self.vision = visionTemp
        return
    
    def find_tile_at_angle(self, i, j, tilemap, height, width, sight_angle):
        """
        Iterate through a range of distance in moderate steps in dir calculated from angle...
        If a tiger or wall is found, return it. If not, keep going until the end and return
        the tile found there.
        """
        numSteps = 6
        stepSize = 40 # ~tile diagonal 
        direction = (math.cos(sight_angle), -math.sin(sight_angle))
        x, y = self.rect.x, self.rect.y
        displacement = tuple(coord * stepSize for coord in direction)
        for step in range(numSteps):
            x += displacement[0]
            y += displacement[1]
            tileX, tileY = int(x/const.TILESIZE), int(y/const.TILESIZE)
            if outOfBounds(tileX, tileY):
                return wall
            try:
                tile = tilemap[tileY][tileX]
            except IndexError: 
                return wall
            if tile == tigerColour and self.ctype == 'deer':
                return tile
            elif tile == deerColour and self.ctype == 'tiger':
                return tile
            elif tile == wall:   
                return tile
        return tile

    def get_directional_vision(self, i, j, tilemap, height, width, centreTile):
        """
        Uses the creatures current direction to generate a set of inputs describing
        which tiles are in their field of view.
        """
        visionTemp = [centreTile]
        numInputs = 7
        angle = self.angle * 180/math.pi # angle in deg
        for i in range(numInputs):
            sight_angle = angle - 60 + i * (60/(numInputs/2))
            visionTemp.append(self.find_tile_at_angle(i, j, tilemap, height, width, sight_angle * math.pi/180))
        self.vision = visionTemp
        return

    def print_vision(self):
        print self.name.rstrip(), self.energy
        # print "Vision: "
        # print "     %s" % (const.tileNames[self.vision[0]])
        # print "  %s  %s  %s" % (const.tileNames[self.vision[2]], 
        #                         const.tileNames[self.vision[4]], 
        #                         const.tileNames[self.vision[3]])
        # print "     %s" % (const.tileNames[self.vision[1]])
        print " Angle: "
        print " raw angle: %s, mod rad: %s" % (self.angle, self.angle % (2*math.pi))
        print " raw deg: %s, mod deg: %s" % (self.angle * 180/math.pi, (self.angle * 180/math.pi) % 360)
        print " dir: %s %s" % (math.cos(self.angle), math.sin(self.angle))
        print " vision: ", self.vision

        print " %s %s %s | %s | %s %s %s " % (const.tileNames[self.vision[0]],
                                              const.tileNames[self.vision[1]],
                                              const.tileNames[self.vision[2]],
                                              const.tileNames[self.vision[3]],
                                              const.tileNames[self.vision[4]],
                                              const.tileNames[self.vision[5]],
                                              const.tileNames[self.vision[6]],
                                              )
        return


    def eat(self, eatEnergy):
        if self.energy < self.maxEnergy:
            self.energy += eatEnergy
        if self.ctype == 'tiger':
            self.killCount += 1

    def die(self, deathByWall = False):
        # print "%s%s %s has died!" % (self.ctype[0].upper(), self.ctype[1:].rstrip(), 
        #     self.name.rstrip())
        if self.ctype == 'tiger':
            fitness = self.calc_fitness()
            fitnesses.append(fitness)
            if not deathByWall:
                wallDeaths.append(0) #see diagnostics, feorh.py

                #If it was good enough to breed, record it for diagnostics
                ga.pool(fitness, self.DNA, self.ctype, self.id)
                for t in ga.tGenepool:
                    if self.id in t:
                        newBreeders.append([self.id, fitness, self.DNA])
            else:
                wallDeaths.append(1) #see diagnostics, feorh.py
            tigerList.remove(self)
        if self.ctype == 'deer':
            if not deathByWall:
                fitness = self.calc_fitness()
                ga.pool(fitness, self.DNA, self.ctype, self.id)
            deerList.remove(self)

    def calc_fitness(self):
        #Fitness function for tigers and deer
        if (self.ctype == 'tiger'):
            fitness = self.killCount * 10 + len(self.tiles) * 3 
        else:
            bonus = 100 if not self.deathByTiger else 0
            fitness = self.age + 5 * epoch + bonus
        return fitness

def spawn_creature(ctype, mapHeight = 100, mapWidth = 150, tileSize = 6, pos=[-1,-1], DNA='', beastMode=False):
    """
    Initialises instance of a creature of type ctype.
    In absence of pos argument, spawn location is randomly generated based on height & width.
    Returns an object and a sprite.
    """
    #if pos is unchanged by user then randomly generate a position
    if pos == [-1,-1]: 
        acceptable = False
        rangeX = (mapWidth-1)*tileSize
        rangeY = (mapHeight-1)*tileSize
        pos = [randint(0,rangeX), randint(0,rangeY)]

    if ctype == 'deer':
        while not acceptable:
            acceptable = True #Tentatively assume the spawn is suitable...
            #Check the spawn against tiger positions to ensure they do not spawn too closely
            for tiger in tigerList:
                if pos[0] < (tiger.rect.centerx + 15) and pos[0] > (tiger.rect.centerx - 15):
                    acceptable = False #Too close to tiger
                    rangeX = (mapWidth-1)*tileSize
                    rangeY = (mapHeight-1)*tileSize
                    pos = [randint(0,rangeX), randint(0,rangeY)]

    #if pos argument is passed but invalid, make it [0,0]
    if pos[0] < 0 and pos[1] < 0: 
        pos = [0,0]

    newCreature = Creature(pos, ctype, DNA, beastMode=beastMode)
    newSprite = pygame.sprite.RenderPlain(newCreature)

    return newCreature, newSprite

def get_id():
    global idNumber
    idNumber += 1
    return idNumber
