import numpy as np
from numba import njit
import time
import itertools

@njit
def digit(n:int) -> int:
    if n < 1:
        return -1
    else:
        return int(np.floor(np.log10(n)+1))
    
@njit
def find_all_mul_for_sol(sol:int, expr_len:int, prefix:str, postfix:str, 
                         multiply_com_num:int = 1) -> list:
    """
    Generates math expr with one operator of the form x * y.

    Args:
        solution (int): The solution the operator should equal
        expr_len (int) : Length of expression: len("x*y")
        prefix (str): prefix to be added to the start of the expression
        postfix (str): postfix to be added to the end of the expression
        multiply_com_num (int): multiply com_sol, based on comb of others

    Returns: list filled with tuples (prefix + "x+y" + postfix, n),
        expr_len = length of "x*y", n = amount of commutative solutions
    """

    results = []
    sol_red = sol
    factors = []
    max_iter = int(np.floor(np.sqrt(sol_red)))
    for iter in range(2,max_iter+1):
        while sol_red % iter == 0:
            factors.append(iter)
            sol_red //= iter
    if sol_red > 1: # sol is prime
        factors.append(sol_red)    
    # Now we have the prime factorization

    # Generate all partitions using bitmasking
    len_factors = len(factors)
    expr = []

    for bitmask in range(1, 2**len_factors):
        part1_primes = []
        part2_primes = []
        
        for i in range(len_factors):
            if bitmask & (1 << i):
                part1_primes.append(factors[i])
            else:
                part2_primes.append(factors[i])
        
        # Calculate product of each partition
        x = 1
        y = 1
        
        for prime in part1_primes:
            x *= prime
        
        for prime in part2_primes:
            y *= prime
        
        # Check if y * z = x
        assert x * y == sol
        if expr_len == digit(x)+digit(y)+1 and (x,y) not in expr:
            if x == y and x != 1 and y != 1:
                results.append((f"{prefix}{x}*{y}{postfix}",1*multiply_com_num))
            elif x != y and x != 1 and y != 1:
                results.append((f"{prefix}{x}*{y}{postfix}",2*multiply_com_num))
            expr.append((x,y))

    return results 

