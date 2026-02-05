# January 2026 Ponder This Challenge
The [January challenge](https://research.ibm.com/haifa/ponderthis/challenges/January2026.html) involves splitting up the decimal digits of natural numbers.

## Challenges

Given a natural number $n$, there are various ways to split its decimal digits into separate sequential groups and take each member of the group as an integer. For example $1234$ could be broken up as $(1,2,3,4)$, $(12,3,4)$, $(1,23,4)$, $(1,2,34)$, $(12,34)$, $(123,4)$, $(1,234)$ or $(1234)$. 

Define $A_n$ as the set of sums of each possible split of the digits on $n$. For example $`A_{1234} = \{10, 19, 28, 37, 46, 127, 235, 1234\}`$

Define $n \cdot A_n$ as the set formed by multiplying each member of $A_n$ by $n$. For example $`1234 \cdot A_{1234} = \{12340, 23446, 34552, 45658, 113528, 156718, 289990, 1522756\}`$

The main challenge asks for the sum of all natural numbers $x$ where there exists $1 \le n \le 10^6$ such that $x \in n \cdot A_n$ and $n \in A_x$.

The bonus challenge asks for the sum of all natural numbers $x$ where that there exists $1 \le n \le 10^7$ such that $x \in n \cdot A_n$ and $n \in A_x$.

## Solution

The solution is implemented in Rust.

Usage:

```console
$ cargo run --release -- [OPTIONS]
```

or

```console
$ cargo build --release
$ ./target/release/jan2026 [OPTIONS]
```

```console
Options:
  -t, --threads <THREADS>  Set maximum number of worker threads [default: 4]
  -b, --bonus              Calculate bonus challenge solution
  -h, --help               Print help
```

Examples:

Find the solution to the main challenge:

```console
$ ./target/release/jan2026
```

Find a solution to the bonus challenge with 10 worker threads:

```console
$ ./target/release/jan2026 --bonus --threads 10
```

## Discussion

Constructing each $n \cdot A_{n}$ set  and testing each member $x \in n \cdot A_{n}$ to check if $n \in A_{x}$ is straightforward but requires a substantial number of operations for the ranges of $n$ in each challenge. However, there is a property of decimal notation that allows a large proportion of the sets to be skipped.

Adjacent to the concept of a [digital root](https://en.wikipedia.org/wiki/Digital_root), the sum of the digits of a natural number $n$ in any base $b \ge 2$ is congruent to $n \bmod (b - 1)$. In base 10 this sum is congruent to $n \bmod 9$. Thinking recursively, this can be applied to any groupings of the digits of $n$ into integers that are summed together. These sums will always be congruent to $n \bmod 9$ and so for all $a \in A_{n}$, $a \equiv n \bmod 9$. As a trivial corollary, $b \not\equiv n \bmod 9$ implies $b \not\in A_{n}$.

When applying this property to the set $n \cdot A_{n}$, this means that for all members $x \in n \cdot A_{n}$, $x \equiv n^2 \bmod 9$. If $n$ is not congruent to $n^2 \bmod 9$, $n$ cannot be a member of $A_{x}$. As a result, only cases where $n \equiv 0 \bmod 9$ or $n \equiv 1 \bmod 9$ can have members of $n \cdot A_{n}$ which contribute to the challenge sums. If $n$ is congruent to any other residue modulo 9,  $n \not\equiv n^2 \bmod 9$ and so any $n$ with these residues cannot have $x \in n \cdot A_{n}$ where $n$ could be a member of $A_{x}$. Any $n$ with these residues can be skipped when iterating over the $n \cdot A_{n}$ sets.

This still involves a large number of $n \cdot A_{n}$ sets to be examined, but parallelizing the search allows results to be found relatively quickly for both challenges.
