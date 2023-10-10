 package main
 
 import (
	"fmt"
	"flag"
	"math/big"
	"time"
	"strings"
	"os"
	"bufio"
	"errors"
)

type Factorizer struct {
	// A generated list of all primes below some bound
	smallPrimes	[]big.Int
	// A list of other primes encountered during runtime
	otherPrimes []big.Int
}

// Returns a list of all positive prime factors of a
func (f *Factorizer) Factorize(a *big.Int) []big.Int {
	// if a is zero
	if a.Sign() == 0 {
		return make([]big.Int, 0)
	}
	factors := make([]big.Int, 0)
	quotient :=  new(big.Int).Set(a)
	// if a is negative
	if quotient.Sign() < 0 {
		quotient = quotient.Neg(quotient)
	}
	one := new(big.Int).SetInt64(1)
	// while quotient > 1, get the next factor
	for quotient.Cmp(one) > 0 {
		factor := f.getFactor(quotient)
		factors = append(factors, factor)
		quotient.Div(quotient, &factor)
	}
    return factors
}

// Return some prime factor of n
func (f *Factorizer) getFactor(n *big.Int) big.Int {
	x_fixed := new(big.Int).SetInt64(2)
	cycle_size := new(big.Int).SetInt64(2)
	count := new(big.Int)
	x_diff := new(big.Int)
	x := new(big.Int).SetInt64(2)
	factor := new(big.Int).SetInt64(1)
	one := new(big.Int).SetInt64(1)
	zero := new(big.Int).SetInt64(0)
	two := new(big.Int).SetInt64(2)
	remainder := new(big.Int)
	if n.Cmp(one) <= 0 {
		panic(fmt.Sprintf("Invalid argument to getFactor: %s. Argument must be greater than 1", n))
	}
	// Actual factoring is slow, and approximately 1/4 of the integers 
	// encountered in the bonus challenge are prime. Test primality using 
	// Miller-Rabin and Baillie-PSW in case we can skip having to factor n.
    // For Miller-Rabin tests, the number of selected bases should be 
	// proportional to the bitlength of n. I think I'm doing something somewhat
	// close to the OpenSSL BN_is_prime spec, but robust primality testing 
	// isn't an area I'm an expert in and I may be under- or over-doing it.
	n_miller_rabin := 64
	if n.BitLen() > 1024 {
		n_miller_rabin = n.BitLen() / 16
	}
	if(n.ProbablyPrime(n_miller_rabin)) {
		factor.Set(n)
		return *factor
	} 
	// Test against our stores of known primes in case we already know a factor
	// of n.
	for i:=0; i < len(f.smallPrimes); i++ {
		if f.smallPrimes[i].Cmp(n) > 0 {
			continue
		}
		remainder.Mod(n, &f.smallPrimes[i])
		if remainder.Cmp(zero) == 0 {
			return f.smallPrimes[i]
		}
	}
	for i:=0; i < len(f.otherPrimes); i++ {
		if f.otherPrimes[i].Cmp(n) > 0 {
			continue
		}
		remainder.Mod(n, &f.otherPrimes[i])
		if remainder.Cmp(zero) == 0 {
			return f.otherPrimes[i]
		}
	}
	// Attempt actual factoring of n
	for factor.Cmp(one) == 0 {
		count.Set(cycle_size)
		for count.Cmp(one) != 0 {
			if factor.Cmp(one) > 0 {
				break
			}
			// x = (x * x + 1) mod n
			x.Exp(x, two, n)				// x = x**2 % n
			x.Add(x, one)	 				// x = (x**2 % n) + 1
			x.Mod(x, n)						// x = (x ** 2 + 1) % n
			x_diff.Sub(x, x_fixed)			// x_diff = x - x_fixed
			factor.GCD(nil, nil, x_diff, n)
			count.Sub(count, one)
		}
		cycle_size.Mul(cycle_size, two)	// double cycle size
		x_fixed.Set(x)
	}
	remainder.Mod(n, factor)
	// add this new prime factor to the otherPrimes store just in case we 
	// encounter it again.
	factorCopy := new(big.Int).Set(factor)
	f.otherPrimes = append(f.otherPrimes, *factorCopy)
	return *factor
}

