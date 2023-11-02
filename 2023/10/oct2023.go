 package main
 
 import (
	"flag"
	"fmt"
	"strconv"
	"math/big"
	"time"
	"sync"
)

// Converts a big.Int into an array of its base-10 digits. Note that sign is 
// ignored.
func Digits(n *big.Int) []int {
	n1 := new(big.Int).Set(n)
	if n1.Sign() == -1 {
		n1.Neg(n1)
	}
	s := n1.Text(10)
	result := make([]int, len(s))
	for i:=0; i < len(s); i++ {
		d, err := strconv.Atoi(string(s[i]))
		if err != nil {
			panic(fmt.Sprintf("Unable to parse digits on string %s at position %d\n", s, i));
		}
		result[i] = d
	}
	return result
}

// Given an array of base-10 digits, produces a big.Int
func FromDigits(digits []int) *big.Int {
	s := ""
	for i:=0; i < len(digits); i++ {
		s = s + fmt.Sprintf("%d", digits[i])
	}
	result := new(big.Int)
	result, ok := result.SetString(s, 10)
	if ok {
		return result;
	} else {
		return  new(big.Int).SetInt64(0);
	}
}

// Returns true iff the base-10 representation of the provided big.Int is a 
// palindrome
func IsPalindrome(n *big.Int) bool {
	digits := Digits(n)
	reverse_digits := make([]int, len(digits))
	for i:=0; i < len(digits); i++ {
		reverse_digits[i] = digits[len(digits) - 1 - i]
	}
	for i:=0; i < len(digits); i++ {
		if(reverse_digits[i] != digits[i]) {
			return false
		}
	}
	return true
}

// Given the lengths x and y and a sequence of digits b_digits, formats and 
// returns an array of digits of a potential asymmetric root of a palindromic 
// square
func AsymmetricRootGenerator(x int, y int, b_digits []int) []int {
	var length = 5 + (2 * x) + (2 * y)
	var b_digits_length = len(b_digits)
	length += 2 * b_digits_length 
	
	result := make([]int, length)
	pos := 0;
	// 1
	result[pos] = 1
	pos += 1
	// x0
	for i:= pos; i < pos + x; i++ {
		result[i] = 0
	}
	pos += x
	// B
	for i := 0; i < b_digits_length; i++ {
		result[pos + i] = b_digits[i]
	}
	pos += b_digits_length
	// 0
	result[pos] = 0
	pos += 1
	// y9
	for i:= pos; i < pos + y; i++ {
		result[i] = 9
	}
	pos += y
	// 9
	result[pos] = 9
	pos += 1
	// y0
	for i:= pos; i < pos + y; i++ {
		result[i] = 0
	}
	pos += y
	// 1
	result[pos] = 1
	pos += 1
	// B'
	for i := 0; i < b_digits_length; i++ {
		result[pos + i] = b_digits[b_digits_length - i - 1]
	}
	pos += b_digits_length
	// x0
	for i:= pos; i < pos + x; i++ {
		result[i] = 0
	}
	pos += x
	// 1
	result[pos] = 1
	pos += 1
	return result;
}

// If any asymmetric roots with the given number of digits and B sequence 
// length produce palindromic squares and are congruent to bigRemainder (mod 
// bigModulus) prints the values to stdout and sends "true" on the channel c.
// If not, sends "false" on channel r.
func AsymmetricRootGenerator_Thread(num_digits int, b_length int, bigRemainder *big.Int, bigModulus *big.Int, c chan bool, wg *sync.WaitGroup) {
	defer wg.Done()
	if (num_digits - 5 - (b_length * 2)) % 4 != 0 || (num_digits - 5 - (b_length * 2)) < 0 {
		c <- false
		return
	}
	// group_length is the base length of x and y groups
	group_length := (num_digits - 5 - (b_length * 2)) / 4
	// test all possible B groups. B is a sequence of digits of length 
	// b_length, with either one or two '1' digits and all others '0'.
	// At present, test all possible arrangements of 1s in B. There may be 
	// arrangements that make a palindromic square impossible and can be 
	// skipped.
	b := make([]int, b_length)
	for i:=0; i <= b_length; i++ {
		for j:=i+1; j <= b_length; j++ {
			var num_ones = 0
			if i > 0 {
				b[i-1] = 0
			}
			if j > 0 {
				b[j-1] = 0
			}
			if i < b_length {
				b[i] = 1
				num_ones += 1
			}
			if j < b_length {
				b[j] = 1
				num_ones += 1
			}
			if num_ones == 0 {
				continue
			}
			// test cases where x = y and cases where y = 0, which seems to cover all
			// distinct asymmetric root arrangements with palindromic squares
			x_length := group_length
			y_length := group_length
			n_digits := AsymmetricRootGenerator(x_length, y_length, b)
			n := FromDigits(n_digits)
			// if n is congruent to bigRemainder (mod bigModulus)
			r := new(big.Int).Mod(n, bigModulus)
			if(r.Cmp(bigRemainder) == 0 && !IsPalindrome(n)) {
				n_2 := new(big.Int).Mul(n,n)
				if IsPalindrome(n_2) {
					fmt.Printf("Found asymmetric root congruent to %s (mod %s)\n", bigRemainder, bigModulus)
					fmt.Printf("Root:\t%s\n", n)
					fmt.Printf("Square:\t%s\n", n_2)
					c <- true
					return
				}
			}
			// if num_digits % 4 == 3, test for y = 0
			if num_digits % 4 == 3 {
				x_length = 2*group_length
				y_length = 0
				n_digits = AsymmetricRootGenerator(x_length, y_length, b)
				n = FromDigits(n_digits)
				// if n is congruent to bigRemainder (mod bigModulus)
				r.Mod(n, bigModulus)
				if(r.Cmp(bigRemainder) == 0 && !IsPalindrome(n)) {
					n_2 := new(big.Int).Mul(n,n)
					if IsPalindrome(n_2) {
						fmt.Printf("Found asymmetric root congruent to %s (mod %s)\n", bigRemainder, bigModulus)
						fmt.Printf("Root:\t%s\n", n)
						fmt.Printf("Square:\t%s\n", n_2)
						c <- true
						return
					}
				}
			}
		}
	}
	c <- false
}

