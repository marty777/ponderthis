

use std::collections::{HashMap, HashSet};
use std::thread;
use std::sync::{Arc,Mutex};

pub enum Dir {
    Up,
    Down,
    Left,
    Right
}

/// Storage for all tiles in an equivalence group. Tiles are represented as 
/// u16 integers.
pub struct TileEquivalenceGroup {
    /// Base id/tile for the group.
    pub id:u16,
    /// All tiles in the group.               
    pub transforms:Vec<u16>,
    /// The count of consecutive pairs of squares of the same color in each row
    /// and column of each tile in the equivalence group. 
    pub pairs:usize}

impl TileEquivalenceGroup {
    /// Builds a new equivalence group with the provided integer as the base 
    /// tile. Expands the group with rotations and reflections to include all 
    /// other member tiles and counts the number of pairs of squares of the 
    /// same color.
    /// 
    /// # Arguments
    ///
    /// * `bits` - A u16 integer describing the layout of a tile.
    ///
    /// # Panics
    /// 
    /// The method will panic if the `bits` argument describes a tile that does
    /// not contain an equal number of black and white squares or contains more
    /// than two consecutive squares of the same color in a row or column.
    pub fn new(bits:u16) -> TileEquivalenceGroup {
        if !TileEquivalenceGroup::bits_okay(bits) {
            panic!("Bad bits for {}", bits);
        }
        let mut transforms = Vec::new();
        for rotation in 0..4 {
            for reflection in 0..2 {
                let mut transformed_bits = bits;
                for _i in 0..rotation {
                    transformed_bits = TileEquivalenceGroup::rotate(transformed_bits);
                }
                if reflection == 1 {
                    transformed_bits = TileEquivalenceGroup::reflect(transformed_bits);
                }
                if !transforms.contains(&transformed_bits) {
                    transforms.push(transformed_bits);
                }                
            }
        }
        let squares:Vec<Vec<bool>> = TileEquivalenceGroup::bits_to_squares(bits);
        let mut horizontal_pairs = 0;
        let mut vertical_pairs = 0;
        let mut last_vertical = 2;
        let mut last_horizontal = 2;
        for y in 0..4 {
            for x in 0..4 {
                let curr_horizontal = if squares[y][x] {1} else {0}; 
                let curr_vertical = if squares[x][y] {1} else {0};
                if curr_horizontal == last_horizontal {
                    horizontal_pairs += 1;
                }
                if curr_vertical == last_vertical {
                    vertical_pairs += 1;
                }
                last_horizontal = curr_horizontal;
                last_vertical = curr_vertical;
            }
            last_vertical = 2;
            last_horizontal = 2;
        }
        return TileEquivalenceGroup{ id:bits, transforms:transforms, pairs: horizontal_pairs + vertical_pairs};
    }

    /// Returns a copy of self.
    pub fn copy(&self) -> TileEquivalenceGroup {
        let mut transforms = Vec::new();
        for i in 0..self.transforms.len() {
            transforms.push(self.transforms[i]);
        }
        return TileEquivalenceGroup{id:self.id, transforms:transforms, pairs: self.pairs};
    }

    /// Reflects a 4x4 tile, represented as an integer, horizontally and 
    /// returns the result.
    pub fn reflect(bits:u16) -> u16 {
        let indexes = vec![3,2,1,0,7,6,5,4,11,10,9,8,15,14,13,12];
        let mut result:u16 = 0;
        for i in 0..indexes.len() {
            let bit = (bits >> indexes[i]) & 0x1;
            result |= bit << i;
        }
        return result;
    }

    /// Rotates a 4x4 tile, represented as an integer, 90 degrees clockwise and
    /// returns the result.
    pub fn rotate(bits:u16) -> u16 {
        let indexes = vec![12,8,4,0,13,9,5,1,14,10,6,2,15,11,7,3];
        let mut result:u16 = 0;
        for i in 0..indexes.len() {
            let bit = (bits >> indexes[i]) & 0x1;
            result |= bit << i;
        }
        return result;
    }

    /// Converts the bits of an integer representing a tile to a two 
    /// dimensional vector of booleans and returns the result.
    fn bits_to_squares(bits:u16) -> Vec<Vec<bool>> {
        let dim = 4;
        let mut squares:Vec<Vec<bool>> = Vec::new();
        for r in 0..dim {
            let mut row = Vec::new();
            for c in 0..dim {
                let bit = (bits >> (dim - 1 - c + dim*(dim - 1 - r))) & 0x1;
                if bit == 1 {
                    row.push(true);
                }
                else {
                    row.push(false);
                }
            }
            squares.push(row);
        }
        return squares;
    }

