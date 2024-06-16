import warnings
import time
import sqlite3
import math
import multiprocessing

# ----- Generate all valid expressions -----

# Only run this file as main if you have some time to spare or need to generate the expressions.
# In its current implementation without any multiprocessing this me around 8h to run.
#
# These are not all valid guesses
# I assume that the evaluation of an expressions has to be an integer.
#   There have been at least two documented cases in the last three years where this has not held true, but these represent a statistical outlier.
# I also assume that no expressions starts with "+" or "-", based on not finding any such solutions.
# That being said, both of these are valid guesses and I have not made the effort to atleast check if they are never the ideal guess concerning
#   our information criterion, despite probably not being the true guess. It is possible, though in my practical experience unlikely, that a guess like +1-2*3/4,
#   gobbling up all the operators, could make sense. In practice however, guessing lesser operators and more numbers seem to narrow the remaining answers down more,
#   as the absence or presense of operators usually narrows down usage of the others quite a bit.
# 
# Additionally -this one I'm sure about- I have (TODO) decided to not include any expressions with brackets that are superfluous, f.e. (12+3)+4.
# And full integers are not considered as a solution either, we want at least one operator.

# UPDATE: given the last month of mathler solutions, I decided not to include any expressions that include the number 0.
#   A lot of solutions include 0, since you can generate say 42 with 42+x*0, where x is any 3-digit-number.
#   Yet I couldn't find a single actual mathler where 0 was used. Thus our predictions will be much better if we don't account for it.
#   Additionally there don't seem to be any mathlers where the solution was negative, thus I'll remove these solutions from the database.

# Commutative solutions are allowed and will be considered in the algorithm. 
#   I assume that green marks are only given for a final commutative solution or for symbols that are in the correct place in the original correct solution.

# remove negative int solutions
# remove single 0's

def get_connection():
    return sqlite3.connect('valid_guesses.db')

def add_expr(data):
    conn = get_connection()
    c = conn.cursor()
    c.executemany("INSERT INTO valid_guesses (integer, string) VALUES (?, ?)", data)
    conn.commit()
    conn.close()


def valid_pos_for_closing_bracket(expr) -> bool:
    """
    Looks for an operator in the bracket
    we don't want brackets around a number like this: (80)
    """
    for char in reversed(expr):
        if char in "+-*/":
            return True
        elif char in "(":
            return False
    return True  # Added default return statement

def is_valid_formula(expr, tolerance=1e-8):
    """
    penultimate expression checker
    checks: expression should be valid
    checks: expression should return an int if calculated
    """

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            result = eval(expr) #filter out all other mathematically invalid options, like division by zero.
            return result >= 0 and abs(result - round(result)) < tolerance
        except Exception:
            return False

def count_digits(n):
    if n == 0:
        return 1
    return math.floor(math.log10(abs(n))) + 1

def generate_simple_expressions_with_one_operator(max_length=8, start_time=None, operations = "+-"):
    conn = get_connection()
    c = conn.cursor()
    batch = []
    iter = 0

    total_iter = 24300000*len(operations)

    for num1 in range(1,1000):
        num2_len = 7-count_digits(num1)
        for num2 in range(10**(num2_len-1), 10**num2_len):
            for oper in operations:
                expr1 = str(num1) + oper + str(num2)
                expr2 = str(num2) + oper + str(num1)
                if (iter - 456789) % (total_iter/100) == 0:
                    percent = ("{0:.0%}").format(iter / total_iter)
                    print(f'[----- simple expressions 1{operations} ----- Current Progress: {percent} ----- Elapsed Time: {round(time.time() - start_time)} seconds -----]')
                if is_valid_formula(expr1):
                    batch.append((round(eval(expr1)), expr1))
                    if len(batch) >= 1000000:
                        add_expr(batch)
                        batch.clear()
                if is_valid_formula(expr2):
                    batch.append((round(eval(expr2)), expr2))
                    if len(batch) >= 1000000:
                        add_expr(batch)
                        batch.clear()
                        
    if len(batch) > 0:
        add_expr(batch)

    print("Total Iters for simple 1: " + str(iter))
    conn.close()

def generate_simple_expressions_with_two_operators(max_length=8, start_time=None):
    conn = get_connection()
    c = conn.cursor()
    batch = []
    iter=0

    for num1 in range(1, 10000):
        num_left = 6-count_digits(num1)
        for num2 in range(1, 10**(num_left-1)):
            num_left2 = num_left - count_digits(num2)
            for num3 in range(max(1,10**(num_left2-1)), 10**num_left2):
                for oper in "+-*/":
                    for oper2 in "+-*/":
                        expr = str(num1) + oper + str(num2) + oper2 + str(num3)
                        if is_valid_formula(expr):
                            iter += 1
                            if (iter - 57) % 546993 == 0: #monitor this outside the if, much easier and more accurate!
                                percent = ("{0:.0%}").format(iter / 54_699_357)
                                print(f'[----- simple expressions 2 ----- Current Progress: {percent} ----- Elapsed Time: {round(time.time() - start_time)} seconds -----]')
                            batch.append((round(eval(expr)), expr))
                            if len(batch) >= 1_000_000:
                                add_expr(batch)
                                batch.clear()
                                         
    if len(batch) > 0:
        add_expr(batch)

    print("Total Iters for simple 2: " + str(iter))
    conn.close()


