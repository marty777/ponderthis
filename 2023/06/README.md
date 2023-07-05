# June 2023 Ponder This Challenge
The [June challenge](https://research.ibm.com/haifa/ponderthis/challenges/June2023.html) asks for the maximum amount of cheese that can be collected by a mouse in a three dimensional maze where the cheese in each cell phases in and out of existence according to a defined function as time advances.

## Challenges

The main challenge asks for the maximum amount of cheese that can be obtained in a 30x30x30 maze in 100 time steps, where at each step the mouse can only wait or move in positive directions along each axis.

The bonus challenge asks for the maximum amount of cheese that can be obtained in a 50x50x50 maze in 200 time steps, where at each step the mouse can wait or move in both positive and negative directions along each axis, and where cheese can be collected in the mouse-occupied cell at any step when it is in phase, even if it was previously obtained.

## Solution

The solution is implemented in Rust.

Usage:

		Usage: jun2023 [OPTIONS]
		or
		cargo run -- [OPTIONS]
	
		Options:
		  -k <k>       Set the dimensions of the maze [default: 30]
		  -n <n>       Set the number of time steps to traverse the maze [default: 100]
		  -b, --bonus  Traverse the maze using the bonus challenge rules
		  -h, --help   Print help



Examples:

Solve the main challenge:

		$  jun2023 -k 30 -n 100
        
Solve the bonus challenge:

		$  jun2023 -k 50 -n 200 --bonus
		
## Discussion

Performing an exhaustive search of all possible paths a mouse can take in either of the challenges is infeasible due to the size of the search space. The rules of the main and bonus challenges fortunately permit a more focused search that can correctly determine the maximum possible amount of cheese obtainable in the maze.

### Approach

Considering the maze and the state of cheese in each cell across all time steps, we can think of any particular path through the bonus or challenge mazes as the traversal of a directed finite graph, where each node represents a coordinate in (*x*,*y*,*z*,*t*) for the spatial axes *x*, *y* and *z* and the time axis *t*.  The particular configuration of the directed edges changes depending on the maze rules; a path can't move in negative *x*, *y* and *z* in the main challenge, but can in the bonus challenge, and in both challenges there are no edges that permit movement to a node where *t* does not increment by 1. The graph has a starting node at (1,1,1,1) and a "goal" state of reaching a node where *t* = *n*. Due to the variation of cheese availability at each maze cell over time, the graph is also weighted graph, where the presence of cheese in the maze cell at the corresponding position and time in a destination node gives the connecting edge a weight of one cheese and otherwise a weight of zero cheese. 

If we have a directed, weighted graph and we wish to find a path from one node to a set of other nodes while maximizing the sum of weights of the traversed edges, this is very close to the general usage of [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm). Dijkstra's algorithm normally seeks to find a traversal that minimizes the sum of the weights of a path through the graph, but it is readily adapted to solving both challenges with an important caveat. In order for the application of the algorithm to be valid, the edge weights of the graph must be fixed. If the particular traversal of a path through the maze could cause a change in the weights, for example by the mouse collecting cheese from one cell causing any edges that return to the same spatial position in future time steps to go to zero, the approach may not be able to find a traversal that obtains the greatest possible amount of cheese. Both challenges have subtly structured their rules to avoid this issue in different ways.

### Main challenge

In the main challenge, the specific path taken to reach a particular cell cannot effect how much cheese can be reached in future steps from that cell because the mouse is only able to move in positive directions. Any cells that are up, right or forward from the mouse's present position cannot have been emptied of cheese previously, and cells that are down, left or backward cannot be returned to for missed cheese. Entering a cell when it contains cheese and waiting for one or more steps is accommodated for by implicitly setting the edge nodes for such wait steps to zero cheese. We are thus able to ignore any changes to edge weights that the framing of the challenge otherwise implies, and Dijkstra's algorithm is effective in finding a path that collects the greatest possible amount of cheese.

### Bonus challenge

In the bonus challenge, the mouse is capable of moving in both positive and negative directions. However, the rule that cheese can be taken from a cell any time it is in phase rather than only once means that the path taken and cheese collected to reach a particular cell has no effect on the amount of cheese that can be obtained in future moves from that cell. The edge weights of the graph are explicitly unchangeable by this rule and so Dijkstra's algorithm is also effective in solving the bonus challenge.