def gen_one_op(solution:int) -> np.ndarray:
    """
    Generates math expr with one operator of the form x oper y.

    Args:
        solution (int): The solution the operator should equal

    Returns:
        ... not sure yet
    """
    @njit
    def gen_one_plus(sol: int):
        """
        Generates math expressions of the form x + y = sol.
        """

        ranges = [
            (1100, 10998, 1000, 999, 99, 9999, 100),
            (10010, 100098, 10000, 99, 9, 99999, 10),
            (100001, 1000008, 100000, 9, 0, 999999, 1)
        ]
        
        expressions = []

        for range_ in ranges:
            RANGE_MIN, RANGE_MAX, x_low, x_high, x_low, y_high, y_low = range_
            if RANGE_MIN <= sol <= RANGE_MAX:
                #x_min = np.max(np.array([x_low, int(np.ceil(sol/2)),
                                         #sol-x_high]))
                #x_max = np.min(np.array([y_high,sol-y_low]))
                x_min = max((x_low, int(np.ceil(sol/2)), sol-x_high))
                x_max = min(y_high,sol-y_low)

                for x in range(x_min, x_max + 1):
                    y = sol - x # x == y impossible due to digit sum
                    expressions.append((x, y, 2))
                    expressions.append((y, x, 2))

        return expressions
    
    @njit
    def gen_one_minus(sol:int):
        """Generates math expr with one operator of the form x - y."""

        x_min = max((1000, sol+1))
        expressions = []

        for x in range(x_min,999_999):
            y = x - sol
            digits = digit(x) + digit(y)
            if digits == 7:
                expressions.append((x,y,1))
            elif digits > 7:
                break

        return expressions # here only x and y, coerse into string
    
    @njit
    def gen_one_mul(sol:int):
        """
        Generates math expr with one operator of the form x * y.

        Args:
            solution (int): The solution the operator should equal
        """
        results = []
        com_sol_num = []

        sol_red = sol
        factors = []
        max_iter = int(np.floor(np.sqrt(sol_red)))
        for iter in range(2,max_iter+1):
            while sol_red % iter == 0:
                factors.append(iter)
                sol_red //= iter
        if sol_red > 1: # sol is prime
            factors.append(sol_red)
        
        # Now we have the prime factorization

            # Generate all partitions using bitmasking

        len_factors = len(factors)
        for bitmask in range(1, 2**len_factors):
            part1_primes = []
            part2_primes = []
            
            for i in range(len_factors):
                if bitmask & (1 << i):
                    part1_primes.append(factors[i])
                else:
                    part2_primes.append(factors[i])
            
            # Calculate product of each partition
            x = 1
            y = 1
            
            for prime in part1_primes:
                x *= prime
            
            for prime in part2_primes:
                y *= prime
            
            # Check if y * z = x
            assert x * y == sol
            if x == y and x != 1 and y != 1:
                results.append((x, y, 1))
                com_sol_num.append(1)
            elif x != y and x != 1 and y != 1:
                results.append((y, x, 2))
                com_sol_num.append(2)

        return results, com_sol_num
    
    @njit
    def gen_one_div(sol):
        """
        Generates math expr with one operator of the form x * y. Numba is used
        to run the code at (rougly) C speed

        Args:
            solution (int): The solution the operator should equal
        """

        # sol = x/y --> x = sol * y 
        y = 2
        x = sol*y
        results = []
        while digit(x) + digit(y) <= 7:
            if (int(np.log10(x))+1 + int(np.log10(y))+1) == 7:
                results.append((x,y,1))
            y += 1
            x = sol*y

        return results

    # Todo change these into: str + number of commutative solutions

    @njit
    def gen_expr(ma_plus, oper:str, sol:int):
        ma_plus = gen_one_plus(sol)
        first_elements = np.array([tup[0] for tup in ma_plus])
        second_elements = np.array([tup[1] for tup in ma_plus])
        third_elements = np.array([tup[2] for tup in ma_plus])
        expr = []
        com_count = []
        for i in range(len(first_elements)):
            expr.append(f"{first_elements[i]}{oper}{second_elements[i]}")
            com_count.append(third_elements[i])
        return expr, com_count

    def safe_gen_expr(gen_func, oper:str, sol:int):
        expr, com_count = [], []
        if gen_func(sol):
            expr, com_count = gen_expr(gen_func, oper, sol)
        return expr, com_count
    
    #expr, com_count = safe_gen_expr(gen_one_plus, "+", solution)
    #expr_min, com_count_min = safe_gen_expr(gen_one_minus, "-", solution)
    #expr_mul, com_count_mul = safe_gen_expr(gen_one_mul, "*", solution)
    #expr_div, com_count_div = safe_gen_expr(gen_one_div, "/", solution)

    operations = [('+', gen_one_plus), ('-', gen_one_minus),
                  ('*', gen_one_mul), ('/', gen_one_div)]
    
    all_expr = []
    all_com_count = []
    for oper, gen_func in operations:
        expr, com_count = safe_gen_expr(gen_func, oper, solution)
        all_expr.extend(expr)
        all_com_count.extend(com_count)

    assert len(all_expr) == len(all_com_count)
    
    return all_expr
        
# ============================================================================ #

