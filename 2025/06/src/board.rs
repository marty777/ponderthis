use std::collections::{HashMap,HashSet};
use std::hash::Hash;
use std::fmt;
use gif::{Frame, Encoder, Repeat};
use std::fs::File;
use std::str::{FromStr};

const SPRITE_DELAY:u16 = 10;
const SPRITE_DIM:usize = 10;
// Color-indexed cell sprite for GIF export
// 0 - white
// 1 - blue
// 2 - blue with frog
// 3 - red
const SPRITES:[[u8;100];4] = [[
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        ],[
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        ],[
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 4, 4, 4, 2, 2, 2,
            0, 2, 2, 4, 4, 4, 4, 4, 2, 2,
            0, 2, 2, 4, 4, 4, 4, 4, 2, 2,
            0, 2, 2, 4, 4, 4, 4, 4, 2, 2,
            0, 2, 2, 2, 4, 4, 4, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            0, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        
        ],[
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            0, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            0, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            0, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            0, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            0, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            0, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            0, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            0, 3, 3, 3, 3, 3, 3, 3, 3, 3,
        ]];

#[derive(Debug, Copy, Clone, PartialEq)]
enum CellColor {
	White,
	Blue,
	Red
}

#[derive(Debug, Copy, Clone, Eq, Hash, PartialEq)]
pub enum Direction {
	A,
	B,
	C,
	D,
	E,
	F,
	G,
	H
}
impl fmt::Display for Direction {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
       write!(f, "{:?}", self)
    }
}

pub struct ParseDirectionError;
impl FromStr for Direction {
    type Err = ParseDirectionError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        return match s {
            "A" => Ok(Direction::A),
            "B" => Ok(Direction::B),
            "C" => Ok(Direction::C),
            "D" => Ok(Direction::D),
            "E" => Ok(Direction::E),
            "F" => Ok(Direction::F),
            "G" => Ok(Direction::G),
            "H" => Ok(Direction::H),
            &_ => Err(ParseDirectionError)
        }
    }
}

/// 2D coordinate vector
#[derive(Debug, Copy, Clone, Hash, Eq, PartialEq)]
pub struct Coord {
    pub x:isize,
    pub y:isize
}
impl Coord {
    pub fn new(x:isize, y:isize) -> Coord {
        return Coord{x:x, y:y};
    }
}
impl std::fmt::Display for Coord {
    fn fmt(&self, f: &mut  std::fmt::Formatter) ->  std::fmt::Result {
		write!(f,"({},{})", self.x, self.y)
    }
}
impl std::ops::Add<&Coord> for &Coord {
    type Output = Coord;
    fn add(self, rhs:&Coord) -> Coord {
        return Coord{x:self.x + rhs.x, y:self.y + rhs.y};
    }
}
impl std::ops::Sub<&Coord> for &Coord {
    type Output = Coord;
    fn sub(self, rhs:&Coord) -> Coord {
        return Coord{x:self.x - rhs.x, y:self.y - rhs.y};
    }
}

/// A sparse map of `CellColor`s assigned to cells, with unassigned cells 
/// defaulting to `CellColor::White`
#[derive(Debug, Clone)]
struct CellMap {
	pub dim:usize,
	pub map:HashMap<Coord, CellColor>,
}
impl CellMap {
    /// Return a new `CellMap` with the specified dimensions
    /// 
    /// * `dim` - height and width of the map
	pub fn new(dim:usize) -> CellMap {
		let map:HashMap<Coord, CellColor> = HashMap::new();
		return CellMap{dim:dim, map:map};
	}
    /// Test if a coordinate is within the bounds of the map
    /// 
    /// * `coord` - the coordinate to test
	pub fn in_bounds(&self,coord:&Coord) -> bool {
		return coord.x >= 0 && coord.x < self.dim as isize && coord.y >= 0 && coord.y < self.dim as isize;
	}
    /// Get the `CellColor`at the specified cell
    /// 
    /// * `coord` - the cell position to return the color of
	pub fn get(&self,coord:&Coord) -> Option<CellColor> {
		if !self.in_bounds(coord) {
			return None;
		}
		else {
			if self.map.contains_key(coord) {
				return Some(*self.map.get(coord).unwrap());
			}
			else {
				return Some(CellColor::White);
			}
		}
	}
	/// Set the `CellColor`at the specified cell
    /// 
    /// * `coord` - the cell position to set the color of
	/// * `color` - the `CellColor` to set
    pub fn set(&mut self, coord:&Coord, color:CellColor) -> Result<(), String>{
		if !self.in_bounds(coord) {
			return Err(format!("Attempt to set color {:?} at position {} in cellmap with dim {}", color, coord, self.dim));
		}
		if !self.map.contains_key(coord) {
			self.map.insert(*coord, color);
		}
		else {
			*self.map.get_mut(coord).unwrap() = color;
		}
        return Ok(());
	}
}

