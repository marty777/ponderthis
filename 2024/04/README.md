# April 2024 Ponder This Challenge
The [April challenge](https://research.ibm.com/haifa/ponderthis/challenges/April2024.html) asks about simultaneous games of the Tower of Hanoi played using strings of moves.

## Challenges

For a game of the [Tower of Hanoi](https://en.wikipedia.org/wiki/Tower_of_Hanoi), played with $n$ disks on three rods arranged in a circle, the *winning state* is for all disks to be on the rod immediately clockwise from the starting rod. At each step in the game, at most three moves are possible: 

- **Move 0**, where the smallest disk is picked up and moved one rod clockwise
- **Move 1**, where the smallest disk is picked up and moved one rod counterclockwise
- **Move 2**, where some disk which is not the smallest is picked up and moved to another rod. Move 2 may not be possible depending on the state of the game, in which case it does nothing, and there can never be more than one possible disk and destination rod available for this move. 

A Tower of Hanoi game can be played by executing strings of these moves, wrapping back to the beginning of the string once the end is reached, and continuing to perform the moves of the string can reach the winning state multiple times. Given two games executing their move strings step-by-step simultaneously, one with $n = 7$ and following the string `12021121120020211202121` and one with $n = 10$ and following the string `0211202112002`, the main challenge asks for the first step where both games are in a winning state at the same time.

The bonus challenge adds a third game with $n = 9$ and the string `20202020021212121121202120200202002121120202112021120020021120211211202002112021120211200212112020212120211`  and asks for the first step where all three games are in a winning state at the same time.

## Solution

The solution is implemented in Python 3

Usage:

	$ python apr2012.py

The solution will calculate and output results for both the main and bonus challenges.

## Discussion

The solutions to both challenges are reachable by brute-force simulation, but at least one quicker method exists.

Because the move strings and the set of all possible states of each game are finite, there must be a periodic cycle to the game if the strings are repeated infinitely. At some step all disks will be returned to the starting position at the same time as the first move in the string is performed, and all subsequent states will exactly repeat the states of the previous cycle. For each simultaneous game considered, the game can be played until the end of the cycle is found while recording the number of steps played each time the winning state is reached.

If the periods of each game were pairwise coprime, it would be straightforward to treat each period and number of steps to reach a winning state as a modular congruence, then take a winning state from each game and find the smallest number of steps where each selected winning state was reached simultaneously by using standard methods for finding solutions to the [Chinese Remainder Theorem](https://en.wikipedia.org/wiki/Chinese_remainder_theorem). By doing this for every combination of winning states between the games the smallest overall number of steps that reached a winning state simultaneously in each game could be found easily. 

### Solving systems of modular congruences with non-coprime moduli

The periods of the games in the main and bonus challenges are not pairwise coprime. It is still possible to find solutions satisfying systems of congruences with non-coprime moduli, although the existence of a solution for a given system is not guaranteed. The approach to doing this efficiently is novel to me, so an approximate explanation of the process follows.

To demonstrate the algorithm, let's take the challenge example of game $A$ with $n=3$  and the string `0202112` and game $B$ with $n = 4$ and the string `200211` and add a third game $C$ with $n = 5$ and the string `2020211`:

* Game $A$ has a period of $28$ steps and reaches the winning state on steps $8$ and $9$.
* Game $B$ has a period of $162$ steps and reaches the winning state on steps $41$ and $122$.
* Game $C$ has a period of $112$ steps and reaches the winning state on steps $37$ and $38$.

Taking one winning state from each game, we'll attempt to solve the system of modular congruences:
* $x \equiv 9 \pmod{28}$ from game $A$
* $x \equiv 41 \pmod{162}$ from game $B$
* $x \equiv 37 \pmod{112}$ from game $C$
1. Factor each modulus under consideration[^1]. For our example moduli:
   * $28 = 2^2 \cdot 7$
   * $162 = 2 \cdot 3^4$ 
   * $112 = 2^4 \cdot 7$ 
2.  By the Chinese Remainder Theorem, if $m = p_1^{q_1}p_2^{q_2} \dots p_n^{q_n}$ for some set of prime factors and exponents then ${x \equiv a \pmod{m}}$ is equivalent to the set of congruences $x \equiv a \pmod{p_1^{q_1}}, x \equiv a \pmod{p_2^{q_2}},\dots, x \equiv a \pmod{p_n^{q_n}}$. Applied to the example congruences:
    * $x \equiv 9 \pmod{2^2}$
    * $x \equiv 9 \pmod{7}$
    * $x \equiv 41 \pmod{2}$
    * $x \equiv 41 \pmod{3^4}$
    * $x \equiv 37 \pmod{2^4}$
    * $x \equiv 37 \pmod{7}$
3. For each of the expanded congruences, sort them into groups by the base prime factor of the modulus. 
   * Group with factor $2$:
      * $x \equiv 9 \pmod{2^2}$
      * $x \equiv 41 \pmod{2}$
      * $x \equiv 37 \pmod{2^4}$
    * Group with factor $3$:
      * $x \equiv 41 \pmod{3^4}$
     * Group with factor $7$:
       * $x \equiv 9 \pmod{7}$
       * $x \equiv 37 \pmod{7}$
4. For groups with more than one member, there must be some minimal integer $x_p$ which satisfies each congruence within the group for prime $p$ if taken as the remainder or else there can be no solution to the original system of congruences. If $x_p$ exists it will necessarily be equivalent to the remainder of a congruence with a modulus raised to the greatest power within the group. In the example, $x_2 \equiv 37 \pmod{2^4} \equiv 5$ satisfies every congruence in the group for factor $2$, and $x_7 \equiv 9 \pmod{7} \equiv 2$ satisfies every congruence in the group with factor $7$.
   * $5 \pmod{2^2} \equiv 9 \pmod{2^2}$
   * $5 \pmod{2} \equiv 41 \pmod{2}$
   * $5 \pmod{2^4} \equiv 37 \pmod{2^4}$
   * $2 \pmod{7} \equiv 9 \pmod{7}$
   * $2 \pmod{7} \equiv 37 \pmod{7}$
5. If an integer $x_p$ satisfying each congruence in prime group $p$ exists, each congruence in the group is implied by $x_p \pmod{p^q}$, where $q$ is the greatest power of a modulus within the group.  All other congruences in the group can be discarded, leaving $x_p \pmod{p^q}$ as the single member. In our example, this leaves the congruences:
   * $x \equiv 5 \pmod{2^4}$
   * $x \equiv 41 \pmod{3^4}$
   * $x \equiv 2 \pmod{7}$
6. Once each of the prime factor groups have been reduced to a single congruence, we have a system of modular congruences with pairwise coprime moduli. Methods for finding solutions to the Chinese Remainder Theorem can be applied to solve for $x$. In the example $x = 6197$ is the smallest non-negative integer satisfying the original three congruences. It is also the only combination of winning steps from $A$, $B$ and $C$ where there is a solution to the system of congruences and thus the smallest number of steps where games $A$, $B$ and $C$ are in a winning state simultaneously.

Applying this approach to every possible combination of winning states between each game and taking the smallest solution of any of the systems that are solvable gives the challenge answers.

[^1]: It's worth noting that it's not necessary to fully factor each modulus with this approach, although it's simpler to explain in a readme.  Factoring each modulus is feasible for these small examples, but for larger integers beyond the scope of this challenge it may be computationally expensive. Repeatedly separating out greatest common divisors - even if composite - can produce a similar set of grouped congruences to those described above for prime divisors of moduli and can either show that the original system has no solutions or find the solution using the CRT. 