# https://research.ibm.com/haifa/ponderthis/challenges/May2025.html

import re
import itertools
import sympy
from math import gcd,log10

MAIN_EQUATIONS = """
5x_2 + 7x_3 + 5x_5 + 3x_6 = ?
A: 2416 B: 2415 C: 2413 D: 2412

8x_1 + 5x_2 + 2x_5 + 5x_8 = ?
A: 7624 B: 7622 C: 7621 D: 7625

7x_1 + 4x_2 + 5x_4 + 2x_5 = ?
A: 638 B: 642 C: 633 D: 637

7x_1 + 9x_3 + x_6 + x_7 = ?
A: 765 B: 761 C: 759 D: 760

8x_3 + 7x_4 + 4x_5 + 3x_6 = ?
A: 2211 B: 2212 C: 2217 D: 2216

2x_3 + 5x_4 + 5x_6 + 5x_7 = ?
A: 3497 B: 3501 C: 3496 D: 3499

5x_2 + 4x_4 + 6x_5 + 7x_6 = ?
A: 4007 B: 4010 C: 4008 D: 4013

7x_3 + x_4 + 8x_6 + 8x_7 = ?
A: 5531 B: 5535 C: 5538 D: 5534

x_1*x_2*x_3*x_4*x_5*x_6*x_7*x_8 = ?
A: -4 B: 1 C: 5 D: 4

x_1*x_3*x_5*x_7 = ?
A: 6544 B: 6546 C: 6545 D: 6550
"""

MAIN_TESTS = """
BABBDDCDCA 6/10
DADBDDAACD 6/10
CADBDBCDCC 7/10
DACBDDCBCB 6/10
DCBBDDCDAB 6/10
DDDBDDCDBD 8/10
DADBDDCCCC 8/10
CADBDDDDAC 7/10
"""

BONUS_EQUATIONS = """
q(5698) = ?
A: 5146 B: 5142 C: 5149 D: 5147

q(1616) = ?
A: 3715 B: 3725 C: 3720 D: 3716

q(1338) = ?
A: 2547 B: 2548 C: 2549 D: 2550

q(7821) = ?
A: 6624 B: 6628 C: 6619 D: 6627

q(4461) = ?
A: 4661 B: 4660 C: 4659 D: 4662

q(2156) = ?
A: 5112 B: 5107 C: 5106 D: 5102

q(7559) = ?
A: 3916 B: 3921 C: 3913 D: 3917

q(5812) = ?
A: 2340 B: 2342 C: 2345 D: 2344

q(794) = ?
A: 6210 B: 6212 C: 6217 D: 6215

q(2595) = ?
A: 3642 B: 3644 C: 3646 D: 3641

q(1640) = ?
A: 1581 B: 1584 C: 1586 D: 1583

q(6779) = ?
A: 6543 B: 6536 C: 6541 D: 6544

q(8362) = ?
A: 3823 B: 3828 C: 3824 D: 3832

q(4605) = ?
A: 5601 B: 5598 C: 5602 D: 5595

q(420) = ?
A: 1272 B: 1274 C: 1278 D: 1275

q(8724) = ?
A: 4410 B: 4420 C: 4415 D: 4412

q(3669) = ?
A: 8974 B: 8973 C: 8976 D: 8971

q(1869) = ?
A: 6723 B: 6720 C: 6728 D: 6721

q(7516) = ?
A: 8244 B: 8247 C: 8246 D: 8243

q(1386) = ?
A: 1571 B: 1570 C: 1569 D: 1568

q(4529) = ?
A: 5504 B: 5501 C: 5503 D: 5506
"""

BONUS_TESTS = """
CCCDDCAADCCCBBDABDBAD 9/21
ADDACCADDDDBACDDBADCD 11/21
DCBABBAADDACBBAAAABDC 12/21
ACAAABABDDDBACAABADDC 11/21
CABAAAABDBDCCBDCBDBCC 12/21
DDDADCADDBDABBDBCADCC 12/21
ACDBBDAADDDABDCBCBCAC 9/21
AABCBDACDBADBDDCDACCB 10/21
BABBBBABAABCBDBCDACCA 9/21
ACCBABADDDDDBBCDDBACC 12/21
ACDBCBBDBDDCBCCADBCAA 9/21
"""

