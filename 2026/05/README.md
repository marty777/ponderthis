# May 2026 Ponder This Challenge
The [May challenge](https://research.ibm.com/blog/ponder-this-may-2026) asks about powers of certain square binary matrices.

## Challenges

Consider a square binary matrix $A$ of order $N$: $A \in M(\mathbb Z_{2})_{N \times N}$ having exactly one 1 entry in each row and column. There is a minimum $m > 0$ such that $A^m = I$.

Define a function $g(N)$ equal to the maximum $m$ when taken over all such matrices in $M(\mathbb Z_{2})_{N \times N}$.

The main challenge asks for $g(10^6) \bmod (10^9 + 7)$.

The bonus challenge asks for $g(10^8) \bmod (10^9 + 7)$.

## Solution

The solution is implemented in Rust.

### Usage

```console
$ cargo run --release -- [OPTIONS]
```

or

```console
$ cargo build --release
$ ./target/release/may2026 [OPTIONS]
```

```console
Options:
  -n, --number <NUMBER>    The value of N to calculate g(N) to [default: 1000000]
  -m, --modulus <MODULUS>  The modulus to calculate g(N) under [default: 1000000007]
  -h, --help               Print help
```

### Examples

Solve the main challenge:

```console
$ ./target/release/may2026
```

Solve the bonus challenge:

```console
$ ./target/release/may2026 -n 100000000
```

The bonus challenge may take some time to complete the calculation. The solution is probably not suitable for $N$ much greater than $10^8$.

## Discussion

A square binary matrix with exactly one 1 entry in each row and column is a [permutation matrix](https://en.wikipedia.org/wiki/Permutation_matrix). A permutation matrix of order $N$ can represent a permutation of the ordering of a list of $N$ elements, and this is a useful way to think about how to compute $g(N)$. For a finite number of elements, there must be a finite number of successive applications of any permutation of those elements that returns the them to their original positions; $A^m = I$ represents a return to the original ordering of the elements after the selected permutation has been applied $m$ times. This makes $m$ the *period* of the permutation $A$, and so the challenges are asking for the greatest possible period of any permutation of $N$ elements.

Any permutation where all positions in the list exchange elements with each other will necessarily have a period equal to the number of elements in the list, because there must be an ordering that forms a single cycle of that length. However, it's not necessarily the case that each element is part of the same set of exchanges. The list of elements could instead be partitioned into sub-groups of elements that exchange positions with other elements of the same group, but not with members of other groups. With successive applications of the overall permutation, each group will cycle its elements with a period equal to the number of elements in the group. The entire list would return to its original ordering on the step when the periods of each of the groups align, with the total period of the permutation being the least common multiple (LCM) of the sizes of each group.

The greatest possible period out of all permutations of a list of elements of size $n$ is [Landau's function](https://en.wikipedia.org/wiki/Landau%27s_function), $g(n)$, the largest LCM of any partition of a natural number $n$. Computing Landau's function directly is not an obvious process. By experimenting with small $n$, it is evident that the maximum LCMs occur when the partition groups all have numbers of elements which are primes, prime powers, or 1. Since all of the group sizes are coprime, the LCM is the product of the group sizes. Exploring all such partitions of $n$ to find the maximal LCM is not feasible in reasonable time beyond small $n$ because the number of possible partitions grows rapidly.

Fortunately, work has been done in this area that is suitable for solving the challenges. [Nicolas (1969)](https://eudml.org/doc/193122)[^1] gives an elegantly simple algorithm for the simultaneous calculation of each $g(x)$ for $0 \le x \le n$ with an implementation in Fortran. [Grantham (1995)](https://pubs.ams.org/journals/mcom/1995-64-209/S0025-5718-1995-1270619-3)[^2] proves an upper bound for the largest prime divisor of $g(n)$ as no greater than $1.328 \sqrt{n \ln n}$ for $n \ge 5$. [Deléglise, Nicolas and Zimmermann (2008)](https://jtnb.centre-mersenne.org/item/?id=JTNB_2008__20_3_625_0)[^3] describe an improved (and quite complicated) algorithm for directly computing $g(n)$ individually for large $n$  without needing to process intermediate values. They also reproduce, in section 2.1, what I believe is Nicolas' 1969 algorithm implemented as a Maple procedure with the refinement of using Grantham's bound for the largest prime divisor. They warn that the older algorithm is unsuitable for $n > 10^6$ and note that a run to calculate that value took 13 hours on a Pentium 4. However, it seems that the pace of computing hardware development combined with only needing to calculate the residue of $g(n)$ makes the older algorithm suitable for solving the challenges. Using it to compute $g(10^6) \bmod (10^9 + 7)$ completes in seconds on a relatively recent desktop PC, and $g(10^8) \bmod (10^9 + 7)$ can be computed in well under an hour using a few GB of memory. I haven't properly explored the 2008 approach although the paper looks very interesting. It should be noted that Jean-Louis Nicolas provides a Maple implementation of the more recent algorithm [here](http://math.univ-lyon1.fr/~nicolas/landaug.html).

[^1]: Nicolas, Jean-Louis. "Calcul de l’ordre maximum d’un élément du groupe symétrique *S<sub>n</sub>*" *ESAIM: Mathematical Modelling and Numerical Analysis - Modélisation Mathématique et Analyse Numérique* vol. 3, issue R2, 1969, pp. 43-50. http://eudml.org/doc/193122

[^2]: Grantham, Jon. "The largest prime dividing the maximal order of an element of *S<sub>n</sub>*", *Math. Comp.* vol. 64, 1995, pp. 407-410. https://pubs.ams.org/journals/mcom/1995-64-209/S0025-5718-1995-1270619-3

[^3]: Deléglise, Marc and Nicolas, Jean-Louis and Zimmermann, Paul. "Landau’s function for one million billions" *Journal de théorie des nombres de Bordeaux* vol. 20 no. 3, 2008, pp. 625-671. https://jtnb.centre-mersenne.org/item/?id=JTNB_2008__20_3_625_0