# March 2024 Ponder This Challenge
The [March challenge](https://research.ibm.com/haifa/ponderthis/challenges/March2024.html) looks at a particular sequence of integers with non-prime terms.

## Challenges

Given the definition of a finite positive integer sequence $X_n$ with terms $a_0, a_1,\ldots, a_{n-1}$ where $a_{i} = a_{i-1} + i$ for $0 < i < n$, none of the terms are prime, and there exists no other positive integer sequence with first two properties and a smaller $a_0$, the main challenge asks for the $a_0$ term of the sequence $X_{1000}$.

The bonus challenge asks for the $a_0$ term of the sequence $X_{2024}$.

## Solution

The solution is implemented in Go

Usage:

	$ go run mar2024 [OPTIONS]

	or 

	$ go build
	$ ./mar2024 [OPTIONS]

	Options:
		-n int
				Set the value for n (default 1000)
		-s int
				Set the starting a0 search value
		-t int
				Set the number of worker threads (default 4)

Examples:

Solve the main challenge:

	./mar2024 -n 1000 
	
Solve the bonus challenge using 16 worker threads in the search:

	./mar2024 -n 2024 -t 16
	
Solve the bonus challenge with the search starting from $a_0$ of $X_{1942}$ (the start of the shelf that precedes the one occupied by $X_{2024}$):

	./mar2024 -n 2024 -s 62776898610

Note that starting the search above the actual $a_0$ for the given $X_n$ will not arrive at the correct result. Reaching the result for the bonus challenge may take several hours.

## Discussion

The most direct approach to the challenge is unexpectedly sufficient to reach both solutions. All potential $a_{0}$ terms for a given $X_{n}$ can be examined and tested, starting from 0 (or ideally $a_0$ for $X_{n-1}$ if known) and incrementing until the first satisfying integer is reached. 

There are some refinements that can be made by observing $a_0$ for $X_n$ as $n$ increases. For $n$ > 2, $a_0$ will always be divisible by 3 and congruent to 0 or 4 mod 5[^1]. These properties allow a decent proportion of candidate  $a_0$ values to be skipped while incrementing.

For each candidate $a_0$, the terms of $X_n$ can be checked for intersections with prime numbers. Using probabilistic tests for primality of terms is possible, but substantially slower than comparing against a collection of known primes.

The ranges of primes needed to reach the solution to the bonus challenge are not necessarily practical to produce directly with a Sieve of Eratosthenes. However a [segmented sieve](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes#Segmented_sieve) is able to produce the relevant primes quickly and with a small memory footprint. In a segmented sieve a starting upper bound is estimated, a set of initial primes up to the square root of that bound are produced, and those initial primes are used to mark intermediate sieves and produce lists of primes within higher integer ranges, including primes to expand the upper bound if needed.

[^1]: Thanks to Serge Batalov on [mersenneforum.org](https://www.mersenneforum.org/index.php) for [pointing out](https://www.mersenneforum.org/showpost.php?p=652840&postcount=49) the congruences for  $a_0$ mod 5