    /// Checks that the provided integer describes a 4x4 tile where there are 
    /// equal numbers of ones and zeros and no more than two consecutive 
    /// squares of the the same color in any row or column
    fn bits_okay(bits:u16) -> bool {
        let dim = 4;
        let squares:Vec<Vec<bool>> = TileEquivalenceGroup::bits_to_squares(bits);
        // Check if equal numbers of ones and zeros
        let mut ones = 0;
        let mut zeros = 0;
        for r in 0..dim {
            for c in 0..dim {
                if squares[r][c] {
                    ones += 1;
                }
                else {
                    zeros += 1;
                }
            }
        }
        if ones != zeros {
            return false;
        }
        // Test if 3 or more ones or zeros are adjacent horizontally or vertically
        for r in 0..dim {
            for c in 1..dim-1 {
                if squares[r][c-1] == squares[r][c] && squares[r][c+1] == squares[r][c] {
                    return false;
                }
            }
        }
        for c in 0..dim {
            for r in 1..dim-1 {
                if squares[r-1][c] == squares[r][c] && squares[r+1][c] == squares[r][c] {
                    return false;
                }
            }
        }
        return true
    }
}

/// Stores lookups of all valid tiles, their equivalence groups, and a map of
/// tiles to permitted adjacent tiles in each direction.
pub struct TileStore {
    /// A set of all equivalence groups in the store, indexed by group id.
    pub equivalence_groups:HashMap<u16, TileEquivalenceGroup>,
    /// A lookup of tiles to their corresponding equivalence group id.
    pub tile_equivalence_group:HashMap<u16, u16>,
    /// A lookup for each tile listing all possible tiles that are legal to be
    /// placed adjacent to the tile up, down, left or right on the board.
    pub tile_adjacency:HashMap<u16, Vec<HashSet<u16>>>
}

impl TileStore {
    /// Builds a new TileStore of all possible tiles that can be arranged on a 
    /// board. If constucted for the bonus challenge, any tiles in equivalence 
    /// groups without exactly 4 members will be omitted.
    pub fn new(bonus:bool) -> TileStore {
        let all_equivalence_groups = TileStore::all_equivalence_groups();
        let mut equivalence_groups:HashMap<u16, TileEquivalenceGroup> = HashMap::new();
        for i in 0..all_equivalence_groups.len() {
            if bonus && all_equivalence_groups[i].transforms.len() != 4 {
                continue;
            }
            equivalence_groups.insert(all_equivalence_groups[i].id, all_equivalence_groups[i].copy());
        }
        let mut tile_equivalence_group:HashMap<u16, u16> = HashMap::new();
        for i in 0..all_equivalence_groups.len() {
            if bonus && all_equivalence_groups[i].transforms.len() != 4 {
                continue;
            }
            for j in 0..all_equivalence_groups[i].transforms.len() {
                tile_equivalence_group.insert(all_equivalence_groups[i].transforms[j], all_equivalence_groups[i].id);
            }
        }
        let tile_adjacency:HashMap<u16, Vec<HashSet<u16>>> = TileStore::tile_adjacencies(&equivalence_groups, true);
        return TileStore{equivalence_groups:equivalence_groups, tile_equivalence_group:tile_equivalence_group, tile_adjacency:tile_adjacency};
    }

