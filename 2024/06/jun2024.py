# https://research.ibm.com/haifa/ponderthis/challenges/June2024.html

from decimal import *
from fractions import Fraction
from math import floor, log10

# Return the number of digits before the decimal place in base 10 for x
def digit_len(x):
    if x < 0:
        return floor(log10(-x)) + 1
    elif x == 0:
        return 1
    return int(floor(log10(x))) + 1

# Return a Pythagorean triple from m and n, with A = 2mn, B = m^2 - n^2, 
# C = m^2 + n^2
def pythagorean_triple(m,n):
    A = 2*m*n
    B = m*m - n*n
    C = m*m + n*n
    return A, B, C

# return the error for A/B approximating x
def approximation_error(A,B,x):
    if B != 0:
        return abs(Decimal(A)/Decimal(B) - x)
    return False
    
# Pi specified to 100 decimal places
def decimal_pi():
    assert getcontext().prec == 100, "Decimal precision must be 100"
    return Decimal("3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679")

# Calculate a rational approximation of x as a finite continued fraction to the
# given number of iterations. 
def continued_fraction(x, iterations):
    # if x is a whole number or fewer than one iteration is specified,
    # return the fraction int(x)/1
    if round(x) == x or iterations < 1:
        return Fraction(int(x), 1)
    numerators = []
    denominators = []
    remainder = x
    for i in range(iterations):
        whole_part = floor(remainder)
        fractional_part = remainder - whole_part
        a_i = int(whole_part)
        q_i = 0
        p_i = 0
        if i == 0:
            q_i = a_i
            p_i = 1
        elif i == 1:
            q_i = 1 + a_i * numerators[-1]
            p_i = a_i * denominators[-1]
        else:
            q_i = numerators[-2] + a_i*numerators[-1]
            p_i = denominators[-2] + a_i*denominators[-1]
        numerators.append(q_i)
        denominators.append(p_i)
        if fractional_part == 0:
            break
        remainder = 1/fractional_part
    # return the final numerator and denominator terms as a Fraction
    return Fraction(numerators[-1], denominators[-1])

# Find a Pythagorean triple (A,B,C) such that |A/B - pi| < 10^-epsilon_exponent 
# and A, B and C are each 100 decimal digits or fewer
def solution(pi, epsilon_exponent):
    epsilon = Decimal(10)**-epsilon_exponent
    # Calculate the ratio n/m = (sqrt(pi^2 + 1) - 1)/pi, given 
    # A = 2mn, B = m^2 - n^2 and A/B ~= pi
    ratio_n_to_m = (Decimal.sqrt(pi*pi + 1) - 1)/pi
    # For each iteration of the continued fraction, take n and m as the 
    # numerator and denominator, use those to compute A,B,C and determine the 
    # error term for |A/B - pi|. Continue until the error term is within 
    # epsilon or any of A,B,C exceed 100 decimal digits. Return A,B,C if a 
    # solution is found.
    continued_fraction_steps = 1
    while True:
        fraction = continued_fraction(ratio_n_to_m, continued_fraction_steps)    
        n = fraction.numerator
        m = fraction.denominator
        A,B,C = pythagorean_triple(m,n)
        if digit_len(A) > 100 or digit_len(B) > 100 or digit_len(C) > 100:
            break
        error = approximation_error(A,B,pi)
        if error != False and error < epsilon:
            return A,B,C
        continued_fraction_steps += 1
    return 0,0,0
    
def main():
    print("\n######## Ponder This Challenge - June 2024 ########\n")
    
    # Get pi to 100 decimal places
    getcontext().prec = 100
    pi = decimal_pi()
    
    print("Main challenge result:\n")
    A,B,C = solution(pi, 20)
    if A == 0:
        print("No solution found")
    else :
        print("A = {}".format(A))
        print("B = {}".format(B))
        print("C = {}".format(C))

    print("\nBonus challenge result:\n")
    D,E,F = solution(pi, 95)
    if D == 0:
        print("No solution found")
    else:
        print("D = {}".format(D))
        print("E = {}".format(E))
        print("F = {}".format(F))
        
if __name__ == "__main__":
    main()