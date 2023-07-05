use std::collections::HashSet;

/// Class for storing and maintaining the state of a partial path through the maze
pub struct MouseState {
	/// X coord of the current position the path reaches
	pub x:usize,
	/// Y coord of the current position the path reaches
	pub y:usize,
	/// Z coord of the current position the path reaches
	pub z:usize,
	/// Timestep the path reaches
	pub t:usize,
	/// List of moves previously added to the path
	pub path:Vec<char>,
	/// List of positions where cheese was previously collected on the path. Not used under the rules of the bonus challenge.
	cheeses:HashSet<usize>,
	/// Amount of cheese previously collected from the path
	cheese_counter:usize,
}

impl MouseState {
	/// Returns a new MouseState initialized to the start of the maze with no cheese collected.
	pub fn new() -> MouseState {
		return MouseState {x:1, y:1, z:1, t:1, path:Vec::new(), cheeses:HashSet::new(), cheese_counter:0};
	}
	
	/// Returns the list of moves in the path as a String
	pub fn path_string(&self) -> String {
		return self.path.iter().collect();
	}
	
	/// Returns a copy of the existing MouseState
	pub fn copy(&self) -> MouseState {
		return MouseState { x:self.x, y:self.y, z:self.z, t:self.t, path:self.path.clone(), cheeses:self.cheeses.clone(), cheese_counter:self.cheese_counter };
	}
	
	/// Adds a collected cheese to the MouseState
	pub fn add_cheese(&mut self, index:usize, bonus:bool) {
		if !bonus {
			if !self.cheeses.contains(&index) {
				self.cheeses.insert(index);
				self.cheese_counter += 1;
			}
		}
		else {
			self.cheese_counter += 1;
		}
	}
	
	/// Returns the amount of cheese previously collected by the MouseState
	pub fn num_cheeses(&self) -> usize{
		return self.cheese_counter;
	}
}

/// Class for caching cheese phases for all positions and timesteps in the maze
pub struct Maze {
	/// Dimension parameter of the maze
	pub k:usize,
	/// Number of timesteps to solve for
	pub n:usize,
	/// Store of cheese phases for all positions and time steps
	pub states:HashSet<usize>, 
}

impl Maze {
	/// Returns a new Maze with a cache of cheese phases for the given k and n.
	/// # Safety
	/// Results in undefined behavior if k + k * (k + 1) + k * (k+1)^2 + n * (k+1)^3 > usize::MAX
	pub fn new(k:usize, n:usize) -> Maze {
		let mut states:HashSet<usize> = HashSet::new();
		for x in 1..=k {
			for y in 1..=k {
				for z in 1..=k {
					let phases = Maze::cheese_phases(x,y,z,n);
					for t in 1..=n {
						if phases.contains(&t) {
							states.insert(Maze::coords4_to_index_static(x,y,z,t,k));
						}
					}
				}
			}
			println!("Building cheese phase cache {:.2}% complete", 100.0 * (x as f64/k as f64));
		}
		
		Maze{ k: k, n:n, states:states }
	}
	
	/// Returns true if cheese is in phase at the given position and time
	pub fn cheese_at_coords4(&self, x:usize, y:usize, z:usize, t:usize) -> bool {
		return self.states.contains(&self.coords4_to_index(x,y,z,t));
	}
	
