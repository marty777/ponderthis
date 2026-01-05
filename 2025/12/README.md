# December 2025 Ponder This Challenge
The [December challenge](https://research.ibm.com/haifa/ponderthis/challenges/December2025.html) asks about the sums of primes and even numbers that are also prime.

## Challenges

Consider a function $f(n)$, with $n$ a natural number, such that $f(n)$ is equal to the total number of pairwise sums between the set of the first $n$ odd primes $(3,5,7,\ldots)$ and the set of the first $n$ positive even integers $(2,4,\ldots,2n)$ where the sum is itself prime.

The main challenge asks for $f(10^8)$.

The bonus challenge asks for $f(10^9)$.

## Solution

The solution is implemented in Go.

Usage:

```console
$ go run dec2025.go [OPTIONS]
```
or 
```console
$ go build
$ ./dec2025 [OPTIONS]
```

```console
Options:
	-b    Solve the bonus challenge
```

Examples:

Solve the main challenge:
```console
$ go run dec2025.go
```

Solve the bonus challenge:
```console
$ go run dec2025.go -b
```

The bonus solution requires several minutes and a significant amount of available memory to reach an answer.

## Discussion

### Listing primes

I'm recycling a [segmented Sieve of Eratosthenes](https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes#Segmented_sieve) I used in the [March 2024](https://research.ibm.com/haifa/ponderthis/challenges/March2024.html) challenge [solution](https://github.com/marty777/ponderthis/tree/main/2024/03) in my approach to the challenges. It's not particularly fast or memory-efficient, but working with lists of primes within incremented integer ranges is a convenient way to think about the problem.

The segmented sieve builds and stores two ordered lists of primes at a time, each covering all primes within adjacent ranges of length $2n$. The $L$ (low) and $H$ (high) lists are initially set up with the $L$ list  including all primes in $[3,3 + 2n - 1]$ and the $H$ list including all primes in $[3+2n,3+4n - 1]$. All primes that could be a sum of one of the primes in $L$ and a positive even number up to $2n$ will be contained in either $L$ or $H$. Once all primes in the $L$ list have been examined, the $L$ list is dropped, the $H$ list becomes the new $L$ list, and the next $H$ list is generated covering primes in the subsequent $2n$ integers. This can continue until the number of prime pairwise sums for the $n$<sup>th</sup> prime is found.

### Enumerating prime pairwise sums

Testing the primality of each pairwise sum for a given prime is as straightforward as looking for a matching prime in the prime lists of suitable ranges, but directly counting the prime sums would involve $n^2$ operations which is not practical for the challenge $n$. However, the number of prime pairwise sums between a prime $p$ and the integers $(2,\ldots,2n)$ is simply the number of primes in the range $[p+2,p+2n]$. Since the lists of primes $L$ and $H$ are ordered, this number can be determined arithmetically. 

Given $L = (p_1, p_2,\ldots,p_{|L|})$ and $H = (q_1, q_2,\ldots,q_{|H|})$, for each $p_{i} \in L$ the largest prime less or equal to $p_{i} + 2n$ will necessarily either be $p_{|L|}$ if $p_{i} + 2n < q_{1}$ or else $q_{j}$ for some $1 \le j \le |H|$ because of the lengths of both ranges have been set as $2n$. Therefore:

- For $p_{|L|} \le p_{i} + 2n < q_{1}$ the number of odd primes in $[p_{i}+2,p_{i} + 2n]$ is $|L| - i$.

- For $q_{j} \le p_{i} + 2n < q_{j+1}$ the number of odd primes in $[p_{i}+2,p_{i} + 2n]$ is $|L| - i + j$.

- For $q_{|H|} \le p_{i} + 2n$ the number of odd primes in $[p_{i}+2,p_{i} + 2n]$ is $|L| - i + |H|$.

The first and third cases are trivial, and the only complexity with the second case is in locating $q_{j}$. I initially used a binary search through the primes in $H$, but since the index of $q_{j}$ for $p_{i}$ will frequently differ by no more than $1$ from that of $p_{i-1}$ (and never by more than $24$ in the bonus challenge) a sequential search performs slightly better.

This brings the computational complexity for determining the number of prime pairwise sums for each of the first $n$ odd primes below the order of $n \ln{n}$[^1], although that doesn't count the operations used to produce the primes. For $n = 10^9$ the task will still take several minutes to complete and enough memory to sieve and store all primes in $[3,3+4\cdot 10^9 - 1]$ initially. The memory use tapers off somewhat as lower ranges are dropped and the density of primes decreases at higher ranges.

[^1]: I think the computational complexity using this method is nearly linear. Nevertheless, the sequential search for prime indexes in the high set increases in cost as *n* increases, although it does so very slowly.