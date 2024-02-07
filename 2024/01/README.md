# January 2024 Ponder This Challenge
The [January challenge](https://research.ibm.com/haifa/ponderthis/challenges/January2024.html) asks about a elementary school student's arithmetical riddle, where the integers 1-16 are assigned without repetition to positions in a board so that 4 horizontal and 4 vertical equations are satisified.

## Challenges

The main challenge asks for a solution that satisfies the board, along with the total number of possible solutions

The bonus challenge asks for two solutions that satisfy the board where the integers assigned by each solution differ from the other in all board positions, and such that at least half of the +/- operators in the board can be changed while having both solutions produce the same horizontal and vertical sums. Note that the sums after the +/- operators are changed can differ from the original sums on the board.

## Solution

The solution is implemented in Go.

Usage:

	$ go run jan2024 [OPTIONS]

	or 

	$ go build
	$ ./jan2024 [OPTIONS]

	Options:
		-t	int	
        	The number of worker threads used to find solutions (default 4)

The program will determine all solutions to the board, output a randomly selected one along with the total number of solutions, and then compare solutions until it outputs a pair that satisfy the bonus challenge along with the list of alternate +/- operators.

## Discussion

The total number of possible arrangements of the integers 1-16 without repetition in the board is 16! (20,922,789,888,000). It would be impractical to exhaustively test the entire set for solutions to the riddle.

The puzzle has 16 variables and 8 equations. If it were possible to vary only 8 board positions and uniquely solve the system of linear equations for the remaining positions, that would reduce the search space to a more manageable 16!/(16-8)! (518,918,400) possibilities.

This was the approach I explored, but I wasn't able to find a way to produce unique solutions to the system of equations while varying fewer than 9 board positions. This reduces the search space to 16!/(16-9)! (4,151,347,200) possibilities, which is substantial but feasible to exhaustively check. The testing of each assignment of variables within this space can performed in parallel to obtain all possible solutions to the riddle relatively quickly.

Once the list of all possible solutions is known, comparing pairs of solutions until two are found that satisfy the bonus challenge conditions is straightforward. Trials of each possible reassignment of +/- signs where half or more are flipped can be attempted and the resulting sums of each horizontal and vertical equation can be compared between the two solutions. If the sums match between the two solutions, the bonus challenge is solved. Testing pairs of solutions and +/- sign assignments can likewise be performed in parallel for faster execution.

