# October 2025 Ponder This Challenge
The [October challenge](https://research.ibm.com/haifa/ponderthis/challenges/October2025.html) asks for the number of perfect mazes possible within rectangular grids of cells.

## Challenges

Consider the set of distinct mazes (ignoring isomorphism up to rotation/reflection) within an $n \times m$ rectangular grid of cells, where:

 - Each cell is connected to its immediate neighbors in the four cardinal directions.
 - Each pair of neighboring cells either does or does not have a wall between them. 
 - There is exactly one path between every two cells in the maze

The main challenge asks for the number of such mazes with dimensions $42 \times 57$, given with four digits of precision in exponential notation.

The bonus challenge asks for the number of such mazes with dimensions $342 \times 357$ in the same format.

## Solution

The solution is implemented in Python and uses the [numpy](https://numpy.org/) and [scipy](https://scipy.org/) packages for matrix operations.

Usage:

```console
$ pip install numpy
$ pip install scipy
$ python oct2025.py
```

The solution will output the answers to the main and bonus challenges.

## Discussion

It's relatively well known that perfect mazes like the ones described by the challenge, having exactly one path between every two cells, are equivalent to [tree graphs](https://en.wikipedia.org/wiki/Tree_(graph_theory)). And it's easy to see that an $n \times m$ grid of cells without any walls between them would be equivalent to a [square lattice graph](https://en.wikipedia.org/wiki/Lattice_graph), where all spatially adjacent cells have edges between their corresponding vertices.

The set of all perfect mazes formed by adding walls between the cells of an $n \times m$ grid, including mazes that are isomorphic to others in the set under rotation/reflection, is therefore equivalent to the set of distinct [spanning trees](https://en.wikipedia.org/wiki/Spanning_tree) of the lattice graph of the grid. Any spanning tree of the graph would have exactly one path between any two cells in the grid, and any neighboring cells that are not adjacent in the tree would have a wall between them in the equivalent maze. 

[Kirchhoff's theorem](https://en.wikipedia.org/wiki/Kirchhoff%27s_theorem) provides a method for the polynomial time calculation of the number of spanning trees for a given graph, which can be applied to find answers to both challenges.

1. Compose a lattice graph $G$ with vertices $(1,1),...,(n, m)$, each connected to their immediate neighbors. Note that this graph does not need to include entry/exit vertices from the maze[^1]. 
2. Construct $L$, the [Laplacian matrix](https://en.wikipedia.org/wiki/Laplacian_matrix) for $G$ ($L = D - A$, where $D$ is a diagonal matrix for the degrees of each vertex in $G$ and $A$ is the adjacency matrix of $G$) 
3. Create a submatrix $S$ by removing one row and one column from $L$. Any combination of row and column removed will arrive at the same magnitude of result, although if the sum of the indexes of the column and row removed is odd the result will be negative. Removing the same row and column index will necessarily have the sum of the indexes as even, which simplifies things.
4. Compute the determinant of $S$. This gives the number of possible spanning trees of $G$. 

The following is an example of the process for the $3 \times 3$ grid. The row/column indexes of each vertex in the degree and adjacency matrices below appear in raster order.

$$D = \begin{bmatrix}
2 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
0 & 3 & 0 & 0 & 0 & 0 & 0 & 0 & 0\\
0 & 0 & 2 & 0 & 0 & 0 & 0 & 0 & 0\\
0 & 0 & 0 & 3 & 0 & 0 & 0 & 0 & 0\\
0 & 0 & 0 & 0 & 4 & 0 & 0 & 0 & 0\\
0 & 0 & 0 & 0 & 0 & 3 & 0 & 0 & 0\\
0 & 0 & 0 & 0 & 0 & 0 & 2 & 0 & 0\\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 3 & 0\\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 2
\end{bmatrix}
$$

$$A = \begin{bmatrix}
0 & 1 & 0 & 1 & 0 & 0 & 0 & 0 & 0\\
1 & 0 & 1 & 0 & 1 & 0 & 0 & 0 & 0\\
0 & 1 & 0 & 0 & 0 & 1 & 0 & 0 & 0\\
1 & 0 & 0 & 0 & 1 & 0 & 1 & 0 & 0\\
0 & 1 & 0 & 1 & 0 & 1 & 0 & 1 & 0\\
0 & 0 & 1 & 0 & 1 & 0 & 0 & 0 & 1\\
0 & 0 & 0 & 1 & 0 & 0 & 0 & 1 & 0\\
0 & 0 & 0 & 0 & 1 & 0 & 1 & 0 & 1\\
0 & 0 & 0 & 0 & 0 & 1 & 0 & 1 & 0
\end{bmatrix}
$$

$$L = D - A = \begin{bmatrix}
2 & -1 & 0 & -1 & 0 & 0 & 0 & 0 & 0\\
-1 & 3 & -1 & 0 & -1 & 0 & 0 & 0 & 0\\
0 & -1 & 2 & 0 & 0 & -1 & 0 & 0 & 0\\
-1 & 0 & 0 & 3 & -1 & 0 & -1 & 0 & 0\\
0 & -1 & 0 & -1 & 4 & -1 & 0 & -1 & 0\\
0 & 0 & -1 & 0 & -1 & 3 & 0 & 0 & -1\\
0 & 0 & 0 & -1 & 0 & 0 & 2 & -1 & 0\\
0 & 0 & 0 & 0 & -1 & 0 & -1 & 3 & -1\\
0 & 0 & 0 & 0 & 0 & -1 & 0 & -1 & 2
\end{bmatrix}
$$

Taking $S$ as $L$ with the final row and column removed:

$$\left|S\right| = \begin{vmatrix}
2 & -1 & 0 & -1 & 0 & 0 & 0 & 0\\
-1 & 3 & -1 & 0 & -1 & 0 & 0 & 0\\
0 & -1 & 2 & 0 & 0 & -1 & 0 & 0\\
-1 & 0 & 0 & 3 & -1 & 0 & -1 & 0\\
0 & -1 & 0 & -1 & 4 & -1 & 0 & -1\\
0 & 0 & -1 & 0 & -1 & 3 & 0 & 0\\
0 & 0 & 0 & -1 & 0 & 0 & 2 & -1\\
0 & 0 & 0 & 0 & -1 & 0 & -1 & 3
\end{vmatrix} = 192
$$

While this is mathematically straightforward, in practice an implementation benefits from using a data structure intended for sparse matrices for the entries of $S$, which would otherwise require memory for $(342\cdot357 - 1)^2 \approxeq 1.49 \times 10^{10}$ integers for the bonus challenge. In addition, the determinants of $S$ for the main and bonus challenges are much larger than can be stored directly by linear algebra libraries using standard data types during calculation, resulting in overflows. The logarithm of the determinant of $S$ can be computed instead, and then $e^{\ln{\left|S\right|}}$ can be calculated in a high-precision math library to give the challenge answer. This process is less precise but the required answers are approximations anyway.

[^1]: There's an argument to be made that mazes with the same internal structure but different entry/exit points should be counted as separate mazes when determining the number of possible mazes for a given grid, even if sets of spanning trees for grids with different entries/exits are isomorphic, but that's not what's indicated by the challenge. The challenge is only asking for the number of distinct internal wall arrangements that form perfect mazes, so we can assume fixed entry/exit points. The number of possible mazes is identical for every two entry/exit points on a given grid in any case, evident from the spanning tree approach to the problem.