// Import a text file of prime numbers relevant to the solution, one per line.
// Will return a non-nil error if the file cannot be opened, cannot be parsed 
// or contains any integers that are non-prime by cursory primality testing 
func (f *Factorizer) importOtherPrimes(filepath string) error {
	file, err := os.OpenFile(filepath, os.O_RDONLY, 0600)
	if err != nil {
		return err
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
    in_prime := new(big.Int)
	lineNum := 0
	for scanner.Scan() {
		lineNum += 1
		// if this line contains a '#', interpret as a comment and truncate the
		// line
		var line string
		hash_index := strings.Index(scanner.Text(), "#")
		if hash_index != -1 {
			line = strings.TrimSpace(scanner.Text()[:hash_index])
		} else {
			line = strings.TrimSpace(scanner.Text())
		}
		if len(line) == 0 {
			continue
		}
        _, ok := in_prime.SetString(scanner.Text(), 10)
		if !ok {
			return errors.New(fmt.Sprintf("Error parsing value on line %d of input file %s as integer", lineNum, filepath))
		}
		found := false
		// Add the parsed integer to the otherPrimes store if it isn't already 
		// present. Return an error if the integer appears to be non-prime by 
		// Miller-Rabin.
		for i:=0; i < len(f.otherPrimes); i++ {
			if in_prime.Cmp(&f.otherPrimes[i]) == 0 {
				found = true
				break
			}
		}
		if !found {
			copy_prime := new(big.Int).Set(in_prime)
			n_miller_rabin := 64
			if(copy_prime.BitLen() > 1024) {
				n_miller_rabin = copy_prime.BitLen() / 16
			}
			if(!copy_prime.ProbablyPrime(n_miller_rabin)) {
				return errors.New(fmt.Sprintf("Value %s on line %d of input file %s may not be prime", copy_prime, lineNum, filepath))
			}
			f.otherPrimes = append(f.otherPrimes, *copy_prime)
		} 
    }
    if err := scanner.Err(); err != nil {
        return err
    }
	return nil
}

// Return a new Factorizer with a list of small primes calculated up to the 
// given bound using the good old sieve of Eratosthenes.
func NewFactorizer(small_prime_bound int) Factorizer {
	small_primes := make([]big.Int, 0)
	prime := make([]bool, small_prime_bound+1)
	// initialize all elements in the sieve as true
	for i := range prime {
		prime[i] = true
	}
	// perform the sieving
	for i := 2; i*i <= small_prime_bound; i++ {
		if prime[i] == true {
			for j := i * 2; j <= small_prime_bound; j += i {
				prime[j] = false
			}
		}
	}
	// extract the list of primes from the sieve
	for i := 2; i <= small_prime_bound; i++ {
		if prime[i] {
			new_prime := new(big.Int).SetInt64(int64(i))
			small_primes = append(small_primes, *new_prime) 
			
		}
	}
	other_primes := make([]big.Int, 0)
	return Factorizer{small_primes, other_primes}
}

func getMillis() int64 {
    return time.Now().UnixNano() / int64(time.Millisecond)
}

type SolutionMode int
const (
	IndexOfNthAppearance SolutionMode = iota
	UntilNonPrime
)

// If SolutionMode = IndexOfNthAppearance, initializes the system with the 
// provided a_1 and return the index n when d_n = targetValue for the 
// maxCount-th time.
// If Solutionmode = UntilNonPrime, initializes the system with the provided 
// a_1 and advances the system until a non-prime d_n is encountered or n 
// exceeds maxCount. If a non-prime d_n is not found, a non-nil error is 
// returned.
// Optionally, a path to a text file containing a list of pre-computed primes 
// may be provided to speed factorization.
func solution(mode SolutionMode, a_1 int, maxCount int, targetValue int, big_prime_import_path string, verbose bool) (big.Int, error) {
	factorizer := NewFactorizer(65536)
	if(len(big_prime_import_path) > 0) {
		factorizer.importOtherPrimes(big_prime_import_path)
	}
	target := new(big.Int).SetInt64(int64(targetValue))
	target_count := 0
	cutoff := new(big.Int).SetInt64(int64(maxCount))
	a := new(big.Int).SetInt64(int64(a_1))
	a_last := new(big.Int).Set(a)
	n := new(big.Int).SetInt64(1)
	n_next := new(big.Int).SetInt64(0)
	zero := new(big.Int).SetInt64(0)
	one := new(big.Int).SetInt64(1)
	m := new(big.Int)
	remainder := new(big.Int)
	best_offset := new(big.Int)
	best_factor_index := -1
	offset := new(big.Int)
	d := new(big.Int)
	
	// advance to the first non-coprime n, a_n-1
	for true {
		n.Add(n, one)
		a_last.Set(a)
		// a = a_last + gcd(n, a_last)
		a.GCD(nil, nil, n, a_last)
		a.Add(a_last, a)
		d.Sub(a, a_last)
		if d.Cmp(one) != 0 {
			if mode == UntilNonPrime {
				factors := factorizer.Factorize(d)
				if len(factors) > 1 {
					if verbose {
						fmt.Printf("Non-prime %s found for k= %d ,n = %s\n", d, a_1, n)
					}
					return *n, nil
				}
			} else {
				if d.Cmp(target) == 0 {
					target_count += 1
					if(verbose) {
						fmt.Printf("%d #%d found at n = %s\n", targetValue, target_count, n)
					}
					if target_count == maxCount {
						return *n, nil
					}
				}
			}
			break
		}
	}
	n_next.Add(n, one)	
	// Repeatedly skip to the index of the next non-one d_n until a completion
	// condition is reached.
	for true {
		if mode == UntilNonPrime && n.Cmp(cutoff) > 0 {
			return *new(big.Int), errors.New("Unable to find non-prime d before exceeding maximum n")
		}
		// At position n, we find all factors of (a_n - n + 1) to help 
		// determine the offset j of the next position n + j such that 
		// d_n+j = gcd(n+j, a_n+j-1) > 1
		m.Sub(a, n_next)
		factors := factorizer.Factorize(m)
		if(len(factors) == 0) {
			return *new(big.Int), errors.New(fmt.Sprintf("There are no further non-one elements of d_n after n=%d", n))
		}
		best_factor_index = -1
		for index := 0; index < len(factors); index++ {
			remainder.Mod(n_next, &factors[index])
			if remainder.Cmp(zero) == 0 {
				best_factor_index = index
				best_offset.Set(zero)
				break
			}
			// offset = p - ((n + 1) % p)
			offset.Mod(n_next, &factors[index])
			offset.Sub(&factors[index], offset)
			// if best_factor_index is unassigned or offset < best_offset
			if best_factor_index == -1 || offset.Cmp(best_offset) < 0 {
				best_factor_index = index
				best_offset.Set(offset)
			}
		}
		// skip to next non-coprime n+1 and a_n.
		// n = n + best_offset + 1
		// a = a + best_offset (equivalent a_n-1 for current n)
		// d = gcd(n, a)
		// a = a + d
		n.Add(n, best_offset)
		n.Add(n, one)
		n_next.Add(n,one)		
		a.Add(a, best_offset)
		d.GCD(nil, nil, n, a)
		if mode == UntilNonPrime {
			if len(factorizer.Factorize(d)) > 1 {
				if verbose {
					fmt.Printf("Non-prime %s found for k = %d,n = %s\n", d, a_1, n)
				}
				return *n, nil
			}
		} else {
			if d.Cmp(target) == 0 {
				target_count += 1
				if(verbose) {
					fmt.Printf("%d #%d found at n = %s \n", targetValue, target_count, n)
				}
				if target_count == maxCount {
					break
				}
			}
		}
		a.Add(a, d)
	}
	return *n, nil
}


func main() {
	bonusPtr := flag.Bool("b", false, "Find the solution to the bonus challenge")
	verbosePtr := flag.Bool("v", false, "Print each occurrence of 5 in d_n as it is found")
	primeFilePtr := flag.String("p", "", "Provide a text file of pre-calculated primes at the given `path` for factorization in the bonus challenge")
	flag.Parse()
	// if the prime file is provided, test that it can be read by the 
	// factorizor importOtherPrimes without errors.
	if len(*primeFilePtr) > 0 {
		f := NewFactorizer(2)
		err := f.importOtherPrimes(*primeFilePtr)
		if err != nil {
			fmt.Printf("Unable to import prime file: %s\n", err)
			flag.Usage()
			return
		}
	}
	fmt.Printf("\n######## Ponder This Challenge - September 2023 ########\n\n")
	startTime := getMillis()
	a_1 := 531
	target_d_n := 5
	if *bonusPtr {
		target_count := 200
		fmt.Printf("Searching for %dth appearance of %d in the sequence defined by a_1 = %d...\n", target_count, target_d_n, a_1)
		n, err := solution(IndexOfNthAppearance, a_1, target_count, target_d_n, *primeFilePtr, *verbosePtr)
		if err != nil {
			fmt.Printf("An error occurred: %s\n", err)
			return
		}
		fmt.Printf("Bonus challenge: For the sequence defined by a_1 = %d, %d appears for the %dth time at n = %s\n", a_1, target_d_n, target_count, n.String())
	} else {
		target_count := 10
		// Note that the primes file is omitted for the main challenge even if 
		// provided as an argument. Checking it takes too long with numbers 
		// this small.
		fmt.Printf("Searching for %dth appearance of %d in the sequence defined by a_1 = %d...\n", target_count, target_d_n, a_1)
		n, err := solution(IndexOfNthAppearance, a_1, target_count, target_d_n, "", *verbosePtr)
		if err != nil {
			fmt.Printf("An error occurred: %s\n", err)
			return
		}
		fmt.Printf("For the sequence defined by a_1 = %d, %d appears for the %dth time at n = %s\n", a_1, target_d_n, target_count, n.String())
		fmt.Printf("Searching for non-prime d_n given by parameters k, n...\n")
		foundNonPrime := false
		min_k := 50000
		max_k := 60000
		max_n := 1000
		for k := min_k; k <= max_k; k++ {
			n, err := solution(UntilNonPrime, k, max_n, 1, "", true)
			if err == nil {
				foundNonPrime = true
				fmt.Printf("There is a non-prime d_n at k = %d, n = %s\n", k, n.String())
				break
			}
		}
		if(!foundNonPrime) {
			fmt.Printf("No non-prime d_n were found in the searched ranges of k and n\n")
		}
		
	}
	endTime := getMillis()
	elapsed := endTime - startTime
	fmt.Printf("Elapsed time : %d ms\n", elapsed)
}