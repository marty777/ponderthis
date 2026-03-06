# February 2026 Ponder This Challenge
The [February challenge](https://research.ibm.com/blog/ponder-this-february-2026) involves the probabilities of a backgammon-like game.

## Challenges

Consider a single-player backgammon-like game. The board has infinite positions, and the game starts with 5 "men" pieces at position 0.

On every turn two dice are rolled. If the two dice are rolled to different values, two moves forward in the indicated amounts are applied to a man or men (both moves may be applied to a single piece). If the two dice are rolled to the same value, each dice is used twice and four moves forward in the indicated amount are applied to men in any combination.

If one man ends up in a location alone, this is called a *blot*. If the player's turn ends with a blot, the game ends.

The main challenge asks for the expected number of dice rolls (except for the final roll) when playing with optimal strategy and when the dice can only have outcomes $1$ and $2$, with equal probability. The answer can be given as a rational number or as a decimal to 6 digits of precision.

The bonus challenge asks for the expected number of dice rolls (except for the final roll) when playing with optimal strategy and the dice can have outcomes $1,2,3,4,5,6$, with equal probability.

## Solution

The solution is implemented in Python and uses the [SymPy](https://www.sympy.org/en/index.html) package for matrix operations with rational numbers.

Usage:

```console
$ pip install sympy
$ python feb2026.py [-h] [-s]
```
```console
optional arguments:
  -h, --help      show this help message and exit
  -s, --strategy  search for the optimal strategy for each challenge rather than using a pre-computed result
```
Examples:

Output the main and bonus challenge answers, using pre-calculated optimal strategies for each.

```console 
$ python feb2026.py
```

Output the main and bonus challenge answers, enabling a full search for the optimal strategies for each. This may take some time to complete.

```console 
$ python feb2026.py --strategy
```

## Discussion

This is a fun problem.

The positions on the board are given with a zero-based index, but it reduces the complexity to think of arrangements of men only in terms of the relative positions of the pieces. The discussion below will indicate non-blot arrangement *states* in forms like $(2,0,0,3)$, indicating two men at the rearmost occupied position and three men at the foremost occupied position, with two empty positions between them.

From any reachable non-blot state it is always possible to reach at least one subsequent non-blot state if the dice roll is a double, but there are several important sub-types of states that arise in the structure of the game. The following terms are used: 

- *Branching* states have more than one choice for next non-blot states on certain dice rolls (and a roll with multiple choices on a branching state is termed a  *branch*). 
- *Special* states have moves available that reach non-blot states on one or more mixed dice rolls.
- *Detached* states have a particular form that means they can only reach other detached states, and only on double rolls. 

Branching states are finite under either challenge. A *strategy* in this game is a set of selections for which next state to choose whenever a branch is reached. In the optimal strategy or strategies, these selections maximize the expected number of dice throws.

### Branching states

The state $(3,0,2)$ is an example of a branching state in the main challenge, having two dice rolls that are branches.

- If the dice are rolled as $(1,1)$, there are two possible non-blot next states. 
    - The two foremost men can be moved forward 2 spaces each to reach the state $(3, 0, 0, 0, 2)$
    - Two of the rearmost men can be moved forward 1 space each, and the final rearmost man can be moved forward 2 spaces to reach the state $(2,3)$
- If the dice are rolled as $(2,2)$ there are two possible non-blot next states.
    - The two foremost men can be moved forward 4 spaces each to reach the state $(3, 0, 0, 0, 0, 0, 2)$
    - The two foremost men can be moved forward 2 spaces each, and one rearmost man can be moved forward 4 spaces to reach the state $(2,0,0,0,3)$

A strategy in the main challenge would select one preferred next state for each branch from this state, along with choices for all other branches across other branching states.

### Special states

The state $(3,0,0,2)$ is an example of a special state in the main challenge, able to reach a non-blot state if mixed dice are rolled:

- If the dice are rolled as $(1,1)$, the two foremost men can be moved forward 2 spaces each to reach the state $(3,0,0,0,0,2)$
- If the dice are rolled as $(2,2)$, the two foremost men can be moved forward 4 spaces each to reach the state $(3,0,0,0,0,0,0,2)$
- If the dice are rolled as $(1,2)$ or $(2,1)$, one rearmost man can be moved forward 3 spaces to reach the state $(2,0,0,3)$

The $(3,0,0,2)$ state is the only special state in the main challenge, but the bonus challenge has fifteen, some with multiple mixed rolls that can reach non-blot states.

If the player can reach one of these states, their probability of creating a blot is reduced (or eliminated) on that turn. Strategies where choices are made at branches that are more likely to reach these special states will have greater expected numbers of dice rolls.

### Detached states

Certain states reach a pattern that cannot reach any other type of state and can only reach subsequent non-blot states of the same pattern with double dice rolls. States with the form $(3,0,0,...,0,0,2)$, where the number of empty positions between the $3$ group and the $2$ group is four times or greater than the greatest face on the dice, can only advance the two foremost men forward some number of spaces to avoid a blot. These states will continue to increase the gap between the rearmost and foremost groups as long as doubles are rolled, but the probability of the game continuing does not change from turn to turn once a detached state has been entered.

There are infinitely many possible detached states (and a finite number of non-detached states). This solution models the set of detached states as a single detached state transitioning to itself if doubles are rolled and to a blot state otherwise. Since it is impossible to return to non-detached states from a detached state, choices that lead to detached states cannot be part of an optimal strategy because special states cannot be reached from them.

### State graphs and game strategies

For a given number of faces on the dice and starting from the $(5)$ state, it's possible to iterate over all possible states that can be reached for each possible dice roll and store the non-blot states indexed by starting state and dice combination, then proceed to do the same with each subsequent state until all non-detached states have been reached. Representing all distinct detached states as a single node means the resulting directed graph is finite.

Many states and rolls lead to detached states, but cycles can be found within the non-detached states that include special states as members. The optimal strategy would be to select routes within the graph such that the overall expected number of rolls is maximized by prioritizing reaching special states as frequently as possible. Selecting the optimal strategy within a complicated directed graph accounting for dice roll probabilities and multiple special states is not a simple process, but determining the expected number of rolls for a given strategy is straightforward.

### Calculating expected number of dice rolls

For a given strategy, an [absorbing Markov chain](https://en.wikipedia.org/wiki/Absorbing_Markov_chain) can be constructed for the resulting game. A single absorbing node in the structure represents all blot states, which end the game when entered. A single transient node represents all detached states, only transitioning to itself or the absorbing node based on the probability of rolling doubles. The remaining non-detached states are represented by transient nodes with transitions according to the probabilities of the dice rolls between them, the connections specified by the state graph, and the selected strategy.

Once the transition matrix has been constructed, the [fundamental matrix](https://en.wikipedia.org/wiki/Absorbing_Markov_chain#Fundamental_matrix) of the Markov chain can be used to calculate the expected number of turns (including the final turn) before an absorbing state is reached when starting from any non-absorbing node in the model. If the transition matrix $P$ for an absorbing Markov chain with $t$ transitional states and $r$ absorbing states is constructed as follows, where $Q$ is a $t \times t$ matrix, $R$ is a nonzero $t \times r$ matrix, $\mathbf {0}$ is a $r \times t$ zero matrix and $I_{r}$ is the $r \times r$ identity matrix:

$$P={\begin{bmatrix}Q&R\\ 
\mathbf {0} &I_{r}\end{bmatrix}}$$

Then the fundamental matrix $N$ of the Markov chain is:

$$N = \sum_{k=0}^{\infty }Q^{k} = (I_{t}-Q)^{-1}$$

Given $N$, the expected number of steps to reach an absorbing state starting from state $i$ is the $i$<sup>th</sup> entry of the vector

$$\mathbf {v} = N \mathbf{1}$$

With $\mathbf {1}$ the $t$-length vector of all ones. 

The entry corresponding to the $(5)$ state gives the expected number of dice rolls for the game using the selected strategy. The calculated amount includes the final dice roll that leads to a blot state. Since the challenge asks for that roll not to be included, the final answer subtracts one from that value.

### Optimal strategies

Once choices that lead to detached states are omitted (because choices leading to detached states cannot be part of an optimal strategy where non-detached options are available), the main challenge has five branches across three branching states, each with two options. The bonus challenge has sixteen branches across ten branching states, each with two options. Although I suspect there's a better approach for this, the problem spaces are small enough that an option for finding the optimal strategy for each challenge is to iterate over all possible permutations of branch choices, calculate the expected number of dice rolls for each, and take the one that maximizes the expected rolls as the optimal strategy. 

For the main challenge, this examines $2^{5} = 32$ strategies. For the bonus challenge, this examines $2^{16} = 65536$ strategies, which is feasible to complete in reasonable time (20-30 minutes in my Python implementation). In the included solution script, the search for the optimal strategies for both challenges is skipped by default and pre-calculated strategies are used. The search can be enabled with the `--strategy` flag.

Once an optimal strategy is found, the corresponding expected number of dice rolls is returned as the challenge answer.