    /// Returns a map of tiles to lookups of permitted adjacent tiles in each
    /// direction. Tiles are not permitted to be adjacent if they would form 
    /// more than two consecutive squares of the same color in a row or column
    /// on the board. Optionally can forbid adjacency of tiles which would form
    /// additional pairs on the board if adjacent.
    ///
    /// # Arguments
    /// * `equivalence_groups` - A previously constructed set of tile 
    /// equivalence groups.
    /// * `no_border_pairs` - If true, forbids adjacency of tiles where extra 
    /// pairs would be formed on the board between the borders of adjacent 
    /// tiles.
    fn tile_adjacencies(equivalence_groups:&HashMap<u16, TileEquivalenceGroup>, no_border_pairs:bool ) -> HashMap<u16, Vec<HashSet<u16>>> {
        let mut adjacencies:HashMap<u16, Vec<HashSet<u16>>> = HashMap::new();
        for (_, &ref equivalence_group1) in equivalence_groups.iter() {
            for &tile1 in equivalence_group1.transforms.iter() {
                let mut adjacency:Vec<HashSet<u16>> = Vec::new();
                adjacency.push(HashSet::new());
                adjacency.push(HashSet::new());
                adjacency.push(HashSet::new());
                adjacency.push(HashSet::new());
                for (_, &ref equivalence_group2) in equivalence_groups.iter() {
                    // members of the same group cannot be adjacent
                    if equivalence_group1.id == equivalence_group2.id {
                        continue;
                    }
                    for &tile2 in equivalence_group2.transforms.iter() {
                        // Tile2 above
                        if TileStore::adjacency(false, tile2, equivalence_group2.pairs, tile1, equivalence_group1.pairs, no_border_pairs) {
                            adjacency[Dir::Up as usize].insert(tile2);
                        }
                        // Tile2 below 
                        if TileStore::adjacency(false, tile1, equivalence_group1.pairs, tile2, equivalence_group2.pairs, no_border_pairs) {
                            adjacency[Dir::Down as usize].insert(tile2);
                        }
                        // Tile2 left
                        if TileStore::adjacency(true, tile2, equivalence_group2.pairs, tile1, equivalence_group1.pairs, no_border_pairs) {
                            adjacency[Dir::Left as usize].insert(tile2);
                        }
                        // Tile2 right
                        if TileStore::adjacency(true, tile1, equivalence_group1.pairs, tile2, equivalence_group2.pairs, no_border_pairs) {
                            adjacency[Dir::Right as usize].insert(tile2);
                        }
                    }
                }
                adjacencies.insert(tile1, adjacency);
            }
        }
        return adjacencies;
    }

    /// Returns if two tiles, either horizontally or vertically, are permitted
    /// to be neighbors. Neighbors are permissible if their adjacency does not 
    /// produce more than two consecutive tiles of the same color at the tile 
    /// border. Optionally forbid tile adjacencies where any extra pairs are 
    /// formed at the tile border.
    /// 
    /// # Arguments
    ///
    /// * `horizontal` - Test for horizontal adjacency if true, vertical 
    /// adjacency if false. If horizontal, `tile1` is taken as left of `tile2`.
    /// If vertical, `tile1` is taken as above `tile2`.
    /// * `tile1` - integer describing the left or above tile.
    /// * `tile1_pairs` -  the number of internal pairs in `tile1` which has 
    /// been previously calculated.
    /// * `tile2` - integer describing the left or above tile.
    /// * `tile2_pairs` -  the number of internal pairs in `tile2` which has 
    /// been previously calculated.
    /// * `no_border_pairs` - If true, adjacency is forbidden if it would form 
    /// additional pairs on the board at the tile borders.
    fn adjacency(horizontal:bool, tile1:u16, tile1_pairs:usize, tile2:u16, tile2_pairs:usize, no_border_pairs:bool) -> bool {
        let dim = 4;
        let mut tile1_squares = TileEquivalenceGroup::bits_to_squares(tile1);
        let mut tile2_squares = TileEquivalenceGroup::bits_to_squares(tile2);
        if horizontal {
            tile1_squares = TileEquivalenceGroup::bits_to_squares(TileEquivalenceGroup::rotate(tile1));
            tile2_squares = TileEquivalenceGroup::bits_to_squares(TileEquivalenceGroup::rotate(tile2));
        }
        let mut horizontal_pairs = 0;
        let mut vertical_pairs = 0;
        for c in 0..dim {
            let mut col = Vec::new();
            for i in 0..dim {
                col.push(tile1_squares[i][c])
            }
            for i in 0..dim {
                col.push(tile2_squares[i][c])
            }
            for i in 1..2*dim-1 {
                if col[i-1] == col[i] && col[i + 1] == col[i] {
                    return false;
                }
            }
            for i in 1..2*dim {
                if col[i-1] == col[i] {
                    vertical_pairs += 1;
                }
            }
        }
        for r in 0..dim {
            for c in 1..dim {
                if tile1_squares[r][c-1] == tile1_squares[r][c] {
                    horizontal_pairs += 1;
                }
                if tile2_squares[r][c-1] == tile2_squares[r][c] {
                    horizontal_pairs += 1;
                }
            }
        }
        if no_border_pairs && horizontal_pairs + vertical_pairs != tile1_pairs + tile2_pairs {
            return false;
        }
        return true;
    }