	/// Convert (x,y,z,t) coordinates to a single index in a static method
	/// # Panics
	/// Panics if x, y or z are greater than k
	pub fn coords4_to_index_static(x:usize,y:usize,z:usize,t:usize, k:usize) -> usize {
		if x > k || y > k || z > k {
			panic!("Invalid coordinates ({},{},{},{}) for conversion to index. Spatial coordinate greater than {}", x, y, z, t, k);
		}
		let a = 1;
		let b = a * (k + 1);
		let c = b * (k + 1);
		let d = c * (k + 1);
		return (a * x) + (b * y) + (c * z) + (d * t);
		
	}
	/// Convert an index to (x,t,z,t) coordinates in a static method
	pub fn index_to_coords4_static(index:usize, k:usize) -> (usize, usize, usize, usize) {
		let mut idx = index;
		let x = idx % (k + 1);
		idx /= k + 1;
		let y = idx % (k + 1);
		idx /= k + 1;
		let z = idx % (k + 1);
		idx /= k + 1;
		let t = idx;
		return (x,y,z,t);
	}
	/// Convert (x,y,z,t) coordinates to a single index
	pub fn coords4_to_index(&self, x:usize,y:usize,z:usize,t:usize) -> usize {
		return Maze::coords4_to_index_static(x,y,z,t,self.k);
	}
	/// Convert an index to (x,t,z,t) coordinates
	pub fn index_to_coords4(&self, index:usize) -> (usize, usize, usize, usize) {
		return Maze::index_to_coords4_static(index,self.k);
	}
	/// Convert (x,y,z) coordinates to an index
	pub fn coords3_to_index(&self, x:usize,y:usize,z:usize) -> usize {
		let a = 1;
		let b = a * (self.k + 1);
		let c = b * (self.k + 1);
		return (a * x) + (b * y) + (c * z);
	}
	/// Convert an index to (x,y,z) coordinates
	pub fn index_to_coords3(&self, index:usize) -> (usize, usize, usize) {
		let mut idx = index;
		let x = idx % (self.k + 1);
		idx /= self.k + 1;
		let y = idx % (self.k + 1);
		idx /= self.k + 1;
		let z = idx;
		return (x,y,z);
	}
	/// Linear conguential generator for cheese phases
	pub fn cheese_phase_func(x:usize) -> usize {
		return  (1103515245 * x + 12345) % (2147483648)
	}
	/// Returns a vector of all t where the cheese at (x,y,z) is in phase
	pub fn cheese_phases(x:usize, y:usize, z:usize, n:usize) -> Vec<usize> {
		let mut cheese_present:Vec<usize> = Vec::new();
		let half_n = n >> 1;
		for t in 1..=n {
			for u in 0..half_n {
				if Maze::cheese_phase_func((x * y * z) + u) % n == t {
					cheese_present.push(t);
					break;
				}
			}
		}
		return cheese_present;
	}
	/// Traces a provided path through the maze for verification and returns the amount of cheese collected.
	pub fn mouse_path(&self, path:String, bonus:bool) -> usize {
		let mut x = 1;
		let mut y = 1;
		let mut z = 1;
		let mut t = 1;
		let mut c = 0;
		let mut cheeses:Vec<usize> = Vec::new();
		
		if self.states.contains(&self.coords4_to_index(x,y,z,t)) {
			if !bonus {
				cheeses.push(self.coords3_to_index(x,y,z));
			}
			c += 1;
		}
		let path_chars:Vec<char> = path.chars().collect();
		for i in 0..path_chars.len() {
			t += 1;
			match path_chars[i] {
				'F' => z += 1,
				'B' => z -= 1,
				'U' => y += 1,
				'D' => y -= 1,
				'R' => x += 1,
				'L' => x -= 1,
				'W' => (),
				_ => {println!("Invalid character found in path {} at position {}", path, i + 1); return 0;}
			}
			if x < 1 || x > self.k || y < 1 || y > self.k || z < 1 || z > self.k || t < 1 || t > self.n {
				println!("Invalid position ({},{},{},{})", x, y, z, t);
				return 0;
			}
			if bonus {
				if self.states.contains(&self.coords4_to_index(x,y,z,t)) {
					c += 1;
				}
			}
			else {
				if !cheeses.contains(&self.coords3_to_index(x,y,z)) && self.states.contains(&self.coords4_to_index(x,y,z,t)) {
					cheeses.push(self.coords3_to_index(x,y,z));
					c += 1;
				}
			}
		}
		return c;
	}
	
}
