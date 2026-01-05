package main

import (
	"flag"
	"fmt"
	"math"
	"time"
)

// Small collection of ordered primes in the range [start,end]
type PrimeRange struct {
	start  int64
	end    int64
	primes []int64
}

// Perform a binary search on the PrimeRange to test if x is a member
func (p *PrimeRange) IsPrime(x int64) bool {
	if x < p.start || x > p.end {
		panic(fmt.Sprintf("Term %d is outside the bounds of the prime group [%d,%d]", x, p.start, p.end))
	}
	var lo int
	var hi int
	var mid int = (len(p.primes) - 1) / 2
	var mid_val int64 = p.primes[mid]
	if x == mid_val || x == p.primes[0] || x == p.primes[len(p.primes)-1] {
		return true
	}
	if x < p.primes[0] || x > p.primes[len(p.primes)-1] {
		return false
	}
	if x < mid_val {
		lo = 0
		hi = mid - 1
	} else {
		lo = mid + 1
		hi = len(p.primes) - 1
	}
	for lo <= hi {
		mid = (lo + hi) / 2
		mid_val = p.primes[mid]
		if x == mid_val {
			return true
		} else if x < mid_val {
			hi = mid - 1
		} else {
			lo = mid + 1
		}
	}
	return false
}

// Intended for queries about the primality of increasing integers, holds a low
// and high PrimeRange and constructs a new high PrimeRange when requested
// using the SequentialSiever object.
type PrimeGrouping struct {
	lo        PrimeRange
	hi        PrimeRange
	increment int64
	siever    *SequentialSiever
}

// Add a new high PrimeRange to the PrimeGrouping, with the previous high
// group moving to the low slot.
func (p *PrimeGrouping) Advance() {
	p.lo = p.hi
	// fmt.Printf("Advancing prime range to a maximum of %d...\n", p.lo.end+1+p.increment)
	p.hi = p.siever.BuildPrimeRange(p.lo.end+1, p.lo.end+p.increment)
}

// Test if x is a member of the low or high PrimeRanges of the PrimeGrouping
func (p *PrimeGrouping) IsPrime(x int64) bool {
	if x < p.lo.start || x > p.hi.end {
		panic(fmt.Sprintf("Term %d is outside the bounds of the prime grouping [%d,%d]", x, p.lo.start, p.hi.end))
	}
	if x <= p.lo.end {
		// binary search on lo
		return p.lo.IsPrime(x)
	} else {
		// binary search on hi
		return p.hi.IsPrime(x)
	}
}

func NewPrimeGrouping(start int64, increment int64, siever *SequentialSiever) PrimeGrouping {
	lo := siever.BuildPrimeRange(start, start+increment-1)
	hi := siever.BuildPrimeRange(start+increment, start+2*increment-1)
	return PrimeGrouping{lo: lo, hi: hi, increment: increment, siever: siever}
}

// SequentialSiever is used to build PrimeRanges for small ranges of integers
// with a modified Sieve of Eratosthenes using an initial set of primes.
type SequentialSiever struct {
	sqrLimit int64
	primes   []int64
}

// Increase the initial prime collection for the SequentialSiever
// to at least the given maximum
func (s *SequentialSiever) ExtendPrimes(max int64) {
	if max < s.sqrLimit*s.sqrLimit {
		return
	}
	var sqrLimit = s.sqrLimit
	for {
		sqrLimit *= 2
		primeRange := s.BuildPrimeRange(s.sqrLimit, sqrLimit)
		for i := 0; i < len(primeRange.primes); i++ {
			s.primes = append(s.primes, primeRange.primes[i])
		}
		s.sqrLimit = sqrLimit
		if s.sqrLimit*s.sqrLimit >= max {
			break
		}
	}
}

// Construct a PrimeRange with all primes between the given start and end
// bounds.
// If the range exceeds the siever sqrLimit, increase it by adding further
// initial primes to the sieve.
func (s *SequentialSiever) BuildPrimeRange(start int64, end int64) PrimeRange {
	if s.sqrLimit*s.sqrLimit < end {
		s.ExtendPrimes(end)
	}
	sieve := make([]bool, end-start+1)
	for i := 0; i < len(sieve); i++ {
		sieve[i] = false
	}
	var true_count1 = 0
	for i := 0; i < len(sieve); i++ {
		if sieve[i] {
			true_count1 += 1
		}
	}
	for i := 0; i < len(s.primes); i++ {
		if s.primes[i] > end {
			break
		}
		start_multiple := (start / s.primes[i]) - 1
		if start_multiple < 2 {
			start_multiple = 2
		}
		end_multiple := (end / s.primes[i]) + 1
		for j := start_multiple; j <= end_multiple; j++ {
			term := s.primes[i] * j
			if term < start || term > end {
				continue
			}
			sieve[term-start] = true
		}
	}
	primes := make([]int64, 0)
	var true_count = 0
	for i := 0; i < len(sieve); i++ {
		if sieve[i] {
			true_count += 1
		}
		if !sieve[i] && start+int64(i) <= end {
			primes = append(primes, start+int64(i))
		}
	}
	return PrimeRange{start: start, end: end, primes: primes}
}