# Basic Sieve of Eratosthenes. Return a list of primes up to sqrLimit
def eratosthenes(limit):
    if limit < 2:
        limit = 2
    primes = []
    sieve = [False] * limit
    increment = 2
    done = False
    while True:
        for i in range(2*increment, limit, increment):
            sieve[i] = True
        done = True
        for i in range(increment+1, limit,1):
            if not sieve[i]:
                increment = i
                done = False
                break
        if done:
            break
    for i in range(2, limit, 1):
        if not sieve[i]:
            primes.append(i)
    return primes

def numbers_in_string(str):
    list = re.findall('-?\d+\.?\d*',str)
    result = []
    for item in list:
        if "." in item:
            result.append(float(item))
        else:
            result.append(int(item))
    return result

class Equation:
    # terms a list of tuples, each containing a multiplicand and an x indexs
    def __init__(self, equation_description, answers_description):
        self.product = False
        if("*" in equation_description):
            self.product = True
        equation_split = ""
        if self.product:
            equation_split = equation_description.split("*")
        else:
            equation_split = equation_description.split(" + ")
        self.terms = []
        for t in equation_split:
            term_split = t.split("x_")
            if term_split[0] == '':
                self.terms.append((1, int(term_split[1])))
            else:
                self.terms.append((int(term_split[0]), int(term_split[1])))
        self.answers = {}
        answer_split = answers_description.split()
        for i in range(0, len(answer_split), 2):
            self.answers[answer_split[i][0]] = int(answer_split[i+1])
    
    def eval(self, p, x_terms):
        if self.product:
            product = 1
            for t in self.terms:
                product *= t[0] * x_terms[t[1] - 1]
            return product % p
        else:
            total = 0
            for t in self.terms:
                total += t[0] * x_terms[t[1] - 1]
            return total % p

class BonusEquation:
    def __init__(self, equation_description, answers_description):
        self.term = int(equation_description[equation_description.index('(') + 1:equation_description.index(')')])
        self.answers = {}
        answer_split = answers_description.split()
        for i in range(0, len(answer_split), 2):
            self.answers[answer_split[i][0]] = int(answer_split[i+1])
        
    # Evaluate the equation given the provided coefficients. Coefficients are 
    # ordered by ascending powers of x.
    def eval(self, p, coefficients):
        total = 0
        for i in range(len(coefficients)):
            total = (total + coefficients[i] * pow(self.term, i)) % p
        return total % p
    
class Test:
    def __init__(self, description):
        desc_split = description.split()
        self.answers = list(desc_split[0])
        self.score = int(desc_split[1].split('/')[0])

def parse_equations(equation_string, bonus):
    lines = list(filter(lambda x: len(x) > 0, equation_string.splitlines()))
    equations = []
    for i in range(0, len(lines), 2):
        equation_description = lines[i].replace(" = ?", "")
        answers_description = lines[i+1]
        if bonus:
            equations.append(BonusEquation(equation_description, answers_description))
        else:
            equations.append(Equation(equation_description, answers_description))
    return equations

def parse_tests(test_string):
    tests = []
    lines = list(filter(lambda x: len(x) > 0, test_string.splitlines()))
    for line in lines:
        tests.append(Test(line))
    return tests

# Try all possible answer keys for the test and return any that produce the 
# given scores exactly
def answer_key(tests):
    if len(tests) == 0:
        return []
    num_questions = len(tests[0].answers)
    options = ['A', 'B', 'C', 'D']
    for answers in itertools.product(options, repeat=num_questions):
        test_matching = 0
        for t in tests:
            correct = 0
            expected = t.score
            for i in range(num_questions):
                if t.answers[i] == answers[i]:
                    correct += 1
            if correct == expected:
                test_matching += 1
        if test_matching == len(tests):
            return list(answers)   
    return None

