# February 2023 Ponder This Challenge
The [February challenge](https://research.ibm.com/haifa/ponderthis/challenges/February2023.html) involves a variation
on the [*n*-queens problem](https://en.wikipedia.org/wiki/Eight_queens_puzzle), where kings are arranged on a solved
*n*-queen board such that they can only occupy 'safe' positions (i.e. positions threatened by exactly two queens) and no 
kings threaten each other.

## Challenges

The main challenge asks for an *n* = 20 queen solution where the total number of ways that *n* kings can be arranged on 
the board in safe positions is 48.

The bonus challenge asks for an *n* >= 26 queen solution where there are zero ways to arrange *n* kings in safe 
positions.

## Solution
The solution is implemented in Python 3.

Usage:

		$  python feb2023.py [-h] [-b] [-m MAXATTEMPTS] outputdir
		
		positional arguments:
		  outputdir             The directory to store successful solutions

		optional arguments:
		  -h, --help            show this help message and exit
		  -b, --bonus           Attempt to solve the bonus problem for 26 queens
		  -m MAXATTEMPTS        Maximum number of solutions to attempt

Example:

		$  mkdir solutions
		$  python feb2023.py -m 1000 solutions/

In either normal or bonus mode, the script will repeatedly generate *n*-queen solutions and test if they match the 
challenge conditions. Any matching solutions will be saved to a text file in the specified output directory. The 
likelihood of a given *n*-queen solution matching the challenge conditions is low so this process may need to run 
for a large number of attempts before a result is found, especially for the bonus challenge.

## Discussion  

### Generating Queen Solutions

I have no prior familiarity with the *n*-queens problem, but a quick review of approaches suggested that an 'iterative 
repair' algorithm would be suitable, as it can handle large *n* values more easily than exhaustive searches of the 
permutation space. The downside is that there's no guarantee of reaching a solution, but the cost of restarting the 
process is low.

Briefly, the algorithm is as follows:

1. Place one queen per column, in a randomly selected row.
2. Until a solution is reached or the available moves that result in previously-unseen queen arrangements are 
exhausted:
	1. Count the threats against each queen. If no queens are under threat, a solution has been reached.
	2. For each queen that has more than zero threats from other queens, examine all possible moves to other positions 
	in the same column. If a move would reduce the number of threats to the queen add it to a list of candidate moves.
	3. Order the list of candidate moves by *reduction in threats* (i.e. the number of threats against the current 
	queen position minus the number of threats if the queen were to be moved)
	4. For each move on the ordered candidate move list check if it results in a board position that has been 
	previously seen. If not, perform the move and return to the top of the loop.
	5. If no candidate moves are available that produce a previously unseen board position, this attempt at an 
	*n*-queen solution has failed and can be restarted with a new random initial queen arrangement.

The iterative repair approach can presumably use other heuristics for improving the queen arrangement, but the one I've
used is effective.

### Total King Arrangements

Once *n*-queen solutions can be produced, the arrangement of kings needs to be considered. Determining the safe 
positions in an *n*-queen arrangement is straightforward, and it seemed that it might be potentially feasible to 
examine all possible king arrangements in safe positions using a breadth first search and count the subset that 
included *n* kings.

At *n* = 20, there are generally between 30 and 50 positions that are safe in an *n*-queen solution, which puts an 
upper bound of king arrangements to consider into the territory of very large numbers. Even with some strategies for 
aggressively pruning king arrangements that would result in mutual threats, the BFS approach tended to run out of 
memory on a desktop PC before fully exploring all possible arrangements.

After some thought and manual inspection of safe positions in sample *n*-queen solutions, it became evident (and hinted 
at in the challenge specification) that these positions do not all directly interact, and can instead be sorted into 
spatially isolated groups or single positions that can be considered independently.

For example, take this 10-queen solution:

	 . . . . . . . . Q .
	 . Q . . . . . . . .
	 . . . Q . . . . . .
	 Q . . . . . . . . .
	 . . . . . . Q . . .
	 . . . . . . . . . Q
	 . . . . . Q . . . .
	 . . Q . . . . . . .
	 . . . . Q . . . . .
	 . . . . . . . Q . .

with the resulting safe positions:

	 . . . . . . S S . .
	 . . . . . . S . . .
	 . . . . . S . . . .
	 . . . . . . . . . .
	 . . . . . . . . . S
	 . . . . . . . . S .
	 S . . . . . . . . S
	 S . . . . . . . . .
	 . . . . . . . . . .
	 . . . . . . . . . .

Some of these positions are within king-threatening distance and must be considered together when placing kings,
but others are not. They can be sorted into groups labeled A, B and C as follows:

	 . . . . . . B B . .
	 . . . . . . B . . .
	 . . . . . B . . . .
	 . . . . . . . . . .
	 . . . . . . . . . C
	 . . . . . . . . C .
	 A . . . . . . . . C
	 A . . . . . . . . .
	 . . . . . . . . . .
	 . . . . . . . . . .
	
Considering each group independently, we can see that there are a limited number of ways to arrange a given number of kings in each 
group such that kings do not threaten each other:

Group A:

| # kings 	| possible ways 	|
|---------	|---------------	|
| 0       	| 1             	|
| 1       	| 2             	|
| 2       	| 0             	|
| etc.    	| 0             	|

Group B:


| # kings 	| possible ways 	|
|---------	|---------------	|
| 0       	| 1             	|
| 1       	| 4             	|
| 2       	| 2             	|
| 3       	| 0             	|
| 4       	| 0             	|
| etc.    	| 0             	|

Group C:  

| # kings 	| possible ways 	|
|---------	|---------------	|
| 0       	| 1             	|
| 1       	| 3             	|
| 2       	| 1             	|
| 3       	| 0             	|
| etc.    	| 0             	|

Because these groups do not interact with each other when placing kings, we don't need to consider each possible 
position of a king when enumerating all possible king arrangements, and only need to know the number of possible 
arrangements across all groups such that the total is equal to our intended number of kings.

Suppose we wanted to place **4** kings across groups A, B and C. The total number of ways to arrange this are:

| Group 	| # kings 	| possible ways 	|
|-------	|---------	|---------------	|
| A     	| 1       	| 2             	|
| B     	| 1       	| 4             	|
| C     	| 2       	| 1             	|
| **Total** | **4**     | 2 x 4 x 1 = **8** |

plus

| Group 	| # kings 	| possible ways 	|
|-------	|---------	|---------------	|
| A     	| 1       	| 2            		|
| B     	| 2       	| 2             	|
| C     	| 1       	| 3             	|
| **Total** | **4**     | 2 x 2 x 3 = **12**|

plus

| Group 	| # kings 	| possible ways 	|
|-------	|---------	|---------------	|
| A     	| 0       	| 1            		|
| B     	| 2       	| 2             	|
| C     	| 2       	| 1             	|
| **Total** | **4**     | 1 x 2 x 1 = **2** |

There are no other ways to distribute 4 kings across groups A, B and C, so there are a total of 8 + 12 + 2 = **22** distinct ways to arrange 4 kings across all safe positions.

The BFS approach to king arrangements was useful here, because the groups are small enough that enumerating all 
possible ways to arrange kings within them is feasible. This was used to build a lookup of number-of-kings to 
number-of-arrangements within each group.

Once the lookup was generated for each group of safe positions, determining the total number of arrangements for *n* 
kings across all groups was a matter of enumerating all the ways that *n* kings could be split up across the groups. 
Using a recursive depth first search across all possible permutations of kings-per-group that matched the total kings 
of 20, with an early exit if the number of arrangements found exceeded the desired total of 48 possible arrangements, 
was able to test for solutions to the main challenge problem with reasonable performance.

Although generating 26-queen solutions for the bonus challenge is slower than 20-queen solutions, evaluating each 
solution for zero possible 26-king arrangements is simpler. After building the lookup for numbers of kings possible 
within each group of safe positions, we can simple check the sum of the largest number of kings it is possible to place 
within each group (in the example above, the largest number of kings that can be placed are 1 from Group A, 2 from 
Group B and 2 from Group C for a maximum of 5 kings). If this sum is less than 26, it is impossible to arrange 26 kings 
across all safe positions on the board.