# July 2023 Ponder This Challenge
The [July challenge](https://research.ibm.com/haifa/ponderthis/challenges/July2023.html) asks for solutions to a game played with shaped pieces on a 2D board, where a goal state is reached from a starting state by sliding pieces up, down, left or right with each move having a cost determined by the size of the piece.

## Challenges

The main challenge asks for a solution with a total cost no greater than 100 that reaches a provided goal state from the starting state of the board.

The bonus challenge asks for a solution with a total cost no greater than 150 that reaches a second provided goal state from the starting state of the board.

## Solution
The solution is implemented in Go.

Usage:
	
	$ go run jul2023 [OPTIONS]
	
	or
	
	$ go build
	$ ./jul2023 [OPTIONS]
	
	Options:
		-b			Find a solution to the bonus challenge
		-v			Print the status of each queue step and a trace of each move in a solution when found
		-h			Print usage

Examples:

Solve the main challenge:

		$  ./jul2023

Solve the bonus challenge:

		$ ./jul2023 -b

## Discussion

The representation and movement of pieces on the board was quite fun to implement on this one.

With some similarities to my approach for the [previous month's challenge](../06/), the space of all states of the board can be considered as a weighted graph; each node represents a distinct arrangement of pieces on the board (making sure to follow the rule that pieces of the same shape are treated as equivalent) and each edge represents a move of one step for a particular piece and direction with a weight equal to the piece's cost. Since we are given start and goal arrangements for the board and seek to find a path through the graph between these states that minimizes the sum of the weights of the traversed edges, this is the perfect application for [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) which successfully finds solutions to both challenges.