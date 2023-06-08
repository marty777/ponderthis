use std::collections::HashMap;

/// Class for indexing all Q vectors and comparison indexes between distinct Q vectors for a given n
pub struct QStore {
	/// The number of q vectors stored, including duplicates.
	q_n:u32,
	/// List of distinct Q vectors, added in the order they're encountered
	q_list:Vec<Vec<u8>>,
	/// Stores a lookup of distinct Q vectors indexed by position in q_list to i for which Qi = the distinct vector.
	pub q_reverse_lookup:Vec<Vec<u32>>,
	/// Stores a lookup of existing Q vectors to the first i that they appear at. This isn't needed after the Q vectors have been indexed and can be safely discarded, but it's small.
	q_hash:HashMap<String, u32>,
	/// For each distinct Q vector, list all combinations with other distinct vectors, indexed by the combined 5-bit comparison index.
	pub q_combinations:Vec<HashMap<u8, Vec<usize>>>,
}

impl QStore {
	pub fn new() -> QStore {
		QStore{ q_n: 0, q_list:Vec::new(), q_reverse_lookup:Vec::new(), q_hash:HashMap::new(), q_combinations:Vec::new()}
	}
	
	/// Returns the number of vectors stored. Should be equal to n after all vectors have been added to the store.
	pub fn q_len(&self) -> u32{
		return self.q_n;
	}
	
	/// Returns the number of distinct Q vectors stored. 
	pub fn q_distinct_len(&self) -> usize{
		return self.q_list.len();
	}
	
	/// Returns a string representation of the given Q vector for use with a hashmap lookup.
	pub fn vec_key(&self, q:&Vec<u8>) -> String {
		return format!("{:?}", q);
	}
	/// Add a Q vector to the store. This has to be run sequentially for Qi where i = 0..n. Vectors added out of order are likely to cause issues.
	pub fn add_q(&mut self, q:Vec<u8>) {
		if self.q_n == u32::MAX {
			panic!("Due to memory issues, QStore can only store 2^32 possible Q vectors.");
		}
		let key = self.vec_key(&q);
		let lookup_index = self.q_n; // the index of the element to be inserted into q_lookup
		if self.q_hash.contains_key(&key) {
			let index = *self.q_hash.get(&key).unwrap() as usize;
			self.q_reverse_lookup[index].push(lookup_index);
		}
		else {
			self.q_list.push(q.clone());
			self.q_reverse_lookup.push(Vec::new());
			let reverse_lookup_index = self.q_reverse_lookup.len() as usize - 1;
			self.q_reverse_lookup[reverse_lookup_index].push(lookup_index);
			self.q_hash.insert(key, self.q_list.len() as u32 - 1);
		}
		self.q_n += 1
	}
	
	/// Given all distinct Q vectors, for each distinct vector determine all distinct bitwise combinations with other distinct vectors and list by q_list index.
	pub fn build_combinations(&mut self) {
		// For each distinct vector I
		for i in 0..self.q_list.len() {
			//self.q_combos4.push(HashMap::new());
			let mut matches:HashMap<u8, Vec<usize>> = HashMap::new();
			// combined with each distinct vector J
			for j in 0..self.q_list.len() {
				let comparison_index:u8 = self.q_compare(&self.q_list[i], &self.q_list[j]);
				if comparison_index != 0 {
					if matches.contains_key(&comparison_index) {
						let vec = matches.get_mut(&comparison_index).unwrap();
						vec.push(j);
					}
					else {
						let mut new_vec:Vec<usize> = Vec::new();
						new_vec.push(j);
						matches.insert(comparison_index, new_vec);
					}
				}
			}
			self.q_combinations.push(matches);
		}
	}

	/// Returns the bitwise comparison index of two Q vectors
	/// 
	/// # Arguments
	/// 
	/// * 'a' - one of two vectors to be compared.
	/// * 'b' - one of two vectors to be compared.
	pub fn q_compare(&self, a:&Vec<u8>, b:&Vec<u8>) -> u8 {
		if a.len() != b.len() {
			panic!("Attempting to compare Q vectors of unequal lengths");
		}
		if a.len() > 8 {
			panic!("Attempting to compare Q vectors that are too large");
		}
		let length = a.len();
		let mut result:u8 = 0;
		for i in 0..length {
			if a[i] == b[i] {
				result |= 1 << (i);
			}
		}
		return result;
	}
	
}

/// Class for generating and indexing *Q*, *a* and *x* vectors for k = 5 and n < 2<sup>32</sup> only. 
pub struct QuadraticK5Solver {
	k:u32,
	pub n:u32,
	pub q_store:QStore,
}

impl QuadraticK5Solver {
	/// Due to choices intended to reduce the memory footprint of the index
	/// of *Q* vectors, *n* cannot exceed u32::MAX.
	pub fn new(n: u32) -> QuadraticK5Solver {
		if n < 5 {
			panic!("n must be greater than or equal to 5.");
		}
		QuadraticK5Solver {k:5, n:n, q_store:QStore::new()}
	}
	/// Return the ith component of the x vector for the given i.
	///
	/// # Arguments
	/// 
	/// * 'i' - The *x* vector index the return
	pub fn get_x(&self, i:usize) -> f64 {
		let n = self.n as usize;
		if i >= n {
			panic!("Requested x {} which exceeds {}", i, self.n - 1)
		}
		if i == 0 {
			return -1.0;
		}
		else if i == n - 1 {
			return 1.0;
		}
		return -1.0 + (((2 * i) as f64)/((n-1) as f64));
	}
	/// Return the constant coefficient of the terms of the *a* vector
	pub fn get_a_coefficient(&self) -> f64 {
		return 1.0 /(((1 << self.k) - 1) as f64);
	}
	/// Return the pseudo-randomly generated coefficient of the *i*th *Q* vector at
	///	index t.
	/// 
	/// # Arguments
	/// 
	/// * 'i' - the index of the vector Q_i.
	/// * 't' - the position of the entry in Q_i to be calculated.
	pub fn qit(&self, i:u32, t:u8) -> u8 {
		let term:f64 = ((i as usize + 1) * (t as usize + 1)) as f64;
		let mult = (1 << self.k) as f64;
		let sin = term.sin();
		return (mult * (sin - sin.floor())).floor() as u8;
	}
	/// Return the ith Q vector
	/// # Arguments
	/// 
	/// * 'i' - the index of the vector Q_i.
	pub fn qi(&self, i:u32) -> Vec<u8> {
		let mut result = Vec::<u8>::new();
		for t in 0..self.k {
			result.push(self.qit(i, t as u8));
		}
		return result;
	}
	/// Generate all Q vectors and add them to an indexed store.
	pub fn build_q_store(&mut self, verbose:bool) {
		let print_progress:usize = if self.n > 1 << 10 { self.n as usize >> 10 } else { 100 };
		let n = self.n as usize;
		for i in 0..n {
			if verbose && i % print_progress == 0 && i > 0 {
				println!("Indexing Q vectors {} / {} ({:.02} % complete)", i, self.n, 100.0 * (i as f64 / self.n as f64));
			}
			self.q_store.add_q(self.qi(i as u32));
		}
		if verbose {
			println!("Q vector store contains {} entries with {} distinct Q vectors", self.q_store.q_len(), self.q_store.q_distinct_len());
		}
		self.q_store.build_combinations();
	}
}