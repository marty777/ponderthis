pub mod fpp;
use fpp::{IncidenceMatrix};
use std::time::{Instant};
use std::thread;
use std::sync::{Arc,Mutex};
use num_bigint::{BigInt};
use clap::{Arg, ArgAction, Command};

fn main() {
    let command = Command::new("may2024").max_term_width(80)
					.about("Solver for the Ponder This May 2024 challenge.")
					.arg(Arg::new("order").help("Set order of the finite projective plane").short('N').long("order").value_name("ORDER").default_value("4"))
					.arg(Arg::new("threads").help("Set maximum number of worker threads").short('t').long("threads").value_name("THREADS").default_value("4"))
                    .arg(Arg::new("verbose").help("Print calculation progress").short('v').long("verbose").action(ArgAction::SetTrue));
	let args = command.get_matches();	
	let mut verbose = false;
	if args.get_flag("verbose") {
		verbose = true;
	}
    let mut threads = 4;
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
    let imatrix:IncidenceMatrix;
    if let Some(order_arg) = args.get_one::<String>("order") {
		match order_arg.parse::<usize>() {
			Ok(n) => {
				match n {
                    2 => {imatrix = IncidenceMatrix::new(fpp::FINITE_PROJECTIVE_PLANE_ORDER_2);}
                    3 => {imatrix = IncidenceMatrix::new(fpp::FINITE_PROJECTIVE_PLANE_ORDER_3);}
                    4 => {imatrix = IncidenceMatrix::new(fpp::FINITE_PROJECTIVE_PLANE_ORDER_4);}
                    5 => {imatrix = IncidenceMatrix::new(fpp::FINITE_PROJECTIVE_PLANE_ORDER_5);}
                    7 => {imatrix = IncidenceMatrix::new(fpp::FINITE_PROJECTIVE_PLANE_ORDER_7);}
                    8 => {imatrix = IncidenceMatrix::new(fpp::FINITE_PROJECTIVE_PLANE_ORDER_8);}
                    _ => {
                        println!("ORDER must be one of 2, 3, 4, 5, 7 or 8 ({} specified)", n);
                        std::process::exit(2);
                    }
                }
			},
			Err(_) => {
				println!("Could not parse ORDER argument '{}' as an integer.", order_arg);
				std::process::exit(2);
			}
		}
	}
    else {
        imatrix = IncidenceMatrix::new(fpp::FINITE_PROJECTIVE_PLANE_ORDER_4);
    }
    
    println!("\n######## Ponder This Challenge - May 2024 ########\n");
    let start_instant = Instant::now();
	if verbose {println!("Calculation starting for order {}...", imatrix.n);}
    // Fixing three columns of the incidence matrix and finding permutations of 
    // the remaining ones that produce the same rows as the initial incidence
    // matrix allows the total number of permutations that produce each 
    // distinct "deck" to be calculated. 
	let imatrix_clone = imatrix.clone();
    let imatrix_arc = Arc::new(imatrix_clone);
    let total_automorphic_permutations = dfs_threaded(&imatrix, &imatrix_arc, threads, verbose);
    if verbose {println!("Automorphic symbol permutations for order {}: {}", imatrix.n, total_automorphic_permutations);}
    // Each distinct deck has the same number of column permutations that 
    // produce it from an initial incidence matrix. Knowing the number of 
    // permutations for one "deck", and knowing that there are (N*N + N + 1)! 
    // total possible permutations allows the number of distinct decks to be 
    // calculated.
    let solution =  factorial_bigint(imatrix.n * imatrix.n + imatrix.n + 1)/total_automorphic_permutations;
    println!("Solution for order {}: {:?}", imatrix.n, solution);
	println!("\nTotal execution time: {:?}", start_instant.elapsed());
}

/// Calculate n! as a BigInt
fn factorial_bigint(n:usize) -> BigInt {
    let mut big_factorial = BigInt::parse_bytes(b"1", 10).unwrap();
    for i in 2..=(n) {
        big_factorial *= i;
    }
    return big_factorial;
}

fn factorial(n:usize) -> usize {
    let mut factorial = 1;
    for i in 2..=n {
        factorial *= i;
    }
    return factorial;
}

