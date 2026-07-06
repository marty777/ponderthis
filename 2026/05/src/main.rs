use clap::{Arg, Command};
use indicatif::{ProgressBar,ProgressStyle};
use std::cmp::{Ordering,max};

/// Returns an ordered list of primes less than `limit`.
pub fn eratosthenes(limit:i128) -> Vec<i128> { 
    let mut local_limit = limit;
    if local_limit < 2 {
        local_limit = 2;
    }
    let mut primes = Vec::new();
    let mut sieve = vec![false; local_limit as usize];
    let mut increment = 2;
    loop {
        for i in (2*increment..local_limit).step_by(increment as usize) {
            sieve[i as usize] = true;
        }
        let mut done = true;
        for i in (increment+1)..local_limit {
            if !sieve[i as usize] {
                increment = i;
                done = false;
                break;
            }
        }
        if done {
            break;
        }
    }
    for i in 2..local_limit {
        if !sieve[i as usize] {
            primes.push(i);
        }
    }
    return primes;
}

/// Re-implementation of a Maple procedure for computing Landau's function 
/// g(`n`) given by Deléglise, Nicolas and Zimmerman in their 2008 paper 
/// "Landau’s function for one million billions", section 2.1. I think this is 
/// the algorithm described by Nicolas in the 1969 paper "Calcul de l’ordre 
/// maximum d’un élément du groupe symétrique S_n" with a refinement of the 
/// upper bound for the greatest prime divisor of g(`n`) proven by Jon Grantham
/// in 1995. It necessarily includes calculation of intermediate g(x) for all 
/// 0 <= x <= `n`.
/// 
/// Due to the magnitudes of integers involved, the logarithms and modular 
/// values of calculations are stored rather than full arbitrary-precision 
/// integers. The returned result is equal to g(`n`) mod `modulus`. This 
/// method is not suitable for `n` substantially larger than 10^8.
fn basic_landau_function_mod(n:usize, modulus:usize) -> Result<usize, String> {
    let primes = eratosthenes(max(6,n) as i128);
    // Stores intermediate ln(g(x)), 0 <= x <= n for comparison of magnitudes
    let mut g_log:Vec<f64> = vec![0.0; n+1];
    // Stores intermediate g(x) % modulus, 0 <= x <= n 
    let mut g_mod:Vec<usize> = vec![1; n+1];
    // Determine the maximum possible prime divisor of g(n) using the bound 
    // proved by Jon Grantham. The bound is only valid for n >= 5, so handle
    // smaller cases manually
    let p_max:i128 = match n.cmp(&4) {
        Ordering::Greater => {
            let n_f64 = n as f64;
            (1.328 * (n_f64 * n_f64.ln()).sqrt()).ceil() as i128
        },
        _ => 3
    };
    // Find the index of the maximum prime divisor in the ordered list of 
    // primes and initialize a progress bar.
    let mut p_max_index = 0;
    for i in 0..primes.len() {
        if primes[i] > p_max {
            break;
        }
        p_max_index = i;
    }
    let bar = ProgressBar::new((p_max_index + 1) as u64);
	bar.set_style(ProgressStyle::with_template("[{elapsed_precise}] {bar:40} {percent}%").unwrap());
    bar.inc(0);
    for p_index in 0..=p_max_index {
        let p = primes[p_index] as usize;
        let p_log = (p as f64).ln();
        for n_1 in (p..=n).rev() {
            let mut k = 1;
            let mut p_k = p;
            let mut p_k_log = p_log;
            while p_k <= n_1 {
                // a = p_k * g[n_1 - p_k] if working with full integers
                let a_log = p_k_log + g_log[n_1 - p_k];
                if g_log[n_1] < a_log {
                    g_log[n_1] = a_log;
                    g_mod[n_1] = ((p_k % modulus) * g_mod[n_1 - p_k]) % modulus;
                }
                k += 1;
                p_k_log = (k as f64) * p_log;
                // Check for possibility of overflow on p_k
                let next_p_k = p_k.checked_mul(p);
                match next_p_k {
                    Some(val) => {
                        p_k = val
                    }
                    None => {
                        bar.finish_and_clear();
                        return Err(format!("Overflow occurred on exponentiation of {}^{}", p, k));
                    }
                }
            }
        }
        bar.inc(1);
    }
    bar.finish_and_clear();
    return Ok(g_mod[n]);
}

fn main() {
    println!("\n######## Ponder This Challenge - May 2026 ########");
    let command = Command::new("may2026").max_term_width(80)
        .about("Solver for the Ponder This May 2026 challenge.")
        .arg(Arg::new("number").help("The value of N to calculate g(N) to").short('n').long("number").value_name("NUMBER").default_value("1000000"))
        .arg(Arg::new("modulus").help("The modulus to calculate g(N) under").short('m').long("modulus").value_name("MODULUS").default_value("1000000007"));
                    
    let args = command.get_matches(); 
    let mut number = 0;
    let mut modulus = 1;
    if let Some(number_arg) = args.get_one::<String>("number") {
        match number_arg.parse::<usize>() {
            Ok(n) => {
                number = n;
            },
            Err(_) => {
                println!("Could not parse NUMBER argument '{}' as an integer.", number_arg);
                std::process::exit(2);
            }
        }
    }
    if let Some(modulus_arg) = args.get_one::<String>("modulus") {
        match modulus_arg.parse::<usize>() {
            Ok(m) => {
                modulus = m;
                if modulus < 1 {
                    println!("MODULUS must be at least 1 ({} provided)", modulus_arg);
                    std::process::exit(2);
                }
            },
            Err(_) => {
                println!("Could not parse MODULUS argument '{}' as an integer.", modulus_arg);
                std::process::exit(2);
            }
        }
    }
    println!("Computing g({}) mod {}...", number, modulus);
    let result = basic_landau_function_mod(number, modulus);
    match result {
        Ok(result_val) => {
            println!("g({}) mod {} = {}", number, modulus, result_val);
        },
        Err(result_err) => {
            println!("Error: {}", result_err);
        }
    }
}
