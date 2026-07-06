 # June 2026 Ponder This Challenge
The [June challenge](https://research.ibm.com/blog/ponder-this-june-2026) looks for an optimized series of superhero movies.

## Challenges

A comic book publisher wishes to plan out a series of movies based on a superhero team franchise. They need the movies to feature action scenes that include all possible combinations of heroes in the roster, but to minimize audience fatigue they would like this to occur over the smallest possible number of action scenes across all the movies.

Each movie follows a simple formula. One hero is introduced and has in an action scene. Each other hero in the movie is sequentially introduced and added to the growing team of heroes, all of whom participate in an action scene together. The climax is reached when the final hero in the movie is introduced, and the entire team has an action scene together. A given movie does not need to include all the heroes in the franchise.

Across all the movies, each hero must have at least one solo action scene, each pair of heroes must have at least one dual action scene, etc. up to the entire roster of heroes participating in an action scene together. For a small number of heroes it is possible to do this without any duplication of hero combinations, but for four or more heroes some duplication is necessary.

The series of movies can be described in a compact string with separators to denote the start of new movies, and sequences of initials listing the heroes appearing in each movie in the order in which they are introduced. For example, for three movies in a franchise with three heroes A,B,C that cover all possible action scene combinations - one with scenes {A}, {A,C}, one with scenes {B}, {B,C} and one with scenes {A}, {A,B}, {A,B,C} - the movies could be written as **0AC0BC0ABC**.

The main challenge asks for the optimal series of movies for $n = 6$ heroes in the compact string format.

The bonus challenge asks for the optimal series of movies for $n = 10$ heroes in the compact string format.

## Solution

The solution is implemented in Python.

### Usage

```console
$ python jun2026.py
```

The script will compute and output the answers to both challenges.

## Discussion


### Initial approach

For $n$ heroes, a lower bound for the minimal number of possible movies and scenes can be established. The number of possible hero combinations of each size $k$ is the binomial coefficient:

$$\binom{n}{k} = \frac{n!}{k!(n-k)!}$$

For example, for $n = 6$:

| Heroes per scene | Number of combinations |
|------------------|------------------------|
| 6                | 1                      |
| 5                | 6                      |
| 4                | 15                     |
| 3                | 20                     |
| 2                | 15                     |
| 1                | 6                      |


Assuming that there exists an assignment of movies that each remove the greatest possible number of hero combinations per movie from this list when added to the series (with the series therefore having the minimum possible number of scenes):

1. Add 1 movie with 6 heros that removes one unique hero combination from sizes 1-6, leaving 0 remaining combinations of size 6, 5 remaining combinations of size 5, 14 remaining combinations of size 4, 19 remaining combinations of size 3, 14 remaining combinations of size 2 and 5 remaining combinations of size 1.
2. Add 5 movies with 5 heroes that remove one unique hero combination each from sizes 1-5, leaving 0 remaining combinations of size 6, 0 remaining combinations of size 5, 9 remaining combinations of size 4, 14 remaining combinations of size 3, 9 remaining combinations of size 2 and 0 remaining combinations of size 1.
3. Add 9 movies with 4 heroes that remove one unique hero combination each from sizes 2-4 (and with 9 duplications of previous scenes with a single hero), leaving 0 remaining combinations of size 6, 0 remaining combinations of size 5, 0 remaining combinations of size 4, 5 remaining combinations of size 3, 0 remaining combinations of size 2 and 0 remaining combinations of size 1.
4. Add 5 movies with 3 heroes that remove one unique hero combination each from size 3 (and with 10 duplications of previous scenes with one or two heroes), leaving 0 remaining combinations of size 6, 0 remaining combinations of size 5, 0 remaining combinations of size 4, 0 remaining combinations of size 3, 0 remaining combinations of size 2 and 0 remaining combinations of size 1.

All possible combinations of heroes would be covered in a minimum of 20 movies with 82 action scenes in total.

For a cast of heroes of size $n$, the minimal number of scenes would be:

$$\sum_{k = \lceil n/2 \rceil}^{n}{\left( \binom{n}{k} - \binom{n}{k+1} \right) \cdot k}$$

and the minimal number of movies would be:

$$ \sum_{k = \lceil n/2 \rceil}^{n} {\binom{n}{k} - \binom{n}{k+1}} = \binom{n}{ \lceil n/2 \rceil }$$

Using this model of minimal movie series, it seems like it should be possible to try tree searches of permutations of hero combinations at each movie size until a set of movies can be found that matches the minimal possible number of scenes. I was able to find solutions fairly quickly up to to $n = 8$ with this approach, but advancing further was not promising.

### Symmetric chain decomposition

I was lucky enough to stumble on [lecture notes](https://ktiml.mff.cuni.cz/~gregor/hypercube/lecture17.pdf)[^1] describing how to construct disjoint chains of "increasing" vertices that cover boolean lattice hypercubes. This is not a concept I had any familiarity with, but it's very applicable to the problem challenges.

In a boolean lattice hypercube of degree $n$, each vertex has an $n$-dimensional coordinate of boolean values and is neighbored by all vertices that differ in exactly one dimension, with one vertex for every possible coordinate. A symmetric chain decomposition (SCD) of a boolean lattice is defined as a set of ordered chains of neighboring vertices such that each vertex is included in exactly one chain, the number of chains is minimal, and the vertices in each chain increase the number of "1" values in their coordinates at each step. Several proofs are offered that there is an SCD for any boolean lattice with degree $n \ge 1$.

Applied to the challenges, one could consider each vertex as having a coordinate where each of the $n$ heroes is either present or not present, representing an action scene with a distinct combination of heroes. A chain of vertices that starts with some number of heroes and sequentially adds one hero at a time would represent a movie (if more than one hero is present on the initial vertex in the chain, the movie could introduce them in any order, and the vertex representing no heroes can be ignored). A symmetric chain decomposition of the entire lattice would necessarily represent a set of movies with the minimal number of possible scenes.

The proofs of the existence of an SCD also give methods for their construction. The method I used was one where the hypercube can be recursively subdivided on one dimension at a time down to a dimensionality where a known SCD exists for a lattice of that degree. The chains for each pair of split sub-lattices can then be combined using a straightforward method up through each level of the recursion until an SCD for the original hypercube is arrived at. These chains can then be translated into the strings describing a series of movies.

[^1]: Gregor, Petr, "Lecture 17: Symmetric chain decompositions." Hypercube structures, June 17, 2018, Charles University. https://ktiml.mff.cuni.cz/~gregor/hypercube/lecture17.pdf