/// Square subregion of a board intended to be fully colored as a segment in a
/// solution path
#[derive(Debug)]
pub struct Tile {
    pub top_left:Coord,
    pub dim: usize,
    pub next_dir:Option<Direction>
}
impl Tile {
    /// Return a new `Tile` with the specified position, dimension and optional 
    /// direction of the next tile to traverse
    /// 
    /// * `top_left` - position of the top left of the tile
    /// * `dim` - height and width of the tile
    /// * `next_dir` - optional direction of the next tile for the frog to traverse
    pub fn new(top_left:Coord, dim:usize, next_dir:Option<Direction>) -> Tile {
        return Tile{top_left:top_left, dim:dim, next_dir:next_dir};
    }
    /// Returns true if the given `Coord` is within the bounds of the tile
    /// 
    /// * `coord` - the `Coord` to test
    pub fn in_bounds(&self, coord:&Coord) -> bool {
        return !(coord.x < self.top_left.x || coord.y < self.top_left.y || coord.x >=  self.top_left.x + self.dim as isize || coord.y >= self.top_left.y + self.dim as isize);
    }    
    /// Return a sequence of tiles to color the entire board
    /// 
    /// * `board` - the `Board` to color
    /// * `tile_dim` - the height and width of each tile to cover the board
    pub fn plan_tiles(board:&Board, tile_dim:usize) -> Result<Vec<Tile>, String> {
        if board.dim % tile_dim != 0 {
            return Err(format!("Board of dim {} cannot be tiled by tiles of dim {}", board.dim, tile_dim));
        }
        let dirmap:HashMap<Coord,Direction> = HashMap::from([(Coord::new(1,0), Direction::A), (Coord::new(0,1), Direction::C), (Coord::new(-1,0), Direction::E), (Coord::new(0,-1), Direction::G),]);
        let tile_dim_i = tile_dim as isize;
        let mut successes:HashSet<Vec<Coord>> = HashSet::new();
        let mut next_candidates:HashSet<Vec<Coord>> = HashSet::new();
        next_candidates.insert(vec![Coord::new(board.start.x / tile_dim_i, board.start.y / tile_dim_i)]);
        while next_candidates.len() > 0 {
            let candidates = next_candidates;
            next_candidates = HashSet::new();
            for candidate in candidates.into_iter() {
                if candidate.len() == (board.dim / tile_dim) * (board.dim / tile_dim) {
                    successes.insert(candidate);
                    continue;
                }
                for delta in dirmap.keys() {
                    let next_coord = candidate.last().unwrap() + delta;
                    if candidate.contains(&next_coord) {
                        continue;
                    }
                    if next_coord.x < 0 || next_coord.y < 0 || next_coord.x >= (board.dim / tile_dim) as isize || next_coord.y >= (board.dim / tile_dim) as isize {
                        continue;
                    }
                    let mut next_candidate = candidate.clone();
                    next_candidate.push(next_coord);
                    next_candidates.insert(next_candidate);
                }
            }
        }
        // return a member of the successes set as a tile plan
        for success in successes.iter() {
            let mut result:Vec<Tile> = Vec::new();
            for i in 0..success.len() {
                if i < success.len() - 1 {
                    let dir = dirmap.get(&(&success[i + 1] - &success[i])).unwrap();
                    let tile = Tile::new(Coord::new(success[i].x * tile_dim_i, success[i].y * tile_dim_i), tile_dim, Some(*dir));
                    result.push(tile);
                }
                else {
                    let tile = Tile::new(Coord::new(success[i].x * tile_dim_i, success[i].y * tile_dim_i), tile_dim, None);
                    result.push(tile);
                }
            }
            return Ok(result);
        }
        return Err(format!("Unable to find a plan to tile board with dim {} and start position {} with tiles of size {}", board.dim, board.start, tile_dim));
    }
    /// Return the board coloring and position after executing the given moves
    /// 
    /// Takes a starting board coloring and frog position, and list of moves, 
    /// applies each move and returns the resulting board coloring and frog 
    /// position if the moves are valid.
    /// 
    /// * `board` - the `Board` to color
    /// * `board_cells` - a `CellMap` giving the starting coloring of the board
    /// * `start_pos` - the starting `Coord` of the frog
    /// * `moves` - A list of valid moves that do not have the frog leave the cell
    fn eval_moves(&self, board:&Board, board_cells:&CellMap, start_pos:&Coord, moves:&Vec<Direction>) -> Result<(CellMap, Coord), String> {
        let mut map = (*board_cells).clone();
        let mut pos = *start_pos;
        for i in 0..moves.len() {
            let next_pos = &pos + &board.dirs.get(&moves[i]).unwrap();
            let next_next_pos = &next_pos + &board.dirs.get(&moves[i]).unwrap();
            if !board.in_bounds(&next_pos) {
                return Err(format!("Invalid move {} at index {} from position {} moves the frog off the board", moves[i], i, pos));
            }
            if map.get(&next_pos).unwrap() != CellColor::White {
                return Err(format!("Invalid move {} at index {} from position {} moves the frog to a non-white cell", moves[i], i, pos));
            }
            if board.in_bounds(&next_next_pos) && map.get(&next_next_pos).unwrap() == CellColor::Blue {
                return Err(format!("Invalid move {} at index {} from position {} moves the frog to a cell where the next cell is blue", moves[i], i, pos));
            }
            map.set(&next_pos, CellColor::Blue).unwrap();
            if board.in_bounds(&next_next_pos) {
                map.set(&next_next_pos, CellColor::Red).unwrap();
            }
            pos = next_pos;
        }
        return Ok((map, pos));
    }

