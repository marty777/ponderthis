# September 2024 Ponder This Challenge
The [September challenge](https://research.ibm.com/haifa/ponderthis/challenges/September2024.html) asks about sibling pair triangles.

## Challenges

Two triangles with sides having integer lengths $(a,b,c_1)$ and $(a,b,c_2)$ are considered *sibling pairs* if $c_1 \neq c_2$ and the areas of both triangles are equal (and non-zero).

The main challenge asks for integers $a$ and $b$ where $a > b$ and there are exactly 50 sibling pairs of triangles with common side lengths $a$ and $b$.

The bonus challenge asks for integers $a$ and $b$ where $a > b$ and there are exactly 50 sibling pairs of triangles with common side lengths $a$ and $b$, at least two sibling pairs having integer areas.

## Solution

The solution is implemented in Python.

Usage:

	python sept2024.py
	
The script will find side lengths $a$ and $b$ satisfying the main and bonus challenges.

## Discussion

### Main challenge

Given only the lengths of the sides $(a,b,c)$, the area of a triangle can be calculated using the *semi-perimeter* $s = \frac{a + b + c}{2}$ as:

$$A = \sqrt{s(s-a)(s-b)(s-c)}$$

If triangles $(a,b,c_1)$ and $(a,b,c_2)$ with semi-perimeters $s_1 = \frac{a + b + c_1}{2}$ and $s_2 = \frac{a + b + c_2}{2}$ have equal areas, this gives the equation:

$$\sqrt{s_1(s_1-a)(s_1-b)(s_1-c_1)} = \sqrt{s_2(s_2-a)(s_2-b)(s_2-c_2)}$$

With some algebraic manipulation:

$$-c_1^4 + c_1^2(2a^2 + 2b^2) = -c_2^4 + c_2^2(2a^2 + 2b^2)$$

$$2a^2 + 2b^2 = \frac{c_2^4 - c_1^4}{c_2^2 - c_1^2} = c_1^2 + c_2^2$$

Thus $2a^2 + 2b^2$ must be expressible as the sum of two squares for any sibling pair to exist. Each distinct pair of integer roots $c_1 \ne c_2$ where $2a^2 + 2b^2 = c_1^2 + c_2^2$ and $\left|a - b\right| < c_1,c_2 < a + b$ are the non-shared side lengths of a sibling pair of triangles for a given $(a,b)$.

The number of ways an integer $n$ can be expressed as a sum of two squared integers is easily calculated with the [sum of squares function for k = 2](https://en.wikipedia.org/wiki/Sum_of_squares_function#k_=_2). For the prime decomposition of $n = 2^{g}p_{1}^{f_1}p_{2}^{f_2}\cdots q_{1}^{h_1}q_{2}^{h_2}\cdots$ with prime factors $p_i \equiv 1 \pmod 4$ and $q_i \equiv 3 \pmod 4$, the number of ways to express $n$ as a sum of squares is $0$ if any $h_i$ is odd, and otherwise:

$$r_2(n) = 4(f_1 + 1)(f_2 + 1)\cdots$$

This amount includes all combinations of positive and negative integer roots of the squares (the multiple by 4), while only positive roots are relevant to the challenge. It may also include positive roots that are too long or too short to be the sides of a triangle for a given $a$ and $b$. Nonetheless, this suggests an approach to  find triangle side lengths $a$ and $b$ that result in 50 sibling pairs.

1. Construct a composite integer $n$ such that $\frac{r_2(n)}{4} > 50$ (in practice this may need to exceed 100) from small primes congruent to $1 \pmod 4$. This will be taken as $n = 2a^2 + 2b^2 = c_1^2 + c_2^2$ so a factor of 2 must be included in $n$ because $2a^2 + 2b^2$ is even.
2. Given a candidate $n$, iterate over all integers $1 \le b < \sqrt{\frac{n}{2}}$ and find iterations where $a = \sqrt{\frac{n - 2b^2}{2}}$ is an integer.
3. For each integer pair $(a,b)$ given $n$, iterate over all integers $\left| a - b\right| < c_1 < a + b$ and count iterations where $c_2 = \sqrt{n - c_1^2}$ is an integer, $c_2 \ne c_1$ and $\left| a - b\right| < c_2 < a + b$. When complete, the count gives the number of sibling pairs for triangles with side lengths $(a,b)$
4. Continue until an $(a,b)$ is found that results in 50 sibling pairs. If no $(a,b)$ are satisfactory, $r_2(n)$ is too small. Construct a new $n$ and repeat.

Examples of $(a,b)$ with exactly 50 sibling pairs can be found quickly with a search across values of $n$.

### Bonus challenge

Triangle sides $(a,b)$ which produce sibling pair triangles with integer areas are relatively rare. However, it can be observed that for any triangle side lengths $(a,b)$ that have a sibling pair with an integer area $A_s$, then for any integer multiple $m \ge 1$ the side lengths $(am,bm)$ must also have a sibling pair with integer area $m^2A_s$. If a small $(a,b)$ with two sibling pairs with integer areas can be found, $m$ can be varied until $(am,bm)$ can be found with 50 sibling pairs, at least two of which will necessarily have integer areas.

One such candidate $(a,b)$ is $(409,123)$, which has exactly two sibling pairs, each with integer areas. Multiplying these initial side lengths by some integer $m = p_{1}^{f_1}p_{2}^{f_2}\cdots$ for some small primes $p_i \equiv 1 \pmod 4$ and exponents will yield a $(409m,123m)$ with 50 sibling pairs, at least two with integer areas, after a short search across possible $m$.