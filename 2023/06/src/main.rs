pub mod cheese_maze;
use cheese_maze::{Maze,MouseState};

use clap::{Arg, ArgAction, Command, value_parser};
use std::time::{Instant};
use std::collections::HashMap;
use rand::{random};

fn main() {

	let command = Command::new("jun2023").max_term_width(80)
					.about("Solver for the Ponder This June 2023 challenge.")
					.arg(Arg::new("k").help("Set the dimensions of the maze").short('k').default_value("30").value_parser(value_parser!(usize)))
					.arg(Arg::new("n").help("Set the number of time steps to traverse the maze").short('n').default_value("100").value_parser(value_parser!(usize)))
					.arg(Arg::new("bonus").help("Traverse the maze using the bonus challenge rules").short('b').long("bonus").action(ArgAction::SetTrue));
	let args = command.get_matches();
	let mut bonus = false;
	let k = args.get_one::<usize>("k").unwrap();
	let n = args.get_one::<usize>("n").unwrap();
	if args.get_flag("bonus") {
		bonus = true;
	}
	
	println!("\n######## Ponder This Challenge - June 2023 ########\n");
	let start_instant = Instant::now();
	let result = challenge(*k,*n,bonus);
	match result {
		Some(path) => {
			println!("The maximum amount of cheese obtainable is: {}", path.num_cheeses());
			println!("One path that can collect the maximum amount of cheese is:\n{}",  path.path_string());
		},
		None => println!("An error occurred an the maximum amount of cheese could not be found"),
	}
	
	let duration = start_instant.elapsed();
	println!("Total execution time: {:?}", duration);
	
}

/// Returns a randomly re-ordered copy of the provided vector of chars
fn shuffle(options:&Vec<char>) -> Vec<char> {
	let mut result = Vec::new();
	let mut options_copy = options.clone();
	while options_copy.len() > 0 {
		let index:usize = random::<usize>() % options_copy.len(); 
		let option = options_copy.remove(index);
		result.push(option);
	}
	return result;
}

/// Updates the one-path-per-cell queue with a new MouseState at the specified cell index
fn update_queue(queue:&mut HashMap<usize,MouseState>, mouse_state:MouseState, index:usize) -> bool {
	if !queue.contains_key(&index) {
		queue.insert(index, mouse_state);
		return true;
	}
	else if (*queue).get(&index).unwrap().num_cheeses() < mouse_state.num_cheeses() {
		*queue.get_mut(&index).unwrap() = mouse_state;
		return true;
	}
	return false;
}

/// Finds a finished MouseState that collects the maximum possible amount of cheese in the maze using 
/// an adapted version of Dijkstra's algorithm. Returns None on error.
/// # Arguments
/// * `k` - The dimensions of the maze
/// * `n` - The maximum number of timesteps to explore the maze
/// * `bonus` - Pass true if exploring the maze using the bonus rules
fn challenge(k:usize,n:usize,bonus:bool) -> Option<MouseState> {
	println!("Finding path to maximum cheese for k = {} and n = {} with {} challenge rules", k, n, if bonus {"bonus"} else {"main"} );
	// randomly order the available moves to add some extra non-deterministic behavior to best paths found
	let options = shuffle(&vec!['R','L','U','D','F','B','W']);
	let maze = Maze::new(k,n);
	let mut queue:HashMap<usize, MouseState>;
	let mut queue_next:HashMap<usize, MouseState> = HashMap::new();
	let mut best_cheeses = 0;
	// Add the initial position to the queue
	let mut start_state = MouseState::new();
	// If cheese is available at the initial position, add it to the mouse state 
	if maze.cheese_at_coords4(1,1,1,1) {
		start_state.add_cheese(maze.coords3_to_index(1,1,1), bonus);
		best_cheeses += 1;
	}
	queue_next.insert(maze.coords3_to_index(start_state.x, start_state.y, start_state.z), start_state);
 
	let mut steps = 0;
	while steps < n - 1 {
		steps += 1;
		queue = queue_next;
		queue_next = HashMap::new();
		println!("At step {} with {} path{} in queue and most cheese obtained {}", steps, queue.len(), if queue.len() == 1 {""} else {"s"}, best_cheeses);
		for cell_index in queue.keys() {
			let mouse_state = queue.get(cell_index).unwrap();
			for i in 0..options.len() {
				let mut delta_x:isize = 0;
				let mut delta_y:isize = 0;
				let mut delta_z:isize = 0;
				match options[i] {
					// left
					'L' => {
						if !(mouse_state.x > 1 && bonus) {
							continue;
						}
						else {
							delta_x = -1;
						}
					}
					// right
					'R' => {
						if !(mouse_state.x < maze.k) {
							continue;
						}
						else {
							delta_x = 1;
						}
					}
					// down
					'D' => {
						if !(mouse_state.y > 1 && bonus) {
							continue;
						}
						else {
							delta_y = -1;
						}
					}
					// up
					'U' => {
						if !(mouse_state.y < maze.k) {
							continue;
						}
						else {
							delta_y = 1;
						}
					}
					// backward
					'B' => {
						if !(mouse_state.z > 1 && bonus) {
							continue;
						}
						else {
							delta_z = -1;
						}
					}
					// forward
					'F' => {
						if !(mouse_state.z < maze.k) {
							continue;
						}
						else {
							delta_z = 1;
						}
					}
					// wait
					_ => ()
				}
				let mut next_state = mouse_state.copy();
				next_state.path.push(options[i].clone());
				next_state.x = next_state.x.wrapping_add_signed(delta_x);
				next_state.y = next_state.y.wrapping_add_signed(delta_y);
				next_state.z = next_state.z.wrapping_add_signed(delta_z);
				next_state.t += 1;
				if maze.cheese_at_coords4(next_state.x, next_state.y, next_state.z, next_state.t) {
					next_state.add_cheese(maze.coords3_to_index(next_state.x, next_state.y, next_state.z), bonus);
				}
				if next_state.num_cheeses() > best_cheeses {
					best_cheeses = next_state.num_cheeses();
				}
				let next_cell_index = maze.coords3_to_index(next_state.x, next_state.y, next_state.z);
				update_queue(&mut queue_next, next_state, next_cell_index);
			}
		}
	}
	let mut best:MouseState = MouseState::new();
	best_cheeses = 0;
	for index in queue_next.keys() {
		if queue_next.get(index).unwrap().num_cheeses() > best_cheeses {
			best_cheeses = queue_next.get(index).unwrap().num_cheeses();
			best = queue_next.get(index).unwrap().copy();
		}
	}
	let test_cheeses = maze.mouse_path(best.path_string(), bonus);
	if test_cheeses != best.num_cheeses() {
		println!("The best path found has failed validation. The expected amount of cheese obtained {} did not match the validation result {}", best.num_cheeses(), test_cheeses);
		return None;
	}
	return Some(best);
}


#[cfg(test)]
mod tests {
	use super::*;
	
	#[test]
	fn test_cheese_phases() {
		let phases = Maze::cheese_phases(3,5,1,20);
		assert_eq!(phases, vec![1,3,4,5,6,7,8,9,10,12]);
	}
	#[test]
	fn test_sample_maze() {
		let bonus = false;
		let best = challenge(5,20,bonus).unwrap();
		assert_eq!(best.num_cheeses(), 10);
	}
	#[test]
	fn test_sample_bonus_maze() {
		let bonus = true;
		let best = challenge(5,20,bonus).unwrap();
		assert_eq!(best.num_cheeses(), 16);
	}
}