# Given the answer key and the exam equations, solve the system of the first 8 
# equations using varying primes to find unique solutions for the variables 
# x_1 to x_8. Return the prime where the coefficient solution evaluates to the
# correct answer for the final two equations.
def solve_main_challenge(answer_key, equations):
    # Using sympy, construct a matrix and answer vector for the system of 
    # linear equations formed by the first 8 exam questions
    answers = []
    equation_mat = []
    num_linear_equations = 0
    for i in range(len(equations)):
        # Only include the first 8 equations in a linear system
        if equations[i].product:
            continue
        num_linear_equations += 1
        row = []
        answer_val = equations[i].answers[answer_key[i]]
        answers.append(answer_val)    
        for j in range(0, 8):
            coefficient = 0
            for k in range(len(equations[i].terms)):
                if equations[i].terms[k][1] == j+1:
                    coefficient = equations[i].terms[k][0]
                    break
            row.append(coefficient)
        equation_mat.append(row)
        
    answer_vec = sympy.Matrix(answers)
    equation_matrix = sympy.Matrix(equation_mat)
    
    # Since 4 digit values appear in the options for exam answers, assume that
    # p has more than 3 digits. For all 4 digit primes, test if there are
    # unique solutions for x_1,...,x_8 that are consistent with the known test
    # answers.
    primes = eratosthenes(10000)
    det = int(equation_matrix.det())
    for p in primes:
        # Skip any primes with fewer than 4 digits
        if log10(p) < 3:
            continue
        # If gcd(determinant, p) = 1, there can be no unique solution to the 
        # linear system
        if gcd(det, p) != 1:
            continue
        solution_vec = pow(det, -1, p) * equation_matrix.adjugate() @ answer_vec % p
        solution_list = []        
        for i in range(num_linear_equations):
            solution_list.append(solution_vec.row(i)[0])
        # Test that the solved system given p matches the known answers to each
        # exam question. If so, p is the challenge answer.
        good_count = 0
        for i in range(len(equations)):
            if equations[i].eval(p, solution_list) == equations[i].answers[answer_key[i]] % p:
                good_count += 1
        if good_count == len(equations):
            return p
    return False

# Given the answer key, the exam equations and p, solve the system of 21 
# equations for the 21 coefficients of q(x)
def solve_bonus_challenge(answer_key, equations, p):
    # Using sympy, construct a matrix and answer vector for the system of 
    # linear equations formed by the exam questions
    answers = []
    equation_mat = []
    num_linear_equations = 0
    for i in range(len(equations)):
        num_linear_equations += 1
        row = []
        answer_val = equations[i].answers[answer_key[i]]
        answers.append(answer_val)    
        for j in range(0, 21):
            term = pow(equations[i].term, j, p)
            row.append(term)
        equation_mat.append(row)
    
    answer_vec = sympy.Matrix(answers)
    equation_matrix = sympy.Matrix(equation_mat)
    
    # Solve the linear system
    det = int(equation_matrix.det())
    coefficient_vec = pow(det, -1, p) * equation_matrix.adjugate() @ answer_vec % p
    coefficient_list = []
    for i in range(num_linear_equations):
        coefficient_list.append(coefficient_vec.row(i)[0])

    # Having found the coefficients of q(x), calculate q(1)
    q_1 = BonusEquation("q(1) = ?","A: 0 B: 0 C: 0 D: 0")
    return q_1.eval(p, coefficient_list)
        
def main():
    
    print("\n######## Ponder This Challenge - May 2025 ########\n")
    
    main_equations = parse_equations(MAIN_EQUATIONS, bonus=False)
    main_tests = parse_tests(MAIN_TESTS)
    main_answer_key = answer_key(main_tests)
    if answer_key is None:
        print("Main answer key not found")
        return
    p = solve_main_challenge(main_answer_key, main_equations)
    if p == False:
        print("Main solution not found")
        return 
    print("Main solution:", p)
    
    bonus_equations = parse_equations(BONUS_EQUATIONS, bonus=True)
    # Bonus answer key was found after a lengthy search in a separate program
    bonus_anwer_key = list("ACBADBADDDDCBBDCBACCC")
    q_1 = solve_bonus_challenge(bonus_anwer_key, bonus_equations, p)
    print("Bonus solution:", q_1)
        
if __name__ == "__main__":
    main()