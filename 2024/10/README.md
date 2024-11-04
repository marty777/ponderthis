# October 2024 Ponder This Challenge
The [October challenge](https://research.ibm.com/haifa/ponderthis/challenges/October2024.html) asks for integers with special properties to their digits.

## Challenges

Consider a positive integer $X$ that has the following properties when expressed in decimal notation.

- The digits $`\{1,2,3,4,6,7,8,9\}`$ each appear at least once in $X$, and the digits $`\{0,5\}`$ do not appear.
- The digits of $X$ are the concatenation of the digits of two integers $A$, the left component, and $B$, the right component, such that $B$ is equal to the product of the digits of $X$, and such that $X$ is a multiple of $B$.

The main challenge asks for the smallest possible $X$ where $B$ is a perfect square.

The bonus challenge asks for the smallest possible $X$ where taking the product of the digits of $A$ gives a perfect cube.

## Solution

The solution is implemented in Python.

Usage:

	python oct2024.py
	
The script will find the solutions to the main and bonus challenges.

## Discussion

There are a few immediate observations that can be made about $X$, $A$ and $B$.

1. Since $B$ is the product of the digits of $X$, $B$ must be divisible by $72576$, the product of the digits $`\{1,2,3,4,6,7,8,9\}`$ which must all appear in $X$ at least once.
2. The only primes that are factors of the allowed digits in $X$ are $`\{2,3,7\}`$. Since $B$ is the product of the digits of $X$, the prime decomposition of $B$ cannot contain any other factors.
3. $X = A \times 10^b + B$, for $b$ the number of digits of $B$. Since $X$ is a multiple of $B$ then $A \times 10^b$ must also be a multiple of $B$.

### Main challenge

$X$ can be found by iterating over possible squares for $B$. Since $B$ can only have prime factors $`\{2,3,7\}`$ we can iterate over $i,j,k \ge 0$ for $B = 2^{2i} \cdot 3^{2j} \cdot 7^{2k}$ rather than the squares of all integers. Any $B$ of this form that is not a multiple of $72576$ or contains the digits $`\{0,5\}`$ can be skipped.

For any candidate $B$, one can note that $A \times 10^b$ must be a multiple of both $B$ and $10^b$, for $b$ the number of digits of $B$. If we take $A' = \text{lcm}(B,10^b)$, then $A \times 10^b$ must be a multiple of $A'$. Iterating over integers $m$ (up to some bound), and testing if $mA' + B$ satisfies the properties of $X$ will find the smallest $X$ with a given $B$. Repeating this over each candidate $B$ up to some bound will allow the smallest satisfying $X$ to be found, giving the main challenge answer. The smallest satisfying $X$ is 19 digits long.

### Bonus challenge

$X$ can be found by iterating over possible cubes $B'$, taken as the digit product of $A$. Since the digit product of $A$ must be the product of digits from the set $`\{1,2,3,4,6,7,8,9\}`$, $B'$ cannot have prime factors other than $`\{2,3,7\}`$. As with the main challenge, it's more straightforward to iterate over $i,j,k \ge 0$ for $B' = 2^{3i} \cdot 3^{3j} \cdot 7^{3k}$ than examine cubes of all integers.

$B$ must be a multiple of $B'$, and can also have no prime factors other than $`\{2,3,7\}`$. Iterating over integers $m = 2^u \cdot 3^v \cdot 7^w$ for $u,v,w \ge 0$ and taking those where $m$ is equal to the digit product of $mB'$ gives candidate integers $B = mB'$.

For each candidate value of $B$ that is found found, the same process used in the main challenge can be used to find the smallest corresponding $X$. The smallest $X$ found across all satisfying $B$ gives the bonus challenge answer. The smallest satisfying $X$ is 22 digits long.