    /// Return all distinct subpaths given a start position and board coloring 
    /// that fully color the tile and end with the frog on the next required 
    /// tile border if specified
    /// 
    /// * `board` - the `Board` to color
    /// * `board_cells` - a `CellMap` giving the starting coloring of the board
    /// * `start_pos` - the starting `Coord` of the frog
    fn moves(&self, board:&Board, board_cells:&CellMap, start_pos:Coord) -> Vec<Vec<Direction>> {
        // Determine acceptable end positions for the frog once the tile is 
		// fully colored based on self.next_dir
		let mut end_positions:HashSet<Coord> = HashSet::new();
        match self.next_dir {
            Some(dir) => {
                match dir {
                    Direction::A => {
                        for y in 0..self.dim {
                            end_positions.insert(Coord::new(self.top_left.x + self.dim as isize - 1, self.top_left.y + y as isize));
                        }
                    },
                    Direction::C => {
                        for x in 0..self.dim {
                            end_positions.insert(Coord::new(self.top_left.x + x as isize, self.top_left.y + self.dim as isize - 1));
                        }
                    },
                    Direction::E => {
                        for y in 0..self.dim {
                            end_positions.insert(Coord::new(self.top_left.x, self.top_left.y + y as isize));
                        }
                    },
                    Direction::G => {
                        for x in 0..self.dim {
                            end_positions.insert(Coord::new(self.top_left.x + x as isize, self.top_left.y ));
                        }
                    },
                    _ => panic!("Unexpected next direction {} in tile", dir)
                }
            }
            None => {
                // if no end direction specified, any end position within the 
                // tile is acceptable
                for y in 0..self.dim {
                    for x in 0..self.dim {
                        end_positions.insert(Coord::new(self.top_left.x + x as isize, self.top_left.y + y as isize));
                    }
                }
            }
        }
        let mut successes:HashSet<Vec<Direction>> = HashSet::new();
        let mut next_candidates:HashSet<Vec<Direction>> = HashSet::new();
        if self.in_bounds(&start_pos) {
            next_candidates.insert(Vec::new());
        }
        else {
            for dir in board.dirs.keys() {
                let next_coord = &start_pos + board.dirs.get(dir).unwrap();
                if self.in_bounds(&next_coord) {
                    next_candidates.insert(vec![*dir]);
                }
            }
        }
        while next_candidates.len() > 0 {
            let candidates = next_candidates;
            next_candidates = HashSet::new();
            for candidate in candidates.into_iter() {
                match self.eval_moves(board, board_cells, &start_pos, &candidate) {
                    Ok((map, pos)) => {
                        let mut colored_cells = 0;
                        for y in 0..self.dim {
                            for x in 0..self.dim {
                                let coord = Coord::new(self.top_left.x + x as isize, self.top_left.y + y as isize);
                                if map.get(&coord).unwrap() != CellColor::White {
                                    colored_cells += 1;
                                }
                            }
                        }
                        if colored_cells == self.dim * self.dim && end_positions.contains(&pos) {
                            successes.insert(candidate);
                            continue;
                        }
                        for dir in board.dirs.keys() {
                            let next_pos = &pos + &board.dirs.get(dir).unwrap();
                            let next_next_pos = &next_pos + &board.dirs.get(dir).unwrap();
                            if !self.in_bounds(&next_pos) || map.get(&next_pos).unwrap() != CellColor::White {
                                continue;
                            }
                            if map.in_bounds(&next_next_pos) && map.get(&next_next_pos).unwrap() == CellColor::Blue {
                                continue;
                            }
                            let mut next_candidate = candidate.clone();
                            next_candidate.push(*dir);
                            next_candidates.insert(next_candidate);
                        }
                    }
                    Err(_) => continue
                }
            }
        }
        return successes.into_iter().collect();
    }
}

