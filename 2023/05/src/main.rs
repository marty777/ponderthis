pub mod quadratic_solver;
use quadratic_solver::QuadraticK5Solver;

use clap::{Arg, ArgAction, Command};
use std::time::{Instant};
use std::thread;
use std::sync::{Arc,Mutex,RwLock};

/// Worker thread for calculating the partial sums of the quadratic form for a subset of the distinct vectors in Q.
/// # Arguments
///
/// * 'solver' - A QuadraticK5Solver object with previously indexed Q vectors and combinations.
/// * 'u_indexes' - A list of indexes to distinct Q vectors to include in the calculation for this thread.
fn thread_quadratic_form(solver:&QuadraticK5Solver, u_indexes:&Vec<usize>) -> f64 {
	let a_coefficient = solver.get_a_coefficient(); // 1/(2^k - 1)
	let mut quadratic_sum = 0.0; 
	for u_1 in 0..u_indexes.len() {
		let u = u_indexes[u_1];
		let mut u_row_sum = 0.0;
		for d_uv in solver.q_store.q_combinations[u].keys() {
			let mut v_term_sum = 0.0;
			for v_1 in 0..solver.q_store.q_combinations[u][d_uv].len() {
				let v = solver.q_store.q_combinations[u][d_uv][v_1];
				for j_1 in 0..solver.q_store.q_reverse_lookup[v].len() {
					let j = solver.q_store.q_reverse_lookup[v][j_1] as usize;
					v_term_sum += solver.get_x(j);
				}
			}
			u_row_sum += v_term_sum * (*d_uv as f64);
		}
		for i_1 in 0..solver.q_store.q_reverse_lookup[u].len() {
			let i = solver.q_store.q_reverse_lookup[u][i_1] as usize;			
			quadratic_sum += u_row_sum * solver.get_x(i);
		}
	}
	quadratic_sum *= a_coefficient;
	return quadratic_sum;
}

/// Obtain the scalar of the quadratic form of the A matrix using partial sums 
/// of terms from distinct combinations of Q vectors
/// 
/// # Arguments 
///
/// * 'solver_lock' - A RwLock in an Arc on a QuadraticK5Solver where Q vectors 
/// and comparison values have already been indexed.
/// * 'batch_amount' - The number of distinct Q vectors for which to apply 
/// partial sums in each worker thread.
/// * 'q_threads' - The number of worker threads to run.
/// * 'n' - the n value of the provided solver.
/// * 'distinct_q_vectors' - The number of distinct Q vectors in the entire set.
fn quadratic_form(solver_lock:&Arc<RwLock<QuadraticK5Solver>>, batch_amount:usize, q_threads:usize, distinct_q_vectors:usize) -> f64 {
	let mut child_results:Vec<f64> = Vec::new();
	for _i in 0..q_threads {
		child_results.push(0.0);
	}
	let mut result = 0.0;
	let mut index = 0;
	let mut handles = Vec::new();
	let arc = Arc::new(Mutex::new(child_results));
	while index < distinct_q_vectors {		
		// set up each woker thread for the batch run.
		for i in 0..q_threads {
			let arc_clone = Arc::clone(&arc);
			// child input contains a list of indexes to distinct Q vectors
			// to be totaled up in the worker thread.
			let mut child_input:Vec<usize> = Vec::new();
			let index_start = index;
			while index < distinct_q_vectors && index < index_start + batch_amount {
				child_input.push(index);
				index += 1
			}
			let thread_lock = solver_lock.clone();
			let handle = thread::spawn( move || {
				if let Ok(read_guard) = thread_lock.read() {
					let thread_result = thread_quadratic_form(&*read_guard, &child_input);
					let mut c_r = arc_clone.lock().unwrap();
					(*c_r)[i] = thread_result;
				}
			});
			handles.push(handle);
		}
		// execute batch
		while handles.len() > 0 {
			let handle = handles.remove(0);
			handle.join().unwrap();
		}
		// Add the individual thread results into the result sum
		let mut batchresult = arc.lock().unwrap();
		for i in 0..q_threads {
			result += batchresult[i];
			batchresult[i] = 0.0;
		}
		println!("Added partial sums from {} / {} distinct Q vectors ({:.02} % complete)", index, distinct_q_vectors, 100.0 * (index as f64 / distinct_q_vectors as f64));
	}	
	return result;
}