def gen_two_oper(sol:int):
    
    def gen_plus_plus(sol): 
        results = []

        #Case: xxxx + y + z = sol
        if 1002 <= sol <= 10017: # xxxx + y + z
            for y in range(1,10):
                for z in range(y,10): # z > y -> no duplicates
                    x = sol - y - z
                    if digit(x) == 4:
                        if y == z:
                            results.extend([
                                (f"{x}+{y}+{y}", 3),
                                (f"{y}+{x}+{y}", 3),
                                (f"{y}+{y}+{x}", 3)
                            ])
                        else:
                            results.extend([
                                (f"{x}+{y}+{z}", 6),
                                (f"{x}+{z}+{y}", 6),
                                (f"{y}+{x}+{z}", 6),
                                (f"{y}+{z}+{x}", 6),
                                (f"{z}+{x}+{y}", 6),
                                (f"{z}+{y}+{x}", 6)
                            ])
        # Case: xxx + yy + z
        if 120 <= sol <= 1197: 
            for x in range(max(1,sol-99-999),min(10, sol-10-100+1)):
                for y in range(max(10,sol-x-999),min(100,sol-x-100+1)):
                    z = sol - x - y
                    if digit(z) == 3:
                        results.extend([
                            (f"{x}+{y}+{z}", 6),
                            (f"{x}+{z}+{y}", 6),
                            (f"{y}+{x}+{z}", 6),
                            (f"{y}+{z}+{x}", 6),
                            (f"{z}+{x}+{y}", 6),
                            (f"{z}+{y}+{x}", 6)
                        ])
    
        # Case: xx + yy + zz
        if 30 <= sol <= 297:
            for x in range(max(10,sol-99-99), min(100,sol-10-10+1)):
                for y in range(max(x,sol-x-99), min(100,sol-10-x+1)):
                    z = sol - x - y
                    if digit(z) == 2 and z > y: # second cond avoids duplicates
                        if x != y and y != z and x != z:
                           results.extend([
                                (f"{x}+{y}+{z}", 6),
                                (f"{x}+{z}+{y}", 6),
                                (f"{y}+{x}+{z}", 6),
                                (f"{y}+{z}+{x}", 6),
                                (f"{z}+{x}+{y}", 6),
                                (f"{z}+{y}+{x}", 6)
                            ])
                        elif x == y and y == z:
                            results.append((f"{x}+{y}+{z}", 1))
                        elif x == y:
                            results.extend([
                                (f"{z}+{x}+{x}", 3),
                                (f"{x}+{z}+{x}", 3),
                                (f"{x}+{x}+{z}", 3)
                            ])
                        elif y == z:
                            results.extend([
                                (f"{x}+{z}+{z}", 3),
                                (f"{z}+{x}+{z}", 3),
                                (f"{z}+{z}+{x}", 3)
                            ])
                        elif x == z:
                            results.extend([
                                (f"{y}+{x}+{x}", 3),
                                (f"{x}+{y}+{x}", 3),
                                (f"{x}+{x}+{y}", 3)
                            ])
        return results
        
    def gen_plus_min(sol):
        results = []

        # Case: xxxx + y - z
        if 992 <= sol <= 10007:
            for x in range(1,10): # the negative number
                for y in range(x,10):
                    z = sol + x - y
                    if digit(z) == 4:
                        results.extend([
                            (f"{z}+{y}-{x}", 4),
                            (f"{y}+{z}-{x}", 4),
                            (f"{z}-{x}+{y}", 4),
                            (f"{y}-{x}+{z}", 4)
                        ])
        # Case: xxx + yy - z
        if 101 <= sol <= 1097:
            for x in range(1,10): #the negative number
                for y in range(10,100):
                    z = sol + x - y
                    if digit(z) == 3:
                        results.extend([
                            (f"{z}+{y}-{x}", 4),
                            (f"{y}+{z}-{x}", 4),
                            (f"{z}-{x}+{y}", 4),
                            (f"{y}-{x}+{z}", 4)
                        ])
        # Case: xxx - yy + z
        if 2 <= sol <= 998:
            for y in range(1,10):
                for x in range(10,100): # the negative number
                    z = sol + x - y
                    if digit(z) == 3:
                        results.extend([
                            (f"{z}+{y}-{x}", 4),
                            (f"{y}+{z}-{x}", 4),
                            (f"{z}-{x}+{y}", 4),
                            (f"{y}-{x}+{z}", 4)
                        ])
        # Case: xx + yy - zz
        if sol <= 188:
            for x in range(10,100): 
                for y in range(x,100):
                    z = x + y - sol
                    if digit(z) == 2:
                        if x != y:
                            results.extend([
                                (f"{x}-{y}-{z}", 4),
                                (f"{y}+{x}-{z}", 4),
                                (f"{x}-{z}+{y}", 4),
                                (f"{y}-{z}+{x}", 4)
                            ])
                        else:                            
                            results.extend([
                                (f"{x}-{x}-{z}", 4),
                                (f"{x}-{z}+{x}", 4)
                            ])

        # Case: xx + y - zzz
        if sol <= 8:
            for z in range(100,108+1): # The negative number
                for y in range(1,10):
                    x = sol - y + z
                    if digit(x) == 2:
                        results.extend([
                            (f"{z}+{y}-{x}", 4),
                            (f"{y}+{z}-{x}", 4),
                            (f"{z}-{x}+{y}", 4),
                            (f"{y}-{x}+{z}", 4)
                        ])
        return results
    
    def gen_min_min(sol):
        # sol = x - y - z
        results = []
        
        # Case: xxxx-y-z
        if 988 <= sol <= 9997:
            for z in range(1,10):
                for y in range(z,10):
                    x = sol + y + z
                    if digit(x) == 4 and y != z:
                        results.append((f"{x}-{y}-{z}", 2))
                        results.append((f"{x}-{z}-{y}", 2))
                    elif digit(x) == 4 and y == z:
                        results.append((f"{x}-{y}-{z}", 1))
        # Case: xxx - yy - z
        if sol <= 988:
            for z in range(1,10):
                for y in range(10,100):
                    x = sol + y + z
                    if digit(x) == 3:
                        results.append((f"{x}-{y}-{z}", 2))
                        results.append((f"{x}-{z}-{y}", 2))
        # Case: xx - yy - zz
        if sol <= 79:
            for z in range(10,89-sol+1):
                for y in range(z,99-z-sol+1):
                    x = sol + y + z
                    if digit(x) == 2 and y != z:
                        results.append((f"{x}-{y}-{z}", 2))
                        results.append((f"{x}-{z}-{y}", 2))
                    elif digit(x) == 2 and y == z:
                        results.append((f"{x}-{y}-{z}", 1))
        return results
    
    def gen_plus_mul(sol):
        results = []

        # Case: xxxx*y+z and xxx*yy+z
        if 1001 <= sol <= 98910:
            for z in range(1,10):
                results.extend(find_all_mul_for_sol(sol-z, 6, f"{z}+","",2))
                results.extend(find_all_mul_for_sol(sol-z, 6, "",f"+{z}",2))

        # Case: xxx*y+zz and xx*yy+zz
        if 110 <= sol <= 9900:
            for z in range(10,100):
                results.extend(find_all_mul_for_sol(sol-z, 5, f"{z}+","",2))
                results.extend(find_all_mul_for_sol(sol-z, 5, "",f"+{z}",2))
        
        # Case: xx*y+zzz
        if 120 <= sol <= 1890:
            for y in range(2,10):
                for x in range(10,100):
                    xy = x*y
                    if xy > sol-100:
                        break
                    z = sol-xy
                    if 100 <= z <= 999:
                        results.extend([
                            (f"{x}*{y}+{z}", 4),
                            (f"{y}*{x}+{z}", 4),
                            (f"{z}+{x}*{y}", 4),
                            (f"{z}+{y}*{x}", 4)
                        ])

        # Case: x*y+zzzz
        if 1004 <= sol <= 10080:
            for x in range(2,10):
                for y in range(x,10):
                    z = sol-x*y
                    if 1000 <= z <= 9999:
                        if x != y:
                            results.extend([
                                (f"{x}*{y}+{z}", 4),
                                (f"{y}*{x}+{z}", 4),
                                (f"{z}+{x}*{y}", 4),
                                (f"{z}+{y}*{x}", 4)
                            ])
                        else:
                            results.extend([
                                (f"{x}*{x}+{z}", 2),
                                (f"{z}+{x}*{x}", 2)
                            ])
        return results

    def gen_min_mul(sol):
        results = []

        # Case: xxxx*y-z and xxx*yy-z
        if 991 <= sol <= 98900:
            for z in range(1,10):
                results.extend(find_all_mul_for_sol(sol+z, 6, "",f"-{z}",1))

        # Case: xx*yy-zz and xxx*y-zz
        if 0 <= sol <= 9791:
            for z in range(10,100):
                results.extend(find_all_mul_for_sol(sol+z, 5, "",f"-{z}",1))

        # Case: xx*y-zzz --> sol + zzz = xx*y
        if 0 <= sol <= 791:
            for y in range(2,10):
                for x in reversed(range(10,100)):
                    xy = x*y
                    if xy < sol+100: #if x*y < sol + min(zzz) --> early exit
                        break
                    z = xy-sol
                    if 100 <= z <= 999:
                        results.extend([
                            (f"{x}*{y}-{z}", 2),
                            (f"{y}*{x}-{z}", 2)
                        ])

        # Case: x*y-zzzz --> not possible with pos solutions!

        return results

    def gen_div_plus(sol):
        # Case: all x/y+z
        results = []
        for y in reversed(range(2,100)): # The divisor
            x = y
            while (x/y+1 <= sol):
                z = int(sol-x/y)
                if digit(x) + digit(y) + digit(z) == 6:
                    results.extend([
                        (f"{x}/{y}+{z}", 2),
                        (f"{z}+{x}/{y}", 2),
                    ])
                x += y
        return results

    def gen_div_min(sol):
        # Case: all sol = x/y-z --> z = x/y-sol --> x/y = z+sol
        results = []
        for y in reversed(range(2,100)): # The divisor
            x = y
            while (x/y - sol <= 499): # Biggest z can be is in xxx/y-zzz
                z = int(x/y-sol)
                if digit(x) + digit(y) + digit(z) == 6 and z > 0:
                    results.extend([
                        (f"{x}/{y}-{z}", 1),
                    ])
                x += y
        return results

    def gen_mul_div(sol):
        # Case: x*y/z = sol <-> sol*z = x*y
        results = []

        # Case: xxxx*y/z and xxx*yy/z:
        if 111 < sol < 49451:
            for z in range(2,10):
                results.extend(find_all_mul_for_sol(int(sol*z), 6, "",
                                                    f"/{z}", 1))

        # Case: xxx*y/zz or xx*yy/zz
        if 1 < sol < 981:
            for z in range(10,100):
                if (sol*z > 9801):
                    break
                results.extend(find_all_mul_for_sol(int(sol*z), 5, "",
                                                    f"/{z}", 1))

        # Case: xx*y/zzz <-> sol*zzz = xx*y
        if 1 <= sol < 9:
            for y in reversed(range(2,10)):
                if (y*99 < sol*100):
                    break
                for x in reversed(range(10,100)):
                    xy = int(x*y)
                    z = int(xy/sol)
                    if (z < 100):
                        break
                    if xy % sol == 0 and digit(z) == 3:
                        results.extend([
                            (f"{x}*{y}/{z}", 2),
                            (f"{y}*{x}/{z}", 2)
                        ])
        return results

    def gen_mul_mul(sol):
        results = []
        sol_red = sol
        factors = []
        expr = []
        
        # Factorize sol
        max_iter = int(np.floor(np.sqrt(sol_red)))
        for iter in range(2, max_iter + 1):
            while sol_red % iter == 0:
                factors.append(iter)
                sol_red //= iter
        if sol_red > 1:  # sol is prime
            factors.append(sol_red)

        # Generate all partitions using bitmasking
        len_factors = len(factors)
        for bitmask in range(1, 2**len_factors):
            part1_primes = []
            part2_primes = []
            part3_primes = []
            
            for i in range(len_factors):
                if bitmask & (1 << i):
                    part1_primes.append(factors[i])
                elif bitmask & (1 << i + 1):
                    part2_primes.append(factors[i])
                else:
                    part3_primes.append(factors[i])
            
            # Calculate product of each partition
            a = 1
            b = 1
            c = 1            
            for prime in part1_primes:
                a *= prime
            for prime in part2_primes:
                b *= prime
            for prime in part3_primes:
                c *= prime
            
            assert a * b * c == sol

            # Check if digits conditions are satisfied
            if (digit(a) + digit(b) + digit(c) == 6
                and a != 1 and b != 1 and c != 1
                and set([a,b,c]) not in expr):                
                if a == b == c and a != 1:
                    results.append((f"{a}*{b}*{c}", 1))
                elif a == b != c:
                    results.extend([
                        (f"{c}*{b}*{b}", 3),
                        (f"{b}*{c}*{b}", 3),
                        (f"{b}*{b}*{c}", 3),
                    ])
                elif a == c != b and a != 1:
                    results.extend([
                        (f"{b}*{a}*{a}", 3),
                        (f"{a}*{b}*{a}", 3),
                        (f"{a}*{a}*{b}", 3),
                    ])
                elif b == c != a and b != 1:
                    results.extend([
                        (f"{a}*{b}*{b}", 3),
                        (f"{b}*{a}*{b}", 3),
                        (f"{b}*{b}*{a}", 3),
                    ])
                    results.append((f"{a}*{b}*{b}", 3))
                elif a != b != c:
                    results.extend([
                        (f"{a}*{b}*{c}", 6),
                        (f"{a}*{c}*{b}", 6),
                        (f"{b}*{a}*{c}", 6),
                        (f"{b}*{c}*{a}", 6),
                        (f"{c}*{a}*{b}", 6),
                        (f"{c}*{b}*{a}", 6),
                        ])
            expr.append(set([a,b,c]))
        return results
        
    def gen_div_div(sol):
        # Case: xxxx / y / z <--> z*y*sol = xxxx
        results = []
        if 1 <= sol < 2500:
            for z in range(2,10):
                for y in range(z,10):
                    x = int(z*y*sol)
                    if x > 9999:
                        break
                    if x >= 1000:
                        if z != y:
                            results.extend([
                                (f"{x}/{y}/{z}", 2),
                                (f"{x}/{z}/{y}", 2)
                            ])
                        else:
                            results.append((f"{x}/{y}/{z}", 1))
        
        # Case: xxx / yy / z <-> z*yy*sol = xxx
        if 1 <= sol < 50:
            for z in range(2,10):
                if (z*10*sol > 999):
                    break
                for y in range(10,100):
                    x = int(z*y*sol)
                    if (x > 999):
                        break
                    if x >= 100:
                        results.extend([
                            (f"{x}/{y}/{z}", 2),
                            (f"{x}/{z}/{y}", 2),
                        ])
        
        # Case: xx / yy / zz not possible, as yy*zz >= 100
        
        return results
    
    def concat_results(sol:int,*functions):
        combined_results = []
        for func in functions:
            combined_results.extend(func(sol))
        return combined_results

    return concat_results(sol, gen_plus_plus,gen_plus_min,gen_min_min,
                          gen_plus_mul,gen_div_plus, gen_min_mul,
                          gen_div_min,gen_mul_mul,gen_div_div,gen_mul_div)
    
