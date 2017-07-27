"""
Name: creatures.py 
Author: Oliver Giles & Max Potter
Date: June 2017
Description:
	- Contains class definitions for the animals of the game
"""

import pygame
from pygame.locals import *
from random import randint, choice
import minds as m
from time import time
import genetic_algorithm as ga
from sys import getrefcount
import constants as const

#Lists of objects
tigerList = pygame.sprite.Group()
deerList = pygame.sprite.Group()

deerSpeed = 0
fitnesses = []
wallDeaths = []
newBreeders = []
epoch = 1
idNumber = 0
wall = const.WALL
deerColour = const.DEERCOLOUR
tigerColour = const.TIGERCOLOUR

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

    def __init__(self, position, ctype, DNA = ''):
        pygame.sprite.Sprite.__init__(self)
        self.ctype = ctype
        self.name = self.get_name()

        #Handle creature type senstive parameters
        if ctype == 'tiger':
            self.image, self.rect = load_png('tiger.png')
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
        self.vision = [wall,wall,wall,wall,wall]

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
        actions = m.think(self.weights, self.vision)

        for action in actions: 
            #Speed up: action[0] = K_SPACE
            # if int(round(action[0])) == 1:
            #     self.speed = self.topSpeed
            # else:
            #     self.speed = self.baseSpeed

            left, right, up, down, speed = False, False, False, False, False
            self.dx, self.dy = 0, 0 #Reset speed

            #Establish 'buttons pressed': 
            if int(round(action[0])) == 1:
                up = True
            if int(round(action[1])) == 1:
                left = True
            if int(round(action[2])) == 1:
                down = True
            if int(round(action[3])) == 1:
                right = True

            if up and not down:
                self.dy = 1
            if down and not up:
                self.dy = -1
            if left and not right:
                self.dx = -1
            if right and not left:
                self.dx = 1

        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
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

    def print_vision():
        print self.name.rstrip(), self.energy
        print "Vision: "
        print "     %s" % (const.tileNames[self.vision[0]])
        print "  %s  %s  %s" % (const.tileNames[self.vision[2]], 
                                const.tileNames[self.vision[4]], 
                                const.tileNames[self.vision[3]])
        print "     %s" % (const.tileNames[self.vision[1]])
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
        return self.killCount * 10 + len(self.tiles) * 3 if self.ctype == 'tiger' else self.age + 5 * epoch

def spawn_creature(ctype, mapHeight = 100, mapWidth = 150, tileSize = 6, pos=[-1,-1], DNA=''):
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

    newCreature = Creature(pos, ctype, DNA)
    newSprite = pygame.sprite.RenderPlain(newCreature)

    return newCreature, newSprite

def get_id():
    global idNumber
    idNumber += 1
    return idNumber