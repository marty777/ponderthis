# March 2023 Ponder This Challenge
The [March challenge](https://research.ibm.com/haifa/ponderthis/challenges/March2023.html) requires a search for 
*n-exception chained primes*, where the decimal expression of an integer is prime (or non-prime, adding an exception) for each digit 
appended on either the left or right.

## Challenges

The main challenge asks for the largest number which is a 5-exception chained prime, where digits are appended on the right.

The bonus challenge asks for the largest number which is a 5-exception reverse chained prime, where digits are appended on the left.

## Solution

The solution is implemented in Rust.

Usage: 

		mar2023 [OPTIONS]
		or
		cargo run -- [OPTIONS]

	Options:
	  -r, --reverse
			  Explore reverse chained primes where digits are appended on the left.
	  -n, --numexceptions <EXCEPTIONS>
			  Maximum prime chain exceptions. [default: 5]
	  -t, --threads <THREADS>
			  Maximum number of worker threads to spawn at each step of chain
			  evaluation. [default: 4]
	  -f, --filter <TOP>
			  Retain only the digit chains with the TOP fewest exceptions at each 
			  step and discard all others.
	  -h, --help
			  Print help

Examples:

Completely explore all 5-exception chained primes and return the largest possible (the main challenge)

		mar2023 -n 5

Attempt to completely explore all 5-exception reverse chained primes and return the largest possible (the bonus challenge)

		mar2023 -n 5 --reverse

Use the filtering approach (see below) for 5-exception reverse chained primes, discarding any digit chains that are not within the top 2 fewest exception groups at each digit step, and return the largest found

		mar2023 -n 5 --reverse --filter 2

Completely explore all 3-exception reverse chained primes and return the largest possible

		mar2023 -n 3 --reverse 

## Discussion

The solution makes use of the OpenSSL library's BIGNUM implementation of large integers and primality testing. The primality testing uses multiple rounds of the Miller-Rabin test (the number of rounds depending on the size of the integer) and some trial division by small primes. Because Miller-Rabin is a probabilistic test there is a possibility of errors occurring in the large number of integers tested for primality in the course of reaching the challenge answer, although the probability of this is extremely low. See the [OpenSSL docs on the primality test](https://www.openssl.org/docs/man3.0/man3/BN_is_prime.html) for more information.

### Main challenge

With a reasonable amount of available memory and processor capacity, the main challenge is relatively straightforward. For a maximum of 5 exceptions, the entire space of possible prime chains can be explored with a breadth first search. Memory for storing the queue may be a limiting factor, as the solution will consume approximately 6.5 GB at the largest queue sizes, and may take several hours to reach an answer depending on the processing capacity available.

Starting from single digits, the BFS expands each digit chain in the queue by all possible digits at each step, discarding any that exceed 5 exceptions. At each step *k*, the starting queue contains all possible *k*-digit prime chains with no more than 5 exceptions. The branching factor at each step (10x) is eventually overcome by the sparsity of primes at higher orders of magnitude, and the surviving population dwindles to a handful and then 0. The largest integer in the queue at the penultimate step gives the challenge answer.

### Bonus challenge

While it's feasible to completely explore all possible 5-exception chained primes, 5-exception reverse chained primes present more of a difficulty. Due to some differences in behavior when digits are added in the most significant position vs. the least significant position, the population of digit chains to be considered at each digit step multiplies more quickly and sustains itself above replacement for more digits. With careful batching of small subsets it might be practical to exhaustively explore all possible 5-exception reverse prime chains but, as I estimated it could take several weeks of processing on my available hardware, an approach to reduce the number of digit chains to consider seemed to be worth pursuing.

#### Filtering out unlikely candidate chains 

Examining the more tractable 1, 2 and 3-exception reverse chained primes exhaustively, it becomes apparent that the predecessors to the eventual largest digit chain almost always have the fewest exceptions of possible digit chains with the same number of digits. They might occasionally reach 1 exception while there are still digit chains with 0 exceptions in the population, or 2 exceptions while there are still chains with 1 exception, but mostly they have the fewest possible exceptions at any digit step. This seems plausible enough, since the largest reverse prime chain will necessarily reach the greatest number of digits, and will likely be a digit chain that adds exceptions at as late a digit step as possible.

By retaining digit chains with the fewest several exceptions at each digit step and discarding all others, the eventual longest possible reverse prime chain can potentially be reached while substantially reducing the number of digit chains to consider.

To illustrate the approach, let's look at the 3-exception reverse chained primes:

| Digits            	| 0 exceptions 	| 1 exception 	| 2 exceptions 	| 3 exceptions 	|
|-------------------	|--------------	|--------------	|--------------	|--------------	|
| 1                 	| 4            	| 5            	| 0            	| 0            	|
| 2                 	| 11           	| 35           	| 35           	| 0            	|
| 3                 	| 39           	| 122          	| 280          	| 288          	|
| 4                 	| 99           	| 586          	| 1065         	| 2342         	|
| 5                 	| 192          	| 1903         	| 6306         	| 9233         	|
| 6                 	| 326          	| 4598         	| 24767        	| 61807        	|
| 7                 	| 429          	| 8952         	| 70461        	| 277792       	|
| 8                 	| 521          	| 14561        	| 156955       	| 896413       	|
| 9                 	| 545          	| 19893        	| 287601       	| 2235033      	|
| 10                	| 517          	| 23926        	| 442400       	| 4519285      	|
| 11                	| 448          	| 25369        	| 586315       	| 7637974      	|
| 12                	| 354          	| 24000        	| 682831       	| 11043089     	|
| 13                	| 276          	| 20634        	| 707433       	| 13924781     	|
| 14                	| 212          	| 16343        	| 659404       	| 15554902     	|
| 15                	| 117          	| 12253        	| 559450       	| 15566600     	|
| 16                	| 72           	| 8252         	| 437571       	| 14107552     	|
| 17                	| 42           	| 5237         	| 316787       	| 11694746     	|
| 18                	| 24           	| 3064         	| 212737       	| 8931004      	|
| 19                	| 13           	| 1773         	| 132977       	| 6320803      	|
| 20                	| 6            	| 965          	| 78824        	| 4164880      	|
| 21                	| 5            	| 483          	| 43817        	| 2571770      	|
| 22                	| 4            	| 230          	| 23209        	| 1493266      	|
| 23                	| 3            	| 148          	| 11665        	| 819556       	|
| 24                	| 1            	| 80           	| 5828         	| 426596       	|
| 25                	| 0            	| 29           	| 2960         	| 213082       	|
| 26                	| 0            	| 9            	| 1347         	| 103393       	|
| 27                	| 0            	| 3            	| 572          	| 47909        	|
| 28                	| 0            	| 2            	| 217          	| 21119        	|
| 29                	| 0            	| 2            	| 80           	| 8794         	|
| 30                	| 0            	| 1            	| 38           	| 3505         	|
| 31                	| 0            	| 0            	| 22           	| 1445         	|
| 32                	| 0            	| 0            	| 6            	| 609          	|
| 33                	| 0            	| 0            	| 2            	| 217          	|
| 34                	| 0            	| 0            	| 3            	| 78           	|
| 35                	| 0            	| 0            	| 1            	| 42           	|
| 36                	| 0            	| 0            	| 1            	| 18           	|
| 37                	| 0            	| 0            	| 1            	| 12           	|
| 38                	| 0            	| 0            	| 0            	| 12           	|
| 39                	| 0            	| 0            	| 0            	| 4            	|
| 40                	| 0            	| 0            	| 0            	| 1            	|
| 41                	| 0            	| 0            	| 0            	| 0            	|
| Sum	             	| 4260         	| 193458       	| 5453968      	| 122659952    	|
| Fraction of total 	| 3.32004E-05  	| 0.00150772   	| 0.042505638  	| 0.955953442  	|


Of note are digits **24**, **30**, and **37**, which are the last digits where chains with 0, 1 and 2 exceptions remain in the population respectively.

The largest possible 3-exception reverse prime chain, 1323136248319687995918918997653319693967, reaches its exceptions at digits **24**, **31** and **38**.

| Digits 	| Value                                    	| Exception                              	|
|--------	|------------------------------------------	|----------------------------------------	|
| 1      	| 7                                        	|                                        	|
| 2      	| 67                                       	|                                        	|
| 3      	| 967                                      	|                                        	|
| 4      	| 3967                                     	|                                        	|
| 5      	| 93967                                    	|                                        	|
| 6      	| 693967                                   	|                                        	|
| 7      	| 9693967                                  	|                                        	|
| 8      	| 19693967                                 	|                                        	|
| 9      	| 319693967                                	|                                        	|
| 10     	| 3319693967                               	|                                        	|
| 11     	| 53319693967                              	|                                        	|
| 12     	| 653319693967                             	|                                        	|
| 13     	| 7653319693967                            	|                                        	|
| 14     	| 97653319693967                           	|                                        	|
| 15     	| 997653319693967                          	|                                        	|
| 16     	| 8997653319693967                         	|                                        	|
| 17     	| 18997653319693967                        	|                                        	|
| 18     	| 918997653319693967                       	|                                        	|
| 19     	| 8918997653319693967                      	|                                        	|
| 20     	| 18918997653319693967                     	|                                        	|
| 21     	| 918918997653319693967                    	|                                        	|
| 22     	| 5918918997653319693967                   	|                                        	|
| 23     	| 95918918997653319693967                  	|                                        	|
| 24     	| 995918918997653319693967                 	| #1 (1 chain remains with 0 exceptions) 	|
| 25     	| 7995918918997653319693967                	|                                        	|
| 26     	| 87995918918997653319693967               	|                                        	|
| 27     	| 687995918918997653319693967              	|                                        	|
| 28     	| 9687995918918997653319693967             	|                                        	|
| 29     	| 19687995918918997653319693967            	|                                        	|
| 30     	| 319687995918918997653319693967           	|                                        	|
| 31     	| 8319687995918918997653319693967          	| #2 (0 chains remain with 1 exception)  	|
| 32     	| 48319687995918918997653319693967         	|                                        	|
| 33     	| 248319687995918918997653319693967        	|                                        	|
| 34     	| 6248319687995918918997653319693967       	|                                        	|
| 35     	| 36248319687995918918997653319693967      	|                                        	|
| 36     	| 136248319687995918918997653319693967     	|                                        	|
| 37     	| 3136248319687995918918997653319693967    	|                                        	|
| 38     	| 23136248319687995918918997653319693967   	| #3 (0 chains remain with 2 exceptions) 	|
| 39     	| 323136248319687995918918997653319693967  	|                                        	|
| 40     	| 1323136248319687995918918997653319693967 	|                                        	|

For the majority of digit steps, the predecessors to the largest possible digit chain were in the group of digit chains with the fewest exceptions in the entire population, only briefly dipping to the second fewest exceptions group at digit 24. Similar behavior is observed for the largest possible 1 and 2-exception reverse prime chains.

By retaining any reverse chained primes that are within 0 or 1 exceptions of the minimum number of exceptions at each digit step and discarding all others, the largest possible reverse chained prime can be found while avoiding consideration of the vast majority of possible digit chains. In the case of the 3-exception reverse chained primes, only 200,254 digit chains need to be considered out of 128,311,638 across all digit steps, or **0.156%** of the exhaustive search. In the provided solution, this can be performed as:

		mar2023 -n 3 --reverse --filter 2

The downside of this approach is that there isn't a rigorous guarantee that the largest possible *n*-exception reverse prime chain will always appear within a particular number of exceptions of the minimum possible at each digit step. It's not inconceivable that the largest possible digit chain for a given *n* might add a significant number of exceptions at relatively low digit steps, then avoid adding any others until many more digits are added before eventually reaching the largest possible number of digits. The filtering approach could fail in this case by removing this digit chain from consideration early on. 

It doesn't seem possible to be completely certain that the largest prime chain found using the filtering approach is the largest possible digit chain without an exhaustive exploration for comparison, but by progressively expanding the exception cutoff used in the filtering it's possible to be more confident. Expanding the cutoff parameter necessarily means that more digit chains need to be considered, eventually out of the area where fully exploring the filtered set is feasible. In the provided solution, one might run the following commands in sequence and examine the results (and note the increase in execution time and memory consumption):

		mar2023 -n 5 --reverse --filter 1
		mar2023 -n 5 --reverse --filter 2
		mar2023 -n 5 --reverse --filter 3
		mar2023 -n 5 --reverse --filter 4

The filtering approach can similarly be applied to regular *n*-exception chained primes. In the provided solution, one could reach the main challenge answer more quickly than the exhaustive approach with the command:

		mar2023 -n 5 --filter 2
