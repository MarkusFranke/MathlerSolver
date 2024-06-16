import warnings
import time
import sqlite3
import math
import multiprocessing
from typing import Iterable


# ----- Generate all valid expressions -----

# Runtime: 30min-60min

def get_connection():
    """Establishes a connection to the SQLite database."""

    return sqlite3.connect('valid_guesses.db')

def add_expr(data):
    """Adds data to the sqlite database

    Args:
        data (list of tuples): A list where each tuple contains:
            - integer (int): evaluation of the math. expression
            - string (str): math. expression as stringS
    """
    conn = get_connection()
    c = conn.cursor()
    c.executemany("INSERT INTO valid_guesses "+
                  "(integer, string) VALUES (?, ?)", data)
    conn.commit()
    conn.close()


def valid_pos_for_closing_bracket(expr) -> bool:
    """Determines if there is an operator within the brackets.

    This function checks an expression in reverse to find an operator within
    brackets. It ensures that brackets do not enclose just a number, e.g., (80).

    Args:
        expr (str): The expression to check.

    Returns:
        bool: True if an operator is found within the brackets, otherwise False.
    
    Example:
        >>> valid_pos_for_closing_bracket("3 + (5 * 2)")
        True
        >>> valid_pos_for_closing_bracket("(80)")
        False
    """
    for char in reversed(expr):
        if char in "+-*/":
            return True
        elif char in "(":
            return False
    return True

