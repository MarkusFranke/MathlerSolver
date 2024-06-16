import sqlite3
import multiprocessing
from collections import defaultdict, Counter

class Expression:
    def __init__(self, expr):
        self.expr = expr
        self.symbols = "0123456789+-*/()"
        self.total_num_dict = self._count_symbols()
        self.guaranteed_num_dict = {pos: char for pos, char in enumerate(self.expr)}
    
    def _count_symbols(self):
        return {char: self.expr.count(char) for char in self.symbols}

class SolutionFilter:
    def __init__(self, solution):
        self.guess_count = 0
        self.symbols = "0123456789+-*/()"
        self.positions = range(8)

        print(f"loading db solutions for {solution}")
        possible_expr = load_expressions(sol = solution)
        self.possible_expr = [Expression(expr) for expr in possible_expr]
        self.unique_expr = load_expressions_with_no_repeating_chars(sol = solution, expressions = possible_expr)
        del possible_expr
        print("loading db solutions done")

        self.min_total_num_dict = {char: 0 for char in self.symbols} # a dict for each symbol "0123456789+-*/()" containing the min number of guaranteed occurrences
        self.max_total_num_dict = {char: 7 for char in self.symbols} # a dict for each symbol "0123456789+-*/()" containing the max number of possible occurrences
        self.has_been_gray_dict = {char: False for char in self.symbols} # a dict specifying if we found grey feedback for this char
        self.guaranteed_num_dict = {pos: None for pos in self.positions} # dict for known symbols for positions
        self.forbidden_num_dict = {pos: [] for pos in self.positions} # dict for each position containing forbidden symbols

    def _update_graybased_max(self):
        """For all gray positions we know the exact number of occurrences, which we keep track with min_count and use this function to set it to equal max_count"""
        for sym in self.symbols:
            if self.has_been_gray_dict[sym]:
                self.max_total_num_dict[sym] = self.min_total_num_dict[sym]
    
    def _is_expression_still_possible(self, expr) -> bool:
        """Update current possible expressions are no longer viable"""
        for pos, sym in enumerate(expr.expr):
            if self.guaranteed_num_dict[pos] is not None and self.guaranteed_num_dict[pos] != sym:
                return False
            #if sym in self.forbidden_num_dict[pos]:
            #    return False
        
        for sym in self.symbols:
            count = expr.total_num_dict[sym]
            if count < self.min_total_num_dict[sym] or count > self.max_total_num_dict[sym]:
                return False
        return True

    def _filter_expressions(self) -> list:
        """Use the updated feedback dicts to reduce current possible expressions"""
        self.possible_expr = [expr for expr in self.possible_expr if self._is_expression_still_possible(expr)]

    def _apply_feedback(self, guess:str, feedback:str):
        """Feedback should be in the form of a list with colours, denoted by 'dark', 'yellow', 'green' """
        self.guess_count += 1
        self.min_total_num_dict = {char: 0 for char in self.symbols} #resetting this is okay, as long as we always keep previously found symbols in the next equation

        for pos, sym in enumerate(guess):
            if feedback[pos] == "dark":
                self.has_been_gray_dict[sym] = True
                self.forbidden_num_dict[pos].append(sym)
            elif feedback[pos] == "yellow":
                self.min_total_num_dict[sym] += 1 # if not reset earlier, this would build up over guesses.
                self.forbidden_num_dict[pos].append(sym)
            elif feedback[pos] == "green":
                self.min_total_num_dict[sym] += 1
                self.guaranteed_num_dict[pos] = sym
        self._update_graybased_max()
        self._filter_expressions()
    
    def _get_first_solution(self) -> str:
        # Local Frequency approach: We calculate the relative frequency for every position, interpret this as its probability and choose the expression, where the 
        # quasi-likelihood, i.e. the product of all rel. frequencies for its positions is the largest.
        # But: these frequencies when interpreted as probabilities are not independent, thus looking at this approach probabilistically is flawed.
        rel_freq = calculate_relative_frequencies(self.unique_expr)

        print("Amount of possible unique first solutions: " + str(len(self.unique_expr)))

        score = []
        for expr in self.unique_expr:
            current_score = 1
            for pos in range(8):
                current_score *= rel_freq[pos][expr[pos]]
            score.append(current_score)
        assert len(score) == len(self.unique_expr)

        best_guess = self.unique_expr[score.index(max(score))]

        print("Approximately the best first guess: " + best_guess)
        return best_guess

    def _get_solution(self) -> str:
        """Get next best guess using information gain
        for guess_expr in self.possible_expr:
            for solution_expr in self.possible_expr:
                # Count how many solution
        """  

        # Placeholder: Based on frequency approach like initial guess:
        # Might need to this anyway if over 100 guesses are left

        possible_expr = [obj.expr for obj in self.possible_expr]

        rel_freq = calculate_relative_frequencies(possible_expr)

        score = []
        for expr in possible_expr:
            current_score = 1
            for pos in range(8):
                current_score *= rel_freq[pos][expr[pos]]
            score.append(current_score)
        assert len(score) == len(self.possible_expr)

        best_guess = possible_expr[score.index(max(score))]

        print("Approximately the best next guess: " + best_guess)
        return best_guess


    def get_solution(self) -> str:
        if self.guess_count == 0: #do == 0 when information solution implemented.
            return self._get_first_solution()
        else:
            return self._get_solution()
        
    def _parse_feedback(self) -> tuple[str, list]:
        """Terminal interaction for entering oracle feedback and submitted guesses"""

        def is_valid_input(string:str) -> bool:
            allowed_chars = {'d', 'y', 'g'}
            return set(string).issubset(allowed_chars) and len(string) == 8
        
        def adjust_colors(colors) -> list:
            colors_array = [None] * 8
            for i in range(len(colors)):
                if colors[i] == "d":
                    colors_array[i] = "dark"
                elif colors[i] == "y":
                    colors_array[i] = "yellow"
                elif colors[i] == "g":
                    colors_array[i] = "green"
            return colors_array
        
        while True:
            print(f"Please enter the expression you guessed:")
            guess = str(input()) #is str needed here?

            while True:
                print(f"Enter the colors as a single string, d=dark, y=yellow, g=green. Example: 'ggdydydg'")
                colors = input()
                if is_valid_input(colors):
                    break
                else:
                    print("Your input was invalid, please try again:")
            
            print(f"This was your last guessed expression: {guess}")
            print(f"And the associated sequence of colors you entered is:")
            colors = adjust_colors(colors)
            print(colors)
            print("Is this correct? [Y/n]")
            yes_or_no = str(input())
            if yes_or_no == "Y" or yes_or_no == "y":
                break
        
        return guess, colors
        
    def enter_feedback(self):
        guess, colors = self._parse_feedback()
        self._apply_feedback(guess, colors)


