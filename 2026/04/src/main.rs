use std::collections::HashSet;
use std::sync::{Arc,Mutex};
use std::thread;
use algebraeon::nzq::{Rational, traits::{Floor}};
use algebraeon::rings::matrix::Matrix;
use clap::{Arg, ArgAction, Command};
use indicatif::{ProgressBar,ProgressStyle};

/// Number of seconds in a full cycle of the clock
const SECONDS_PER_CLOCK_CYCLE:u32 = 43200;
/// Number of hands on the clock
const NUM_HANDS:usize = 3;
/// Enum representing the individual hands of the clock
#[derive(Debug, Copy, Clone, PartialEq)]
enum ClockHand {
	S,
	M,
	H
}
/// Represents a 43200 second analog clock with parameters for numbers of 
/// seconds per minute `s`, numbers of minutes per hour `m` and number of 
/// hours per full cycle of the clock `h`.
#[derive(Debug, Copy, Clone, Hash, Eq, PartialEq)]
pub struct Clock {
    /// Number of hours for a full rotation of the hours hand.
    pub h:u32,
    /// Number of minutes for a full rotation of the minutes hand.
    pub m:u32,
    /// Number of seconds for a full rotation of the seconds hand.
    pub s:u32
}
impl Clock {
    /// Returns a new `Clock` with parameters `h`,`m`,`s`.
    pub fn new(h:u32, m:u32, s:u32) -> Clock {
        assert!(h > 1, "Invalid H ({}) M ({}) S ({}) provided. H must be greater than 1", h,m,s);
        assert!(h <= m && m <= s, "Invalid H ({}) M ({}) S ({}) provided. H <= M <= S required", h,m,s);
        assert!(h*m*s == SECONDS_PER_CLOCK_CYCLE, "Invalid H ({}) M ({}) S ({}) provided. Product is {} rather than the required {}", h,m,s,h*m*s, SECONDS_PER_CLOCK_CYCLE);
        return Clock{h,m,s};
    }
    /// Returns the set of all possible clocks with distinct `h`,`m`,`s`.
    pub fn possible_clocks() -> HashSet<Clock> {
        let mut clocks = HashSet::new();
        for s in 1..=SECONDS_PER_CLOCK_CYCLE {
            if SECONDS_PER_CLOCK_CYCLE % s != 0 {
                continue;
            }
            let m_max = SECONDS_PER_CLOCK_CYCLE/s;
            for m in 1..=m_max {
                if SECONDS_PER_CLOCK_CYCLE % (m*s) != 0 {
                    continue;
                }
                let h = SECONDS_PER_CLOCK_CYCLE/(m*s);
                if 1 < h && h <= m && m <= s {
                    clocks.insert(Clock::new(h,m,s));
                }
            }
        }
        return clocks;
    }
    /// Find pairs of moments which produce hand positions which are equivalent 
    /// under rotation on the face of the clock and return the size of the set 
    /// of all undeducible moments and the provided `result_id` as a tuple.
    pub fn undeducible_moments(&self, result_id:usize) -> (usize, usize) {
        let mut result_set:HashSet<Rational> = HashSet::new();
        // All possible pairings of hands for times with undeducible hand 
        // positions. Note that the s_1 = s_2 + C, m_1 = m_2 + C, h_1 = h_2 + C
        // pairing has no solutions.
        let eqn_pairs = vec![
                vec![(ClockHand::S, ClockHand::S), (ClockHand::M, ClockHand::M), (ClockHand::H, ClockHand::H)],
                vec![(ClockHand::S, ClockHand::S), (ClockHand::M, ClockHand::H), (ClockHand::H, ClockHand::M)],
                vec![(ClockHand::S, ClockHand::M), (ClockHand::M, ClockHand::S), (ClockHand::H, ClockHand::H)],
                vec![(ClockHand::S, ClockHand::M), (ClockHand::M, ClockHand::H), (ClockHand::H, ClockHand::S)],
                vec![(ClockHand::S, ClockHand::H), (ClockHand::M, ClockHand::S), (ClockHand::H, ClockHand::M)],
                vec![(ClockHand::S, ClockHand::H), (ClockHand::M, ClockHand::M), (ClockHand::H, ClockHand::S)],
            ];
        let s_coefficient = Rational::from_integers(1,self.s as i128);
        let m_coefficient = Rational::from_integers(1,(self.s*self.m) as i128);
        let h_coefficient = Rational::from_integers(1,(self.s*self.m*self.h) as i128);
        let one = Rational::from_integers(1,1);
        let neg_one = Rational::from_integers(-1,1);
        for pair in eqn_pairs {
            // Compose the matrix for the linear system for the given pairing
            // of hands and the floored terms for the right-hand side of the
            // equations
            let mut left_hand_terms:Vec<Vec<Rational>> = Vec::new();
            let mut right_hand_terms:Vec<Vec<Rational>> = Vec::new();
            for i in 0..NUM_HANDS {
                let mut left_terms = Vec::new();
                let mut right_terms = Vec::new();
                // Add the t_1 left and right hand (floor) terms
                match pair[i].0 {
                    ClockHand::S => {
                        left_terms.push(s_coefficient.clone());
                        right_terms.push(s_coefficient.clone());
                    },
                    ClockHand::M => {
                        left_terms.push(m_coefficient.clone());
                        right_terms.push(m_coefficient.clone());
                    },
                    ClockHand::H => {
                        left_terms.push(h_coefficient.clone());
                        right_terms.push(h_coefficient.clone());
                    },
                }
                // Add the t_2 left and right hand (floor) terms
                match pair[i].1 {
                    ClockHand::S => {
                        left_terms.push(&neg_one * &s_coefficient);
                        right_terms.push(s_coefficient.clone());
                    },
                    ClockHand::M => {
                        left_terms.push(&neg_one * &m_coefficient);
                        right_terms.push(m_coefficient.clone());
                    },
                    ClockHand::H => {
                        left_terms.push(&neg_one * &h_coefficient);
                        right_terms.push(h_coefficient.clone());
                    },
                }
                // Add the C term
                left_terms.push(&neg_one * &one);
                
                left_hand_terms.push(left_terms);
                right_hand_terms.push(right_terms);
            }            
            let a = Matrix::<Rational>::from_rows(left_hand_terms.clone());
            let determinant = a.det().unwrap();
            // If the determinant of the linear system is zero, we have either 
            // no solutions or infinite solutions. Since the challenge answers
            // are finite, it must be no solutions.
            if determinant == Rational::ZERO {
                continue;
            }
            let inverse = Matrix::inv(&a).unwrap();
            // Iterate over all possible integer values for floored terms in 
            // the three equations, and find solutions to the resulting systems
            // of equations using the matrix inverse. Note that the minimum 
            // granularity needed to cover all floored terms is `s`.
            for t_1_val in (0..SECONDS_PER_CLOCK_CYCLE).step_by((self.s) as usize) {
                for t_2_val in (0..SECONDS_PER_CLOCK_CYCLE).step_by((self.s) as usize) {
                    // Calculate the b vector from the floor terms on the right
                    // hand side of the equation.
                    let val_0 = (&right_hand_terms[0][0] * Rational::from(t_1_val)).floor() - (&right_hand_terms[0][1] * Rational::from(t_2_val)).floor();
                    let val_1 = (&right_hand_terms[1][0] * Rational::from(t_1_val)).floor() - (&right_hand_terms[1][1] * Rational::from(t_2_val)).floor();
                    let val_2 = (&right_hand_terms[2][0] * Rational::from(t_1_val)).floor() - (&right_hand_terms[2][1] * Rational::from(t_2_val)).floor();
                    let b_vec = vec![val_0.clone(), val_1.clone(), val_2.clone()];
                    let b:Matrix<Rational> = Matrix::from_col(b_vec);
                    let result = Matrix::mul(&inverse, &b).unwrap();
                    let t_1 = r_mod(result.at(0,0).unwrap(), SECONDS_PER_CLOCK_CYCLE);
                    let t_2 = r_mod(result.at(1,0).unwrap(), SECONDS_PER_CLOCK_CYCLE);
                    if t_1 != t_2 {
                        result_set.insert(t_1.clone());
                        result_set.insert(t_2.clone());
                    }
                }
            }
        }
        return (result_set.len(), result_id);
    }
}

