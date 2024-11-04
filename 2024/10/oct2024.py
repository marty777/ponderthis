# https://research.ibm.com/haifa/ponderthis/challenges/October2024.html

from functools import reduce
import math

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)

# Returns the number of digits of x expressed as an integer in decimal notation
def digit_len(x):
    return int(math.floor(math.log10(x))) + 1    

# Returns the digits of x expressed as an integer in decimal notation
def digits(x):
    digits = []
    while x > 0:
        digit = x % 10
        digits.append(digit)
        x -= digit
        x //= 10
    return digits

# Returns the product of the digits of x
def digit_product(x):
    return reduce(lambda x,y: x*y, digits(x), 1)

# Returns false if the digits 0 or 5 are among the digits of x      
def digits_no_0_or_5(x):
    for d in digits(x):
       if d % 5 == 0:
           return False
    return True

# Finds the smallest x satisfying the main challenge, limiting the search to
# x having the specified number of digits or fewer.
def main_challenge(digit_limit):
    x_candidates = []
    # Limits for prime exponents on b are used to reduce the search size to 
    # areas known to contain the challenge answer for performance reasons and 
    # were tuned by experimentation after the fact.
    i_j_k_limit = 10
    for k in range(i_j_k_limit):
        for j in range(i_j_k_limit):
            for i in range(i_j_k_limit):
                # b must be divisible only by primes 2,3,7
                b = (2**(2*i)) * (3**(2*j)) * (7**(2*k))
                # If not divisibly by 72576, b cannot be the product of the 
                # digits of x which must include 1,2,3,4,6,7,8,9 at least once
                if b % 72576 != 0:
                    continue
                # b cannot contain the digits 0 or 5
                if not digits_no_0_or_5(b):
                    continue
                # Find the smallest valid x with the given b
                x_given_b = first_x_given_b(b, digit_limit)
                if x_given_b != False:
                    x_candidates.append(x_given_b)
    if len(x_candidates) == 0:
        return False
    return min(x_candidates)

# Finds the smallest x satisfying the bonus challenge, limiting the search to 
# x having the specified number of digits or fewer.
def bonus_challenge(digit_limit):
    b_candidates = []
    # Limits for prime exponents on b and m are used to reduce the search size
    # to areas known to contain the challenge answer for performance reasons
    # and were tuned by experimentation after the fact.
    i_j_k_limit = 10
    u_v_w_limit = 15
    for k in range(i_j_k_limit):
        for j in range(i_j_k_limit):
            for i in range(i_j_k_limit):
                # b_prime a cube with no prime factors other than 2,3,7
                b_prime = (2**(3*i)) * (3**(3*j)) * (7**(3*k))
                # b must be a multiple of b_prime and can only have factors 
                # 2,3,7
                for w in range(u_v_w_limit):
                    for v in range(u_v_w_limit):
                        for u in range(u_v_w_limit):
                            m = (2**(u)) * (3**(v)) * (7**(w))
                            b = m * b_prime
                            if digit_len(b) > digit_limit:
                                continue
                            # b must be equal to the cube b_prime * the digit 
                            # product of b, be divisible by 72576, and contain 
                            # no digits 0 or 5
                            if b == digit_product(b) * b_prime and b % 72576 == 0 and digits_no_0_or_5(b):
                                if b not in b_candidates:
                                    b_candidates.append(b)
    if len(b_candidates) == 0:
        return False
    x_candidates = []
    # Given a set of candidate b's, find the smallest x corresponding to each
    for b in b_candidates:
        # b = 9289728 has no x less than 23 digits long and requires a long 
        # time to search up to that number of digits. Skip it.
        if b == 9289728:
            continue
        x = first_x_given_b(b, digit_limit)
        if x != False:
            x_candidates.append(x)
    if len(x_candidates) == 0:
        return False
    return min(x_candidates)

# Given b, find the smallest valid x with the given number of digits or fewer
def first_x_given_b(b, digit_limit):
    a_prime = lcm(b, 10 ** digit_len(b))
    m = 1
    while True:
        m += 1            
        x = b + m*a_prime
        if digit_len(x) > digit_limit:
            return False
        if valid_x(x):
            return x

# Test if x has the correct digits, ends with a b that is the sum of the digits
# of x, and is a multiple of b
def valid_x(x):
    digits_x = digits(x)
    # check valid digits
    for i in range(10):
        if i % 5 == 0:
            if digits_x.count(i) > 0:
                return False
        else:
            if digits_x.count(i) < 1:
                return False
    b = digit_product(x)
    # x ends in b - listen, it works
    if not "{}".format(x).endswith("{}".format(b)):
        return False
    # x a multiple of b
    if not x % b == 0:
        return False 
    return True
    
def main():
    print("\n######## Ponder This Challenge - October 2024 ########\n")
    
    # Cutoffs for number of digits in the searches below were arrived at by 
    # experimentation 
    
    # Search for solutions to the main challenge no more than 20 decimal digits
    # long
    main_challenge_result = main_challenge(20)
    if main_challenge_result == False:
        print("Main challenge: \tNo solution found")
    else:
        print("Main challenge: \t{}".format(main_challenge_result))
    
    # Search for solutions to the bonus challenge no more that 22 decimal 
    # digits long
    bonus_challenge_result = bonus_challenge(22)
    if bonus_challenge_result == False:
        print("Bonus challenge:\tNo solution found")
    else:
        print("Bonus challenge:\t{}".format(bonus_challenge_result))
    return

if __name__ == "__main__":
    main()