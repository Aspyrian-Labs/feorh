"""
Name: plotter.py 
Authors: Oliver Giles & Max Potter
Date: July 2017
Description:
    - Use matplotlib to produce plots in order to analyse the performance of feorh.py
"""

import matplotlib.pyplot as plt
import numpy as np

#Get data
time,epoch,avFitness,avBreederFitness,wallDeathRate,killTotal = np.genfromtxt('fitnessAndDeath_160717_mutations_normal movement_01.txt', delimiter=',', skip_header=1, unpack=True)

#Clean data
time = time * 0.001
mask = np.where(avBreederFitness > 0)
avBreederFitness = avBreederFitness[mask]
timeReduced = time[mask]

#Set up plot area
fig = plt.figure(figsize=(12,6))
# ax1 = fig.add_subplot(121)
# ax2 = fig.add_subplot(122)

# #Plotting
# ax1.plot(time,avFitness)
# ax1.set_title('Average fitness for live tigers')
# ax1.set_xlabel('time')
# ax1.set_ylabel('Live average fitness')
# ax1.set_xlim([0,200])
# ax1.set_ylim(bottom = 0)

# ax2.plot(timeReduced,avBreederFitness)
# ax2.set_title('Average fitness of genepool')
# ax2.set_xlabel('time')
# ax2.set_ylabel('Gene pool average fitness')
# ax2.set_xlim([0,200])
# ax2.set_ylim(bottom = 0)

plt.plot(time,avFitness, label='Live average fitness')
plt.plot(timeReduced,avBreederFitness, label='Gene pool average fitness')
plt.title('Fitness values against time - mutations, normal movement')
plt.xlabel('time')
plt.ylabel('fitness')
plt.xlim([0,200])
plt.ylim(bottom = 0)
plt.legend()

# plt.show()

plt.savefig('fitness-mut-normMov-02.png')