    /// Constructs all valid 4x4 tiles and returns a set of their equivalence 
    /// groups. 
    fn all_equivalence_groups() -> Vec<TileEquivalenceGroup> {
        let mut tiles = Vec::new();
        let mut seen_tiles:HashSet<u16> = HashSet::new();
        for i in 0..=65535 {
            if TileEquivalenceGroup::bits_okay(i) && !seen_tiles.contains(&i){
                let tile = TileEquivalenceGroup::new(i);
                for transform in tile.transforms.iter() {
                    seen_tiles.insert(transform.clone());
                }
                tiles.push(tile);
            }
        }
        return tiles;
    }

    /// Returns the minimum possible number of pairs that can appear on the 
    /// board and the largest number of pairs in any equivalence group that 
    /// could be part of this lower bound. 
    ///
    /// # Arguments
    ///
    /// * `tiles_on_the_board` - the total number of tiles that fit on a board. 
    /// E.g. 16.
    ///
    /// # Panics
    ///
    /// The method will panic if `tiles_on_the_board` is greater then the 
    /// number of equivalence groups in the `TileStore`.

    pub fn minimum_pairs(self:&TileStore, tiles_on_the_board:usize) -> (usize,usize) {
        let mut pair_list:Vec<usize> = Vec::new();
        for (_, group) in self.equivalence_groups.iter() {
            pair_list.push(group.pairs);
        }
        pair_list.sort();
        if pair_list.len() < tiles_on_the_board {
            panic!("Too few equivalence groups ({}) to calculate the minimum possible sum of pairs across {} board positions.", pair_list.len(), tiles_on_the_board);
        }
        let mut pair_sum = 0;
        let mut largest_pairs = 0;
        for i in 0..tiles_on_the_board {
            pair_sum += pair_list[i];
            if i == tiles_on_the_board - 1 {
                largest_pairs = pair_list[i];
            }
        }
        return (pair_sum, largest_pairs);
    }
}

/// Stores a partially completed board state
pub struct BoardState {
    pub dim:usize,
    pub board:Vec<u16>,
    pub pairs:usize
}

impl BoardState {
    /// Returns a new empty board of dimensions `dim`x`dim` tiles.
    pub fn new(dim:usize) -> BoardState {
        let mut board:Vec<u16> = Vec::new();
        while board.len() < dim*dim {
            board.push(0);
        }
        return BoardState{dim:dim, board:board, pairs: 0};
    }

    /// Returns a copy the current board state.
    pub fn copy(self:&BoardState) -> BoardState {
        let mut board:Vec<u16> = Vec::new();
        for i in 0..self.board.len() {
            board.push(self.board[i])
        }
        return BoardState{dim:self.dim, board:board, pairs:self.pairs};
    }

    /// Print the number of pairs on the board and the completed board state to
    /// `stdout`.
    pub fn print(self:&BoardState) {
        println!("{}", self.pairs);
        for r in 0..self.dim*4 {
            let board_row = r/4;
            for c in 0..self.dim*4 {
                let board_col = c/4;
                if self.board[board_col + self.dim*board_row] == 0 {
                    print!(".")
                }
                else {
                    let tile_row = r % 4;
                    let tile_col = c % 4;
                    let bit = (self.board[board_col + self.dim*board_row] >> (4 - 1 - tile_col + 4*(4 - 1 - tile_row))) & 0x1;
                    print!("{}", bit);
                }
            }
            println!();
        }
    }

    /// Returns true if all positions on the board have been filled with a 
    /// tile.
    pub fn complete(self:&BoardState) -> bool {
        for row in 0..self.dim {
            for col in 0..self.dim {
                if self.board[col + self.dim*row] == 0 {
                    return false;
                }
            }
        }
        return true;
    }