/// Represents a board for the game
pub struct Board {
    pub dim:usize,
	pub start:Coord,
    pub dirs:HashMap<Direction, Coord>,
}
impl Board {
    /// Return a new board with the specified dimension and frog start coordinate
    /// 
    /// * `dim` - height and width of the board
    /// * `start` - start coordinate of the frog
    pub fn new(dim:usize, start:Coord) -> Board {
        let dirs:HashMap<Direction, Coord> = HashMap::from(
		[(Direction::A, Coord::new(1,0)), 
		(Direction::B, Coord::new(1,1)), 
		(Direction::C, Coord::new(0,1)), 
		(Direction::D, Coord::new(-1,1)), 
		(Direction::E, Coord::new(-1, 0)), 
		(Direction::F, Coord::new(-1, -1)), 
		(Direction::G, Coord::new(0, -1)), 
		(Direction::H, Coord::new(1, -1))]);
        return Board{dim:dim, start:start, dirs:dirs};
    }
    /// Returns true if the given `Coord` is within the bounds of the board
    /// 
    /// * `coord` - the `Coord` to test
	pub fn in_bounds(&self,coord:&Coord) -> bool {
		return coord.x >= 0 && coord.x < self.dim as isize && coord.y >= 0 && coord.y < self.dim as isize;
	}
    /// Returns true if the given moves are a valid path to color the entire
    /// board
    /// 
    /// * `moves` - the list of moves in the frog's path
	pub fn validate(&self, moves:&Vec<Direction>) -> Result<String, String> {
		let mut move_strings:Vec<String> = Vec::new();
		
		let mut pos:Coord = self.start;
		let mut cells:CellMap = CellMap::new(self.dim);
		cells.set(&self.start, CellColor::Blue).unwrap();
		
		for i in 0..moves.len() {
			let next_pos = &pos + &self.dirs.get(&moves[i]).unwrap();
			let next_next_pos = &next_pos + &self.dirs.get(&moves[i]).unwrap();
			if cells.get(&next_pos).unwrap() != CellColor::White {
				return Err(format!("Frog tries to move to position {:?} at index {}, move {:?}: Destination cell is non-white", next_pos, i, moves[i]));
			}
			if cells.in_bounds(&next_next_pos) && cells.get(&next_next_pos).unwrap() == CellColor::Blue {
				return Err(format!("Frog tries to move to position {:?} at index {}, move {:?}: Next cell {:?} is blue", next_pos, i, moves[i], next_next_pos));
			}
			cells.set(&next_pos, CellColor::Blue).unwrap();
			if cells.in_bounds(&next_next_pos) {
				cells.set(&next_next_pos, CellColor::Red).unwrap();
			}
			pos = next_pos;
			move_strings.push(format!("{:?}", moves[i]));
			
		}
		let mut colored_cell_count = 0;
		for y in 0..self.dim {
			for x in 0..self.dim {
				let coord = Coord::new(x as isize, y as isize);
				if cells.get(&coord).unwrap() != CellColor::White {
					colored_cell_count += 1;
				}
			}
		}
		if colored_cell_count == self.dim * self.dim {
			return Ok(move_strings.join(""));
		}
		return Err(format!("Board is not fully colored ({}/{} cells colored)", colored_cell_count, self.dim * self.dim));
	}

