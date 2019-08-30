# feorh
A simple simulation of animals hunting written in pygame.

Top-down 2D tile based map with animals represented by coloured squares. 
Deer eat grass. Tigers hunt deer. Tigers hide in forests. 
The distribution of grass, forest and neutral tiles is randomly generated (Voronoi map generation).
Animals have neural network 'minds' with weights defined in their DNA (weight floats converted to sequences of bits).
Breeding is performed by splicing parent DNA and flipping bits for mutations.

AI is implemented as a static Keras neural network.

Implemented:
- Map generator
- Creature class to populate map with tigers and deer
- Vision system - each creature casts a number of rays evenly spread across their vision range. These form the inputs to the brains.
- Brains - each creature has 65 neuron neural network. Two output neurons control four movement states: forward, turn left/right and stop.
- Game loop - check for collisions, move creatures, pass new vision information, update screen.
- Pseudo-DNA generation - each network has weights that are initially generated from a randomised binary sequences, which are stored as strings.
- Genetic algorithm - fitness assessment determines which animals will breed, then by manipulation of a pair of DNA sequences offspring are generated.
