# June 2024 Ponder This Challenge
The [June challenge](https://research.ibm.com/haifa/ponderthis/challenges/June2024.html) asks for approximations of $\pi$ using the ratio of terms of a Pythagorean triple.

## Challenges

A [Pythagorean triple](https://en.wikipedia.org/wiki/Pythagorean_triple) is a group of positive integers $(A,B,C)$ such that $A^2 + B^2 = C^2$.

The main challenge asks for a Pythagorean triple $(A,B,C)$ such that $\left|\frac{A}{B} - \pi\right| < 10^{-20}$ and $A$, $B$, and $C$ each have 100 decimal digits or fewer.

The bonus challenge asks for a Pythagorean triple $(D,E,F)$ such that $\left|\frac{D}{E} - \pi\right| < 10^{-95}$ and $D$, $E$, and $F$ each have 100 decimal digits or fewer.

## Solution

The solution is implemented in Python.

Usage: 

	$ python jun2024.py
	
The script will output triples satisfying the main and bonus challenges.

## Discussion

There are a few different methods to generate arbitrary Pythagorean triples, but for the purposes of the challenge I'm using Euclid's formula. $A = 2mn$, $B = m^2 - n^2$, $C = m^2 + n^2$ forms a Pythagorean triple $(A,B,C)$ for any integers $m > n > 0$, although this formula doesn't describe all possible triples. Exchanging the formulas for the first two terms will also work, although the details below will differ.

Even though $\pi$ is irrational, assume $\frac{A}{B} = \pi$. This allows an ideal ratio to be determined between $n$ and $m$:

$$\frac{2mn}{m^2 - n^2} = \pi$$

$$ n = m \cdot \frac{\pm \sqrt{\pi^2 + 1} - 1}{\pi} $$

Since $m$ and $n$ must be positive, the negative solution for $n$ can be ignored and the ratio of $n$ to $m$ is:

$$\frac{n}{m} = \frac{m \cdot \frac{\sqrt{\pi^2 + 1} - 1}{\pi} }{m} = \frac{\sqrt{\pi^2 + 1} - 1}{\pi}$$

By constructing a [continued fraction](https://en.wikipedia.org/wiki/Continued_fraction) approximating $\frac{\sqrt{\pi^2 + 1} - 1}{\pi}$, the numerator and denominator of the fraction can be taken as $n$ and $m$ and a Pythagorean triple $(2mn, m^2 - n^2, m^2 + n^2)$ can be generated. As the number of iterations used to build the fraction is increased, both the accuracy of the approximation as well as the number of digits for the terms of the triple increase. There are multiple iterations where the terms of the resulting Pythagorean triple do not exceed 100 digits and $\frac{2mn}{m^2 - n^2}$ is sufficiently close to $\pi$ to solve the main and bonus challenges.