    /// Recursive method to produce a list of moves using a repeating pattern
    /// that forms a spiral which fully colors the main board
    /// 
    /// * `region_dim` - Dimensions of the remaining uncolored region on the board
    pub fn external_spiral(&self, region_dim:usize) -> Vec<Direction> {
		if region_dim < 6 {
			return vec![Direction::A, Direction::D, Direction::A];
		}
		let mut moves:Vec<Direction> = Vec::new();
		// left border moving down
		for _ in 0..region_dim - 2 {
            moves.append(&mut vec![Direction::A, Direction::D]);   
		}
		// bottom left corner
        moves.append(&mut vec![Direction::B, Direction::E, Direction::H]);
		// bottom border moving right
		for _ in 2..region_dim - 2 {
            moves.append(&mut vec![Direction::B, Direction::G]);
		}
		// bottom right corner
        moves.append(&mut vec![Direction::B, Direction::H, Direction::C, Direction::F]);
		// right border moving up
		for _ in 2..region_dim - 2 {
            moves.append(&mut vec![Direction::H, Direction::E]);
		}
		// top-right corner
        moves.append(&mut vec![Direction::H, Direction::F, Direction::A, Direction::D]);
		// top border moving left
		for _ in 2..region_dim - 5 {
            moves.append(&mut vec![Direction::F, Direction::C]);
		}
		// top-right internal corner
		moves.append(&mut vec![Direction::F, Direction::D, Direction::G, Direction::B, Direction::D, Direction::A, Direction::D]);
		let mut next = self.external_spiral(region_dim - 6);
		moves.append(&mut next);
		return moves;
	}	
	
    /// Solve the main challenge, optionally using a heuristic pattern
    /// 
    /// If a pattern is used, the board will be fully colored using a sequence 
    /// of heuristic moves. If not, a strategy of fully coloring connected 
    /// regions of the board until a path that colors the entire board will be
    /// used.
    /// 
    /// * `use_pattern` - use the pattern strategy for coloring the board
    pub fn solve_main(&self, use_pattern:bool) -> Result<Vec<Direction>, String> {
        if self.dim != 20 || self.start != Coord::new(0,0) {
            return Err("Method can only be used for a 20x20 board with start position (0,0)".to_string());
        }
		if use_pattern {
            return Ok(self.external_spiral(self.dim));
        }
        else {
            return self.tiled_solution();
        }
    }
    /// Solve the bonus challenge, optionally using a heuristic pattern
    /// 
    /// If a pattern is used, the interior of the board will be colored using
    /// a semi-arbitrary path while the exterior will be colored using a 
    /// repeating pattern. If not, a strategy of fully coloring connected 
    /// regions of the board until a path that colors the entire board will be
    /// used.
    /// 
    /// * `use_pattern` - use the pattern strategy for coloring the board
	pub fn solve_bonus(&self, use_pattern:bool) -> Result<Vec<Direction>,String> {
		if self.dim != 10 || self.start != Coord::new(4,4) {
            return Err("Method can only be used for a 10x10 board with start position (4,4)".to_string());
        }
        if use_pattern {
            // find a path to color the interior 4x4 region of the board that 
			// ends at (3,5)
            let interior_destination = Coord::new(3,5);
            let tile = Tile::new(Coord::new(3,3), 4, None);
            let mut start_cells:CellMap = CellMap::new(self.dim);
            start_cells.set(&self.start, CellColor::Blue).unwrap();
            let candidates = tile.moves(&self, &start_cells, self.start);
            let mut moves:Vec<Direction> = Vec::new();
            for i in 0..candidates.len() {
                let (_, frog_pos) = tile.eval_moves(self, &start_cells, &self.start, &candidates[i]).unwrap();
                if frog_pos == interior_destination {
                    moves = candidates[i].clone();
                    break;
                }
            }
            if moves.len() == 0 {
                return Err("Unable to find a path to color the interior of the bonus board".to_string());
            }
            // Leave the interior from (2,5)
            moves.append(&mut vec![Direction::D, Direction::G]);
            // Corner
            moves.append(&mut vec![Direction::D, Direction::F, Direction::C, Direction::H]);
            // Move up along the left edge of the board
            for _ in 5..self.dim - 2 {
                moves.append(&mut vec![Direction::F, Direction::A]);
            }
            // Corner
            moves.append(&mut vec![Direction::F, Direction::H, Direction::E, Direction::B]);            
            // Move right along the top edge of the board
            for _ in 2..self.dim - 2 {
                moves.append(&mut vec![Direction::H, Direction::C]);
            }
            // Corner
            moves.append(&mut vec![Direction::H, Direction::B, Direction::G, Direction::D]); 
            // Move down along the right edge of the board
            for _ in 2..self.dim - 2 {
                moves.append(&mut vec![Direction::B, Direction::E]);
            }
            // Corner
            moves.append(&mut vec![Direction::B, Direction::D, Direction::A, Direction::F]);
            // Move left until complete
            for _ in 2..self.dim {
                moves.append(&mut vec![Direction::D, Direction::G]);
            }
            return Ok(moves);
        }
		else {
            return self.tiled_solution();
        }
		
	}

