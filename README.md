## MathlerSolver

This repository contains a Python-based solver for the game Mathler, specifically the hard version of mathler. Running generate_valid_expressions.py generates all equations that we believe are used in the game. (Even more are valid, like starting with "+", or "-" or using zeros on their own, or (very rarely) a non-integer solution). These equations are stored in an sql database, and take up 3-4GB of disk space. The generator terminates in under 60 min even on below average hardware.

Running mathler_solver.py then allows you to get optimized equations for your next guess. The optimization of equations is still a work-in-progress:

Current Progress:
- Can solve the hard version of mathler in the terminal with you acting as agent for the information flow between website and solver. 
- First guess frequency approach has been implemented.
- Subsequent guesses currently also run this approach, but the approach is not adapted (repeats should be avoided here, too, if using this approach).
- Plan is to solve subsequent guesses using an information criterium, if the number of leftover possible solutions make it computationally feasible.