// Runs until one or more asymmetric roots of palindromic squares that are 
// congruent to remainder (mod modulus) are found or all asymmetric patterns 
// are exhausted for the given number of digits.
func AsymmetricRootGenerator_Threaded(n_digits, n_threads int, remainder, modulus int64) bool {
	if n_digits < 11 {
		panic(fmt.Sprintf("Too few digits %d in AysncGenerator2 (minimum 11)", n_digits));
	}
	fmt.Printf("Searching for an asymmetric root with a palindromic square and %d digits congruent to %d (mod %d)...\n", n_digits, remainder, modulus)
	bigModulus := big.NewInt(modulus)
	bigRemainder := big.NewInt(remainder)
	
	var wg sync.WaitGroup
	routine_results := make([]chan bool, n_threads)
	for i := 0; i < n_threads; i++ {
		routine_results[i] = make(chan bool, 1)
	}
	var numAdded = 0
	for b_length := 1; b_length < ((n_digits - 5)/2) - 1; b_length++ {
		if (n_digits - 5 - (b_length * 2)) % 4 == 0 && (n_digits - 5 - (b_length * 2)) / 4 >= 0 {
			
			if(numAdded == n_threads) {
				wg.Wait()
				for i:=0; i < numAdded; i++ {
					has_result := <- routine_results[i]
					if has_result == true {
						return true;
					}
				}
				fmt.Printf("%d%% complete\n", b_length * 100 / (((n_digits - 5)/2) - 1))
				numAdded = 0
			}
			
			wg.Add(1)
			go AsymmetricRootGenerator_Thread(n_digits, b_length, bigRemainder, bigModulus, routine_results[numAdded], &wg)
			numAdded += 1
		}
	}
	// wait for any remaining threads
	if(numAdded > 0) {
		wg.Wait()
		for i:=0; i < numAdded; i++ {
			has_result := <- routine_results[i]
			if has_result {
				return true;
			}
		}
		fmt.Printf("100%% complete\n")
	}
	return false;
}

 func getMillis() int64 {
    return time.Now().UnixNano() / int64(time.Millisecond)
}
 
 func main() {
	modulusPtr := flag.Int64("m", 1201, "The modulus to test for congruence in asymmetric roots.")
	remainderPtr := flag.Int64("r", 845, "The remainder to test for congruence in asymmetric roots.")
	numDigitsPtr := flag.Int("d", 11, "The number of digits used to generate asymmetric roots")
	threadsPtr := flag.Int("t", 4, "The number of worker threads used in generating asymmetric roots.")
	flag.Parse();
	if *numDigitsPtr < 11 {
		fmt.Printf("The entered number of digits %d is too small and must be greater than 10\n", *numDigitsPtr)
		flag.Usage()
		return
	}
	if *numDigitsPtr % 2 == 0 {
		fmt.Printf("The entered number of digits %d is even. No asymmetric roots of palindromic squares exist with an even number of digits.\n", *numDigitsPtr)
		flag.Usage()
		return
	}
	if *modulusPtr < 1 {
		fmt.Printf("The entered modulus %d is too small and must be greater than zero\n", *modulusPtr)
		flag.Usage()
		return
	}
	if *remainderPtr < 0 {
		fmt.Printf("The entered remainder %d cannot be negative\n", *remainderPtr)
		flag.Usage()
		return
	}
	if *threadsPtr < 1 {
		fmt.Printf("The entered number of worker threads %d must be greater than zero\n", *threadsPtr)
		flag.Usage()
		return
	}
	
	fmt.Printf("\n######## Ponder This Challenge - October 2023 ########\n\n")
	startTime := getMillis()
	success := AsymmetricRootGenerator_Threaded(*numDigitsPtr, *threadsPtr, *remainderPtr, *modulusPtr);
	if success {
		fmt.Printf("A congruent asymmetric root of a palindromic square with %d digits has been found\n", *numDigitsPtr)
	} else {
		fmt.Printf("No congruent asymmetric roots of palindromic squares found for %d digits\n", *numDigitsPtr)
	}
	endTime := getMillis()
	elapsed := endTime - startTime
	fmt.Println(fmt.Sprintf("Elapsed time : %d ms", elapsed))
}