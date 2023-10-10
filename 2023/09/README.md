# September 2023 Ponder This Challenge
The [September challenge](https://research.ibm.com/haifa/ponderthis/challenges/September2023.html) asks about a recursively defined sequence ***a*** where *a*<sub>*n*</sub> = *a*<sub>*n*-1</sub> + gcd(*n*, *a*<sub>*n*-1</sub>) and an associated sequence of differences ***d*** between consecutive terms of ***a***, where *d*<sub>*n*</sub> = *a*<sub>*n*</sub> - *a*<sub>*n*-1</sub> = gcd(*n*, *a*<sub>*n*-1</sub>) and the first term in the sequence is *d*<sub>2</sub>.

## Challenges

The main challenge asks for the index *n* such that *d*<sub>*n*</sub> is the 10<sup>th</sup> occurrence of five in the sequence ***d*** where *a*<sub>1</sub> = 531. It also asks for some *k* and *n* such that *d*<sub>*n*</sub> for *a*<sub>1</sub> = *k* is greater than one and not prime.

The bonus challenge asks for the index *n* such that *d*<sub>*n*</sub> is the 200<sup>th</sup> occurrence of five in the sequence ***d*** where *a*<sub>1</sub> = 531.

## Solution

The solution is implemented in Go.

Usage:

	$ go run sept2023 [OPTIONS]

	or

	$ go build
	$ ./sept2023 [OPTIONS]

	Options:
		-b          Find the solution to the bonus challenge
		-v          Print each occurrence of 5 in d_n as it is found
		-p path     Provide a text file of pre-calculated primes at the given path for factorization in the bonus challenge
		-h          Print usage
		
Examples:

Solve the main challenge:

	$ ./sept2023
	
Solve the bonus challenge:

	$ ./sept2023 -b -v
	
Solve the bonus challenge with a pre-computed set of primes for the *a*<sub>1</sub> = 531 sequence for faster factorization:

	$ ./sept2023 -b -p big_primes_531.txt -v

## Discussion

### Main challenge

The main challenge is relatively easy to solve. It's straightforward to iterate over ***d*** for *a*<sub>1</sub> = 531 until the 10<sup>th</sup> five is found and to trial varying *k* and *n* for the second part of the main challenge until a non-prime *d*<sub>*n*</sub> is reached. 

### Bonus challenge 

Iterating over ***d*** one step at a time to reach the undoubtedly large index of the 200<sup>th</sup> occurrence of five is not practical in reasonable time. The presence of the GCD in the recursive definition of the terms of ***a*** makes it unlikely that a closed form of the sequence exists (although I would love to be surprised), so traversing ***a*** and ***d*** in some way must be necessary to obtain the challenge answer.

If we can't determine the index of the challenge answer without traversing the sequences, and doing so in increments of one is prohibitively slow, then we need some method to skip over predictable parts. Fortunately, there are substantial sections where consecutive *n* and *a*<sub>*n*-1</sub> are co-prime, and so *d*<sub>*n*</sub> = gcd(*n*, *a*<sub>*n*-1</sub>) = 1. If we can find a way to predict the length of a section of ones, we can avoid iterating over it and skip to the next position in the sequence where *d*<sub>*n*</sub> > 1 with simple arithmetic. The process can be repeated until the 200<sup>th</sup> occurrence of  *d*<sub>*n*</sub> = 5 is reached.

The method to determine the length of these sections uses some basic properties of modular congruence:

1. <a name="property1"></a>If *x* mod *m* ≡ *y* mod *m* then *x* + *z* mod *m* ≡ *y* + *z* mod *m* for any integers *x*, *y*, *z* and *m* > 0. That is, modular congruence is preserved in addition operations.
2. <a name="property2"></a>For any integers *x* and *y* and all integers *m* > 0 such that *m* divides (*x* - *y*), *x* mod *m* ≡ *y* mod *m*.
3. <a name="property3"></a>For any composite integer *m* > 0 and some integer *x* such that *x* mod *m* ≡ 0, there is at least one prime factor *p* of *m* such that *x* mod *p* ≡ 0.

Suppose we know some index *i* where *d*<sub>*i*</sub> > 1. Assuming that *d*<sub>*i*</sub> is not the final non-one term in ***d***, the next will appear some distance in the sequence away, at *d*<sub>*i* + *j*</sub> for some offset *j* > 0. Because index *i* + *j* follows a section of *j* consecutive ones in ***d***,  this means that *a*<sub>*i* + *j* - 1</sub> = *a*<sub>*i* - 1</sub> + *j*. We wish to determine *j*.

Since *d*<sub>*i* + *j*</sub> = gcd(*i* + *j*, *a*<sub>*i* + *j* -1</sub>) > 1,  there will be some non-zero number of common divisors that divide both *i* + *j* and  *a*<sub>*i* + *j* -1</sub>. For each common divisor *c*,   *i* + *j* mod *c* ≡ *a*<sub>*i* + *j* - 1 </sub> mod *c* ≡ 0. Because we know that *a*<sub>*i* + *j* - 1</sub> = *a*<sub>*i*- 1</sub> + *j*, this means that:

- *i* + *j* mod *c* ≡ *a*<sub>*i* + *j* - 1</sub> mod *c*

- *i* + *j* mod *c* ≡ *a*<sub>*i* - 1</sub> + *j* mod *c*

- *i* mod *c* ≡ *a*<sub>*i* - 1</sub> mod *c* (by [property 1](#property1))

In other words, there exists one or more moduli *c* such that *i* and *a*<sub>*i* - 1</sub> are congruent mod *c* and some *j* such that *i* + *j* mod *c* ≡ 0. Determining these moduli allows us to solve for *j* = *c* - (*i* mod *c*). 

If there is no *c* > 1 that satisfies these congruences, then there are no subsequent non-one terms of ***d***. If there is more than one *c* that satisfies these congruences, then we are looking for one that yields the smallest offset *j*, which will correspond to the next non-one term of ***d***. 

By [property 2](#property2), all possible moduli *c* > 0 where *a*<sub>*i* - 1</sub> and *i* are congruent modulo *c* must divide (*a*<sub>*i* - 1</sub> - *i*). We can determine these divisors by factoring (*a*<sub>*i* - 1</sub> - *i*). We only need to examine the prime factors of (*a*<sub>*i* - 1</sub> - *i*) and can ignore any composite divisors by [property 3](#property3) since we are looking for the smallest offset *j* to reach the next non-one index of ***d***. Trivially, if there is some composite modulus *c* such that *i* + *j* mod *c* ≡ 0, then *i* + *j* mod *p* ≡ 0 for at least one prime factor *p* of *c*, and the offset corresponding to *c* cannot be less than the offset corresponding to *p*. Once the smallest offset *j* is determined to skip to the next non-one term, the process can be repeated until the desired term of ***d*** is reached.

While the factoring of each intermediate (*a*<sub>*i* - 1</sub> - *i*) is computationally expensive, it is feasible for the ranges of integers involved. Skipping over the sections of ones allows the bonus challenge solution to be reached in approximately 2000 relatively expensive steps rather than the 2 x 10<sup>38</sup> inexpensive steps to iterate over ***d*** directly, a beneficial trade-off. This method can also be applied to the main challenge.

The solution includes a file (big_primes_531.txt) with a pre-calculated list of prime factors relevant to reaching the bonus challenge solution for the *a*<sub>1</sub> = 531 sequence that can optionally be provided for faster execution with the "-p" argument.
