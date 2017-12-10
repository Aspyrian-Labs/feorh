"""
Name: genetic_algorithm.py
Author: Oliver Giles & Max Potter
Date: June 2017
Description:
	- Contains functions for DNA crossover and mutation
	  as well as management of the gene pool.
"""

import random
import constants as const

#How many creatures are added to the gene pool in the epoch
epochTigers = const.GENE_POOL_SIZE
epochDeers = const.GENE_POOL_SIZE

#Lists of children waiting to be born
tPregnancies = []
dPregnancies = []

#Lists of most fit parents
tGenepool = []
dGenepool = []

#List for selecting index when choosing parents
idxList = ([0] * 15 + [1] * 14 + [2] * 13 + [3] * 12 + [4] * 11 +
			[5] * 10 + [6] * 9 + [7] * 8 + [8] * 7 + [9] * 6 + 
			[10] * 5 + [11] * 4 + [12] * 3 + [13] * 2 + [14] * 1)

def DNA_crossover(f, m):
	numSplices = random.randint(15, 35)
	spliceLocs = []
	DNA = ''
	for i in range(numSplices):
		splice = random.randint(1, len(f))
		if splice in spliceLocs:
			pass
		else:
			spliceLocs.append(splice)
	spliceLocs.sort()
	readLoc = 0
	if random.random() >= 0.5:
		f, m = m, f #50% chance to begin with either male or female splice
	DNA_c1 = []
	DNA_c2 = []
	for idx, i in enumerate(spliceLocs):
		[DNA_c1.append(f[readLoc:i]) if idx % 2 else DNA_c1.append(m[readLoc:i])]
		[DNA_c2.append(m[readLoc:i]) if idx % 2 else DNA_c2.append(f[readLoc:i])]
		readLoc = i
	if len(spliceLocs) % 2:
		DNA_c1.append(m[readLoc:])
		DNA_c2.append(f[readLoc:])
		DNA1 = ''.join(DNA_c1)
		DNA2 = ''.join(DNA_c2)
	else:
		DNA_c1.append(f[readLoc:])
		DNA_c2.append(m[readLoc:])
		DNA1 = ''.join(DNA_c1)
		DNA2 = ''.join(DNA_c2)
	return DNA1, DNA2

def mutate(DNA, ctype):
	DNA = list(DNA)
	#Function to increase to mutations when evolution slows
	if ctype == 'tiger':
		maxMutations = (len(DNA) / 12) / (5 + epochTigers) 
	else:
		maxMutations = (len(DNA) / 12) / (5 + epochDeers)
	numMutations = random.randint(0, maxMutations)

	for i in range(numMutations):
		mutation = random.randint(0, (len(DNA) - 1))
		if DNA[mutation] == '0':
			DNA[mutation] = '1'
		else:
			DNA[mutation] = '0'
	DNA = ''.join(DNA)
	return DNA

def breed(ctype):
	#Select parents, with preference given to higher fitness scores
	idx = random.choice(idxList)
	idx2 = idx
	while idx2 == idx:
		idx2 = random.choice(idxList)
	
	if ctype == "tiger":
		#Take the DNA component from our random index values
		DNA1, DNA2 = DNA_crossover(tGenepool[idx][1], tGenepool[idx2][1])
		DNA1 = mutate(DNA1, ctype)
		DNA2 = mutate(DNA2, ctype)
		tPregnancies.append(DNA1)
		tPregnancies.append(DNA2)

	elif ctype == "deer":
		#Take the DNA component from our random index values
		DNA1, DNA2 = DNA_crossover(dGenepool[idx][1], dGenepool[idx2][1])
		DNA1 = mutate(DNA1, ctype)
		DNA2 = mutate(DNA2, ctype)
		dPregnancies.append(DNA1)
		dPregnancies.append(DNA2)

def get_DNA(ctype):
	DNA = ''
	if ctype == "tiger":
		DNA = tPregnancies[0]
		del tPregnancies[0]
	elif ctype == "deer":
		DNA = dPregnancies[0]
		del dPregnancies[0]
	return DNA

def pool(fitness, DNA, ctype, idNum):
	"""
	Check if our candidate has a good enough fitness score to be a
	candidate parent. If so, add it to the list and if necessary sort
	and trim the list to keep it at the appropriate size.
	"""
	if ctype == "deer" and len(dGenepool) < 15:
		dGenepool.append([fitness, DNA])
		dGenepool.sort(key=lambda x: x[0], reverse=True)
		# print 'THE LENGTH OF DNA:', len(DNA)
	elif ctype == "deer" and len(dGenepool) >= 15:
		if fitness > dGenepool[14][0]:
			dGenepool.append([fitness, DNA])
			dGenepool.sort(key=lambda x: x[0], reverse=True)
			del dGenepool[15:]

	elif ctype == "tiger" and len (tGenepool) < 15:
		tGenepool.append([fitness, DNA, idNum])
		tGenepool.sort(key=lambda x: x[0], reverse=True)
	elif ctype == "tiger" and len(tGenepool) >= 15:
		if fitness > tGenepool[14][0]:
			tGenepool.append([fitness, DNA, idNum])
			tGenepool.sort(key=lambda x: x[0], reverse=True)
			del tGenepool[15:]

#**********STUFF TO MOVE TO CONSTANTS*****************
poolSize = 30
plebPoolSize = 3
plebPoolChance = 0.1

#**********STUFF TO MOVE TO THE TOP*****************
tpool = []
dpool = []
tPlebPool = [] #pools for less fit individuals, included in breeding process for diversity
dPlebPool = []
def pool_2a(fitness, DNA, ctype, idNum):
	pool = tpool if ctype == "tiger" else dpool
	plebPool = tPlebPool if ctype == "tiger" else dPlebPool

	if len(pool) < poolSize: 
		#pool isn't full
		pool.append([fitness, DNA, idNum])
		pool.sort(key=lambda x: x[0], reverse=True)
	else if fitness > pool[poolSize-1][0]: 
		#pool is full, fitter than worst pool member
		pool.append([fitness, DNA, idNum])
		pool.sort(key=lambda x: x[0], reverse=True)
		del pool[poolSize:]
	else if random.random() <= plebPoolChance: 
		#small chance to get in to pleb pool
		plebPool.append([fitness, DNA, idNum])
		random.shuffle(plebPool)
		del plebPool[plebPoolSize:]



