use astro_float::{Consts,Radix,Sign,BigFloat,RoundingMode,expr,ctx::Context};
use std::time::Instant;

/// Returns the full set of decimal digits representing the greatest integer < a computed BigFloat value as a String
fn floored_decimal_string(value: &BigFloat) -> String {
	if value.is_inf_pos() {
		return String::from("Inf")
	}
	if value.is_inf_neg() {
		return String::from("-Inf")
	}
	if value.is_nan() {
		return String::from("NaN")
	}
	let mut val = value.clone();
	// We're looking for an integer < value, so if value is already a whole number subtract one
	if val.is_int() {
		let one = BigFloat::from_u64(1, val.precision().unwrap());
		val = val.sub_full_prec(&one);
	}
	let (s,m,e) = val.convert_to_radix(Radix::Dec, RoundingMode::Down).unwrap();
	let mut result = String::new();
	if s == Sign::Neg {
		result += "-";
	}
	for i in 0..e as usize {
		result += &m[i].to_string();
	}
	return result;
}

/// Returns the kth square-triangular number using Euler's formula as a BigFloat. Not suitable for very large k.
fn square_triangular_number(k:usize) -> BigFloat {
	// Create a astro_float context with precision 128, and rounding to zero.
	let precision = 128;
	let rounding_mode = RoundingMode::ToZero;
	let mut ctx = Context::new(precision, rounding_mode, Consts::new().expect("Constants cache initialized"));
	let mut term1 = expr!(17 + (12 * sqrt(2)), &mut ctx);
	let mut term2 = expr!(17 - (12 * sqrt(2)), &mut ctx);
	let two = BigFloat::from_u64(2, precision);
	let thirtytwo = BigFloat::from_u64(32, precision);
	term1 = term1.powi(k, precision, rounding_mode);
	term2 = term2.powi(k, precision, rounding_mode);
	let mut result = term1.add_full_prec(&term2);
	result = result.sub_full_prec(&two);
	return result.div(&thirtytwo, precision, rounding_mode);
}

/// Solve the main challenge by calculating the kth square-triangular number Nk from k=1 until Nk exceeds a googol
///
/// Returns the count of positive square-triangular numbers lower than a googol as a usize
fn solve_main_challenge() -> usize {
	let precision = 512;
	let rounding_mode = RoundingMode::ToZero;
	let mut googol= BigFloat::from_u64(10, precision);
	googol = googol.powi(100, precision, rounding_mode);
	let mut k = 1;
	loop {
		let n_k = square_triangular_number(k);
		if googol.cmp(&n_k).unwrap() <= 0 {
			break;
		}
		k += 1;
	}
	return k - 1;
}

/// Calculate the greatest integer k such that the kth square-triangular number Nk does not exceed a googolplex
///
/// Returns the decimal representation of k as a String
fn solve_bonus_challenge() -> String {
	// Create a astro_float context with precision 512, and rounding to zero. 512 bits of precision is sufficient for the bonus challenge
	let precision = 512;
	let rounding_mode = RoundingMode::ToZero;
	let mut ctx = Context::new(precision, rounding_mode, Consts::new().expect("Constants cache initialized"));	
	// From some algebraic manipulation of Euler's formula for square-triangular numbers, k must be less than
	// (log_10(googolplex) + log10(32)) / log10(17 + 12 * sqrt(2)). Note that log10(googolplex) = pow(10,100)
	let k_upper_bound = expr!( (pow(10,100) + log10(32))/log10(17 + (12 * sqrt(2))), &mut ctx );
	// return a string of the full decimal digits of the largest integer less than k_upper_bound
	return floored_decimal_string(&k_upper_bound);
}

fn main() {
    println!("\n######## Ponder This Challenge - August 2023 ########\n");
	let start_instant = Instant::now();
	println!("Main challenge result:\t{}",solve_main_challenge());
	println!("Bonus challenge result:\t{}",solve_bonus_challenge());
	let duration = start_instant.elapsed();
	println!("Total execution time:\t{:?}", duration);
}