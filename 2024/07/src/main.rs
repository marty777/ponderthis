pub mod tile;
use clap::{Arg, Command};
use std::time::{Instant};

fn main() {
    let command = Command::new("may2024").max_term_width(80)
        .about("Solver for the Ponder This July 2024 challenge.")
        .arg(Arg::new("threads").help("Set maximum number of worker threads").short('t').long("threads").value_name("THREADS").default_value("4"));
    let args = command.get_matches();    
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

    println!("\n######## Ponder This Challenge - July 2024 ########");
    let start_instant = Instant::now();    
    println!("\nSearching for main challenge solution...\n");
    let main_challenge_best_state = tile::solution(false, threads);
    main_challenge_best_state.print();
    println!("\nSearching for bonus challenge solution...\n");
    let bonus_challenge_best_state = tile::solution(true, threads);
    bonus_challenge_best_state.print();
    println!("\nTotal execution time: {:?}", start_instant.elapsed());
}