// Use a Sieve of Eratosthenes to build an initial set of primes for the
// SequentialSiever
func NewSequentialSiever(sqrLimit int64) SequentialSiever {
	if sqrLimit < 2 {
		panic(fmt.Sprintf("Sequential siever must be initialized with a square limit of at least 2 (%d provided)", sqrLimit))
	}
	primes := make([]int64, 0)
	sieve := make([]bool, sqrLimit)
	for i := int64(0); i < sqrLimit; i++ {
		sieve[i] = false
	}
	var increment = int64(2)
	var done = false
	for {
		for i := 2 * increment; i < sqrLimit; i += increment {
			sieve[i] = true
		}
		done = true
		for i := increment + 1; i < sqrLimit; i++ {
			if !sieve[i] {
				increment = i
				done = false
				break
			}
		}
		if done {
			break
		}
	}
	for i := int64(2); i < sqrLimit; i++ {
		if !sieve[i] {
			primes = append(primes, i)
		}
	}
	return SequentialSiever{sqrLimit: sqrLimit, primes: primes}
}

// / Calculate the total number of pairwise sums that are prime between the
// primes in [3,n] and even integers (2,..,2n).
func f(n int64) int64 {
	sequentialSiever := NewSequentialSiever(int64(math.Sqrt(float64(n))))
	var count = int64(0)
	var primeCount = int64(0)
	var done = false
	// Start with lists of primes in the ranges lo: [3,3+2n-1],
	// hi: [3+2n, 3+4n-1] with subsequent ranges advancing by 2n.
	primeGrouping := NewPrimeGrouping(3, 2*n, &sequentialSiever)
	for {
		var q_index = 0
		// For each prime in the lo list, determine the number of primes in
		// the integer range [p+2, p+2n] using the current lo and hi prime
		// lists.
		for p_index := 0; p_index < len(primeGrouping.lo.primes); p_index++ {
			p_plus_2n := primeGrouping.lo.primes[p_index] + 2*n
			if p_plus_2n < primeGrouping.hi.primes[0] {
				// If p+2n is less than the first prime in hi, the final prime
				// in lo must be the greatest prime <= p+2n, so the number of
				// pairwise prime sums for p is the number of primes in lo
				// greater than p.
				count += int64(len(primeGrouping.lo.primes) - (p_index + 1))
			} else {
				// Otherwise, find the index of the first prime q in hi where
				// q <= p+2n. The number of pairwise prime sums for p must be
				// the number of primes in lo greater than p plus the number
				// of primes in hi up to q.
				// Note that as lo is iterated over, the index of q rarely
				// increases by more that 1 per step (with a max of 24 over
				// the course of the bonus challenge) so a sequential search
				// manages to out perform a binary search across hi.
				for q_index+1 < len(primeGrouping.hi.primes) && primeGrouping.hi.primes[q_index+1] <= p_plus_2n {
					q_index++
				}
				count += int64(len(primeGrouping.lo.primes) - (p_index + 1) + (q_index + 1))
			}
			primeCount += 1
			// End if the nth prime has been reached
			if primeCount == n {
				done = true
				break
			}
		}
		if done {
			break
		}
		// If not finished, drop the current lo list, move the current hi list
		// to the lo range, and generate a new hi list from among the
		// subsequent 2n integers.
		primeGrouping.Advance()
	}
	return count
}

func getMillis() int64 {
	return time.Now().UnixNano() / int64(time.Millisecond)
}

func main() {
	bonusPtr := flag.Bool("b", false, "Solve the bonus challenge")
	flag.Parse()
	fmt.Printf("\n######## Ponder This Challenge - December 2025 ########\n\n")
	startTime := getMillis()
	if *bonusPtr {
		fmt.Printf("Bonus solution:\t%d\n", f(1000_000_000))
	} else {
		fmt.Printf("Main solution:\t%d\n", f(100_000_000))
	}
	endTime := getMillis()
	elapsed := endTime - startTime
	fmt.Printf("Elapsed time :\t%d ms\n", elapsed)
}