/// Return the smallest non-negative residue of `val` divided by `modulus`
pub fn r_mod(val:&Rational, modulus:u32) -> Rational {
    let mut v = (*val).clone();
    let m = Rational::from_integers(modulus as i128,1);
    if v < Rational::ZERO {
        v += &m * Rational::from(-(&v/&m).floor());
    }
    if v < m {
        return v;
    }
    v -= &m *  Rational::from((&v/&m).floor());
    return v;
}
/// Calculate the number of undeducible moments across all possible clocks and 
/// return the clock and moment count for the clock with the greatest count in 
/// the set.
fn bonus_solution(threads:usize) -> (Clock, usize) {
    let clocks:Vec<Clock>;
    clocks = Vec::from_iter(Clock::possible_clocks().into_iter());
    let mut clock_results:Vec<usize> = vec![0;clocks.len()];
    println!("Searching for undeducible instants on {} clock(s) with {} worker threads...", clocks.len(), threads);
    let mut child_results:Vec<(usize, usize)> = Vec::new();
    for _i in 0..threads {
        child_results.push((0,0));
    }
    let mut handles = Vec::new();
    let mut added = 0;
    let results_arc = Arc::new(Mutex::new(child_results));
    let mut finished = false;
    // Initialize a progress bar to display calculation progress.
    let bar = ProgressBar::new((clocks.len()) as u64);
	bar.set_style(ProgressStyle::with_template("[{elapsed_precise}] {bar:40} {percent}%").unwrap());
    bar.inc(0);
    // Create batched worker threads for calculating undeducible moments of
    // each clock in the set in parallel.
    let mut clock_index = 0;
    while clock_index < clocks.len() {
        for _ in 0..threads {
            if clock_index >= clocks.len() {
                finished = true;
                break;
            }
            let results_arc_clone = Arc::clone(&results_arc);
            let clock_clone = clocks[clock_index].clone();
            let handle = thread::spawn( move || {
                let thread_result = clock_clone.undeducible_moments(clock_index);
                let mut c_r = results_arc_clone.lock().unwrap();
                (*c_r)[added] = thread_result;
            });
            handles.push(handle);
            added += 1;
            clock_index += 1;
        }
        if added == threads {
            // Execute the batch
            while handles.len() > 0 {
                let handle2 = handles.remove(0);
                handle2.join().unwrap();
            }
            let batchresult = results_arc.lock().unwrap();
            // Add the worker thread results to the result list
            for i in 0..added {
                clock_results[batchresult[i].1] = batchresult[i].0;
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
        // Add the worker thread results to the result list
        for i in 0..added {
            clock_results[batchresult[i].1] = batchresult[i].0;
            bar.inc(1);
        }
    }
    // Clear the progress bar
    bar.finish_and_clear();
    // Return the clock and count for the greatest count in the results
    let max_index = clock_results
        .iter()
        .enumerate()
        .max_by(|(_, a), (_, b)| a.cmp(b))
        .map(|(index, _)| index).unwrap();
    return (clocks[max_index], clock_results[max_index]);
}
fn main() {
    println!("\n######## Ponder This Challenge - April 2026 ########");
    let command = Command::new("apr2026").max_term_width(80)
        .about("Solver for the Ponder This April 2026 challenge.")
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
    if bonus {
        let bonus_result = bonus_solution(threads);
        println!("Bonus solution: A clock with H = {}, M = {}, S = {} has {} undeducible moments", bonus_result.0.h, bonus_result.0.m, bonus_result.0.s, bonus_result.1);
    }
    else {
        let main_clock = Clock::new(12,60,60);
        let main_result = main_clock.undeducible_moments(0);
        println!("Main solution: A clock with H = {}, M = {}, S = {} has {} undeducible moments", main_clock.h, main_clock.m, main_clock.s, main_result.0);
    }
}
