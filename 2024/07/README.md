# July 2024 Ponder This Challenge
The [July challenge](https://research.ibm.com/haifa/ponderthis/challenges/July2024.html) asks about ways to arrange 4x4 tiles made up of black and white squares on a board while minimising the number of adjacent squares of the same color.

## Challenges

Consider all possible 4x4 tiles made up of black and white squares limited to tiles where the number of black and white squares are equal. These tiles can be classified into *equivalence groups*, where all tiles in the group are equivalent to each other under some combination of rotations and reflections. Depending on the symmetry of the tile it may belong to a group with 1, 2, 4 or 8 distinct members.

The main challenge asks for an example arrangement of 16 tiles on a 16x16-square board such that:

 - There are no more than two consecutive squares of the same color on the board in any row or column.
 - No two tiles on the board are members of the same equivalence group.
 - The number of pairs of consecutive squares of the same color in each row and column is minimal.

The bonus challenge asks for an example arrangement of 25 tiles on a 20x20-square board such that:
 
 - There are no more than two consecutive squares of the same color on the board in any row or column
 - No two tiles on the board are members of the same equivalence group.
 - The number of pairs of consecutive squares of the same color in each row and column is minimal.
 - Each tile on the board is a member of an equivalence group with exactly 4 members.

## Solution

The solution is implemented in Rust.

Usage:

    $ cargo build --release
	$ ./target/release/jul2024 [OPTIONS]
    or
    $ cargo run jul2024 -- [OPTIONS]

    Options:
        -t, --threads <THREADS>  Set maximum number of worker threads. [default: 4]
        -h, --help               Print help

Example:

Find solutions to the main and bonus challenges using 8 worker threads in the search for tile arrangements:
    
    $ cargo build --release
    $ ./target/release/jul2024 --threads 8

## Discussion

### Tiles and equivalence groups

Building up an initial list of all tiles and equivalence groups is simple enough. There are 2<sup>16</sup> possible ways to arrange a 4x4 tile with black and white squares and these can be iterated over quickly. Any examples where the number of black and white squares are not equal can be discarded, and each tile can be sorted into an equivalence group by performing all combinations of rotations and reflections on it. Additionally, any tiles containing more than two consecutive squares of the same color horizontally or vertically can be skipped since these cannot be used when tiling the main or challenge boards. 

This process leaves 130 equivalence groups containing a total of 882 distinct tiles. Of those there are 30 equivalence groups with exactly 4 members, giving 120 distinct tiles for the bonus challenge. 

### Board tiling

The number of possible arrangements of tiles is too large to exhaustively enumerate in order to find an example with the minimal number of pairs of consecutive squares of the same color in each row or column (just "pairs" from here on for brevity) in either the main or bonus challenges. However, it is possible to determine the lower bound of pairs on a board by counting the number of pairs within each equivalence group. 

| # of pairs | # of equivalence groups |
|------------|-------------------------|
| 0          | 1                       |
| 3          | 2                       |
| 4          | 6                       |
| 5          | 6                       |
| 6          | 18                      |
| 7          | 16                      |
| 8          | 32                      |
| 9          | 16                      |
| 10         | 18                      |
| 11         | 6                       |
| 12         | 6                       |
| 13         | 2                       |
| 16         | 1                       |

For the main challenge the smallest number of pairs possible on a board cannot be less than the sum of pairs from 16 equivalence groups with the fewest numbers of pairs. This is (0 pairs x 1 tile) + (3 pairs x 2 tiles) + (4 pairs x 6 tiles) + (5 pairs x 6 tiles) + (6 pairs x 1 tile) = 66 pairs across 16 tiles.

Limiting the count of pairs to the 30 equivalence groups with 4 members for the bonus challenge:

| # of pairs | # of equivalence groups |
|------------|-------------------------|
| 4          | 3                       |
| 6          | 8                       |
| 8          | 8                       |
| 10         | 8                       |
| 12         | 3                       |

For the bonus challenge the smallest number of pairs possible on a board cannot be less than (4 pairs x 3 tiles) + (6 pairs x 8 tiles) + (8 pairs x 8 tiles ) + (10 pairs x 6 tiles) = 184 pairs across 25 tiles.

There's no obvious guarantee that valid arrangements of tiles with the fewest internal pairs can be produced on a single board without introducing any extra pairs between tile borders. Nevertheless, searches for tiling a board, restricted to the set of tiles from the equivalence groups with the potential to be part of a minimal board and pruning any branches where the selected tiling produces extra pairs, can quickly find tile arrangements that reach the known lower bounds.