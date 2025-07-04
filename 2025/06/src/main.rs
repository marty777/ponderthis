
mod board;
use board::{Board, Coord};
use std::time::{Instant};
use clap::{Arg, ArgAction, Command};

fn main() {
    println!("\n######## Ponder This Challenge - June 2025 ########");
	let command = Command::new("jun2025").max_term_width(80)
					.about("Solver for the Ponder This June 2025 challenge.")
                    .arg(Arg::new("bonus").help("Calculate bonus challenge solution").short('b').long("bonus").action(ArgAction::SetTrue))
                    .arg(Arg::new("pattern").help("Use heuristic patterns in solution").short('p').long("pattern").action(ArgAction::SetTrue))
                    .arg(Arg::new("gif").help("Export solution as an animated GIF").short('g').long("gif").value_name("PATH"));
	let args = command.get_matches();	
	let bonus = args.get_flag("bonus");
	let use_pattern = args.get_flag("pattern");
	let gif:bool;
	let gif_path:String;
	if let Some(path) = args.get_one::<String>("gif") {
		gif = true;
		gif_path = path.to_string();
	}
	else {
		gif = false;
		gif_path = "".to_owned();
	}
    let start_instant = Instant::now();
	if bonus {
		let bonus_board = Board::new(10, Coord::new(4,4));
		let bonus_solution = bonus_board.solve_bonus(use_pattern);
		match bonus_solution {
			Ok(path) => {
                match bonus_board.validate(&path) {
                    Ok(path_string) => {
                        println!("Bonus solution:\t{}", path_string);
                        if gif {
                            bonus_board.to_gif(&path, gif_path.as_str(), None, None, true);
                        }
                    }
                    Err(err) => { 
                        println!("Unable to solve bonus challenge: {}", err);
                        return;
                    }
                }
            }
			Err(err) => {
				println!("Unable to solve bonus challenge: {}", err);
				return;
			}
		}
	}
	else {
		let main_board = Board::new(20, Coord::new(0,0));
		let main_solution = main_board.solve_main(use_pattern);
		match main_solution {
			Ok(path) => {
                match main_board.validate(&path) {
                    Ok(path_string) => {
                        println!("Main solution:\t{}", path_string);
                        if gif {
                            main_board.to_gif(&path, gif_path.as_str(), None, None, true);
                        }
                    }
                    Err(err) => { 
                        println!("Unable to solve main challenge: {}", err);
                        return;
                    }
                }
            }
			Err(err) => {
				println!("Unable to solve main challenge: {}", err);
				return;
			}
		}
	}
	println!("\nTotal execution time: {:?}", start_instant.elapsed());
}