    /// Returns the number of horizontal and vertical pairs of consecutive 
    /// squares of the same color currently on the board.
    fn pairs(self:&mut BoardState) -> usize {
        let mut horizontal_doubles = 0;
        let mut vertical_doubles = 0;
        for x in 0..self.dim*4 {
            let mut last_horizontal = 2;
            let mut last_vertical = 2;
            for y in 0..self.dim*4 {
                let horizontal_tile = self.board[y/4 + self.dim*(x/4)];
                if horizontal_tile == 0 {
                    last_horizontal = 2;
                }
                else {
                    let curr_horizontal = (horizontal_tile >> (4 - 1 - (y % 4) + 4*(4 - 1 - (x % 4)))) & 0x1;
                    if curr_horizontal== last_horizontal {
                        horizontal_doubles += 1;
                    }
                    last_horizontal = curr_horizontal;
                }
                let vertical_tile = self.board[x/4 + self.dim*(y/4)];
                if vertical_tile == 0 {
                    last_vertical = 2;
                }
                else {
                    let curr_vertical = (vertical_tile >> (4 - 1 - (x % 4) + 4*(4 - 1 - (y % 4)))) & 0x1;
                    if curr_vertical== last_vertical {
                        vertical_doubles += 1;
                    }
                    last_vertical = curr_vertical;
                }
            }
        }
        return horizontal_doubles + vertical_doubles;
    }

    /// Returns true if the given tile can be placed at the given position on 
    /// the board.
    ///
    /// # Arguments
    ///
    /// * `tile` - The tile to test for placement.
    /// * `row` - The row of the board to position the tile.
    /// * `col` - The column of the board to position the tile.
    /// * `store` - A previously built `TileStore`.
    /// 
    /// # Panics
    ///
    /// Panics if the provided row or column are out of the bounds of the 
    /// board.
    pub fn can_assign(self:&BoardState, tile:u16, row:usize, col:usize, store:&TileStore) -> bool {
        if row >= self.dim || col >= self.dim {
            panic!("Position {},{} out of bounds for board of dimension {}", row, col, self.dim);
        }
        if self.board[col + self.dim*row] != 0 {
            return false;
        }
        // check left
        if col > 0 {
            let left_tile = self.board[col - 1 + self.dim*row];
            if left_tile != 0 && !store.tile_adjacency[&tile][Dir::Left as usize].contains(&left_tile) {
                return false;
            }
        }
        // check right
        if col < self.dim - 1 {
            let right_tile = self.board[col + 1 + self.dim*row];
            if right_tile != 0 && !store.tile_adjacency[&tile][Dir::Right as usize].contains(&right_tile) {
                return false;
            }
        }
        // check up
        if row > 0 {
            let up_tile = self.board[col + self.dim*(row - 1)];
            if up_tile != 0 && !store.tile_adjacency[&tile][Dir::Up as usize].contains(&up_tile) {
                return false;
            }
        }
        // check down
        if row < self.dim - 1 {
            let down_tile = self.board[col + self.dim*(row + 1)];
            if down_tile != 0 && !store.tile_adjacency[&tile][Dir::Down as usize].contains(&down_tile) {
                return false;
            }
        }
        return true;
    }

    /// Place the given tile at the given position on the board.
    ///
    /// # Arguments
    /// * `tile` - The tile to place.
    /// * `row` - The row of the board to position the tile.
    /// * `col` - The column of the board to position the tile.
    /// * `store` - A previously built `TileStore`.
    ///
    /// # Panics
    /// 
    /// Panics if the given tile can't be legally assigned at the given 
    /// position.
    pub fn assign(self:&mut BoardState, tile:u16, row:usize, col:usize, store:&TileStore) {
        if!self.can_assign(tile, row, col, store) {
            self.print();
            panic!("Invalid assignment of tile {} at row {} col {}", tile, row, col);
        }
        self.board[col + self.dim*row] = tile;
        self.pairs = self.pairs();
    }
}

