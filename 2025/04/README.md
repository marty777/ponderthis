# April 2025 Ponder This Challenge
The [April challenge](https://research.ibm.com/haifa/ponderthis/challenges/April2025.html) asks about the movements of a giant cube.

## Challenges

In a game of *Klumpengeist*, the eponymous giant cube starts at the top-left corner of a square board with one *growth point*. The Klumpengeist can move up, left, down or right between positions on the board, devouring any items it reaches that it is large enough to consume. At the start of the game each position on the board is either empty or contains an item with a given size. The cube may only move to a position that is empty or where its current size (the integer component of the square root of the cube's growth points) is greater than or equal to the size of the item at that position. Moving to a position occupied by an item consumes the item, adding its size to the growth points of the cube and making the position empty.

The main challenge gives a 20 x 20 board and asks for a path where the Klumpengeist consumes all items in 500 steps or fewer.

The bonus challenge gives a 30 x 30 board and asks for a path where the Klumpengeist reaches a size of 30 in 150 steps or fewer.

## Solution

The solution is implemented in Python.

Usage:
```
apr2025 [-h] [-b] [-v]

optional arguments:
  -h, --help     show this help message and exit
  -b, --bonus    solve the bonus challenge
  -v, --verbose  print each solution step
```
Examples:

Solve the main challenge:

```console
$ python apr2025.py 
```

Solve the bonus challenge and print each step of the solution:

```console
$ python apr2025.py --verbose --bonus 
```

The script uses semi-random trials to find solutions and is likely but not guaranteed to succeed within a maximum number of attempts. In the event of failure, the script can be re-run.

## Discussion

Although this appears to be a graph traversal problem where a search algorithm could be applicable, optimal solutions are not required. In a method more suited to a ravenous Klumpengeist, a simple heuristic can find solutions to both challenges:

 - Locate all edible items that can be reached from the current position without passing through any non-empty positions.
 - Randomly select one of the items that can be reached in the fewest steps.
 - Move to the item's position and consume it.
 - Repeat until a successful solution is reached or the maximum number of steps for the challenge is exceeded.

A single run using this approach is not guaranteed to find a valid path, but repeated trials will be quickly successful. Other heuristics may be able to reach solutions as well.