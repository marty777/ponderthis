# April 2023 Ponder This Challenge
The [April challenge](https://research.ibm.com/haifa/ponderthis/challenges/April2023.html) asks for solutions to a game played on a square grid of lightbulbs, where at each step an unlit bulb can be lit, and all bulbs in the same row and column will be toggled between lit and unlit. The goal is to reach a state where all bulbs on the grid are lit.

## Challenges

The main challenge asks for a solution to a provided 24 x 24 grid of bulbs.

The bonus challenge asks for a solution with fewer than 430 steps to a provided 30 x 30 grid of bulbs.

## Solution
The solution is implemented in Python 3.

Usage:

		$  python apr2023.py [-h] [-m MAXATTEMPTS] [-t] inputfile
		
		positional arguments:
		  inputfile             An input text file containing a bulb grid

		optional arguments:
		  -h, --help            show this help message and exit
		  -m MAXATTEMPTS, --maxattempts MAXATTEMPTS
								Maximum number of trial solutions to attempt
		  -t, --trace           Print a step-by-step trace of a successful solution
								when found

Example:

		$  python apr2023.py sample.txt

The sample lightbulb grid text file (sample.txt) should demonstrate the required format. Bulb grids from the challenge specification can be copied and pasted into a new text file and run as the input to the solution script. The script will determine the specific bulbs that must be selected to reach the goal state for the provided bulb grid, and then attempt randomized trial solutions with that set of bulbs until an ordering that can be completed is found or the maximum number of attempts is exceeded. 

## Discussion

I really enjoyed this one.

If we ignore the requirement that a bulb must be unlit before it can be selected, it's straightforward to see that selecting a bulb is effectively an exclusive or (XOR) transformation applied to the bulb grid, with each bulb selection having a particular mask for its row and column. Importantly, XOR transformations are *commutative*. Given a set of specific bulbs to select, the resulting state of the lightbulb grid will be identical no matter what order the bulbs are selected in. An XOR transformation is also its own *inverse*. If the same bulb is selected twice, its changes to the grid would be canceled out. These properties allow us to determine exactly which bulbs need to be selected to yield a fully lit grid.

To demonstrate the approach, let's take the example grid provided with the challenge:

	0 0 1 1
	1 1 0 1
	0 1 1 0
	0 0 0 1

The selection of the bulb at position (1,1) is an XOR transformation on the bulb grid with the mask:

	1 0 0 0
	1 0 0 0
	1 0 0 0
	1 1 1 1

The selection of the bulb at position (2,1) is an XOR transformation on the bulb grid with the mask:
	
	0 1 0 0
	0 1 0 0
	0 1 0 0
	1 1 1 1

and so on...

We can represent these as masks as linear vectors. Using the raster order of bulbs given in the challenge, the above transformations would have the vectors:

	[1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
and

	[1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
	
The vectors for each bulb selection taken together form a 16 x 16 matrix of XOR transformations:

	[[1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0], 
	 [1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0], 
	 [1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0], 
	 [1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1], 
	 [1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0], 
	 [0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0], 
	 [0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0], 
	 [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1], 
	 [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0], 
	 [0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0], 
	 [0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0], 
	 [0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1], 
	 [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1], 
	 [0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1], 
	 [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1], 
	 [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1]]

This matrix and the equivalent transformation matrices for 24 x 24 and 30 x 30 lightbulb grids have the interesting property that each matrix is its own inverse in the field of integers modulo two (GF(2)). This appears to be true of the transformation matrix for any *n* x *n* grid of lightbulbs where *n* is even, although I haven't verified this.

To transform the example grid into a fully lit state, the sequence of transformations must result in a net change to the state of every initially unlit bulb and no net change to the state of every initially lit bulb. The XOR mask for this net transformation of the example grid, which is just the initial state of the grid with the values inverted, looks like:

	1 1 0 0
	0 0 1 0
	1 0 0 1
	1 1 1 0

And converted to a vector, this would be:

	[1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0]

Due to the commutative and inverse properties of the XOR transformations, we can express a set of lightbulb selections as a vector **v**<sub>bulbs</sub>, where each entry specifies a coefficient for each possible transformation. *1* would represent an odd number of times the transformation is applied, and *0* would represent an even number of times the transformation is applied. Multiplying this vector in GF(2) by the transformation matrix **M** would give a vector **v**<sub>result</sub> representing the net transformation applied to the lightbulb grid after every transformation was made. 

**v**<sub>result</sub> = **M** **v**<sub>bulbs</sub>

Knowing **v**<sub>result</sub>, the desired net transformations to the lightbulb grid, and knowing that the transformation matrix **M** is its own inverse, we can obtain **v**<sub>bulbs</sub> easily:

**v**<sub>bulbs</sub> = **M**<sup>-1</sup> **v**<sub>result</sub> = **M** **v**<sub>result</sub>

For the example grid, this yields the following **v**<sub>bulbs</sub>

	[1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1]

Converted back to a grid:

	0 1 0 1 
	0 1 0 0 
	0 0 0 0 
	1 0 0 0

This means that the bulbs at positions (1,1), (2,3), (2,4) and (4,4) must all be selected an odd number of times, and every other bulb must be selected an even number of times, in order to fully light the grid. Ideally there is a possible sequence of selections where (1,1), (2,3), (2,4) and (4,4) can each be selected exactly one time, and all other bulbs are selected zero times (and indeed there are several).
	
The order in which lightbulbs are selected doesn't matter for the transformations, but it does matter for the game due to the rule that only unlit bulbs can be selected. Making the assumption that that there's a permissible sequence of steps where each bulb with a nonzero coefficient can be selected exactly once and no bulbs with zero coefficients are ever selected, we can attempt trial solutions where at each step a bulb with a nonzero coefficient that is currently unlit is selected at random. For the challenge lightbulb grids, this will eventually find a successful solution that fully lights the grid in the minimum number of steps possible.