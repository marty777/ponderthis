# May 2025 Ponder This Challenge
The [May challenge](https://research.ibm.com/haifa/ponderthis/challenges/May2025.html) ask about tests taken in a class on arithmetic in a prime field.

## Challenges

The challenge describes a classroom for arithmetic in the field $F_p$ for some obscured prime $p$. A pair of exams for this class have been left around to be examined, but are missing some important details.

The main challenge presents an exam with a series of arithmetic expressions in $F_p$ with unknown values $x_1,\ldots,x_8$. The expression for each question, multiple choice answers for the evaluation of each expression, and a set of student answers to the exam along with their scores are provided. Given this information, the challenge asks for $p$.

The bonus challenge presents an exam involving $q(x)$, a monic polynomial of degree 20 in $F_p$ with unknown coefficients. A series of questions evaluating $q(x)$ for various $x$, multiple choice answers for each question, and a set of student answers to the exam along with their scores are provided. Given this information and the value of $p$ deduced in the main challenge, the bonus challenge asks for the value of $q(1)$.

## Solution

The solution is implemented in Python and uses the [SymPy library](https://www.sympy.org/en/index.html) for solving systems of linear equations in finite fields.

Usage:

```console 
$ pip install sympy
$ python may2025.py

```
The script will calculate the solutions to the main and bonus challenges.

## Discussion

For both the main and bonus challenges, the solutions can be determined once the correct answer key to each exam is deduced from the student answers and corresponding scores. One way to achieve this is by exhaustively testing all possible answer keys until one is found that exactly produces identical scores for the student answers. The exam for the main challenge has few enough questions that this can be quickly done in Python, but for the bonus challenge the answer key was found in a lengthy search using a separate program. The solution script will directly find the answer key for the main challenge, but uses the pre-computed key for the bonus challenge.

### Main challenge.

 1. The correct answers to each exam question must first be deduced. One way is to use the student exam answers and corresponding scores by iterating over all possible answer keys to the exam and evaluating each set of student answers against it. Since there are 10 questions with 4 possible answers each, there are $4^{10} = 1{\small,}048{\small,}576$ possible keys to check. There is only one answer key where each student's score against the key exactly matches their score on the exam. 
 2. Iterating over all primes $p$ up to some reasonable bound and knowing the answer to each exam question, the 8 unknown $x_{i}$ values can be found by solving the system of linear equations in $F_p$ formed by the first 8 exam questions. After building the matrix of coefficients from these questions, any $p$ where $\text{gcd}(\text{det},p) = 1$, with $\text{det}$ the determinant of the matrix, will have a unique solution for each $x_{i}$.
 3. While there are many $p$ where a unique solution for $x_{i}$ is possible, only one is the correct answer to the challenge. The final two exam questions provide additional constraints on $p$ and $x_{i}$. The first $p$ where both expressions evaluate to the known exam answers is the solution to the main challenge.
 
### Bonus challenge.

 1. As with the main challenge, the correct answers to each exam question must be found. A search across all possible answer keys is effective. Since there are 21 questions with 4 possible answers each, there are $4^{21} = 4{\small,}398{\small,}046{\small,}511{\small,}104$ possible keys to check, which is substantial but feasible in reasonable time. In the provided solution script this search is skipped and a pre-computed answer key arrived at in a separate compiled program is used instead. There is only one answer key corresponding exactly to each student's exam score.
 2. Knowing the answer to each exam question and that the $q(x)$ function is a 20<sup>th</sup> degree polynomial, the questions and answers form a system of 21 linear equations in $F_p$ that can be solved for the 21 unknown coefficients of $q(x)$. Once the coefficients have been determined, $q(1)$ is straightforward to compute.



