## MathlerSolver

Work-In-Progress

Workflow:
- Generate a .db with all possible expressions and the values of their evaluation
- Call those that evaluate to the desired solution.
- For the first guess it's computationally too expensive to use an good information criterium, as we usually have 5000-10000 possible solutions
- --> Use a frequency approach
- Use information criterium after receiving feedback

- Current Progress: Generation of sequences is done. First guess is done.
- ToDo come up with a convenient way to specify feedback (i.e. green, yellow, gey coloring of the positions of our guesses).
- find best possible guesses using an information criterium (which expression narrows down future solutions the most
- also deal with commutative solutions
