# https://research.ibm.com/haifa/ponderthis/challenges/September2024.html

import math
from decimal import *
import random

# Collection of small primes congruent to 1 mod 4
small_primes_1_mod_4 = [5, 13, 17, 29, 37, 41, 53, 61, 73, 89, 97]

# Calculate area of a triangle as a high-precision decimal given side lengths 
# a,b,c
def area(a,b,c):
    if a + b <= c or a + c <= b or b + c <= a:
        return False
    dec_a = Decimal(a)
    dec_b = Decimal(b)
    dec_c = Decimal(c)
    s = (dec_a+dec_b+dec_c)
    return (s*(s - 2*dec_a)*(s - 2*dec_b)*(s - 2*dec_c)).sqrt()*Decimal(0.25)

# Find all distinct integer [x, y] such that x,y > 0, x != y and 
# x^2 + y^2 = n
def n_roots(n):
    root_pairs = []
    max = math.isqrt(n//2)
    for x in range(1, max + 1):
        y_squared = n - x*x
        y = math.isqrt(y_squared)
        if y*y == y_squared and y != 0 and y != x:  
            root_pairs.append([x, y])
    return root_pairs

# Determine the number of sibling pairs for a triangle with side lengths a and 
# b, along with count of pairs with integer areas.
def sibling_pairs(a,b,roots=None):
    n = 2*a*a + 2*b*b
    if roots is None:
        roots = n_roots(n)
    c_lower_bound = abs(a - b) + 1
    c_upper_bound = a + b
    points = []
    integer_area_count = 0
    for r in roots:
        if r[0] < c_lower_bound or r[0] > c_upper_bound or r[1] < c_lower_bound or r[1] > c_upper_bound:
            continue
        A = area(a,b,r[0])
        if is_int(A):
            integer_area_count += 1
        points.append([r[0], r[1]])
    return len(points), integer_area_count

def is_int(x):
    return x.as_integer_ratio()[1] == 1

# Find some (a,b) having exactly 50 sibling pairs
def main_challenge():
    # n = 2*a^2 = 2*b^2 for (a,b) having 50 sibling pairs can be found with n 
    # having prime factors 2 and some number of primes congruent to 1 mod 4.
    # Random walk n until an answer is found. Once n is picked, vary (a,b) 
    # until there is a solution or 50 sibling pairs cannot be reached, in which
    # case restart with a new n.
    n_primes = 8
    while True:
        n = 2
        for i in range(n_primes):
            n *= random.choice(small_primes_1_mod_4)
        # All possible roots c1^2 + c2^2 = n are shared as a,b are iterated 
        # over, so they only need to be calculated once
        roots = n_roots(n)
        half_n = n//2
        sqrt_half_n = math.isqrt(half_n)
        for a in range(1, sqrt_half_n):
            a_squared = a*a
            b_squared = half_n - a_squared
            b = math.isqrt(b_squared)
            # if integers a,b satisfying 2a^2 + 2b^2 = n have been found, count
            # the number of sibling pairs given a,b.
            if b*b == b_squared:
                n_pairs, _ = sibling_pairs(a,b,roots)
                if n_pairs == 50:
                    if (a < b):
                        return b,a
                    elif a > b:
                        return a,b
    return False
    
# Find some (a,b) having exactly 50 sibling pairs, at least two with integer 
# areas
def bonus_challenge():
    # The side lengths a,b = 409,123 give 2 sibling pairs, each with integer 
    # areas. Any integer multiple of 409,123 will give at least 2 sibling pairs
    # with integer areas as well. Try varying multiples m of 409,123 using 
    # composites of primes congruent to 1 mod 4, until side lengths are found 
    # that yield exactly 50 sibling pairs.
    base_a = 409
    base_b = 123
    # random walk a multiple composed of small 1 mod 4 primes until a match is 
    # found
    n_primes = 3
    while True:
        m = 1
        for i in range(n_primes):
            m *= random.choice(small_primes_1_mod_4)
        # To reduce the number of calculation attempts, restrict composite 
        # multiples to a range where there are known solutions.
        if m < 20_000 or m > 40_000:
            continue
        n_pairs, integer_areas = sibling_pairs(base_a * m, base_b * m)
        if n_pairs == 50 and integer_areas >= 2:
            return [base_a * m, base_b * m, integer_areas]
    return False
    
def main():
    print("\n######## Ponder This Challenge - September 2024 ########\n")
    
    # Set decimal precision suitably high to prevent inaccuracies in 
    # determining integer triangle areas
    getcontext().prec = 20
    
    main_result = main_challenge()
    if main_result == False:
        print("Main:\tNo solution found")
    else:
        print("Main:\ta = {}, b = {} has 50 sibling pairs".format(main_result[0], main_result[1]))
    
    bonus_result = bonus_challenge()
    if bonus_result == False:
        print("Bonus:\tNo solution found")
    else:
        print("Bonus:\ta = {}, b = {} has 50 sibling pairs, {} with integer areas".format(bonus_result[0], bonus_result[1], bonus_result[2]))
    
if __name__ == "__main__":
    main()