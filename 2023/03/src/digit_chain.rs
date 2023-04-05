
use openssl::bn::BigNum;
use openssl::bn::BigNumContext;

/// A representation of a prime digit chain with exceptions.
#[derive(Eq, PartialEq)]
pub struct DigitChain {
	/// OpenSSL BIGNUM object storing the integer value of the digit chain.
	bignum:BigNum,
	/// Number of non-prime exceptions in the digit chain.
	exceptions:usize,
	/// Number of decimal digits in the chain.
	len:usize
}

impl DigitChain {
	/// Returns a new digit chain with no digits added.
	pub fn new() -> DigitChain {
		DigitChain { bignum: BigNum::new().unwrap(), exceptions: 0, len:0}
	}
	/// Creates a copy of this digit chain
	pub fn copy(&self) -> DigitChain {
		let mut copy:DigitChain = DigitChain::new();
		copy.bignum = self.bignum.to_owned().unwrap();
		copy.len = self.len;
		copy.exceptions = self.exceptions;
		return copy;
	}
	
	/// Comparison function returning -1 if self < other, 0 if self == other, 1 if self > other.
	///
	/// # Arguments
	/// 
	/// * 'other' - The digit chain to compare against.
	pub fn cmp(&self, other:&DigitChain) -> i32{
		if self.bignum < other.bignum {
			return -1;
		}
		else if self.bignum == other.bignum {
			return 0;
		}
		return 1;
	}
	
	/// The number of decimal digits present in the digit chain.
	pub fn len(&self) -> usize {
		return self.len
	}
	
	/// The number of non-prime exceptions in the digit chain.
	pub fn exceptions(&self) -> usize {
		return self.exceptions;
	}
	
	/// Prepend the provided digit value to the digit chain.
	///
	/// # Arguments
	/// 
	/// * 'value' - the integer value of the decimal digit to prepend.
	/// * 'ctx' - A shared OpenSSL BigNumContext object.
	///
	/// # Panics
	/// Panics if 'value' is greater than 9.
	pub fn push_left_ctx(&mut self, value:u16, ctx: &mut BigNumContext) {
		if value > 9 {
			panic!("The provided value {} cannot be added as a single decimal digit", value);
		}
		if self.bignum == BigNum::from_u32(0).unwrap() {
			let result = self.bignum.add_word(value as u32);
			if result.is_err() {
				return;
			}
		}
		else {
			let mut val:BigNum = BigNum::new().unwrap();
			let mut ten:BigNum = BigNum::new().unwrap();
			let mut pow:BigNum = BigNum::new().unwrap();
			ten.add_word(10).unwrap();
			pow.add_word(self.len as u32).unwrap();
			val.exp(&ten, &pow, ctx).unwrap();
			val.mul_word(value as u32).unwrap();
			let orig = self.bignum.to_owned().unwrap();
			self.bignum.checked_add(&orig, &val).unwrap();
		}
		self.len += 1;
	}
	
	/// Append the provided digit value to the digit chain.
	/// 
	/// # Arguments
	///
	/// * 'value' - the integer value of the decimal digit to append.
	/// 
	/// # Panics
	/// Panics if 'value' is greater than 9.
	pub fn push_right(&mut self, value:u16) {
		if value > 9 {
			panic!("The provided value {} cannot be added as a single decimal digit", value);
		}
		self.bignum.mul_word(10).unwrap();
		self.bignum.add_word(value as u32).unwrap();
		self.len += 1;
	}
	
	/// Append or prepend the provided decimal digit to the digit chain.
	/// 
	/// # Arguments
	///
	/// * 'value' - the integer value of the decimal digit to append or prepend.
	/// * 'push_left' - Pass false to append the digit on the right of the digit chain, or true to prepend the digit on the left.
	/// * 'ctx' - A shared OpenSSL BigNumContext object.
	/// 
	/// # Panics
	/// Panics if 'value' is greater than 9.
	pub fn push_ctx(&mut self, value:u16, push_left:bool, ctx: &mut BigNumContext) {
		if value > 9 {
			panic!("The provided value {} cannot be added as a single decimal digit", value);
		}
		if push_left {
			self.push_left_ctx(value, ctx);
		}
		else {
			self.push_right(value);
		}
		if !self.is_prime_ctx(ctx) {
			self.exceptions += 1;
		}
	}
	
	/// Returns a string of the decimal representation of the digit chain together with the current number of exceptions.
	/// 
	/// # Examples
	/// "73939133 - 0 exceptions"
	pub fn to_string(&self) -> String {
		let suffix = if self.exceptions == 1 {
			""
		}
		else {
			"s"
		};
		return self.bignum.to_dec_str().unwrap().to_string() + " - " + &self.exceptions.to_string() + " exception" + suffix;
	}
	
	/// Returns a string of the decimal representation of the digit chain.
	pub fn to_dec_string(&self) -> String {
		return self.bignum.to_dec_str().unwrap().to_string();
	}
	
	/// Returns true if the digit chain represents a prime integer, according to the OpenSSL library BN_is_prime_fasttest method.
	///
	/// # Arguments 
	///
	/// * 'ctx' - A shared OpenSSL BigNumContext object.
	pub fn is_prime_ctx(&self, ctx: &mut BigNumContext) -> bool {
		// Passing nchecks as 0 should perform the default number of Miller-Rabin
		// tests for the given integer size. Trial division by small primes is 
		// enabled.
		return self.bignum.is_prime_fasttest(0, ctx, true).unwrap();
	}
	
	/// Prints each step in the digit chain
	/// 
	/// # Arguments
	/// 
	/// * 'push_left' - Pass false if the digit chain should be treated as having digits appended on the right, true if prepended on the left.
	pub fn print_trace(&self, push_left:bool) {
		let digits:Vec<char> =  self.bignum.to_dec_str().unwrap().to_string().chars().collect();
		let mut ctx = BigNumContext::new().unwrap();
		let mut digit_chain = DigitChain::new();
		println!("Trace {}", self.to_string());
		for i in 0..digits.len() {
			if push_left {
				let digit = (digits[digits.len() - i - 1].to_string()).parse::<u16>().unwrap();
				digit_chain.push_ctx(digit, push_left, &mut ctx);
			}
			else {
				let digit = (digits[i].to_string()).parse::<u16>().unwrap();
				digit_chain.push_ctx(digit, push_left, &mut ctx);
			}
			println!("\t{}", digit_chain.to_string());
		}
		let suffix = if self.len == 1 {
			""
		}
		else {
			"s"
		};
		println!("Length: {} digit{}", self.len(), suffix);
	}
}