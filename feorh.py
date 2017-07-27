"""
Name: feorh.py 
Author: Oliver Giles & Max Potter
Date: July 2017
Description:
    - Contains class definitions for game
"""

import pygame
import sys
from pygame.locals import *
from copy import deepcopy
import constants as const
import mapfuncs as mf
import creatures as c
import minds as m
import genetic_algorithm as ga

class Feorh():
    """
    Feorh - Class describing a simple hunting game, played by AI.
    """
    epoch = 1
    width = const.WIDTH
    height = const.HEIGHT
    tileSize = const.TILESIZE

    def __init__(self):
        self.start_diagnostics()

        #Initialise display
        self.display, self.displayRect = start_display('Feorh')

        #Create & show map
        self.tilemap = mf.create_map(self.width, self.height, const.MINSEEDS, 
                                     const.MAXSEEDS)
        self.tilemapMaster = deepcopy(self.tilemap) #edits to sub arrays in tilemap 
                                                    #won't edit tilemapMaster                    
        self.make_background()

        #Spawn creatures
        for i in range(const.TIGERPOP):
            self.populate('tiger', const.TIGERPOP)
        for i in range(const.DEERPOP):
            self.populate('deer', const.DEERPOP)

        #Set up housekeeping lists and counters
        self.oldDeerPoints = [] #used for tracking past locations of deer
        self.oldTigerPoints = []
        self.pause = False
        self.epochCounter = 0
        self.timeCounter = 0
        self.killTotal = 0

        self.fps = const.START_FPS
        self.clock = pygame.time.Clock()
        return

    def update(self): 
        """
        Limit fps, handle user input and, if not paused, run game logic.
        """
        self.clock.tick(self.fps)
        self.handle_user_input()
        if not self.pause:
            self.run_game_logic()
        else:
            self.run_pause_logic()
        return

    def run_game_logic(self):
        """
        The structure of the main game loop.
        Everything here is ran once per update when not paused.
        """        
        #************ UPDATE CREATURES
        #Detect collisions between tigers and deer
        self.kill_detection()

        #Gather all living sprites into one list
        self.cList = c.tigerList.sprites() + c.deerList.sprites()

        #Update tilemap with position of all creatures
        self.update_tilemap()

        #Update creatures: update & supply vision, get and enact actions
        for creature in self.cList:
            i, j = mf.find_tile(creature, self.tileSize, self.height, self.width)
            creature.get_vision(i, j, self.tilemap, self.height, self.width, 
                                self.tilemapMaster[i][j])
            #Kill any creature that walks off the map.
            if not self.displayRect.colliderect(creature.rect):
                creature.die(deathByWall = True)
        c.deerList.update()
        c.tigerList.update()

        #Check if there are enough tigers and deer - if not, create children
        self.populate('tiger', const.TIGERPOP, len(c.tigerList), 
                      len(ga.tGenepool), len(ga.tPregnancies))
        self.populate('deer', const.DEERPOP, len(c.deerList), 
                      len(ga.dGenepool), len(ga.dPregnancies))

        #************ END OF STEP: visualisation and diagnostics
        update_display(self.display, self.cList, [c.deerList, c.tigerList], 
                       self.bgSurface)

        self.diagnostics()
        return

    def run_pause_logic(self):
        pygame.event.pump()
        return

    def running(self):
        """
        Describes the conditions under which the game will keep running.
        Returns the truth value of these conditions.
        """
        return True

    def quit_game():
        if const.RUN_DIAGNOSTICS:
            for f in self.openFiles:
                f.close()
        pygame.quit()
        sys.exit()
        return

    def start_diagnostics(self):
        """
        Open output files. Toggleable with RUN_DIAGNOSTICS flag in constants.
        """
        if const.RUN_DIAGNOSTICS:        
            self.f = open('bestTigers.txt', 'w')
            self.f2 = open('fitnessAndDeath.txt', 'w')
            self.f.write("epoch,fitness,DNA,ID\n")
            self.f2.write("time,epoch,live average fitness,"
                     "average fitness of breeders,%wall deaths,killTotal\n")
            self.openFiles = [self.f,self.f2]
        return

    def make_background(self):
        """
        Generate a pygame rect to represent the map, draw it to a surface.
        Blit that surface to the display.
        """
        self.bgSurface = pygame.Surface(self.display.get_size())
        for row in range(self.height):
            for column in range(self.width):
                self.bgRect = pygame.draw.rect(self.bgSurface, 
                                               const.colours[self.tilemap[row][column]], 
                                               (column*self.tileSize, 
                                                row*self.tileSize, 
                                                self.tileSize, 
                                                self.tileSize))
        self.bgSurface = self.bgSurface.convert()
        self.display.blit(self.bgSurface,(0,0)) # blit the map to the screen
        return

    def populate(self, ctype, popSize, cListSize = 0, poolSize = 0, 
                 pregListSize = 0):
        """
        Check if there are enough tigers and deers. If not, create children.
        """
        #Do we need to spawn a creature?
        if cListSize < popSize: 
            if poolSize < const.GENE_POOL_SIZE:
                #If genepool is small, spawn creature with randomised DNA
                c.spawn_creature(ctype, mapHeight=self.height, mapWidth=self.width, 
                                 tileSize=self.tileSize)
            else:
                #If not, make sure DNA is ready (a 'pregnancy')
                if pregListSize == 0:
                    #Make DNA through breeding creatures in genepool
                    ga.breed(ctype)
                DNA = ga.get_DNA(ctype)
                c.spawn_creature(ctype, mapHeight=self.height, mapWidth=self.width, 
                                 tileSize=self.tileSize, DNA=DNA)
        return

    def handle_user_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN: 
                #print creature's vision on mouse click
                for creature in self.cList:
                    if creature.rect.collidepoint(event.pos):
                        creature.print_vision()
            elif event.type == pygame.KEYDOWN:
                #Increase/decrease speed of newly spawning deer on =/-
                if event.key == K_EQUALS:
                    c.deerSpeed += 1
                    print "Deer speed increased to %d" % c.deerSpeed
                elif event.key == K_MINUS:
                    c.deerSpeed = c.deerSpeed - 1 if c.deerSpeed > 0 else 0
                    print "Deer speed decreased to %d" % c.deerSpeed
                #Raise/lower fps by 10 (never goes below 1) on ]/[
                elif event.key == K_LEFTBRACKET:
                    self.fps = self.fps - 10 if self.fps >= 0 else 1
                    self.fps = self.fps if self.fps >= 1 else 1
                    print " * FPS = %d" % self.fps
                elif event.key == K_RIGHTBRACKET:
                    self.fps += 10
                    print " * FPS = %d" % self.fps
                #Pause game on space
                elif event.key == K_SPACE:
                    if not self.pause:
                        print " * PAUSED * "
                        self.pause = True
                    else:
                        print " * RESUMED * "
                        self.pause = False
        return

    def kill_detection(self):
        """
        Detect collisions between each tiger and all the deer on the map. 
        If there is a collision, kill the deer and feed the tiger. Record kill.
        """
        for tiger in c.tigerList:
            collision_list = pygame.sprite.spritecollide(tiger, c.deerList, True)
            for col in collision_list:
                # print "%s was eaten by %s!" % (col.name.rstrip(), tiger.name.rstrip())
                tiger.eat(const.TIGER_EAT_ENERGY)
                self.killTotal += 1
        return

    def update_tilemap(self):
        """
        Store the position of all creatures on the tilemap. tilemapMaster 
        records the original tile in order to revert once a creature moves.
        """
        tigerPoints = []
        deerPoints = []
        for creature in self.cList:
            #what tile is the creature on? If it stands on a tile not previously
            #visted, update creature.tiles.
            i, j = mf.find_tile(creature, self.tileSize, self.height, self.width)
            unique = True
            for t in creature.tiles:
                if i == t[0] and j == t[1]:
                    unique = False
                    break
            if unique:
                creature.tiles.append((i,j))

            #Update tilemap to reflect what creatures are on each tiles
            # * tigers trump deer and are invisible in forests.
            isTiger = creature.ctype == "tiger"
            isNotInWood = self.tilemapMaster[i][j] != const.WOOD
            isDeer = creature.ctype == "deer"
            tigerNotOnTile = self.tilemap[i][j] != const.TIGERCOLOUR
            if isTiger and isNotInWood: 
                tigerPoints.append([i,j])
                self.tilemap[i][j] = const.TIGERCOLOUR
            elif isDeer and tigerNotOnTile: 
                self.tilemap[i][j] = const.DEERCOLOUR
                deerPoints.append([i,j])
                if self.tilemapMaster[i][j] == const.GRASS: 
                    #don't forget to feed the deer!
                    creature.eat(const.DEER_EAT_ENERGY)

        #Gather list of empty tiles by comparing old and new lists, then replace
        #the tiles with their original types.
        emptyTiles = [point for point in self.oldTigerPoints \
                      if point not in tigerPoints]
        emptyTiles.extend([point for point in self.oldDeerPoints \
                           if point not in deerPoints])
        for tile in emptyTiles:
            self.tilemap[tile[0]][tile[1]] = self.tilemapMaster[tile[0]][tile[1]]
        self.oldDeerPoints = deerPoints
        self.oldTigerPoints = tigerPoints
        return

    def diagnostics(self):
        """
        Collect and dump information about average fitness, rate of wall deaths
        and total kills.
        """
        self.timeCounter += 1
        self.epochCounter += 1
        if const.RUN_DIAGNOSTICS:
            if self.epochCounter % 100 == 0:
                #Calculate rolling average fitness values from last 50 deaths
                fitnessesLength = len(c.fitnesses)
                fitnessesExist = fitnessesLength > 0
                liveFitness = 100 * sum(c.fitnesses) / fitnessesLength if fitnessesExist else 0.0
                if fitnessesLength > 50:
                    del c.fitnesses[:fitnessesLength - 50]

                #Record fitness of breeding pool
                avBreedingFitness = 0
                for t in ga.tGenepool:
                    avBreedingFitness += t[0]
                breedersExist = len(ga.tGenepool) > 0
                avBreedingFitness = avBreedingFitness/len(ga.tGenepool) if breedersExist else 0.0
                
                #Calculate rolling average wall death rate as above                
                wallDeathLength = len(c.wallDeaths)
                wallDeathsExist = wallDeathLength > 0
                wallDeathRate = 100 * sum(c.wallDeaths) / wallDeathLength if wallDeathsExist else 0.0
                if wallDeathLength > 50:
                    del c.wallDeaths[:wallDeathLength - 50]
                
                self.f2.write("%d,%d,%f,%f,%f,%d\n" % (self.timeCounter,
                                                       self.epoch,
                                                       liveFitness,
                                                       avBreedingFitness,
                                                       wallDeathRate,
                                                       self.killTotal))
            if self.epochCounter >= 2000: #End of epoch diagnostics
                #Dump current best tiger list 
                newTigerCount = 0
                for t in c.newBreeders:
                    print "New tiger added to bestTigers.txt! Fitness = %d." % t[1]
                    self.f.write("%d,%d,%d,%s\n" % (self.epoch, t[0], t[1], t[2]))
                    newTigerCount += 1
                ga.epochTigers = newTigerCount
                c.newBreeders = []
                
                self.epochCounter = 0
                self.epoch += 1
                c.epoch = self.epoch
                print ' *                            Epoch:', self.epoch    
        return

def start_display(title, w = const.WIDTH, h = const.HEIGHT, 
                  tileSize = const.TILESIZE):
    """
    Initialise pygame, open and title a window.
    """
    pygame.init()
    display = pygame.display.set_mode((w * tileSize, h * tileSize))
    drect = display.get_rect()
    pygame.display.set_caption(title)
    return display, drect

def update_display(display, spriteList, groupsList, background):
    display.blit(background,(0,0))
    for sprite in spriteList:
        display.blit(background, sprite.rect, sprite.rect) 
    for group in groupsList:
        group.draw(display)
    pygame.display.update()
    return
