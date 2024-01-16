 # December 2023 Ponder This Challenge
The [December challenge](https://research.ibm.com/haifa/ponderthis/challenges/December2023.html) considers circles that pass through points on a triangular grid.

## Challenges

Given a grid of equilateral triangles with sides of length 1, the challenge defines a function *f*(*m*) for integers *m* > 0, which is the number of distinct circles centered at (0,0) with non-integer radii *r* such that *m* < *r* < *m* + 1 that intersects point on the grid. The challenge asks for an *m* such that *f*(*m*) = 1,000,000.

The bonus challenge asks for all *m* such that *f*(*m*) = 1,000,000.

## Solution

The solution is implemented in Go.

Usage:

	$ go run dec2023.go [OPTIONS]

	or

	$ go build
	$ ./dec2023 [OPTIONS]

	OPTIONS:
		-max int
			The maximum in the range of m values to test (default 4314000)
		-min int
			The minimum in the range of m values to test (default 4310900)
		-t int
			The number of worker threads to run in parallel (default 4)
		-v
			Verbosely print each m and f(m) calculated in each batch of threads

Example:

	$ ./dec2023 -min 4310900 -max 4314000 -t 4 -v

The solution will calculate *f*(*m*) for each *m* in the specified range and display any found where *f*(*m*) = 1,000,000 when the process is complete. All satisfying values of *m* are found within the default range.
    
## Discussion 

Apart from the hint given that one of the possible solution *m* values is a base-10 palindrome, the main challenge seems more difficult than the bonus challenge, which is relatively straightforward once *f*(*m*) can be calculated efficiently.

### Calculating *f*(*m*)

At first approach, it seems like calculating *f*(*m*) for a given *m* will involve testing a very large number of grid positions as *m* increases. There are fortunately some geometric simplifications.

For any given circle centered at (0,0) that intersects one or more points on the triangular grid, these intersection will be mirrored across the grid's three axes of symmetry. This means that only 1/6<sup>th</sup> of the grid needs to be examined when searching for intersections. The description below describes coordinates for the area immediately above the *x*-axis in the upper right-quadrant, where *x* ≥ 0, *y* ≥ 0 and *y* ≤ *x* / √(3/4). A previous version of this solution unnecessarily searched the entire *x* ≥ 0, *y* ≥ 0 quadrant for intersections.

Rather than looking for distinct circles that intersect points on the grid, we're actually looking for points on the grid that are a distinct distance (i.e. a radius) from the origin. We want to examine each grid point with a distance from the origin *d* with *m* < *d* < *m* + 1, and add it to a collection of distances if *d* has not been added previously. Once all grid points have been examined, the size of the collection of distinct distances is *f*(*m*).

### Candidate grid points

The coordinate of each point in *x* is either *u* + 1/2 on an odd row or *u* on an even row for some integer *u*.

The height of each triangle row is √(1<sup>2</sup> - (1/2)<sup>2</sup>) or simply √(3/4). The coordinate of each grid point in *y* is *v*√(3/4) for some integer *v*.

Limiting the area examined to a 60 degree arc due to the symmetry of the grid, the intersection of the circle with radius *m* + 1 and the line *y* = *x* / √(3/4) is at coordinates *y* = (*m* + 1)√(12/21), x = (*m* + 1)√(9/21). The greatest row number to be examined is therefore:

 *v*<sub>max</sub> = floor((*m* + 1)√(12/21) / √(3/4))

or 

*v*<sub>max</sub> = floor((*m* + 1)√(48/63)).

Iterating from *v* = 1 (all grid points on the 0<sup>th</sup> row have integer radii) to *v*<sub>max</sub>, we can determine the *x* coordinates of the points on the *v*<sup>th</sup> row that intersect the circle of radius *m* and the circle of radius *m* + 1 as:

*x*<sub>*v*,*m*</sub> = √(*m*<sup>2</sup> + (*v* √(3/4))<sup>2</sup>)

*x*<sub>*v*,*m* + 1</sub> = √((*m* + 1)<sup>2</sup> + (*v* √(3/4))<sup>2</sup>)

We can then calculate the distance to the origin for each grid point on the *v*<sup>th</sup> row with an *x* coordinate between these bounds. It's both faster and less prone to floating point errors to calculate the square of the distance from the grid point to the origin and store that in the collection of distinct distances. If a grid point has a squared distance to the origin that has been previously added to the collection, it can be discarded. Once all points have been examined below, the collection of distinct distances is complete and the number of elements in it can be returned as the value of *f*(*m*).

### Finding *f*(*m*) = 1,000,000

The function *f*(*m*) is not exactly monotonic, but on average it increases as *m* increases. By examination, it's possible to find bounds *m*<sub>min</sub> < *m*<sub>max</sub>, where for all *m* < *m*<sub>min</sub>, *f*(*m*) < 1,000,000 and for all *m* > *m*<sub>max</sub>,  *f*(*m*) > 1,000,000. Once those bounds are approximately determined then all *m* where *f*(*m*) = 1,000,000 must lie between them. Calculating *f*(*m*) for each *m* in that range allows us to enumerate all *m* that satisfy the challenge conditions.

I used relatively broad bounds for *m*<sub>min</sub> and *m*<sub>max</sub> initially, with a difference of roughly 20,000. The answers to the bonus challenge were found in a fairly narrow range within it, which I've approximately included as the default range for the Go solution.

