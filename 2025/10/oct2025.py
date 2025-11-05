# https://research.ibm.com/haifa/ponderthis/challenges/October2025.html

import numpy as np
import scipy as sp
from decimal import *
import warnings

# Ignore a scipy warning about a sparse matrix type conversion when computing 
# LU decompositions. It's fine.
warnings.filterwarnings("ignore", category=sp.sparse.SparseEfficiencyWarning)

DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Given a scipy.sparse matrix M, compute ln(|M|) via LU decomposition, needed
# because the sparse matrix classes don't include a determinant or log 
# determinant method without converting to a dense matrix first (undesirable in
# this case due to the sizes of matrices involved). 
# An approach taken from https://stackoverflow.com/a/60982033
def sparse_log_determinant(M):
    # The determinant |M| of a matrix M can be calculated from the product of 
    # the determinants of the upper and lower triangular decompositions of M.
    # M = L*U
    # so
    # |M| = |L|*|U|
    # so ln(|M|) = ln(|L|*|U|)
    # and by logarithmic identity ln(a*b) = ln(a) + ln(b)
    # ln(|M|) = ln(|L|) + ln(|U|)
    # The determinant of a triangular matrix is the product of its 
    # diagonals |X| = x_1,1 * x_2,2 * ... * x_n,n
    # and by that logarithmic identity again
    # ln(|X|) = ln(x_1,1) + ln(x_2,2) + ... + ln(x_n,n)
    # and so:
    # ln(|M|) 
    #   = ln(|L|) + ln(|U|) 
    #   = ln(l_1,1) + ... + ln(l_n,n) + ln(u_1,1) + ... + ln(u_n,n)
    
    # Get the LU decomposition of M.
    lu = sp.sparse.linalg.splu(M)
    # Return the sums of the logs of the diagonals of L and U.
    return np.log(lu.L.diagonal()).sum() + np.log(lu.U.diagonal()).sum()
    
# Calculate the number of perfect mazes possible in a n x m rectangular grid of
# cells using Kirschhoff's theorem for the number of spanning trees of a graph.
def kirschhoffs_maze_enumerator(n, m):
    # List of nodes in the lattice graph of the grid.
    graph_nodes = []
    for y in range(m):
        for x in range(n):
            graph_nodes.append((x,y))
            
    # Lookup of graph nodes to indexes.
    graph_node_indexes = {}
    for i in range(len(graph_nodes)):
        graph_node_indexes[graph_nodes[i]] = i
    
    # Omit the final row and column when constructing the submatrix of the 
    # Laplacian.
    omit_row_column = len(graph_nodes) - 1
    # Create new zeroed sparse matrix to store the submatrix of the Laplacian.
    # lil_matrix seems to be the best performing sparse matrix type for how 
    # this solution populates the matrix.
    laplacian_submatrix = sp.sparse.lil_matrix((len(graph_nodes) - 1, len(graph_nodes) - 1), dtype=np.int64)
    # Set entries in the submatrix.
    for i in range(len(graph_nodes) - 1):
        node_coord = graph_nodes[i]
        if i == omit_row_column:
            continue
        for delta in DIRS:
            neighbor_coord = (node_coord[0] + delta[0], node_coord[1] + delta[1])
            if neighbor_coord not in graph_node_indexes:
                continue
            j = graph_node_indexes[neighbor_coord]
            # only update if neighbor cell not previously handled
            if j <= i:
                continue
            laplacian_submatrix[i,i] += 1
            if j != omit_row_column:
                laplacian_submatrix[j,j] += 1
                laplacian_submatrix[i,j] = -1
                laplacian_submatrix[j,i] = -1  

    # The determinant is too large to be handled by scipy directly. Compute the 
    # log of the determinant instead, then return e^{ln(det)} as a Decimal.
    logdet = sparse_log_determinant(laplacian_submatrix)
    determinant_log = Decimal(logdet)
    return determinant_log.exp()

# Strip '+' sign for positive exponents in the standard exponential decimal 
# format.
def exponent_format(decimal):  
    return "{:1.3e}".format(decimal).replace("+", "")
    
def main():
    print("\n######## Ponder This Challenge - October 2025 ########\n")
    print(f"Main solution:\t{exponent_format(kirschhoffs_maze_enumerator(42,57))}")
    print(f"Bonus solution:\t{exponent_format(kirschhoffs_maze_enumerator(342,357))}")

if __name__ == "__main__":
    main()