/// Runs a series of BFS searches in parallel for minimal board arrangements,
/// each with a different initial starting tile. Returns early if a board with
/// the minimum possible number of pairs is found.
/// 
/// # Arguments
/// 
/// * `bonus` - If false, will run a search for a minimal 4x4-tile board and
/// will run a search for a minimal 5x5-tile board restricted to equivalence 
/// groups with 4 members otherwise
/// * `threads` - Maximum number of threaded searches to run at one time.
pub fn solution(bonus:bool, threads:usize) -> BoardState {
    let board_dim:usize = if bonus {5} else {4};
    let mut best_result = BoardState::new(board_dim);
    // Set up a TileStore of tiles relevant to the challenge
    let store = TileStore::new(bonus);
    // Set up a thread-safe pointer to the store
    let store_arc = Arc::new(store);
    // Tuned parameter for pruning search branches that underperform the best
    // result at the same depth. The bonus search needs more slack.
    let pruning_cutoff = if bonus {4} else {0};
    // Determine the lower bound on possible number of pairs on the board based
    // on the the minimal number of pairs across the number of tile positions on
    // the board from the given tile store.
    let (minimum_possible_pairs, equivalance_group_max_pairs) = store_arc.minimum_pairs(board_dim*board_dim);

    let mut child_results:Vec<BoardState> = Vec::new();
    for _i in 0..threads {
        child_results.push(BoardState::new(board_dim));
    }
    let mut handles = Vec::new();
    let mut added = 0;
    let results_arc = Arc::new(Mutex::new(child_results));
    for &start_tile in store_arc.tile_equivalence_group.keys() {
        // Set up each worker thread for the batch run. 
        let results_arc_clone = Arc::clone(&results_arc);
        let store_arc_clone = store_arc.clone();
        let handle = thread::spawn( move || {
            let thread_result = bfs(&store_arc_clone, start_tile, board_dim, pruning_cutoff, minimum_possible_pairs, equivalance_group_max_pairs);
            let mut c_r = results_arc_clone.lock().unwrap();
            (*c_r)[added] = thread_result;
        });
        handles.push(handle);
        added += 1;
        if added == threads {
            // Execute the batch
            while handles.len() > 0 {
                let handle2 = handles.remove(0);
                handle2.join().unwrap();
            }
            let mut batchresult = results_arc.lock().unwrap();
            for i in 0..added {
                if best_result.pairs == 0 || best_result.pairs > batchresult[i].pairs {
                    best_result = batchresult[i].copy();
                }
                // Early return if we hit the minimum possible number of pairs
                if best_result.pairs == minimum_possible_pairs {
                    return best_result;
                }
                batchresult[i] = BoardState::new(board_dim);
            }
            added = 0;
        }        
    }
    // Run any remaining jobs
    if added > 0 {
        while handles.len() > 0 {
            let handle = handles.remove(0);
            handle.join().unwrap();
        }
        let mut batchresult = results_arc.lock().unwrap();
        for i in 0..added {
            if best_result.pairs == 0 || best_result.pairs > batchresult[i].pairs {
                best_result = batchresult[i].copy();
            }
            // Early return if we hit the minimum possible number of pairs
            if best_result.pairs == minimum_possible_pairs {
                return best_result;
            }
            batchresult[i] = BoardState::new(board_dim);
        }
    }
    return best_result;
}

/// Runs a single breadth first search for minimal board arrangements, given a 
/// starting tile to be placed at the top-left of the board. 
///
/// # Arguments
/// 
/// * `store` - A previously built `TileStore` with precomputed tile and 
/// adjacency lookups.
/// * `start_tile` - A tile to be placed at the top-left position on the board.
/// * `board_dim` - The dimensions of the board (in tiles rather than squares).
/// * `pruning_cutoff` - A parameter for pruning branches of the search that 
/// underperform the lowest pair score at the current depth of the search.
/// * `minimum_possible_pairs` - the previously calculated lower bound for 
/// number of pairs on the board.
/// * `equivalance_group_max_pairs` - Equivalence groups with internal pairs 
/// greater than this cutoff will not be considered for placement on the board
/// in the search.
pub fn bfs(store: &TileStore, start_tile:u16, board_dim:usize, pruning_cutoff:usize, minimum_possible_pairs:usize, equivalance_group_max_pairs:usize) -> BoardState {
    let mut best_count = 0;
    let mut best_state = BoardState::new(board_dim);
    let mut frontier:Vec<BoardState>;
    let mut frontier_next = Vec::new();
    let mut start_state = BoardState::new(board_dim);
    start_state.assign(start_tile, 0, 0, store);
    let mut best_in_step = 0;
    let mut best_in_last_step = start_state.pairs;
    frontier_next.push(start_state);
    
    while frontier_next.len() > 0 {
        frontier = frontier_next;
        frontier_next = Vec::new();
        while frontier.len() > 0 {
            let state = frontier.pop().unwrap();
            if state.complete() {
                // Early return if an example state with the minimum possible
                // pairs is found.
                if state.pairs == minimum_possible_pairs {
                    return state;
                }
                let doubles = state.pairs;
                if best_count == 0 || best_count > doubles {
                    best_state = state.copy();
                    best_count = doubles;
                }
            }
            if state.pairs > best_in_last_step + pruning_cutoff {
                continue;
            }

            let mut next_row = 0;
            let mut next_col = 0;
            for i in 0..state.board.len() {
                if state.board[i] == 0 {
                    next_row = i / state.dim;
                    next_col = i % state.dim;
                    break;
                }
            }
            let mut assigned_groups = HashSet::new();
            for i in 0..state.board.len() {
                if state.board[i] != 0 {
                    assigned_groups.insert(store.tile_equivalence_group[&state.board[i]]);
                }
            }
            let mut permitted_tiles = Vec::new();
            for &tile in store.tile_equivalence_group.keys() {
                if assigned_groups.contains(&store.tile_equivalence_group[&tile]) {
                    continue;
                }
                if !state.can_assign(tile, next_row, next_col, store) {
                    continue;
                }
                if store.equivalence_groups[&store.tile_equivalence_group[&tile]].pairs <= equivalance_group_max_pairs {
                    permitted_tiles.push(tile);
                }
            }
            for &tile in permitted_tiles.iter() {
                let mut next_state = state.copy();
                next_state.assign(tile, next_row, next_col, store);
                if best_in_step == 0 || next_state.pairs < best_in_step {
                    best_in_step = next_state.pairs;
                }
                if next_state.pairs > best_in_step + pruning_cutoff && best_in_step > 0 {
                    continue;
                }
                frontier_next.push(next_state);
            }
        }
        best_in_last_step = best_in_step;
        best_in_step = 0;
    }
    return best_state;
}

