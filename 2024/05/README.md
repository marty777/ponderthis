# May 2024 Ponder This Challenge
The [May challenge](https://research.ibm.com/haifa/ponderthis/challenges/May2024.html) explores the mathematics of the card game *Dobble*.

## Challenges

In the card game [Dobble](https://en.wikipedia.org/wiki/Dobble) (also marketed as *Spot It!* in the US), each of the 55 cards in the deck is marked with 8 symbols out of a possible 57. The deck is constructed in such a way that any two cards share exactly one symbol in common, the task of the players being to spot the common symbol.

It's possible to construct a Dobble-like deck for any given order $N$ with $N$ a prime power, where there are $N^2 + N + 1$ symbols and cards in the deck, and each card contains $N + 1$ symbols, *Dobble* being an example for $N = 7$ with two cards omitted out of the available 57.

The main challenge asks for the number of all possible Dobble-like decks for $N=4$

The bonus challenge asks for the number of all possible Dobble-like decks for $N=8$

## Solution

The solution is implemented in Rust.

Usage:

    $ cargo build --release
	$ ./target/release/may2024 [OPTIONS]
    or
    $ cargo run may2024 -- [OPTIONS]

    Options:
        -N, --order <ORDER>      Set the order of the finite projective plane. [default: 4]
        -t, --threads <THREADS>  Set maximum number of worker threads. [default: 4]
        -v, --verbose            Print calculation progress.
        -h, --help               Print help

Examples:

Solve the main challenge:
    
    $ cargo build --release
    $ ./target/release/may2024 --verbose -N 4

Solve the bonus challenge with 12 worker threads (runtime likely to exceed an hour on a recent desktop PC):

    $ cargo build --release
    $ ./target/release/may2024 --threads 12 --verbose -N 8

Solutions for $N=2,3,4,5,7,8$ are supported.

## Discussion

I didn't get the bonus answer on this one. I found a reasonable-seeming and very fast shortcut which was coincidentally accurate for $N = 4$ and incorrect for $N = 8$. A good learning experience, and after some further work this solution determines the correct number of distinct Dobble-like decks up to $N = 8$.

*Dobble* is an application of a [finite projective plane](https://en.wikipedia.org/wiki/Projective_plane#Finite_projective_planes), a geometrically-motivated construction of lines and points connected to (or *incident with*) each other. For a given order $N$, a finite projective plane has the following characteristics:

 * Given any two distinct points, exactly one line is incident with them.
 * Given any two distinct lines, exactly one point is incident with them.
 * There are $N^2 + N + 1$ points.
 * There are $N^2 + N + 1$ lines.
 * Each line is incident with $N + 1$ points.
 * Each point is incident with $N + 1$ lines.

If we swap "lines" and "points" with "cards" and "symbols", it's straightforward to see the equivalence of the concepts.

Consider an incidence matrix for the finite projective plane of order $N = 2$. In *Dobble* terms, let's say the rows represent cards and the columns represent symbols, with a 1 indicating that the card corresponding to the row contains the symbol corresponding to the column:

    1 1 1 0 0 0 0
    1 0 0 1 1 0 0
    0 0 1 1 0 1 0
    0 0 1 0 1 0 1
    0 1 0 1 0 0 1
    1 0 0 0 0 1 1
    0 1 0 0 1 1 0

Importantly, all possible arrangements of lines and points in finite projective planes of orders $N = 2, 3, 4, 5, 7, 8$ are each known to be *isomorphic* to each other.  Thanks to this isomorphism, all possible incidence matrices that describe a finite projective plane of order 2 can be found by re-ordering the rows and columns of this incidence matrix. The same principal applies to incidence matrices for any other finite projective plane of the above orders.

For a deck of cards, the same set of cards arranged in a different order is still the same deck, so row order can be ignored when determining the number of distinct decks. Symbol order is  a different matter, since rearranging which symbols are incident with cards may produce distinct decks. There are $(N^2 + N + 1)!$ ways to permute the columns of the incidence matrix, which makes directly enumerating the distinct resulting decks impractical for $N = 4$ and $N = 8$.

Let's call the total number of distinct decks $D_N$ for a given order $N$. By exhaustively permuting incidence matrices for low $N$, we can observe that every distinct deck has an identical number $C_N$ of column permutations that produce it. With $(N^2 + N + 1)!$ possible column permutations, this means:

$$D_N = \dfrac{(N^2 + N + 1)!}{C_N}$$

Since counting $D_N$ cannot be done in reasonable time, determining $C_N$ will allow us to solve for it.

For brevity, let's call a deck the set of all incidence matrices which contain identical rows, possibly re-ordered. Since $C_N$ is the number of column permutations of an initial incidence matrix that produce a specific deck, it's convenient to examine permutations that are *automorphic*, producing members of the deck containing the initial incidence matrix. For $N = 8$ the space to be searched is still too large to find $C_N$ directly. It is instead possible to enumerate a small subset of column permutations, count the automorphic permutations within that subset, and infer the total number of possible automorphic permutations arithmetically.

Intuitively, if we're looking for all permutations of symbols/columns that result in the same deck of cards/rows, then symbols cannot be swapped between cards/rows or the permutation will result in a different deck. By fixing 3 columns/symbols incident with a single card/row, and counting all the remaining permutations of the symbols common to the same card, we obtain a count of automorphic permutations $C_N'$ for this subset that can be reached in reasonable time. Extrapolating this amount across all possibly ways to chose 3 fixed columns/symbols:

$$C_N = C_N' \cdot (N^2 + N + 1) \cdot \dfrac{(N+1)!}{(N + 1 - 3)!}$$

That is, $C_N$ is $C_N'$ multiplied by the number of ways to select 3 fixed columns/symbols (remembering that any 3 columns/symbols will be incident with exactly one of $N^2 + N + 1$ rows), multiplied by the number of ways to permute the remaining columns incident with the row.

Once $C_N$ is known, $D_N$ can be calculated easily. For the $N=2$ example above, the search for automorphic column permutations with 3 columns fixed finds $C_2' = 4$, so:

$$C_2 = 4 \cdot 7 \cdot \dfrac{(2 + 1)!}{(2 + 1 - 3)!} = 168$$

$$D_2 = \dfrac{7!}{168} = 30$$

Sample incidence matrices for finite projective planes of orders $N=2,3,4,5,7,8$ used in this solution were mostly generated using the [SageMath package](https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/designs/block_design.html#sage.combinat.designs.block_design.projective_plane).