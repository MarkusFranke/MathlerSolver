### Showcase

ToDo (after UI is done)

### What in it?

A work-in-progess solver for the hard mathler: mathler.com/hard

### Why is this challenging:

- simple vectorisation is infeasible, since if we include infeasible equations of length 8 such as ")554+5/05" then we have 16^8 > 4e9 possible equations. This consumes a lot of disk space and buffers too long.
- finding all possible valid solutions that are exactly of length 8 and equal the solutionis also not an easy task. I could not think of a way to vectorise this.
- to find the "best" solution we need to evaluate how much the solution space decreases for each valid choice (to make a best greedy choice). This is also challenging to calculate for the first guess.
- the computational burden increases if we try more elaborate algorithmns, running f.e. Adaboost for every possible solution currently just takes too long.