fn main() {
	let command = Command::new("may2023").max_term_width(80)
					.about("Solver for the Ponder This May 2023 challenge.")
					.arg(Arg::new("bonus").help("Calculate the quadratic form for the bonus challenge.").short('b').long("bonus").action(ArgAction::SetTrue))
					.arg(Arg::new("threads").help("Set number of worker threads to use during matrix multiplication.").short('t').long("threads").value_name("THREADS").default_value("8"));
	let args = command.get_matches();	
	let mut threads = 8;
	if let Some(threads_arg) = args.get_one::<String>("threads") {
		match threads_arg.parse::<usize>() {
			Ok(n) => {
				threads = n;
				if threads < 1 {
					println!("THREADS must be at least 1 ({} provided)", threads_arg);
					std::process::exit(2);
				}
			},
			Err(_) => {
				println!("Could not parse THREADS argument '{}' as an integer.", threads_arg);
				std::process::exit(2);
			}
		}
	}
	let mut bonus = false;
	if args.get_flag("bonus") {
		bonus = true;
	}
	println!("\n######## Ponder This Challenge - May 2023 ########\n");
	let n = if bonus { 1 << 30 } else { 1 << 20 };
	if bonus {
		println!("Calculating the quadratic form for k = 5, n = 2^30 (the bonus challenge) ");
	}
	else {
		println!("Calculating the quadratic form for k = 5, n = 2^20 (the main challenge) ");
	}
	
	let mut solver:QuadraticK5Solver = QuadraticK5Solver::new(n);
	let start_instant = Instant::now();
	println!("Indexing Q vectors...");
	solver.build_q_store(true);
	println!("Q vector indexing complete");
	let r = solver.q_store.q_combinations.len();
	let mut matrix_multiplication_batch_size = solver.q_store.q_distinct_len() / (threads << 6);
	if matrix_multiplication_batch_size == 0 {
		matrix_multiplication_batch_size = 1;
	}
	let solver_rw_lock = Arc::new(RwLock::new(solver));
	println!("Calculating quadratic form...");
	let result = quadratic_form(&solver_rw_lock, matrix_multiplication_batch_size, threads, r);
	println!("Result: {:.3}", result); 
	let duration = start_instant.elapsed();
	println!("Total execution time: {:?}", duration);
}

#[cfg(test)]
mod tests {
	use super::*;
	/// Test generation of x[i] values
	#[test]
	fn test_x_values() {
		let x_expected = vec![-1.0,-0.5,0.0,0.5,1.0];
		let solver = QuadraticK5Solver::new(5);
		for i in 0..x_expected.len() {
			assert_eq!(x_expected[i], solver.get_x(i));
		}
	}
	/// Test bitwise combination of Q vectors
	#[test]
	fn test_q_combination() {
		let solver = QuadraticK5Solver::new(5);
		let q_i = vec![1,5,7,8,1];
		let q_j = vec![2,5,6,8,2];
		let q_i2 = vec![1,2,3,4,12];
		let q_j2 = vec![1,0,3,0,16];
		let expected:u8 = 10;
		let expected2:u8 = 0b0101;
		let comparison = solver.q_store.q_compare(&q_i, &q_j);
		let comparison2 = solver.q_store.q_compare(&q_i2, &q_j2);
		assert_eq!(expected, comparison);
		assert_eq!(expected2, comparison2);
	}
	/// Test pseudorandom function generating components of Q vectors
	#[test]
	fn test_pseudorandom_q_components() {
		let solver = QuadraticK5Solver::new(5);
		let pseudo_rand_i = 13;
		let pseudo_rand_expected = vec![31,8,2,15,24];
		let pseudo_rand_q = solver.qi(pseudo_rand_i);
		assert_eq!(pseudo_rand_q, pseudo_rand_expected);
	}
	/// Verify solver against matrix multiplication of small matrices
	#[test]
	fn test_matrix_multiplication() {
		let worker_threads = 4;
		for i in 5..11 {
			let n:usize = 1 << i;
			let mut solver = QuadraticK5Solver::new(n as u32);
			// Obtain the quadratic form using conventional matrix multiplication
			let mut result_1 = 0.0;
			for i in 0..n {
				let mut row_result = 0.0;
				for j in 0..n {
					let q_i = solver.qi(i as u32);
					let q_j = solver.qi(j as u32);
					let combination = solver.q_store.q_compare(&q_i, &q_j);
					row_result += solver.get_x(j) * combination as f64 * solver.get_a_coefficient();
				}
				row_result *= solver.get_x(i);
				result_1 += row_result;
			}
			solver.build_q_store(false);
			solver.q_store.build_combinations();
			let r = solver.q_store.q_distinct_len();
			let solver_rw_lock = Arc::new(RwLock::new(solver));
			let result_2 = quadratic_form(&solver_rw_lock, r / (worker_threads), worker_threads, r);
			// Some variation between the partial sums approach and conventional matrix multiplication is expected, but it should be small.
			assert!((result_1 - result_2).abs() < 0.0000000001);
		}
	}
}
