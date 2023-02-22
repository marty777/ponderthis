# January 2023 Ponder This Challenge
The [January challenge](https://research.ibm.com/haifa/ponderthis/challenges/January2023.html) deals with strings of 
characters ("genes") that can be transformed according to specific rules. 

## Challenges

The main challenge asks for a 20-character starting string composed only of 'A' or 'C' characters that can be 
transformed, with a minimum number of steps between 880,000 and 890,000, into an all-'G' state, along with the 
number of steps required.

The bonus challenge asks for the minimum number of steps required to reach an all-'G' state from a 100-character 
starting string of all-'T's.

## Solution
The solution is implemented in Python 3.

Usage:

		$ python jan2023.py

The script will output one possible solution for the main challenge (if successsful), plus the number of steps for the 
bonus challenge. 

## Discussion 

For an initial approach to a solution, I tried a very simple breadth first search which attempted all possible 
transformations of the string at each step, returning a result when the first all-'G' state was reached. While this 
made it straightforward to implement the various rules that can transform the string, the search space increases 
dramatically with each step. On a desktop PC, the naive BFS approach became unworkable on strings longer than about 10
characters, both in terms of required execution time and in memory demands. It did, however, allow me to validate my 
results against the sample all-'G' transformation steps provided in the challenge specification.

Plainly the BFS approach would not be directly useful for a 20-character string, let alone a 100-character string. 
Sitting down and manually working through transformations of short strings, it became increasingly obvious that the minimum 
number of steps to reach an all-'G' state could be determined recursively.

Reproducing the transformation rules for reference:

*In one step, the leftmost letter in the gene can be changed to any character in the set {‘G’, ‘A’, ‘C’, ‘T’}. Changing the remaining letters is subject to additional constraints:*

1. *‘T’ can be changed to ‘C’ if all the letters to its left are ‘C’.*
2. *‘T’ can be changed to ‘G’ if the letter to its immediate left is ‘C’, and the remaining letters to its left are ‘A’.*
3. *‘C’ can be changed to ‘T’ if all the letters to its left are ‘T’.*
4. *‘C’ can be changed to ‘A’ if the letter to its immediate left is ‘C’, and the remaining letters to its left are ‘A’.*
5. *‘A’ can be changed to ‘C’ if the letter to its immediate left is ‘C’, and the remaining letters to its left are ‘A’.*
6. *‘G’ can be changed to ‘T’ if all the letters to its left are ‘T’.*

The rules suggest that for any desired transformation of any string to any other string, the priority should be to 
transform the rightmost characters into the desired state, with sub-transformations on characters to the left to 
reach a state to permit this. Once the rightmost character has been set to the desired state, it no longer needs 
to be considered  and operations can repeated for the next-rightmost character, until the entire desired string is 
reached. This gives excellent properties for a recursive approach:

* The size of the string to be considered decreases in length the further down the recursive chain we move. This remains true for any sub-transformations as well.
* The recusion will always arrive at trivial cases, since the leftmost character in the string can always be transformed into any other character.

A recursive solver seemed like an approach that was more likely to handle 20-character strings successfully.

The difficulty is that handling the transformation rules recursively is more conceptually complicated than the BFS 
approach. For this reason, the BFS solver was enormously useful for debugging the recursive solver and it's been 
retained in the python script in the BFSGeneSolver class. Once the recursive approach was working together with 
dynamic programming to keep a record of the minimum steps for previously-determined substring transformations, 
determining the steps to reach an all-'G' state was suprisingly fast in lengthy strings.

Determining the number of steps to reach an all-'G' state is only part of the problem. To find a 20-character starting 
state that takes between 880,000 and 890,000 steps to reach an all-'G' state, I implemented a simple genetic algorithm
that operated on randomized starting populations of strings. This was probably unnecessary, as in testing I generally 
needed to test fewer than 100 randomized starting strings to find one that matched the requirements, but it was fun to 
do and converges on a solution well. It should be noted that the genetic algorithm is not guaranteed to yield 
a solution, although in practice it does so reliably. The script may be re-run if a solution is not found.

Thanks the the recursive solver, determining the number of steps for a 100-character all-'T' state was unexpectedly
trivial.