# ---------------------------------------------------------------------------- #
import ast
import operator
        
def gen_three_oper(sol): # Maybe use a database for this one? eh
    # a oper b oper c oper d = sol

    results = []
    # op3 in "+-", op2, op1 free
    for a, b, c in itertools.product(list(range(1,10)), repeat=3):
        for op1, op2 in itertools.product(["+", "-", "*", "/"], repeat=2):
            if op1 in "*/" and (a == 1 or b == 1):
                continue
            if op2 in "*/" and (b == 1 or c == 1):
                continue
            for op3 in "+-":
                if op3 == "+":
                    d = sol-(eval(f"{a}{op1}{b}{op2}{c}"))
                    if 10 <= d <= 99:
                        d = int(d)
                        results.append((f"{a}{op1}{b}{op2}{c}{op3}{d}"))
                        results.append((f"{a}{op1}{b}{op3}{d}{op2}{c}"))
                        results.append((f"{a}{op3}{d}{op1}{b}{op2}{c}"))
                        results.append((f"{d}{op3}{a}{op1}{b}{op2}{c}"))
                else:
                    d = (eval(f"{a}{op1}{b}{op2}{c}"))-sol
                    if 10 <= d <= 99:
                        d = int(d)
                        results.append((f"{a}{op1}{b}{op2}{c}{op3}{d}"))
                        results.append((f"{a}{op1}{b}{op3}{d}{op2}{c}"))
                        results.append((f"{a}{op3}{d}{op1}{b}{op2}{c}"))
    
    # all "*" and "/"
    for a, b, c in itertools.product(list(range(2,10)), repeat=3):
        for op1, op2, op3 in itertools.product(["*", "/"], repeat=3):
            partial_sol = eval(f"{a}{op1}{b}{op2}{c}")
            if op3 == "*" and partial_sol != 0:
                d = sol/partial_sol
                if 10 <= d <= 99 and d.is_integer():
                    how_many_mul = (op1 == "*") + (op2 == "*") + (op3 == "*")
                    n_c = (how_many_mul + 1) * 6
                    results.append((f"{a}{op1}{b}{op2}{c}{op3}{int(d)}", n_c))
                    results.append((f"{a}{op1}{b}{op3}{int(d)}{op2}{c}", n_c))
                    results.append((f"{a}{op3}{int(d)}{op1}{b}{op2}{c}", n_c))
                    results.append((f"{int(d)}{op3}{a}{op1}{b}{op2}{c}", n_c))
            elif sol != 0:
                d = (eval(f"{a}{op1}{b}{op2}{c}"))/sol
                if 10 <= d <= 99 and d.is_integer():
                    how_many_mul = (op1 == "*") + (op2 == "*") + (op3 == "*")
                    n_c = (how_many_mul + 1) * 6
                    results.append((f"{a}{op1}{b}{op2}{c}{op3}{int(d)}", n_c))
                    results.append((f"{a}{op1}{b}{op3}{int(d)}{op2}{c}", n_c))
                    results.append((f"{a}{op3}{int(d)}{op1}{b}{op2}{c}", n_c))

    # op1 free, op2 is in "+-", op3 in "*/"

    for a, b, c in itertools.product(list(range(1,10)), repeat=3):
        for op1 in "+-*/":
            for op2 in "+-":
                for op3 in "*/":
                    if op1 in "*/" and (a == 1 or b == 1):
                        continue
                    if op2 in "*/" and c == 1:
                        continue
                    if op2 == "+":
                        partial_sol = sol - eval(f"{a}{op1}{b}")
                    else:
                        partial_sol = eval(f"{a}{op1}{b}") - sol
                    if op3 == "*":
                        d = partial_sol / c
                        if 10 <= d <= 99 and d.is_integer():
                            d = int(d)
                            results.append((f"{a}{op1}{b}{op2}{c}{op3}{d}"))
                            results.append((f"{a}{op1}{b}{op3}{d}{op2}{c}"))
                            results.append((f"{a}{op3}{d}{op1}{b}{op2}{c}"))
                            results.append((f"{d}{op3}{a}{op1}{b}{op2}{c}")) 
                    else:
                        d = partial_sol * c
                        if 10 <= d <= 99 and d.is_integer():
                            d = int(d)
                            results.append((f"{a}{op1}{b}{op2}{c}{op3}{d}"))
                            results.append((f"{a}{op1}{b}{op3}{d}{op2}{c}"))
                            results.append((f"{a}{op3}{d}{op1}{b}{op2}{c}"))

    # op1 "+-", op2 in "*/", op3 in "*/"
    for a in range(1,10):
        for b, c in itertools.product(list(range(2,10)), repeat=2):
            for op1 in "+-":
                for op2, op3 in itertools.product(["*", "/"], repeat=2):
                    if op1 == "+":
                        partial_sol = sol - a
                    else:
                        partial_sol = a - sol

                    if op3 == "*":
                        bc = eval(f"{b}{op1}{c}")
                        if bc == 0:
                            continue
                        d = partial_sol / bc
                        if 10 <= d <= 99 and d.is_integer():
                            d = int(d)
                            n_c = ((op1 == "+")+1)
                            n_c *= ((op2 == "*")+(op3 == "*")+1)*2
                            results.append((f"{a}{op1}{b}{op2}{c}{op3}{d}",n_c))
                            results.append((f"{a}{op1}{b}{op3}{d}{op2}{c}",n_c))
                            results.append((f"{a}{op3}{d}{op1}{b}{op2}{c}",n_c))
                            results.append((f"{d}{op3}{a}{op1}{b}{op2}{c}",n_c))
                    else:
                        if partial_sol == 0:
                            continue
                        d = eval(f"{b}{op1}{c}") / partial_sol
                        if 10 <= d <= 99 and d.is_integer():
                            d = int(d)
                            n_c = ((op1 == "+")+1)
                            n_c *= ((op2 == "*")+(op3 == "*")+1)*2
                            results.append((f"{a}{op1}{b}{op2}{c}{op3}{d}",n_c))
                            results.append((f"{a}{op1}{b}{op3}{d}{op2}{c}",n_c))
                            results.append((f"{a}{op3}{d}{op1}{b}{op2}{c}",n_c))

    return results