def generate_simple_expressions_with_three_operators(max_length=8, start_time=None):
    conn = get_connection()
    c = conn.cursor()
    batch = []
    iter = 0

    for num1 in range(1,100):
        num_left = 5-count_digits(num1)
        for num2 in range(1, 10**(num_left-2)):
            num_left2 = num_left - count_digits(num2)
            for num3 in range(1, 10**(num_left2-1)):
                num_left3 = num_left2- count_digits(num3)
                for num4 in range(max(1,10**(num_left3-1)), 10**num_left3):
                    for oper in "+-*/":
                        for oper2 in "+-*/":
                            for oper3 in "+-*/":
                                expr = str(num1) + oper + str(num2) + oper2 + str(num3) + oper3 + str(num4)
                                if is_valid_formula(expr):
                                    iter += 1
                                    if (iter - 97) % 65687 == 0:
                                        percent = ("{0:.0%}").format(iter / 6_568_797)
                                        print(f'[----- simple expressions 3 ----- Current Iter: {percent} ----- Elapsed Time: {round(time.time() - start_time)} seconds -----]')
                                    batch.append((round(eval(expr)), expr))
                                    if len(batch) >= 1_000_000:
                                        add_expr(batch)
                                        batch.clear()
                                        
    if len(batch) > 0:
        add_expr(batch)

    print("Total Iters for simple 3: " + str(iter))
    conn.close()

def generate_bracket_expressions(max_length=8, starting_expr="", iter=0, start_time=None):
    if start_time is None:
        start_time = time.time()

    conn = get_connection()
    c = conn.cursor()
    batch = []    

    full_digit = [str(num) for num in range(1,100)]
    single_digit = [str(num) for num in range(1,10)]
    double_digit = [str(num) for num in range(10,100)]

    def mirror_expression(expr):
        '''mirrors by mirroring full numbers'''

        def is_int(expr):
            """Checks whether expression consists of only integer values"""
            try:
                int(expr) #filter out all other mathematically invalid options, like division by zero. 
                return True
            except Exception:
                return False
        
        if is_int(expr[1:3]): #double digit is first number
            return expr[::-1][:2] + "(" + expr[::-1][3:5] + expr[1:3] + ")"
        elif is_int(expr[3:5]): #double digit is middle number
            return expr[::-1][:2] + "(" + expr[3:5] + expr[::-1][5:7] + ")" 
        else:
            return expr[6:] + expr[5] + "(" + expr[::-1][4:7] + ")"

    def recurse_left(current_expr):
        nonlocal iter, batch
        
        if len(current_expr) == 0:
            recurse_left("(")
                
        elif len(current_expr) == max_length:
            if is_valid_formula(current_expr):
                iter += 1
                if (iter - 69) % 3453 == 0:
                    percent = ("{0:.0%}").format(iter / 345369)
                    print(f'[----- bracket expressions  ----- Current Progress: {percent} ----- Elapsed Time: {round(time.time() - start_time)} seconds -----]')
                batch.append((round(eval(current_expr)), current_expr))
                if len(batch) >= 10000:
                    add_expr(batch)
                    batch.clear()
            mirror_expr = mirror_expression(current_expr)
            if is_valid_formula(mirror_expr):
                iter += 1
                if (iter - 69) % 3453 == 0:
                    percent = ("{0:.0%}").format(iter / 345369)
                    print(f'[----- bracket expressions  ----- Current Progress: {percent} ----- Elapsed Time: {round(time.time() - start_time)} seconds -----]')
                batch.append((round(eval(mirror_expr)), mirror_expr))
                if len(batch) >= 1000000:
                    add_expr(batch)
                    batch.clear()
            return
        
        elif len(current_expr) == 1: # (
            for num in full_digit:
                recurse_left(current_expr + num)

        elif len(current_expr) == 2: # (1
            for oper in "+-*/":
                recurse_left(current_expr + oper)

        elif len(current_expr) == 3: # (12 or (1+
            if current_expr[-1] in "+-*/":
                for num in full_digit:
                    recurse_left(current_expr + num)
            else:
                for oper in "+-*/":
                    recurse_left(current_expr + oper)

        elif len(current_expr) == 4: # (1+2 or (12+
            if current_expr[-1] in "+-*/":
                for num in single_digit:
                    recurse_left(current_expr + num)
            else:
                recurse_left(current_expr + ")")
        
        elif len(current_expr) == 5: # (1+2) or (12+3 or (1+23
            if current_expr[-1] == ")":
                for oper in "+-*/":
                    recurse_left(current_expr + oper)
            else:
                assert current_expr[-1] not in "+-*/"
                recurse_left(current_expr + ")")
        
        elif len(current_expr) == 6: # (1+2)+ or (12+2) or (1+12)
            if current_expr[-1] == ")":
                for oper in "+-*/":
                    recurse_left(current_expr + oper)
            else:
                assert current_expr[-1] in "+-*/"
                for num in double_digit:
                    recurse_left(current_expr + num)
        
        elif len(current_expr) == 7:
            assert current_expr[-1] in "+-*/"
            for num in single_digit:
                recurse_left(current_expr + num)

    recurse_left(starting_expr)

    if len(batch) > 0:
        add_expr(batch)
    print("Total Iters for brackets: " + str(iter))

    conn.close()

    
def main():
    start_time = time.time()
    
    pool = multiprocessing.Pool()

    tasks = [
        pool.apply_async(generate_simple_expressions_with_one_operator, (8, start_time, "+-")),
        pool.apply_async(generate_simple_expressions_with_one_operator, (8, start_time, "*/")),
        pool.apply_async(generate_simple_expressions_with_two_operators, (8, start_time)),
        pool.apply_async(generate_simple_expressions_with_three_operators, (8, start_time)),
        pool.apply_async(generate_bracket_expressions,)
    ]

    for task in tasks:
        task.get()
    
    pool.close()
    pool.join()

    print("done")

if __name__ == '__main__':
    conn = sqlite3.connect('valid_guesses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS valid_guesses (integer INTEGER, string TEXT)''')
    main()
    conn.close()
