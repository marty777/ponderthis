# October 2023 Ponder This Challenge
The [October challenge](https://research.ibm.com/haifa/ponderthis/challenges/October2023.html) asks about palindromic squares with non-palindromic roots.

## Challenges

The main challenge asks for an integer *n* such that *n*<sup>2</sup> is a palindrome (in base 10), *n* is not a palindrome, and *n* ≡ 845 (mod 1201).

The bonus challenge asks for an integer *n* satisfying the main challenge conditions and also where *n* ≡ 2256 (mod 3565).

## Solution

The solution, which is more of a tool for finding asymmetric roots of palindromic squares with specific modular congruences, is implemented in Go.

Usage:

	$ go run oct2023 [OPTIONS]
	
	or 
	
	$ go build
	$ ./oct2023 [OPTIONS]
	
	Options:
		-d		The number of digits used to generate asymmetric roots (default 11)
		-m		The modulus to test for congruence in asymmetric roots. (default 1201)
		-r		The remainder to test for congruence in asymmetric roots. (default 845)
		-t		The number of worker threads used in generating asymmetric roots. (default 4)
		
Examples:
	
Find a solution to the main challenge with an asymmetric root 45 digits long:
	
	./oct2023 -r 845 -m 1201 -d 45

Find a solution to the bonus challenge (also satisfying the main challenge) with an asymmetric root 953 digits long. Note that the specified remainder and modulus are derived from the main and bonus congruence constraints via the Chinese Remainder Theorem:
	
	./oct2023 -r 1599376 -m 4281565 -d 953
	
The 45 and 953 digit parameters given for the main and bonus challenges were arrived at by experimentation. I believe those are the minimum lengths of asymmetric roots that satisfy the challenge conditions, but they are not the only lengths with solutions.
	
## Discussion

The topic of palindromic squares has received some study (usefully collected at [World!Of Numbers](https://www.worldofnumbers.com/square.htm)), and efforts at finding new ones are ongoing. 

Palindromic squares have been categorized into several distinct families[^1]:

1. The Binary Root family, where the root *n* consists of only the digits 0 and 1 and is a palindrome. An example is 1001001, which has the square 1002003002001.
2. The Ternary Root family, where the root *n* consists of only the digits 0, 1 and 2, is odd, and is a palindrome. An example is 10201, which has the square 104060401.
3. The Even Root family, where the root *n* consists of only the digits 0, 1 and 2, is even, and is a palindrome. Examples are 20102 or 2002, with the squares 404090404 and 4008004.
4. The Asymmetric Root family, where the root *n* consists of the the digits 0, 1 and 9 and is not a palindrome. An example is 10109901101, which has the square 102210100272001012201.

In addition the regular families, there are a number of Sporadic palindromic squares with roots that do not match a particular pattern. As we are looking for roots of palindromic squares which are not palindromes, the challenge answers must be either from the asymmetric root family or the sporadics. The full list of currently known sporadics can be found [here](https://www.worldofnumbers.com/Plain%20Text%20SSP.txt) and none satisfy the challenge congruences, so any challenge solutions must be found in the the asymmetric root family.

### Asymmetric Root Generating Function

The roots of all palindromic squares in the asymmetric root family have digits of a specific form, although not all integers with this form have palindromic squares:

	1 [x0] [B] 0 [y9] 9 [y0] 1 [B'] [x0] 1

	where:
	[x0] is a sequence of 0s of length x
	[y0] and [y9] are sequences of 1s and 9s of length y
	[B] is a sequence of digits of some length with either one or two 1 digits and all other digits 0 
	[B'] is the sequence [B] reversed
	
Most roots of this form that produce palindromic squares have x = y, but not all. All asymmetric roots with palindromic squares for a given number of digits can be produced by examining all variations of lengths of [B] combined with all possible arrangements of digits within [B] combined with all variations of lengths x and y such that the total number of digits reaches the desired count, although this process may yield some duplicate integers. Observed by experimentation, we can yield all distinct asymmetric roots with palindromic squares for a given number of digits in the root by varying the length and digits of [B] and only examining lengths of x and y where x = y or y = 0, which reduces the search space substantially.

### Main challenge

Armed with a generating function for asymmetric roots, it's straightforward to generate all possible roots in the asymmetric root family with a given number of digits and test each for congruence with the challenge conditions and a palindromic square. The number of digits provided to the generating function can be incremented (skipping even number of digits) until a solution is found.

The smallest satisfying root found for the main challenge was 45 digits long.

### Bonus challenge

By the Chinese Remainder Theorem, an integer that is congruent to both 845 (mod 1201) and 2256 (mod 3565) will be congruent to 1599376 (mod 4281565), simplifying the test for a satisfying asymmetric root somewhat. When generating asymmetric roots with hundreds of digits, the growth in possible digit configurations to construct and test for congruence starts to significantly increase the execution time for examining a particular number of digits. Parallelizing this process can improve performance, and by continuing to increment the number of digits of the generated asymmetric roots a solution can eventually be reached.

The first satisfying root found for the bonus challenge was 953 digits long.

[^1]: Michael Keith: *Classification and enumeration of palindromic squares*, J. Rec. Math., **22** (1990), no. 2, 124-132.