    /// Return a `Frame` of the board state for export to an animated GIF
    /// 
    /// * `cells` - A `CellMap` giving the current coloring of the board
    /// * `frog_pos` - A `Coord` giving the current position of the frog
    fn state_frame(&self, cells:&CellMap, frog_pos:&Coord) -> Frame {        
        let mut indexed_pixels:Vec<u8> = vec![0; (SPRITE_DIM * self.dim + 1) * (SPRITE_DIM * self.dim + 1)];
        for y in 0..self.dim {
            for x in 0..self.dim {
                let cell_pos = Coord::new(x as isize,y as isize);
                let cell_color = cells.get(&cell_pos);
                let cell_sprite_index:usize;
                if cell_pos == *frog_pos {
                    cell_sprite_index = 2;
                }
                else {
                    cell_sprite_index = match cell_color.unwrap() {
                        CellColor::White => 0,
                        CellColor::Blue => 1,
                        CellColor::Red => 3
                    }
                }
                let x_offset = x * SPRITE_DIM;
                let y_offset = y * SPRITE_DIM;
                for x1 in 0..SPRITE_DIM {
                    for y1 in 0..SPRITE_DIM {
                        let x_prime = x1 + x_offset;
                        let y_prime = y1 + y_offset;
                        let frame_index = y_prime * (self.dim * SPRITE_DIM + 1) + x_prime;
                        let color_map_index = SPRITES[cell_sprite_index][y1 * SPRITE_DIM + x1];
                        indexed_pixels[frame_index] = color_map_index;
                    }
                }
            }
        }
        let mut frame = Frame::from_indexed_pixels((SPRITE_DIM * self.dim + 1) as u16, (SPRITE_DIM * self.dim + 1) as u16, indexed_pixels, None);
        frame.delay = SPRITE_DELAY;
        return frame;
    }

