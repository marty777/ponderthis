 # November 2023 Ponder This Challenge
The [November challenge](https://research.ibm.com/haifa/ponderthis/challenges/November2023.html) asks about the [15 Puzzle](https://en.wikipedia.org/wiki/15_Puzzle) 4 x 4 sliding tile game where the tiles can be arranged to form a 4 x 4 [magic square](https://en.wikipedia.org/wiki/Magic_square).

## Challenges

Starting from a sorted board (exactly half of all possible arrangements of tiles can be reached from a standard sorted board, with the other half reachable from a sorted board with the 14 and 15 tiles swapped. Either arrangement of sorted board is acceptable for the challenge solution), the main challenge asks for a sequence of no more than 150 moves that results in the tiles forming a magic square, along with the initial and final board states. 

The bonus challenge asks for a sequence of no more than 50 moves that results in a magic square.

## Solution

The solution is implemented in Python.

Usage:

	$ python nov2023.py [-h] [-m MAXDEPTH] inputfile

	positional arguments:
		inputfile		a provided file listing all 880 distinct 4x4 magic squares
    
	optional arguments:
		-h, --help		show this help message and exit
		-m MAXDEPTH, --maxdepth MAXDEPTH
						maximum move depth to explore for solutions.
Example:
	
	$ python nov2023.py all_magic_squares_order_4.txt --maxdepth 50
	
Note that searching to a depth of 50 moves will take a relatively long time to evaluate each magic square. Passing 40 or lower is substantially faster. There are no possible solutions with fewer than 35 moves.
    
## Discussion 

### Magic squares

Magic squares, arrangements of integers into an *n* x *n* grid where each row, column and the two main diagonals all sum to the same amount, are a longstanding area of mathematical, aesthetic and even mystical interest with surviving examples dating back to at least 190 BCE. Efforts in generating and enumerating magic squares are ongoing, and the number of distinct magic squares of order 6 is believed to have been correctly calculated in a [project](https://magicsquare6.net/doku.php?id=magicsquare6) headed by Hidetoshi Mino in July 2023.

This solution does not make any attempt to generate magic squares directly. The list of all 880 distinct magic squares of order 4[^1] was  compiled by Bernard Frénicle de Bessy in the late 17th c. (the precise date is unclear, the treatise containing them was published postumously in 1693) and verified by many since, and so we can take advantage of that work. The included `all_magic_squares_order_4.txt` file, adapted from a  [dataset of the order 4 magic squares](http://recmath.org/Magic%20Squares/order4list.htm) made available by Harvey Heinz,  lists each distinct 4 x 4 magic square composed of the digits 0-15. When read in by the solution, this list is expanded to include all reflections and rotations of each square for a total 7040 magic square arrangements.

### 15 Puzzle

The 15 Puzzle sliding tile game, where a set of 15 tiles are laid out in a 4 x 4 grid with one empty space and can be slid horizontally or vertically, should be familiar to most readers.

All possible arrangements of tiles on the board form two disjoint sets, where each member of a set can be reached by some finite sequence of moves from any other member of the same set, and there are no possible sequences of moves that can reach an arrangement in the other set. Any magic square in the expanded list will be reachable from one of two sorted goal states (and vice versa). Members of these sets can be identified by sums of permutation inversions, discussed [here](https://mathworld.wolfram.com/15Puzzle.html), allowing us to quickly determine which of the goal states can reach a given magic square arrangement.

Finding the shortest sequence of moves between any two mutually reachable states of the *p* x *q* board is an NP-hard problem, but approaches exist that can generally find optimal sequences for the 4 x 4 board in reasonable time.

### Graph traversal and heuristics

With a list of all possible 4 x 4 magic square arrangements, finding a challenge answer is as straightforward as examining each one and finding optimal sequences of moves between it and the sorted board states in the 15 Puzzle. This can continue until we find a magic square that can reach a sorted state in 50 moves or fewer. As with similar problems we can treat the space of possible moves as a finite graph, where each node represents a distinct board state and each edge represents a move on the board. We wish to find a path between each magic square and a sorted board state that traverses the fewest edges.

[Michael Kim](https://michael.kim/blog/puzzle) provides a good overview of approaches to solving the 15 Puzzle. It's worth noting that the worst cases for the puzzle, where the optimal solution to reach the sorted state can reach as many as 80 moves, may make an approach like an [A* search](https://en.wikipedia.org/wiki/A*_search_algorithm) prohibitively expensive in terms of memory. We're trying to find magic squares with solutions of 50 moves or fewer so this is less of a concern; an A* search can be set to terminate early if it exceeds a particular bound. Nevertheless I've used the recommended [Iterative Deepening A* search](https://en.wikipedia.org/wiki/Iterative_deepening_A*) (IDA*) instead, which requires minimal memory with the tradeoff that some nodes will be visited multiple times.

Like A*, IDA* uses a heuristic to prioritize exploring parts of the graph most likely to yield an optimal solution. I've elected to use the Walking Distance heuristic developed by [Ken'ichiro Takahashi](https://computerpuzzle.net/) and visually explained [here](https://computerpuzzle.net/english/15puzzle/wd.gif). The Walking Distance heuristic is *admissable*: It may not perfectly estimate the length of a sequence of moves between states but it can never *overestimate* the length, meaning that non-optimal branches in the traversal can be correctly skipped. It also has the benefit that there are relatively few distinct Walking Distance states that a given 4 x 4 board state can map to (only 24,964) which means they can be pre-computed into a lookup table for fast evaluation during traversal of the graph.

Since there are a large number of candidate magic square arrangements to evaluate, determining the correct starting board to use and then running IDA* limited to explore no more than 50 moves deep for each magic square is able to effectively run through the list with reasonable performance. There are a number of magic square arrangements that will satisfy the bonus challenge requirements, and this approach will eventually find one. Performance can be improved by limiting the search depth to 40 moves or fewer. There are no solutions with fewer than 35 moves.

Finally, it's worth pointing out that Herbert Kociemba gives the magic square that is reachable in the shortest number of moves from the normal sorted starting 15 Puzzle board at the bottom of the page [here](http://kociemba.org/themen/fifteen/fifteensolver.html).


[^1]: Frénicle de Bessy, *Des Quarrez ou Tables Magiques*, including: *Table generale des quarrez de quatre*. Mem. de l’Acad. Roy. des Sc. 5 (1666-1699) (1729) 209-354.