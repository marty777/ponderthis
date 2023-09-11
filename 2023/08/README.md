# August 2023 Ponder This Challenge
The [August challenge](https://research.ibm.com/haifa/ponderthis/challenges/August2023.html) asks about square-triangular numbers, numbers which are equal to *n*<sup>2</sup> for some integer *n* and also equal to the sum 1 + 2 + 3 + ... + *m* for some integer *m*.

## Challenges

The main challenge asks for the number of positive square-triangular numbers below 10<sup>100</sup> (a *googol*)

The bonus challenge asks for the number of positive square-triangular numbers below 10<sup>10<sup>100</sup></sup> (a *googolplex*)

## Solution

The solution is implemented in Rust.

Usage:
	
	$ cargo run aug2023
	
	or
	
	$ cargo build --release
	$ ./target/release/aug2023
	
		
## Discussion

The solution makes use of the [astro-float](https://github.com/stencillogic/astro-float/) arbitrary-precision floating point math library, which includes a pretty slick macro for constructing values.

Markdown is a bit crude for writing algebraic expressions, but hopefully the rest of this readme is comprehensible.

From an expansion of an [explicit formula derived by Euler](https://en.wikipedia.org/wiki/Square_triangular_number#Explicit_formulas) as an [example application of a method for finding solutions to certain Diophantine equations](https://scholarlycommons.pacific.edu/euler-works/739/)[^1], the *k*th square-triangular number *N<sub>k</sub>* is given by:

	N_k = ( ((17 + 12 * sqrt(2)) ** k) - 2 + ((17 - 12 * sqrt(2)) ** k) ) / 32
    
Since *N*<sub>0</sub> = 0 isn't positive, asking for the number of positive square-triangular numbers less than some bound is equivalent to asking for the greatest *k* such that *N<sub>k</sub>* is less than that bound.

### Main challenge

For the main challenge, an arbitrary-precision math library can easily calculate *N<sub>k</sub>* using the above formula, incrementing *k* from 1 until *N<sub>k</sub>* exceeds 10<sup>100</sup> to determine the solution.

### Bonus challenge

Working with values near the range of a googolplex or attempting non-modular exponentiation with exponents large enough to result in such values is not practical. Instead, we can turn to logarithms. To simplify handling the googolplex value the below description uses log<sub>10</sub>, although converting to natural logs can work equally well for the actual calculation.

Some replacements for more concise algebraic manipulation:

  	A = 17 + 12 * sqrt(2) (from Euler's formula above)
  	B = 17 - 12 * sqrt(2)
    C = 10 ** (10 ** 100)

	Note that log10(C) = 10 ** 100

We want to determine the greatest *k* such that *N<sub>k</sub>* < *C*. With some substitutions to the formula:

		            C > ((A ** k) - 2 + (B ** k)) / 32
	           32 * C > (A ** k) - 2 + (B ** k)
           32 * C + 2 > (A ** k) + (B ** k)
  	log10(32 * C + 2) > log10((A ** k) + (B ** k))
    
By the identity log(x + y) = log(x) + log(1 + y/x), we get:

	log10(32 * C) + log10(1 + 2/(32 * C)) > log10(A ** k) + log10(1 + (B ** k) / (A ** k))

As *B* is less than one (approximately 0.029) and *A* is greater (approximately 33.97), *B<sup>k</sup>* / *A<sup>k</sup>* approaches zero as *k* increases. Likewise, 2/(32 * *C*) is so effectively close to zero that it is very unlikely to contribute to the eventual result of the calculation. Since trying to evaluate these terms directly is impractical anyway, taking them to be equivalent to zero simplifies the inequality to:

	log10(32 * C) + log10(1 + 0) > log10(A ** k) + log10(1 + 0)
	    log10(32 * C) + log10(1) > log10(A ** k) + log10(1)
	           log10(32 * C) + 0 > log10(A ** k) + 0
                   log10(32 * C) > log10(A ** k)
    
And rearranging to isolate *k* using logarithmic identities for products and powers:

	       log10(32 * C) > log10(A ** k)
	log10(32) + log10(C) > k * log10(A)
    				   k < (log10(32) + log10(C)) / log10(A)
                       k < (log10(32) + 10 ** 100) / log10(17 + 12 * sqrt(2))
    
All these terms are feasible to perform calculations with and so a real value that *k* is bounded by can be computed (making sure to calculate the logarithms with sufficient precision). Taking the closest integer below that bound gives the greatest possible *k* such that *N<sub>k</sub>* < 10<sup>10<sup>100</sup></sup>, solving the bonus challenge. 

Note that this approach can also be used to produce the correct solution to the main challenge.

[^1]: Not relevant to the solution, but interesting to me: Euler's [article](https://scholarlycommons.pacific.edu/cgi/viewcontent.cgi?article=1738&context=euler-works) casually characterizes triangular numbers as integers of the form (*xx* + *x*)/2 (in Exemplum I, p. 12). I'd always been under the impression that this formula was originated by Gauss as a youth but Gauss was born in 1777, a year before the article is dated. It's entirely plausible that Gauss derived it independently, supposedly to get out of classroom busywork, but per the [Wikipedia article](https://en.wikipedia.org/wiki/Triangular_number) there are surviving records of it back to 816 and it may have been known to the Pythagoreans in 5<sup>th</sup> c. BC. It's also possible the Gauss story is [apocryphal](https://web.archive.org/web/20150219200405/http://www.americanscientist.org/issues/pub/gausss-day-of-reckoning/99999). Regardless, Euler plainly felt the formula was common enough knowledge that there was no need to justify it to the reader.