
use std::collections::HashSet;
use std::sync::{Arc,Mutex};
use std::thread;
use std::time::{Instant};
use std::cmp::max;
use clap::{Arg, ArgAction, Command};
use indicatif::{ProgressBar,ProgressStyle};

/// Returns the number of digits representing `x` in base 10
fn digit_len(x:usize) -> usize {
    return (x as f64).log10().floor() as usize + 1;
}
/// Returns the set `A_x`, the distinct sums of groups of integers formed by 
/// breaking apart the decimal digits of `x` in all possible ways.
fn a(x:usize) -> HashSet<usize> {
    let ten:usize = 10;
    let digit_len = digit_len(x) as u32;
    let mut digit_sums = HashSet::new();
    digit_sums.insert(x);
    for i in 1..digit_len {
        // For each length, split x into an integer of that length and an
        // integer of the remaining digits. Recurse on the remaining 
        // integer, and add the first integer to each resulting sum from
        // the recursion. 
        let first_group = x / ten.pow(i);
        let remainder = x - (ten.pow(i) * first_group);
        let remainder_sums = a(remainder);
        for remainder_sum in remainder_sums {
            digit_sums.insert(remainder_sum + first_group);
        }
    }
    return digit_sums;
}
/// Returns the set `n` * `A_n`
fn n_dot_a_n(n:usize) -> HashSet<usize> {
    return a(n).iter().map(|x| x*n).collect();
}
/// Returns true if `n` is a member of the set `A_x`
fn n_in_a_x(n:usize,x:usize) -> bool {
    let ten:usize = 10;
    let digit_len = digit_len(x) as u32;
    if x == n {
        return true;
    }
    else {
        for i in 1..digit_len {
            let first_group = x / ten.pow(i);
            // If the first_group > n, n can't be in any of the resulting sums
            if first_group > n {
                continue;
            }
            let remainder = x - (ten.pow(i) * first_group);
            let remainder_sums = a(remainder);
            for remainder_sum in remainder_sums {
                if remainder_sum + first_group == n {
                    return true;
                }
            }
        }
    }
    return false;
}
/// Returns all integers `x` such that for any 
/// `batch_start` <= `n` <= `batch_max`, `x` is a member of  `n` * `A_n` and 
/// `n` is a member of  `A_x`
fn solution_batch(batch_start:usize, batch_max:usize) -> HashSet<usize> {
    let mut x_terms = HashSet::new();
    for n in ((batch_start)..=batch_max).step_by(9) {
        // n == 0 mod 9
        let n_dot_a_n_0 = n_dot_a_n(n);
        for x in n_dot_a_n_0 {
            if n_in_a_x(n,x) {
                x_terms.insert(x);
            }
        }
        // n + 1 == 1 mod 9
        if n + 1 <= batch_max {
            let n_dot_a_n_1 = n_dot_a_n(n+1);
            for x in n_dot_a_n_1 {
                if n_in_a_x(n+1,x) {
                    x_terms.insert(x);
                }
            }
        }
    }
    return x_terms;
}
/// Return the sum of integers `x` over 1 < `n` < `max_n` such that `x` is a 
/// member of the set `n` * `A_n` and `n` is a member of the set `A_x` using 
/// `threads` worker processes to examine the full range of sets.
fn solution(max_n:usize, threads:usize) -> usize {
    let mut x_set:HashSet<usize> = HashSet::new();
    // Cases for selecting suitable ranges of n to cover for each
    // worker thread depending on max_n.
    let thread_size:usize;
    if max_n > 1000_000 {
        thread_size = 9 * (max_n/100000*threads);
    }
    else if max_n < 100_000 {
        thread_size = max(9 * (max_n/100*threads), 1);
    }
    else {
        thread_size = 9 * (max_n/10000*threads);
    }
    println!("Summing terms to a maximum n of {} with {} worker threads...", max_n, threads);
    let mut child_results:Vec<HashSet<usize>> = Vec::new();
    for _i in 0..threads {
        child_results.push(HashSet::new());
    }
    let mut handles = Vec::new();
    let mut added = 0;
    let results_arc = Arc::new(Mutex::new(child_results));
    let mut finished = false;
    let mut batch_start = 0;
    // Initialize a progress bar to display calculation progress.
    let bar = ProgressBar::new((max_n/thread_size) as u64);
	bar.set_style(ProgressStyle::with_template("[{elapsed_precise}] {bar:40} {percent}%").unwrap());
    bar.inc(0);
    // Create batched worker threads for distributing work on examining each n 
    // in the challenge range
    loop {
        for _ in 0..threads {
            let mut thread_max = batch_start + thread_size - 1;
            if thread_max > max_n {
                thread_max = max_n;
                finished = true;
            }
            let results_arc_clone = Arc::clone(&results_arc);
            let handle = thread::spawn( move || {
                let thread_result = solution_batch(batch_start, thread_max);
                let mut c_r = results_arc_clone.lock().unwrap();
                (*c_r)[added] = thread_result;
            });
            handles.push(handle);
            added += 1;
            if finished {
                break;
            }
            batch_start += thread_size;
        }
        if batch_start > max_n {
            break;
        }
        if added == threads {
            // Execute the batch
            while handles.len() > 0 {
                let handle2 = handles.remove(0);
                handle2.join().unwrap();
            }
            let batchresult = results_arc.lock().unwrap();
            // Add any x values found in each worker thread to the main x set
            for i in 0..added {
                x_set.extend(&batchresult[i]);
                bar.inc(1);
            }
            added = 0;
        }
        if finished {
            break;
        }
    }
    // Run any remaining jobs
    if added > 0 {
        // Execute the batch
        while handles.len() > 0 {
            let handle = handles.remove(0);
            handle.join().unwrap();
        }
        let batchresult = results_arc.lock().unwrap();
        // Add any x values found in each worker thread to the main x set
        for i in 0..added {
            x_set.extend(&batchresult[i]);
            bar.inc(1);
        }
    }
    bar.finish_and_clear();
    // Return the sum of the elements of the x set
    return x_set.iter().fold(0, |acc, x| acc + x);
}

fn main() {
    println!("\n######## Ponder This Challenge - January 2026 ########");
    let command = Command::new("jan2026").max_term_width(80)
        .about("Solver for the Ponder This January 2026 challenge.")
        .arg(Arg::new("threads").help("Set maximum number of worker threads").short('t').long("threads").value_name("THREADS").default_value("4"))
        .arg(Arg::new("bonus").help("Calculate bonus challenge solution").short('b').long("bonus").action(ArgAction::SetTrue));
                    
    let args = command.get_matches();    
    let mut threads = 4;
    let bonus = args.get_flag("bonus");
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
    let main_max = 1000000;
    let bonus_max = 10000000;
    let start_instant = Instant::now();
    if bonus {
        println!("Bonus challenge solution {}", solution(bonus_max, threads));
    }
    else {
        println!("Main challenge solution {}", solution(main_max, threads));
    }
    println!("\nTotal execution time: {:?}", start_instant.elapsed());
}
