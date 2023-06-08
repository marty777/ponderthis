# May 2023 Ponder This Challenge
The [May challenge](https://research.ibm.com/haifa/ponderthis/challenges/May2023.html) asks for the scalar result of the quadratic form *x*<sup>T</sup> ***A*** *x* of a particular real-valued *n* x *n* matrix ***A*** and vector *x* of length *n*, generated from the parameters *k* and *n*. 

## Challenges

The main challenge asks for the quadratic form where *k* = 5, *n* = 2<sup>20</sup>, rounded to three decimal places.

The bonus challenge asks  for the quadratic form where *k* = 5, *n* = 2<sup>30</sup>, rounded to three decimal places.

## Solution

The solution is implemented in Rust.

Usage:

		Usage: may2023 [OPTIONS]
		or
		cargo run -- [OPTIONS]
	
		Options:
		  -b, --bonus              Compute the quadratic form for the bonus challenge.
		  -t, --threads <THREADS>  Set number of worker threads to use during matrix multiplication. [default: 8]
		  -h, --help               Print help


Examples:

Solve the main challenge:

		$  may2023
        
Solve the bonus challenge:

		$  may2023 --bonus

Increasing the number of worker threads to a value close to the number of available cores will increase the speed of the matrix multiplication step.

## Discussion

Performing conventional multiplication between a *n* x *n* matrix and a vector of length *n* where *n* = 2<sup>20</sup> is non-trivial on a relatively current desktop PC. Where *n* = 2<sup>30</sup> it is impractical. Fortunately the matrix specified in the challenge allows for some simplifications that can yield the quadratic form more efficiently than standard multiplication. Only the specifics of the *k* = 5, *n* = 2<sup>30</sup> bonus challenge are discussed below, but the same method is used for the main challenge.

### Overview

The entries of the matrix ***A*** are defined by an interesting algorithm in the challenge description. We are given a set of vectors *Q*<sub>*i*</sub> for *i* in 0...*n*-1, where each vector *Q*<sub>*i*</sub> is of length *k* and the entry at position *t* in *Q*<sub>*i*</sub> is given by a specified pseudo-random number generator function with the parameters *i* and *t*. For lack of a better term, any pair of *Q* vectors can be taken together to produce a *comparison index* obtained by comparing the entries at each position in both vectors. The comparison index *c*<sub>*ij*</sub> of *Q*<sub>*i*</sub> and *Q*<sub>*j*</sub> is given by:

	c_ij = 0
	for t in 0 to k-1:
		if Q_i[t] == Q_j[t]:
			c_ij += pow(2,t)

Effectively *c*<sub>*ij*</sub> is a *k*-digit binary value (in little-endian form) where digit *t* is 1 if entry *t* is the same in both *Q*<sub>*i*</sub> and *Q*<sub>*j*</sub> and 0 otherwise. For *k* = 5, this means that any comparison index will be between 0 (no entries the same) and 31 (all entries the same). As an example, the *Q* vectors [29, 10, 17, 31, 24] and [1, 12, 17, 31, 2] would have the comparison index 12, because the entries in position 2 (zero-indexed) and position 3 are the same, and 2<sup>2</sup> + 2<sup>3</sup> = 12.

For any entry *A*<sub>*ij*</sub> at column *i* and row *j* in matrix ***A***, the value is calculated from the comparison index *c*<sub>*ij*</sub> of the vectors *Q*<sub>*i*</sub> and *Q*<sub>*j*</sub>: 

*A*<sub>*ij*</sub> = *c*<sub>*ij*</sub> / (2<sup>*k*</sup> - 1)

Since 1/(2<sup>*k*</sup> - 1) is constant for a given *k*, it can be useful to simplify *A*<sub>*ij*</sub> as *c*<sub>*ij*</sub> and multiply the result by 1/(2<sup>*k*</sup> - 1) after calculating the quadratic form, but this is not required.

As a consequence of how *A*<sub>*ij*</sub> is defined, ***A*** is a symmetric and relatively sparse matrix, where approximately 83% of entries have zero values in the bonus challenge. Most pairs of *Q* vectors have no elements in common, so their comparison index is zero.

### Distribution of *Q* vectors

The pseudo-random number generator function (see the [challenge description](https://research.ibm.com/haifa/ponderthis/challenges/May2023.html) for the definition) that produces the entries in each *Q* vector provides the entry point to overcoming the formidable scale of the bonus challenge, as it produces an acutely non-uniform distribution of values when *k* = 5. Examining the system for *k* = 5, *n* = 2<sup>10</sup>, I mistakenly believed it had a period of 710 *Q* vectors. Although examining larger systems shows that the period is not nearly that short, the number of distinct *Q* vectors the pseudo-random number generator produces is suprisingly small. 

For the bonus challenge, there are only **1876** distinct vectors among the 2<sup>30</sup> *Q* vectors used in generating the entries of ***A***. With a perfectly uniform distribution we might expect the number of distinct vectors to approach 2<sup>25</sup> for *k* = 5. In the method used for the matrix multiplication step, the number of operations needed to calculate the quadratic form is largely determined by the number of distinct *Q* vectors. With a more uniform distribution this method would offer less of a shortcut.

Let's call *r* the number of distinct vectors *Q*<sub>*i*</sub> for *i* in 0...*n*-1 and call each distinct vector *P*<sub>*u*</sub> for *u* in 0...*r*-1. For a given distinct vector *P*<sub>*u*</sub>, we can generate the comparison index with each other *P*<sub>*v*</sub> for *v* in 0...*r*-1 , which I'm going to call *d*<sub>*uv*</sub> rather than *c*<sub>*uv*</sub> due to the change in indexes. 

We can build a lookup where for each *u* we list each distinct non-zero *d*<sub>*uv*</sub>, together with a list of all *v* that produce the same comparison index. Taking this lookup, together with a lookup for each *u* in 0...*r*-1 giving the list of all *i* in 0...*n*-1 such that *Q*<sub>*i*</sub> = *P*<sub>*u*</sub>, provides all the information we need to efficiently calculate the quadratic form.

### Matrix multiplication by partial sums

Thanks to the distribution of the pseudo-random number generator, it is possible to produce *x*<sup>T</sup> ***A*** *x* with substantially fewer operations than conventional matrix and vector multiplication, although for *n* = 2<sup>30</sup> it will still require quite a lot of arithmetic.

Rather than producing a sum of terms for each row of ***A*** *x* and then multiplying by *x*<sup>T</sup> (or vice versa), we instead calculate partial sums for sets of terms which are equivalent over multiple rows thanks to the relatively few distinct comparison indexes involved. The total of these partial sums over all combinations of pairs of distinct vectors results in the vector ***A*** *x*, and with an additional multiplication step can go directly to the scalar *x*<sup>T</sup> ***A*** *x* without having to store a vector of length 2<sup>30</sup>. 

In pseudocode:
	
	# For i in 0 to n-1
	function x(i):
		return -1 + (2/(n-1)) * i
    
    function quadratic_form():
		quadratic_sum = 0
		for u in 0 to r-1:
			u_row_sum = 0
			for v in 0 to r-1 where the comparison index d_uv of distinct Q vectors P_u and P_v is not zero:
				v_term_sum = 0
				coefficient = d_uv / (pow(2,k) - 1)
				for all j such that Q_j == P_v:
					v_term_sum += x(j)
				u_row_sum += v_term_sum * coefficient
			for all i such that Q_i == P_u:
				quadratic_sum += u_row_sum * x(i) 
		return quadratic_sum

Breaking the overall solution up into small subsets of *u* in 0 to r-1 that can be calculated separately in parallel and then summed together allows the result to be reached more quickly than a single-threaded approach. Due to the limits of floating point representation, the partial sums method may produce a slightly different result than by using standard matrix multiplication, but this difference is well below 3 decimal places of accuracy, satisfying the challenge requirements.