def is_valid_formula(expr, tolerance=1e-8):
    """
    Checks if the given expression is a valid formula.

    This function evaluates an expression to determine if it is valid, i.e.
    does not contain divisions by zero.
    Furthermore the result of the (mathematical) expression shall be an integer.

    Args:
        expr (str): The expression to evaluate.
        tolerance (float, optional): The tolerance level for checking if the
        result is an integer. Defaults to 1e-8.

    Returns:
        bool: True if the expression is valid and evaluates to a non-negative
        integer within the specified tolerance, False otherwise.
    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            result = eval(expr) #filter remaining div by 0 and similar errors
            return result >= 0 and abs(result - round(result)) < tolerance
        except Exception:
            return False

def count_digits(n):
    """Counts the number of digits in an integer.

    Args:
        n (int): The integer whose digits are to be counted.

    Returns:
        int: The number of digits in the integer `n`.
    """

    if n == 0:
        return 1
    else:
        return math.floor(math.log10(abs(n))) + 1
    
def print_progress(start_time, operations,
                   iteration:int, total_iterations:int) -> None:
    """Prints the Progress"""

    if iteration % round(total_iterations / 100) == 0:
        percent = "{:.0%}".format(iteration / total_iterations)
        elapsed_time = round(time.time() - start_time)
        print(f"[----- Simple expressions {operations} ----- " +
                f"Current Progress: {percent} ----- " +
                f"Elapsed Time: {elapsed_time} seconds -----]")

def generate_expr_w_one_oper(start_time=time.time(), operations = "+-") -> None:
    # split this in "+-" and "*/" for better multiprocessing

    """
    Generates mathematical expressions with one operator of the form x oper y.

    Args:
        start_time (float, optional): The start time for measuring the elapsed
            time. Used to track progress.
        operations (str, optional): The operators to use in the expressions.
            Defaults to "+-". --> run twice, once with "+-", once with "*/"
    """

    conn = get_connection()
    c = conn.cursor()
    batch = []
    iter = 0
    total_iter = 24_300_000*len(operations)
    batch_size = 1_000_000

    def add_full_batches(num1:int, num2:int, oper:str, iter:int) -> int:
        expr1 = f"{num1}{oper}{num2}"
        expr2 = f"{num2}{oper}{num1}"
        iter += 1
        print_progress(start_time, operations, iter, total_iter)
        if is_valid_formula(expr1):
            batch.append((round(eval(expr1)), expr1))
        if is_valid_formula(expr2):
            batch.append((round(eval(expr2)), expr2))
        if len(batch) >= batch_size:
            add_expr(batch)
            batch.clear()
        return iter

    for num1 in range(1,1000):
        num2_len = 7-count_digits(num1)
        for num2 in range(10**(num2_len-1), 10**num2_len):
            for oper in operations:
                iter = add_full_batches(num1, num2, oper, iter)
                        
    if len(batch) > 0:
        add_expr(batch)

    conn.close()

    print(f"Generating expressions with {operations} is done.")

def generate_expr_w_two_opers(start_time=time.time()) -> None:
    """
    Generates simple mathematical expressions with two operators.
        They are of the form: x oper y oper z

    Args:
        start_time (float, optional): The start time for measuring the elapsed
            time.
    """
    conn = get_connection()
    c = conn.cursor()
    batch = []
    iter = 0
    total_iter = 116_640_000
    batch_size = 1_000_000
    operators = "+-*/"

    def generate_num1():
        for num1 in range(1, 10000):
            yield num1, 6 - count_digits(num1)

    def generate_num2(num_left):
        for num2 in range(1, 10 ** (num_left - 1)):
            yield num2, num_left - count_digits(num2)

    def generate_num3(num_left2):
        for num3 in range(max(1, 10 ** (num_left2 - 1)), 10 ** num_left2):
            yield num3

    def generate_all_numbers():
        for num1, num_left in generate_num1():
            for num2, num_left2 in generate_num2(num_left):
                for num3 in generate_num3(num_left2):
                    yield num1, num2, num3

    def gen_expr(num1:int, num2:int, num3:int) -> Iterable:
        for oper1 in operators:
            for oper2 in operators:
                yield f"{num1}{oper1}{num2}{oper2}{num3}"

    for num1, num2, num3 in generate_all_numbers():
        for expr in gen_expr(num1, num2, num3):
            iter += 1
            print_progress(start_time, "2o", iter, total_iter)
            if is_valid_formula(expr):
                batch.append((round(eval(expr)), expr))
                if len(batch) >= batch_size:
                    add_expr(batch)
                    batch.clear()
                
    if len(batch) > 0:
        add_expr(batch)

    print(f"Generating expressions with two operators is done.")

    conn.close()

def generate_expr_w_three_opers(start_time = time.time()) -> None:
    """
    Generates simple mathematical expressions with two operators.
        They are of the form: a oper b oper c oper d

    Args:
        start_time (float, optional): The start time for measuring the elapsed
            time.
    """

    conn = get_connection()
    c = conn.cursor()
    batch = []
    iter = 0
    total_iter = 16_796_160
    batch_size = 1_000_000
    operators = "+-*/"

    def generate_num1():
        for num1 in range(1, 100):
            yield num1, 5 - count_digits(num1)

    def generate_num2(num_left):
        for num2 in range(1, 10 ** (num_left - 2)):
            yield num2, num_left - count_digits(num2)

    def generate_num3(num_left2):
        for num3 in range(1, 10 ** (num_left2 - 1)):
            yield num3, num_left2 - count_digits(num3)

    def generate_num4(num_left3):
        for num4 in range(max(1, 10 ** (num_left3 - 1)), 10 ** num_left3):
            yield num4
        
    def generate_all_numbers():
        for num1, num_left in generate_num1():
            for num2, num_left2 in generate_num2(num_left):
                for num3, num_left3 in generate_num3(num_left2):
                    for num4 in generate_num4(num_left3):
                        yield num1, num2, num3, num4
    
    def gen_expr(num1:int, num2:int, num3:int, num4:int) -> Iterable:
        for oper1 in operators:
            for oper2 in operators:
                for oper3 in operators:
                    yield f"{num1}{oper1}{num2}{oper2}{num3}{oper3}{num4}"

    for num1, num2, num3, num4 in generate_all_numbers():
        for expr in gen_expr(num1, num2, num3, num4):
            iter += 1
            print_progress(start_time, "3o", iter, total_iter)
            if is_valid_formula(expr):
                batch.append((round(eval(expr)), expr))
                if len(batch) >= batch_size:
                    add_expr(batch)
                    batch.clear()
                            
    if len(batch) > 0:
        add_expr(batch)

    print(f"Generating expressions with three operators is done.")
    conn.close()

def generate_bracket_expressions(starting_expr="", iter=0,
                                 start_time=time.time()):
    """
    Generates the mathematical expressions with brackets.

    Args:
        starting_expr (str, optional): The starting expression for generating 
            bracket expressions.
        iter (int, optional): The initial iteration count.
        start_time (float, optional): The start time for measuring elapsed time. 
    """

    if start_time is None:
        start_time = time.time()

    conn = get_connection()
    c = conn.cursor()
    batch = []    

    full_digit = [str(num) for num in range(1,100)]
    single_digit = [str(num) for num in range(1,10)]
    double_digit = [str(num) for num in range(10,100)]

    total_iterations = 7_000_000
    iter = 0

    def is_int(expr):
        """
        Checks whether expression consists of only integer values.

        Args:
            expr (str): The expression to check.

        Returns:
            bool: True if the expression is an integer, False otherwise.
        """
        
        try:
            int(expr) #filter out all other mathematically invalid options
            return True
        except Exception:
            return False

    def mirror_expression(expr):
        """
        Mirrors the expression, i.e. a+(b-c) --> (c-b)+a

        Args:
            expr (str): The expression to mirror.

        Returns:
            str: The mirrored expression.
        """

        if is_int(expr[1:3]): #double digit is first number
            return expr[::-1][:2] + "(" + expr[::-1][3:5] + expr[1:3] + ")"
        elif is_int(expr[3:5]): #double digit is middle number
            return expr[::-1][:2] + "(" + expr[3:5] + expr[::-1][5:7] + ")" 
        else:
            return expr[6:] + expr[5] + "(" + expr[::-1][4:7] + ")"

    def print_progress(start_time, iteration:int, total_iterations:int) -> None:
        """
        Prints the progress of the expression generation.

        Args:
            start_time (float): The start time for measuring the elapsed time.
            iteration (int): The current iteration count.
            total_iterations (int): The total number of iterations.
        """

        if iteration % round(total_iterations / 100) == 0:
            percent = "{:.0%}".format(iteration / total_iterations)
            elapsed_time = round(time.time() - start_time)
            print(f"[----- Bracket expressions B ----- "
                    f"Current Progress: {percent} ----- "
                    f"Elapsed Time: {elapsed_time} seconds -----]")

    def is_valid_formula(expr, tolerance=1e-8):        
        """
        Checks if the given expression is a valid formula.

        Three checks:
            - is the expression mathematically valid or do we divide by 0.
            - is the result of the evaluation an integer
            - are the superfluous (which we do not believe happens in mathler) 

        Args:
            expr (str): The expression to evaluate.
            tolerance (float, optional): The tolerance level for checking if the
            result is an integer. Defaults to 1e-8.

        Returns:
            bool: True if the expression is valid and evaluates to a
            non-negative int within the specified tolerance, False otherwise.
        """

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                result = eval(expr) #filter remaining div by 0 and similar errors
                is_pos = result >= 0 
                is_int = abs(result - round(result)) < tolerance
                equation_no_brackets = expr.replace('(', '').replace(')', '')
                superfluous_brackets = eval(equation_no_brackets) == eval(expr)
                return is_pos and is_int and superfluous_brackets
            except Exception:
                return False
    def handle_complete_expression(current_expr):
        """
        Handles a complete expression and its mirrored version.

        Args:
            current_expr (str): The current complete expression.
        """
        nonlocal iter, batch

        def handle_expression(expr):
            nonlocal iter
            iter += 1
            print_progress(start_time, iter, total_iterations)
            if is_valid_formula(expr):
                batch.append((round(eval(expr)), expr))
                if len(batch) >= 10000:
                    add_expr(batch)
                    batch.clear()

        handle_expression(current_expr)
        mirror_expr = mirror_expression(current_expr)
        handle_expression(mirror_expr)

    def recurse_left(current_expr):
        """
        Recursively generates expressions by adding characters.

        Args:
            current_expr (str): The current partial expression.
        """
        nonlocal iter, batch

        def add_next_chars(next_chars):
            for char in next_chars:
                recurse_left(current_expr + char)

        if len(current_expr) == 8:
            handle_complete_expression(current_expr)
            return
        
        if len(current_expr) == 0:
            next_chars = ["("]
        else:
            next_chars_dict = {
                0: ["("],
                1: full_digit,
                2: "+-*/",
                3: full_digit if current_expr[-1] in "+-*/" else "+-*/",
                4: single_digit if current_expr[-1] in "+-*/" else [")"],
                5: "+-*/" if current_expr[-1] == ")" else [")"],
                6: "+-*/" if current_expr[-1] == ")" else double_digit,
                7: single_digit if current_expr[-1] in "+-*/" else []
            }
            next_chars = next_chars_dict.get(len(current_expr), [])
        add_next_chars(next_chars)

    recurse_left(starting_expr)

    if len(batch) > 0:
        add_expr(batch)

    conn.close()

    print(f"Generating bracket expressions is done.")

    
def main():
    """
    Generates various types of mathematical expressions using multiprocessing.
    """

    start_time = time.time()
    pool = multiprocessing.Pool()
    tasks = [
        pool.apply_async(generate_expr_w_one_oper, (start_time, "+-")),
        pool.apply_async(generate_expr_w_one_oper, (start_time, "*/")),
        pool.apply_async(generate_expr_w_two_opers, (start_time,)),
        pool.apply_async(generate_expr_w_three_opers, (start_time,)),
        pool.apply_async(generate_bracket_expressions, )
    ]
    for task in tasks:
        task.get()
    pool.close()
    pool.join()
    print("done")

if __name__ == '__main__':
    conn = sqlite3.connect('valid_guesses.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS valid_guesses " +
              "(integer INTEGER, string TEXT)")
    main()
    conn.close()