# ---------------------------------------------------------------------------- #

def gen_brackets(sol):
    # Idea: Generate x oper c first. Then express x = (a oper b) with brackets.
    def bracket_expr(solx:int, lenx, prefix:str, postfix:str,
                     multiply_com_num:int = 1):
        
        # Case: (aa+b)
        expr = []
        if 11 <= solx <= 108 and lenx == 6:
            for b in range(1,10):
                a = int(solx - b)
                if digit(a) == 2:
                    expr.extend([
                        (f"{prefix}({a}+{b}){postfix}",2*multiply_com_num),
                        (f"{prefix}({b}+{a}){postfix}",2*multiply_com_num)
                    ])
        # Case: (a+b)
        if 2 <= solx <= 18 and lenx == 5:
            for b in range(1,10):
                a = int(solx-b)
                if digit(a) == 1 and a != b and a > 0:
                    expr.extend([
                        (f"{prefix}({a}+{b}){postfix}",2*multiply_com_num)
                    ])
                elif a == b:
                    expr.extend([
                        (f"{prefix}({a}+{b}){postfix}",1*multiply_com_num)
                    ])
        # Case: (aa-b)
        if 1 <= solx <= 98 and lenx == 6:
            for b in range(1,10):
                a = int(solx+b)
                if 10 <= a <= 99:
                    expr.append((f"{prefix}({a}-{b}){postfix}",
                                 1*multiply_com_num))
        # Case: (a-b)
        if 1 <= solx <= 8 and lenx == 5:
            for a in range(2,10):
                b = int(solx+a)
                if 0 < b <= 9:
                    expr.append((f"{prefix}({a}-{b}){postfix}",
                                 1*multiply_com_num))
        # Case: (aa*b)
        if 10 <= solx <= 891 and lenx == 6:
            for b in range(2,10):
                a = sol/b
                if a.is_integer() and 10 <= a <= 99:
                    expr.extend([
                        (f"{prefix}({int(a)}*{b}){postfix}",2*multiply_com_num),
                        (f"{prefix}({b}*{int(a)}){postfix}",2*multiply_com_num)
                    ])
        # Case: (a*b)
        if 4 <= solx <= 81 and lenx == 5:
            for a in range(2,10):
                b = sol/a
                if b.is_integer() and 2 <= b <= 9:
                    if a != b:
                        expr.append((f"{prefix}({a}*{int(b)}){postfix}",
                                    2*multiply_com_num))
                    else:
                        expr.append((f"{prefix}({a}*{int(b)}){postfix}",
                                     1*multiply_com_num))
        # Case: (aa/b)
        if 2 <= solx < 50 and lenx == 6:
            for b in range(2,10):
                a = int(sol*b)
                if 10 <= a <= 99:
                    expr.append((f"{prefix}({a}/{b}){postfix}",
                                    1*multiply_com_num))
        # Case: (a/b)
        match solx:
            case 1:
                for i in range(2,10):
                    expr.append((f"{prefix}({i}/{i}){postfix}",
                                    1*multiply_com_num))
            case 2:
                for i in range(2,5):
                    expr.append((f"{prefix}({i*2}/{i}){postfix}",
                                    1*multiply_com_num))
            case 3:
                for i in range(2,4):
                    expr.append((f"{prefix}({i*3}/{i}){postfix}",
                                    1*multiply_com_num))
            case 4:
                    expr.append((f"{prefix}({8}/{4}){postfix}", 
                                 1*multiply_com_num))
        return expr
            
    def gen_b_plus(sol): # sol = x + c = (a oper b) + c
        results = []
        for c in range(1,100):
            x = sol - c
            if 1 <= c <= 9:
                results.extend(bracket_expr(x, 6, f"{c}+", "", 2))
                results.extend(bracket_expr(x, 6, "", f"+{c}", 2))
            else:
                results.extend(bracket_expr(x, 5, f"{c}+", "", 2))
                results.extend(bracket_expr(x, 5, "", f"+{c}", 2))
        return results
    
    def gen_b_minus(sol):
        # sol = x - c = (a oper b) - c
        results = []
        for c in range(1,100):
            x = sol + c
            if 1 <= c <= 9:
                results.extend(bracket_expr(x, 6, "", f"-{c}", 1))
            else:
                results.extend(bracket_expr(x, 5, "", f"-{c}", 1))
        # sol = c - x = c - (a oper b)
        for c in range(1,100):
            x = c - sol
            if 1 <= c <= 9 and x > 0:
                results.extend(bracket_expr(x, 6, f"{c}-", "", 1))
            elif 10 <= c <= 99 and x > 0:
                results.extend(bracket_expr(x, 5, f"{c}-", "", 1))
        return results

    def gen_b_mul(sol): # sol = x * c = (a oper b) * c
        results = []
        for c in range(2,100):
            x = sol/c
            if x.is_integer():
                if 1 <= c <= 9:
                    results.extend(bracket_expr(x, 6, f"{c}*", "", 2))
                    results.extend(bracket_expr(x, 6, "", f"*{c}", 2))
                else:
                    results.extend(bracket_expr(x, 5, f"{c}*", "", 2))
                    results.extend(bracket_expr(x, 5, "", f"*{c}", 2))
        return results

    def gen_b_div(sol):
        # sol = x / c = (a oper b) / c
        results = []
        for c in range(2,100):
            x = sol/c
            if x.is_integer():
                if 1 <= c <= 9:
                    results.extend(bracket_expr(x, 6, "", f"/{c}", 2))
                else:
                    results.extend(bracket_expr(x, 5, "", f"/{c}", 2))
        # sol = c / x = c / (a oper b)
        for c in range(2,100):
            x = c/sol
            if x.is_integer():
                if 1 <= c <= 9:
                    results.extend(bracket_expr(x, 6, f"{c}/", "", 2))
                else:
                    results.extend(bracket_expr(x, 5, f"{c}/", "", 2))
        return results
    return gen_b_div(sol)
# ---------------------------------------------------------------------------- #

if __name__ == '__main__':
    sol = 42
    start_time = time.time()

    expr = gen_three_oper(sol)
    if expr is not None:
        expr_list_as_string = '\n'.join(map(str, expr))
        with open("output.txt", "w") as file:
            file.write(expr_list_as_string)
    else:
        print("No solution found")
    
    print(f"Generated {len(expr)} valid solutions in " +
          f"{time.time()-start_time:.2f}s")
    
    def find_duplicates(lst):
        seen = set()
        duplicates = []
        for item in lst:
            if item in seen:
                duplicates.append(item)
            else:
                seen.add(item)
        return duplicates
        
    print(find_duplicates(expr))

# ToDo: calculate frequencies for 3 oper expressions!
# ToDo: Calculations in 3 oper are often wrong! look through logic