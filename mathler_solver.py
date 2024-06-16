import myutils # type: ignore

def main():
    print("Please enter the solution that the hidden calculation equals:")
    solution = input()

    solver = myutils.SolutionFilter(solution)

    while True:
        solver.get_solution()
        solver.enter_feedback()
        print(f"There are {len(solver.possible_expr)} possible expressions left:")
        
if __name__ == '__main__':
    main()