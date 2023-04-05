pub mod digit_chain;
use digit_chain::DigitChain;

use clap::{Arg, ArgAction, Command};
use openssl::bn::BigNumContext;
use std::time::{Instant};
use std::thread;
use std::sync::{Arc,Mutex};

fn main() {

	let mut command = Command::new("mar2023").max_term_width(80)
					.about("Solver for the Ponder This March 2023 challenge.")
					.arg(Arg::new("reverse").help("Explore reverse chained primes where digits are appended on the left.").short('r').long("reverse").action(ArgAction::SetTrue))
					.arg(Arg::new("numexceptions").help("Maximum prime chain exceptions.").short('n').long("numexceptions").value_name("EXCEPTIONS").default_value("5"))
					.arg(Arg::new("threads").help("Maximum number of worker threads to spawn at each step of chain\nevaluation.").short('t').long("threads").value_name("THREADS").default_value("4"))
					.arg(Arg::new("filter").help("Retain only the digit chains with the TOP fewest exceptions at each\nstep and discard all others.").short('f').long("filter").value_name("TOP"))
					.after_help("This solver attempts to find the largest n-exception chained prime in decimal \n\
notation. The main solver will exhaustively check all possibilities at each \n\
digit-appending step until the largest digit chain is reached. Enabling the \n\
reverse option will perform the same operations for n-exeception reverse \n\
chained primes.
\n\
While it's possible for the solver to completely exhaust the search space\n\
for chained primes at n=5 in reasonable time on a desktop PC, the behaviour of \n\
reverse-chained primes makes this much less feasible. For this reason, it's \n\
recommended to enable the filter option (-f or --filter), which will discard \n\
any digit chains which have exceeded a certain cutoff of exceptions as each \n\
digit is added. While not rigorously guaranteed, the largest possible chained \n\
prime or reverse chained prime will generally have its predecessors appear \n\
within the top few lowest-exception categories of all possible digit chains at \n\
each digit step. Discarding the highest-exception categories at each step \n\
greatly reduces the number of digit chains to process.\n\
\n\
To demonstrate this, examine the behavior of the following commands:\n\
\n\
mar2023 -n 5 --filter 1\n\
mar2023 -n 5 --filter 2\n\
mar2023 -n 5 --filter 3\n\
mar2023 -n 5 --filter 4\n\
\n\
These will find the largest 5-exception chained prime while retaining digit \n\
chains with the 1, 2, 3, or 4 fewest exceptions at each step. Note that \n\
filtering only the top 1 exception group will exclude a larger possible digit \n\
chain that is reached when filtering the top 2, 3 or 4 exception groups. \n\
Retaining a larger number of filtered exceptions is more likely to reach the \n\
largest possible digit chain for a given number of exceptions, but also \n\
increases the execution time. These results can be compared with the exhaustive\n\
search for 5-exception chained primes (which will take substantially longer to \n\
complete):\n\
\n\
mar2023 -n 5
\n\
For the bonus challenge, filtering by the top 2 or 3 exception groups is \n\
recommended:\n\
\n\
mar2023 -n 5 --filter 3 --reverse
");
	let help = command.render_usage();
	let args = command.get_matches();
	// Parameters
	// Threads
	let mut threads:usize = 4;
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
	// Numexceptions
	let mut max_exceptions:usize = 5;
	if let Some(exceptions_arg) = args.get_one::<String>("numexceptions") {
		match exceptions_arg.parse::<usize>() {
			Ok(n) => max_exceptions = n,
			Err(_) => {
				println!("Could not parse EXCEPTIONS argument '{}' as an integer.", exceptions_arg);
				std::process::exit(2);
			}
		}
	}
	// Reverse prime chains
	let mut reverse = false;
	if args.get_flag("reverse") {
		reverse = true;
	}
	// Filtering
	let mut filter = false;
	let mut top:usize = 3;
	if let Some(filter_arg) = args.get_one::<String>("filter") {
		filter = true;
		match filter_arg.parse::<usize>() {
			Ok(n) => {
				top = n;
				if top < 1 {
					println!("TOP must be at least 1 ({} provided)", filter_arg);
					std::process::exit(2);
				}
				if top > max_exceptions + 1 {
					println!("Provided TOP value {} has been set to {}, the maximum number of exception groupings.", filter_arg, max_exceptions + 1);
					top = max_exceptions + 1;
				}
			},
			Err(_) => {
				println!("Could not parse TOP argument '{}' as an integer.", filter_arg);
				println!("{}", help);
				std::process::exit(2);
			}
		}
	}
	
	println!("\n######## Ponder This Challenge - March 2023 ########\n");
	if reverse {
		println!("Searching for the largest {}-exception reverse chained prime...", max_exceptions);
	}
	else {
		println!("Searching for the largest {}-exception chained prime...", max_exceptions);
	}
	if filter {
		println!("Filtering out digit chains that exceed the lowest {} exceptions at each digit", top);
	}
	println!();
	
	let start_instant = Instant::now();
	// generate an initial population of 1..9
	let start_pop = init_population();
	let result = challenge(max_exceptions, threads, filter, top, start_pop, reverse);
	println!("Final result: {}", result.to_dec_string());
	result.print_trace(reverse);
	let duration = start_instant.elapsed();
	println!("Total execution time: {:?}", duration);
	
}

fn init_population() -> Vec<DigitChain> {
	let mut ctx = BigNumContext::new().unwrap();
	let mut start:Vec<DigitChain> = Vec::new();
	for i in 1..=9 {
		let mut chain = DigitChain::new();
		chain.push_ctx(i,false,&mut ctx);
		start.push(chain);
	}
	return start;
}

// Advances the provided population one step to the left
fn thread_step_left(max_exceptions:usize, start_pop: &Vec<DigitChain>) -> Vec<DigitChain> {
	let mut ctx = BigNumContext::new().unwrap();
	let push_left:bool = true;
	let mut result:Vec<DigitChain> = Vec::new();
	for digit_chain in start_pop {
		// I'm pretty sure prepending 0 to a decimal string doesn't make sense for reverse-chained primes,
		for d in 1..=9 {
			let mut next_digit_chain = digit_chain.copy();
			next_digit_chain.push_ctx(d as u16,push_left, &mut ctx);
			if next_digit_chain.exceptions() <= max_exceptions {
				result.push(next_digit_chain);
			}
		}
	}
	return result;
}

// Advances the provided population one step to the right.
fn thread_step_right(max_exceptions:usize, start_pop: &Vec<DigitChain>) -> Vec<DigitChain> {
	let mut ctx = BigNumContext::new().unwrap();
	let push_left:bool = false;
	let mut result:Vec<DigitChain> = Vec::new();
	for digit_chain in start_pop {
		for d in 0..=9 {
			// skip a bit of testing and copying for obvious non-primes if the chain is at the exception limit
			// and this isn't the first digit.
			if digit_chain.exceptions() >= max_exceptions && digit_chain.len() > 1 {
				if d == 0 || d == 2 || d == 4 || d == 5 || d == 6 || d == 8 {
					continue;
				}
			}
			let mut next_digit_chain = digit_chain.copy();
			next_digit_chain.push_ctx(d as u16,push_left, &mut ctx);
			if next_digit_chain.exceptions() <= max_exceptions {
				result.push(next_digit_chain);
			}
		}
	}
	return result;
}

/// Attempts to determine the largest possible prime digit chain that can be reached with the provided parameters
/// 
/// # Arguments
/// 
/// * 'max_exceptions' - The maximum number of non-prime exceptions that a digit chain may include. E.g. 5 for a 5-exception prime chain.
/// * 'threads' - Number of worker threads to spawn for processing the digit chain population at each digit step.
/// * 'filter_by_top_exception_groups' - If set to true, the digit chain population at each digit step will filter out any digit chains that exceed the current minimum number of exceptions in the digit chain population plus a cutoff parameter.
/// * 'top_exceptions_groups' - If filtering is enabled, sets the cutoff parameter for filtering out digit chains at each digit step.
/// * 'starting_pop' - A starting population of digit chains to process. E.g. the integers 1-9.
/// * 'push_left' - If set to true, digit chains will prepend new digits on the left at each digit step. If set to false, digits will be appended on the right.
fn challenge(max_exceptions:usize, threads:usize, filter_by_top_exception_groups:bool, top_exception_groups:usize, starting_pop:Vec<DigitChain>, push_left:bool) -> DigitChain {
	if starting_pop.len() == 0 {
		println!("Solver has an empty starting population");
		return DigitChain::new();
	}
	let mut best = DigitChain::new();
	let mut child_frontiers:Vec<Vec<DigitChain>> = Vec::new();
	let mut child_results:Vec<Vec<DigitChain>> = Vec::new();
	for _i in 0..threads {
		child_frontiers.push(Vec::new());
		child_results.push(Vec::new());
	}
	let mut handles = Vec::new();
	let arc = Arc::new(Mutex::new(child_results));
	let mut population:Vec<DigitChain> = Vec::new();
	
	// Add the starting population to the working set, removing any digit 
	// chains that have exceeded the maximum number of exceptions.
	for i in 0..starting_pop.len() {
		let digit_chain = starting_pop[i].copy();
		if digit_chain.exceptions() <= max_exceptions {
			if best.cmp(&digit_chain) < 0 {
				best = digit_chain.copy();
			}
			population.push(digit_chain);
		}
	}
	let mut instant = Instant::now();
	while population.len() > 0 {
		let digits = population[0].len();
		println!("Processing digit {}", digits);
		// determine the distribution of exception counts in the population, 
		// perform any filtering and distribute the population into the child
		// thread input vectors from the working set.
		let start_population_len = population.len();
		let mut filtered_population_len = 0;
		let mut exception_counts = vec![0; max_exceptions + 1];
		for i in 0..population.len() {
			exception_counts[population[i].exceptions()] += 1;
		}
		for i in 0..=max_exceptions {
			println!("{} exceptions:\t{}",i,exception_counts[i]);
		}
		let mut top_exception = 0;
		let mut top_exception_found = false;
		for i in 0..=max_exceptions {
			if exception_counts[i] != 0 {
				top_exception = i;
				top_exception_found = true;
				break;
			}
		}
		if !top_exception_found {
			println!("Execution completed");
			return best;
		}
		let mut bottom_exception = top_exception + top_exception_groups - 1;
		if bottom_exception > max_exceptions {
			bottom_exception = max_exceptions;
		}
		if !filter_by_top_exception_groups {
			bottom_exception = max_exceptions;
		}
		// fill the child vectors with the filtered population
		let mut child_index = 0;
		while population.len() > 0 {
			let digit_chain = population.pop().unwrap();
			if digit_chain.exceptions() >= top_exception && digit_chain.exceptions() <= bottom_exception {
				child_frontiers[child_index].push(digit_chain);
				child_index = (child_index + 1) % threads;
				filtered_population_len += 1;
			}
		}
		// attempt to dealloc the working set memory after emptying.
		population = Vec::new();
		if filter_by_top_exception_groups {
			println!("Starting population of {} filtered by top {} exception groups to {}", start_population_len, top_exception_groups, filtered_population_len);
		}
		else {
			println!("Starting population of {}", start_population_len);
		}
		// spawn the child threads
		for i in 0..threads {
			let arc_clone = Arc::clone(&arc);
			let mut child_frontier:Vec<DigitChain> = Vec::new();
			
			while child_frontiers[i].len() > 0 {
				let digit = child_frontiers[i].pop().unwrap();
				child_frontier.push(digit);
			}
			// attempt to deallocate and replace the child frontier vec once it's empty
			child_frontiers[i] = Vec::new();
			let handle = thread::spawn(move || {
				let result = if push_left {
					thread_step_left(max_exceptions, &child_frontier)
				}
				else {
					thread_step_right(max_exceptions, &child_frontier)
				};
				if result.len() != 0 {
					let mut c_r = arc_clone.lock().unwrap();
					(*c_r)[i] = result;
				}
			});
			handles.push(handle);
		}
		// execute batch
		while handles.len() > 0 {
			let handle = handles.remove(0);
			handle.join().unwrap();
		}
		// move the results back out of the child output vectors and into 
		// the working set for the next round.
		let mut runresult = arc.lock().unwrap();
		for i in 0..threads {
			while runresult[i].len() > 0 {
				let res = runresult[i].pop().unwrap();
				if best.cmp(&res) < 0 {
					best = res.copy();
				}
				population.push(res);
			}
			// attempt to deallocate and replace the vec once it's empty
			runresult[i] = Vec::new();
		}
		let duration = instant.elapsed();
		println!("Digit {} completed in {:?} with next population size {}", digits, duration, population.len());
		instant = Instant::now();
	}
	return best;
}

#[cfg(test)]
mod tests {
	use super::*;
	
	#[test]
	fn test_digitchain_push_left() {
		let mut d = DigitChain::new();
		let mut ctx = BigNumContext::new().unwrap();
		let push_left = false;
		d.push_ctx(7, push_left, &mut ctx);
		d.push_ctx(2, push_left, &mut ctx);
		assert_eq!(d.to_dec_string(), "72");
	}
	#[test]
	fn test_digitchain_push_right() {
		let mut d = DigitChain::new();
		let mut ctx = BigNumContext::new().unwrap();
		let push_left = true;
		d.push_ctx(7, push_left, &mut ctx);
		d.push_ctx(2, push_left, &mut ctx);
		assert_eq!(d.to_dec_string(), "27");
	}
	#[test]
	fn test_digitchain_exceptions() {
		let mut d = DigitChain::new();
		let mut ctx = BigNumContext::new().unwrap();
		let push_left = false;
		d.push_ctx(7, push_left, &mut ctx);
		d.push_ctx(2, push_left, &mut ctx);
		assert_eq!(d.exceptions(), 1);
	}
	#[test]
	fn test_digitchain_length() {
		let mut d = DigitChain::new();
		let mut ctx = BigNumContext::new().unwrap();
		let push_left = true;
		d.push_ctx(1, push_left, &mut ctx);
		d.push_ctx(2, push_left, &mut ctx);
		d.push_ctx(3, push_left, &mut ctx);
		assert_eq!(d.len(), 3);
	}
	
	#[test]
	fn test_largest_prime_chain_no_exceptions() {
		let start_pop = init_population();
		let result = challenge(0, 4, false, 1, start_pop, false);
		assert_eq!(result.to_dec_string(), "73939133");
	}
	#[test]
	fn test_largest_reverse_prime_chain_no_exceptions() {
		let start_pop = init_population();
		let result = challenge(0, 4, false, 1, start_pop, true);
		assert_eq!(result.to_dec_string(), "357686312646216567629137");
	}
	#[test]
	fn test_largest_prime_chain_2_exceptions_filter_2() {
		let start_pop = init_population();
		let result = challenge(2, 4, true, 2, start_pop, false);
		assert_eq!(result.to_dec_string(), "238339393693993337");
	}
	#[test]
	fn test_largest_reverse_prime_chain_3_exception_filter_2() {
		let start_pop = init_population();
		let result = challenge(3, 4, true, 2, start_pop, true);
		assert_eq!(result.to_dec_string(), "1323136248319687995918918997653319693967");
	}
}