def load_expressions(sol:int) -> list:
    """Loads all expressions that equal the given solution"""

    conn = sqlite3.connect('valid_guesses.db')
    c = conn.cursor()

    def get_expr(solution:int) -> list:
        c.execute("SELECT string FROM valid_guesses WHERE integer = ?", (solution,))
        return [row[0] for row in c.fetchall()]

    solutions = get_expr(sol)
    c.close()
    return solutions

def has_unique_chars(input_str:str) -> bool:
    seen_chars = set()
    for char in input_str:
        if char in seen_chars:
            return False
        seen_chars.add(char)
    return True

def load_expressions_with_no_repeating_chars(sol:int, expressions:list = []) -> list:
    """Loads all expressions that do not have repeating characters and equal the solution"""


    def find_strings_with_unique_chars(string_list):
        pool = multiprocessing.Pool()
        results = pool.map(has_unique_chars, string_list)

        # Close the pool to free resources
        pool.close()
        pool.join()

        # Filter the original list based on the results
        return [string_list[i] for i, result in enumerate(results) if result]
    
    if len(expressions) < 1:
        return find_strings_with_unique_chars(load_expressions(sol))
    else:
        return find_strings_with_unique_chars(expressions)
    
def calculate_relative_frequencies(expr:list):
    
    expr_length = len(expr[0])
    assert expr_length > 0

    position_counters = [Counter() for _ in range(expr_length)]

    for s in expr:
        for i, char in enumerate(s):
            position_counters[i][char] += 1
    
    relative_frequencies = []
    for counter in position_counters:
        total_counts = sum(counter.values())
        relative_frequency = {char: count / total_counts for char, count in counter.items()}
        relative_frequencies.append(relative_frequency)
    
    return relative_frequencies