/// Obtain the number of permutations of columns of an incidence matrix that 
/// map to the original matrix, ignoring row ordering, dividing the work
/// across multiple threads.
/// 
/// # Arguments 
///
/// * 'matrix' - An initialized IncidenceMatrix for a finite projective plane 
/// of order N.
/// * 'imatrix_arc' - A thread-friendly Arc pointing to a copy of the incidence
/// matrix.
/// * 'threads' - The number of worker threads to run simultaneously while 
/// performing depth first searches on subsets of the remaining column 
/// permutations.
/// * 'verbose' - If true, print the calculation progress.
fn dfs_threaded(imatrix:&IncidenceMatrix, imatrix_arc:&Arc<IncidenceMatrix>, threads:usize, verbose:bool) -> BigInt {
    // For N up to 4, a single-threaded search is more than fast enough.
    if imatrix.n <= 4 {
        let fixed_columns:Vec<usize> = (0..3).collect();
        let result = dfs(imatrix, &fixed_columns);
        if verbose {println!("Symbol permutations 100.0% completed");}
        return result * (imatrix.n*imatrix.n + imatrix.n + 1) * factorial_bigint(imatrix.n + 1)/factorial_bigint(imatrix.n + 1 - 3);
    }
	let mut child_results:Vec<usize> = Vec::new();
	for _i in 0..threads {
		child_results.push(0);
	}
	let mut result:usize = 0;
	let mut handles = Vec::new();
    let mut added = 0;
    let results_arc = Arc::new(Mutex::new(child_results));
    let job_total = factorial(imatrix.n - 2)/factorial(imatrix.n - 5);
    let mut job_count = 0;
    for batch_index1 in 3..imatrix.n+1 {
        for batch_index2 in 3..imatrix.n+1 {
            for batch_index3 in 3..imatrix.n+1 {
                if batch_index2 == batch_index1 || batch_index3 == batch_index1 || batch_index3 == batch_index2 {
                    continue;
                }
                // set up each worker thread for the batch run. 
                let results_arc_clone = Arc::clone(&results_arc);
                let mut child_input:Vec<usize> = (0..3).collect();
                child_input.push(batch_index1);
                child_input.push(batch_index2);
                child_input.push(batch_index3);
                let imatrix_arc_clone = imatrix_arc.clone();
                let handle = thread::spawn( move || {
                    let thread_result = dfs(&*imatrix_arc_clone, &child_input);
                    let mut c_r = results_arc_clone.lock().unwrap();
                    (*c_r)[added] = thread_result;
                });
                handles.push(handle);
                added += 1;
                job_count += 1;
                if added == threads {
                    // execute the batch
                    while handles.len() > 0 {
                        let handle2 = handles.remove(0);
                        handle2.join().unwrap();
                    }
                    let mut batchresult = results_arc.lock().unwrap();
                    for i in 0..added {
                        result += batchresult[i];
                        batchresult[i] = 0;
                    }
                    if verbose {println!("Symbol permutations {:.2}% completed", 100.0*(job_count as f32)/(job_total as f32));}
                    added = 0;
                }
            }
        }
    }
    // Run any incomplete batches
    if added > 0 {
        while handles.len() > 0 {
            let handle = handles.remove(0);
            handle.join().unwrap();
        }
        let mut batchresult = results_arc.lock().unwrap();
        for i in 0..added {
            result += batchresult[i];
            batchresult[i] = 0;
        }
        if verbose {println!("Symbol permutations 100.0% completed");}
    }
    // With the result for 3 fixed columns/symbols, the total number of 
    // automorphic permutations of the original matrix (ignoring row order) is
    //  result 
    //  * N*N+N+1 
    //      ways to select a row incident with 3 fixed symbols
    //  * (N+1)!/(N+1-3)! 
    //      ways to permute the remaining symbols incident with the row
    return result * (imatrix.n * imatrix.n + imatrix.n + 1) * factorial_bigint(imatrix.n + 1)/factorial_bigint(imatrix.n + 1 - 3);
}

/// Entry method for a worker thread that performs a depth first search of all 
/// column permutations of an incidence matrix that produce identical rows to
/// the initial matrix, given some initial assignments of columns. Returns the
/// count of automorphic permutations found.
/// 
/// #Arguments
/// 
/// * 'imatrix' - an incidence matrix for a finite projective plane
/// * 'start_permutations' - A pre-specified partial list of column 
///    permutations
fn dfs(imatrix:&IncidenceMatrix, start_permutations:&Vec<usize>) -> usize {
	let mut remaining:Vec<usize> = Vec::new();
    let mut selected:Vec<usize> = Vec::new();
	for i in 0..start_permutations.len() {
		selected.push(start_permutations[i])
	}
	for i in 0..imatrix.dim {
		let mut found = false;
		for j in 0..start_permutations.len() {
			if start_permutations[j] == i {
				found = true;
				break
			}
		}
		if !found {
			remaining.push(i);
		}
	}
    let mut count = 0;
    dfs_recurse(imatrix, selected, remaining, &mut count);
    return count;
}

/// Recursive submethod of the DFS. Increments a count pointer with each 
/// automorphic permutation of columns found.
///
/// #Arguments
/// 
/// * 'imatrix' - an incidence matrix for a finite projective plane
/// * 'selected' - the column permutations assigned so far in the recursive 
/// search.
/// * 'remaining' - a list of remaining column permutations to be assigned.
/// * 'count' - pointer to a counter of automorphic permutations found.
fn dfs_recurse(imatrix:&IncidenceMatrix, selected:Vec<usize>, remaining:Vec<usize>, count:&mut usize) {
    if selected.len() == imatrix.dim {
        *count += 1;
        return;
    }
    for i in 0..remaining.len() {
        let mut next_selected = selected.clone();
        next_selected.push(remaining[i]);
        // Determine if the permutations selected so far can be automorphic.
        // If not, this branch of the search does not continue.
        let rows_okay = imatrix.permutation_potentially_automorphic(&next_selected);
        if rows_okay {
            let mut next_remaining:Vec<usize> = Vec::new();
            for j in 0..remaining.len() {
                if j != i {
                    next_remaining.push(remaining[j]);
                } 
            }
            dfs_recurse(imatrix, next_selected, next_remaining, count);
        }
    }
}