/// Tests of tile and adjacency functions
#[cfg(test)]
mod tests {
    use super::*;    
    #[test]
    fn test_reflection() {
        // 0010
        // 1101
        // 0100
        // 1011
        // should reflect horizontally to
        // 0100
        // 1011
        // 0010
        // 1101
        let source:u16 = 0b0010110101001011;
        let expected:u16 = 0b0100101100101101;
        let result = TileEquivalenceGroup::reflect(source);
        assert_eq!(expected, result);
    }
    #[test]
    fn test_rotation() {
        // 0010
        // 1101
        // 0100
        // 1011
        // should rotate 90 degrees to
        // 1010
        // 0110
        // 1001
        // 1010
        let source:u16 = 0b0010110101001011;
        let expected:u16 = 0b1010011010011010;
        let result = TileEquivalenceGroup::rotate(source);
        assert_eq!(expected, result);
    }
    #[test]
    fn test_commutative_transforms() {
        // 0010
        // 1101
        // 0100
        // 1011
        // with 3 clockwise 90 degree rotations and one reflection should result in
        // 0101
        // 0110
        // 1001
        // 0101
        // if the reflection occurs after an even number of rotations and 
        // 1010
        // 1001
        // 0110
        // 1010
        // if the reflection occurs after an odd number of rotations
        let source:u16 = 0b0010110101001011;
        let expected_even:u16 = 0b101011010010101;
        let expected_odd:u16 = 0b1010100101101010;
        let mut result1:u16 = source;
        result1 = TileEquivalenceGroup::rotate(result1);
        result1 = TileEquivalenceGroup::rotate(result1);
        result1 = TileEquivalenceGroup::reflect(result1);
        result1 = TileEquivalenceGroup::rotate(result1);
        assert_eq!(expected_even, result1);
        let mut result2:u16 = source;
        result2 = TileEquivalenceGroup::reflect(result2);
        result2 = TileEquivalenceGroup::rotate(result2);
        result2 = TileEquivalenceGroup::rotate(result2);
        result2 = TileEquivalenceGroup::rotate(result2);
        assert_eq!(expected_even, result2);
        let mut result3:u16 = source;
        result3 = TileEquivalenceGroup::rotate(result3);
        result3 = TileEquivalenceGroup::reflect(result3);
        result3 = TileEquivalenceGroup::rotate(result3);
        result3 = TileEquivalenceGroup::rotate(result3);
        assert_eq!(expected_odd, result3);
        let mut result4:u16 = source;
        result4 = TileEquivalenceGroup::rotate(result4);
        result4 = TileEquivalenceGroup::rotate(result4);
        result4 = TileEquivalenceGroup::rotate(result4);
        result4 = TileEquivalenceGroup::reflect(result4);
        assert_eq!(expected_odd, result4);
    }
    #[test]
    fn test_bad_tile() {
        // 0011
        // 1100
        // 0101
        // 1011
        // has an unequal number of ones and zeros and should fail
        let source_unequal_colors:u16 = 0b0011110001011011;
        assert_eq!(TileEquivalenceGroup::bits_okay(source_unequal_colors), false); 
        // 0011
        // 1001
        // 1001
        // 0101
        // has an equal number of ones and zeros, but 4 1s in a single column
        // and should fail
        let source_consecutive_1s:u16 = 0b0011100110010101;
        assert_eq!(TileEquivalenceGroup::bits_okay(source_consecutive_1s), false); 
        // 0011
        // 0011
        // 1100
        // 1100
        // is a valid tile
        let source_okay:u16 = 0b0011001111001100;
        assert_eq!(TileEquivalenceGroup::bits_okay(source_okay), true); 
    }
    #[test]
    fn test_equivalence_groups() {
        // 0011
        // 1100
        // 0010
        // 1101
        // should have an equivalence group with 8 members and 7 internal pairs
        let source8:u16 = 0b0011110000101101;
        let source8group = TileEquivalenceGroup::new(source8);
        assert_eq!(source8group.transforms.len(), 8);
        assert_eq!(source8group.pairs, 7);
        // 0011
        // 0100
        // 1011
        // 1010
        // should have an equivalence group with 4 members and 8 internal pairs
        let source4:u16 = 0b0011010010111010;
        let source4group = TileEquivalenceGroup::new(source4);
        assert_eq!(source4group.transforms.len(), 4);
        assert_eq!(source4group.pairs, 8);
        // 0011
        // 0101
        // 1010
        // 1100
        // should have an equivalence group with 2 members and 8 internal pairs
        let source2:u16 = 0b0011010110101100;
        let source2group = TileEquivalenceGroup::new(source2);
        assert_eq!(source2group.transforms.len(), 2);
        assert_eq!(source2group.pairs, 8);
        // 1001
        // 0110
        // 0110
        // 1001
        // should have an equivalence group with 1 member and 8 internal pairs
        let source1:u16 = 0b1001011001101001;
        let source1group = TileEquivalenceGroup::new(source1);
        assert_eq!(source1group.transforms.len(), 1);
        assert_eq!(source1group.pairs, 8);
    }
    #[test]
    fn test_adjacency() {
        // 0010
        // 1101
        // 0100
        // 1011
        // and
        // 1010
        // 0110
        // 1001
        // 1010
        // cannot be adjacent because they're members of the same equivalence group
        let test1_tile1:u16 = 0b0010110101001011;
        let test1_tile2:u16 = 0b1010011010011010;
        assert_eq!(TileStore::adjacency(false, test1_tile1, 6, test1_tile2, 6, false), false);
        // 1001
        // 0110
        // 0110
        // 1001
        // cannot be adjacent to the left of  
        // 0011
        // 0101
        // 1010
        // 1100
        // because three consecutive 1s will appear in the forth row
        let test2_tile1:u16 = 0b1001011001101001;
        let test2_tile2:u16 = 0b0011010110101100;
        assert_eq!(TileStore::adjacency(true, test2_tile1, 8, test2_tile2, 8, false), false);
        // 0011
        // 0100
        // 1011
        // 1010
        // cannot be adjacent above 
        // 0011
        // 1100
        // 0010
        // 1101
        // because 3 consecutive 0s will appear in the second column
        let test3_tile1:u16 = 0b0011010010111010;
        let test3_tile2:u16 = 0b0011110000101101;
        assert_eq!(TileStore::adjacency(false, test3_tile1, 8, test3_tile2, 7, false), false);
        // 0011
        // 1100
        // 0010
        // 1101
        // can be adjacent above
        // 0011
        // 0100
        // 1011
        // 1010
        let test4_tile1:u16 = 0b0011110000101101;
        let test4_tile2:u16 = 0b0011010010111010;
        assert_eq!(TileStore::adjacency(false, test4_tile1, 7, test4_tile2, 8, false), true);
        // 0011
        // 1100
        // 0010
        // 1101
        // cannot be adjacent above
        // 0011
        // 0100
        // 1011
        // 1010
        // if adjacencies that form extra pairs between the borders of tiles 
        // are forbidden
        let test5_tile1:u16 = 0b0011110000101101;
        let test5_tile2:u16 = 0b0011010010111010;
        assert_eq!(TileStore::adjacency(false, test5_tile1, 7, test5_tile2, 8, true), false);
    }
}