    /// Write an animated GIF of the given move sequence to the given path
    /// 
    /// * `moves` - The sequence of moves to render
    /// * `path` - Destination file path for the GIF
    /// * `start` - If not None, no board states prior to the given start move index will be exported
    /// * `end` - If not None, no board states after to the given end move index will be exported
    /// * `verbose` - If true, prints a confirmation when the GIF has been exported
    pub fn to_gif(&self, moves:&Vec<Direction>, path:&str, start:Option<usize>, end:Option<usize>, verbose:bool) {
        // color map 
        // 0 - black
        // 1 - white
        // 2 - blue 
        // 3 - red
        // 4 - green
        let color_map = &[0x00, 0x00, 0x00, 0xff, 0xff, 0xff, 0x33, 0x33, 0xff, 0xff, 0x33, 0x33, 0x33, 0xff, 0x33];
        let image_dim = ((SPRITE_DIM * self.dim) + 1) as u16; // plus one for right/bottom border
        
        let mut image = File::create(path).unwrap();
        let mut encoder:Encoder<&mut File>; 
        match Encoder::new(&mut image, image_dim, image_dim, color_map) {
            Ok(enc) => encoder = enc,
            Err(err) => {
                println!("Unable to write animated gif to {}: {}", path, err);
                return;
            }
        }
        match encoder.set_repeat(Repeat::Infinite) {
            Err(err) => {
                println!("Unable to write animated gif to {}: {}", path, err);
                return;
            },
            _ => {}
        }

        let mut frog_pos = self.start;
        let mut cell_states: CellMap = CellMap::new(self.dim);
        cell_states.set(&self.start, CellColor::Blue).unwrap();
		
		let start_frame:usize;
		let end_frame:usize;
		match start {
			Some(i) => {
				if i < moves.len() {
					start_frame = i;
				}
				else {
					start_frame = 0;
				}
			},
			None => start_frame = 0
			
		}
		match end {
			Some(i) => {
				if i < moves.len() {
					end_frame = i;
				}
				else {
					end_frame = moves.len() - 1;
				}
			},
			None => end_frame = moves.len() - 1
		}
        if end_frame <= start_frame {
            println!("Unable to write animated gif to {}: End frame {} is less than start frame {} ", path, end_frame, start_frame);
            return;
        }
		
        // Write frame of initial board state unless omitted by `start` argument
        if start_frame == 0 {
			// initial board state
			let start_frame = self.state_frame(&cell_states, &frog_pos);
			match encoder.write_frame(&start_frame) {
                Err(err) => {
                    println!("Unable to write animated gif to {}: {}", path, err);
                    return;
                },
                _ => {}
            }
		}
        // Write frames for each move
        for i in 0..moves.len() {
            let next_pos = &frog_pos + self.dirs.get(&moves[i]).unwrap();
            let next_next_pos = &next_pos + self.dirs.get(&moves[i]).unwrap();
            cell_states.set(&next_pos, CellColor::Blue).unwrap();
            if self.in_bounds(&next_next_pos) {
                cell_states.set(&next_next_pos, CellColor::Red).unwrap();
            }
            frog_pos = next_pos;
			if i >= start_frame && i <= end_frame {
				let frame = self.state_frame(&cell_states, &frog_pos);
				match encoder.write_frame(&frame) {
                    Err(err) => {
                        println!("Unable to write animated gif to {}: {}", path, err);
                        return;
                    },
                    _ => {}
                }
			}
        }
        if verbose {
            println!("Saved animated GIF to {}", path);
        }
    }
	
    /// Attempt to fully color the board using a tiling strategy
    pub fn tiled_solution(&self) -> Result<Vec<Direction>, String> {
        let tile_dim = 5;
        let per_tile_candidate_limit = 500;
        
        if self.dim % tile_dim != 0 {
            return Err(format!("Tiled solutions are restricted to board where the dimension is a multiple of 5 ({} provided)", self.dim));
        }
        // build a tile plan
        let plan:Vec<Tile>;
        match Tile::plan_tiles(self, tile_dim) {
            Ok(tiles) => plan = tiles,
            Err(err) => return Err(err)
        }
        if plan.len() < 1 {
            return Err("Tile plan contains no tiles".to_string());
        }
        
        let mut next_candidates:HashSet<Vec<Direction>> = HashSet::new();
        let mut start_cells = CellMap::new(self.dim);
        start_cells.set(&self.start, CellColor::Blue).unwrap();
        for path in plan[0].moves(self, &start_cells, self.start) {
            next_candidates.insert(path);
        }
        for tile_index in 1..plan.len() {
            let candidates = next_candidates;
            next_candidates = HashSet::new();
            let mut candidate_count = 0;
            for candidate in candidates.into_iter() {
                let (candidate_cells, candidate_pos) = plan[tile_index].eval_moves(self, &start_cells, &self.start, &candidate).unwrap();
                let tile_candidates = plan[tile_index].moves(self, &candidate_cells, candidate_pos);
                for mut tile_candidate in tile_candidates.into_iter() {
                    let mut next_candidate = candidate.clone();
                    next_candidate.append(&mut tile_candidate);
                    next_candidates.insert(next_candidate);
                    candidate_count += 1;
                    if candidate_count > per_tile_candidate_limit {
                        break;
                    }
                }
                if candidate_count > per_tile_candidate_limit {
                    break;
                }
            }
        }
        // return one candidate path
        for candidate in next_candidates.into_iter() {
            return Ok(candidate);
        }
        return Err("Could not find a solution path".to_string());
    }
}
