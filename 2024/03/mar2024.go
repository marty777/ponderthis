package main
 
import (
	"flag"
	"fmt"
	"time"
	"sync"
)

// Small collection of ordered primes in the range [start,end]
type PrimeRange struct {
	start int64
	end int64
	primes []int64
}

// Perform a binary search on the PrimeRange to test if x is a member
func (p* PrimeRange) IsPrime(x int64) bool {
	if x < p.start || x > p.end {
		panic(fmt.Sprintf("Term %d is outside the bounds of the prime group [%d,%d]", x, p.start, p.end))
	}
	var lo int
	var hi int
	var mid int = (len(p.primes) - 1) /2
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
		mid = (lo + hi)/2
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
	lo PrimeRange 
	hi PrimeRange 
	increment int64
	siever *SequentialSiever
}

// Add a new high PrimeRange to the PrimeGrouping, with the previous high
// group moving to the low slot.
func (p *PrimeGrouping) Advance() {
	p.lo = p.hi
	fmt.Printf("Advancing prime range to a maximum of %d...\n",  p.lo.end + 1 + p.increment)
	p.hi = p.siever.BuildPrimeRange(p.lo.end + 1, p.lo.end + 1 + p.increment)
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
	lo := siever.BuildPrimeRange(start, start + increment)
	hi := siever.BuildPrimeRange(start+increment+1, start+2*increment)
	return PrimeGrouping{lo:lo, hi:hi, increment: increment, siever:siever}
}

// SequentialSiever is used to build PrimeRanges for small ranges of integers 
// with a modified Sieve of Eratosthenes using an initial set of primes. 
type SequentialSiever struct {
	sqrLimit	int64
	primes		[]int64
}

// Increase the initial prime collection for the SequentialSiever
// to at least the given maximum
func (s *SequentialSiever) ExtendPrimes(max int64) {
	if max < s.sqrLimit*s.sqrLimit {
		return 
	}
	var sqrLimit = s.sqrLimit
	for true {
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
	if s.sqrLimit*s.sqrLimit < start || s.sqrLimit*s.sqrLimit < end {
		s.ExtendPrimes(end)
	}
	sieve :=make([]bool, end-start + 1)
	for i := 0; i < len(sieve); i++ {
		sieve[i] = false
	}
	var true_count1 = 0
	for i := 0; i < len(sieve); i++ {
		if sieve[i] {
			true_count1 += 1
		}
	}
	for i := 0; i < len(s.primes);i++ {
		if s.primes[i] > end {
			break
		}
		start_multiple := (start/s.primes[i]) - 1
		if start_multiple < 2 {
			start_multiple = 2
		}
		end_multiple := (end/s.primes[i]) + 1
		for j := start_multiple; j <= end_multiple; j++ {
			term := s.primes[i]*j
			if term < start || term > end {
				continue
			}
			sieve[term - start] = true
		}
	}
	primes := make([]int64, 0)
	var true_count = 0
	for i := 0; i < len(sieve); i++ {
		if sieve[i] {
			true_count += 1
		}
		if sieve[i] == false && start + int64(i) <= end {
			primes = append(primes, start + int64(i))
		}
	}
	return PrimeRange{start:start, end:end, primes:primes}
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
	for true {
		for i := 2*increment; i < sqrLimit; i += increment {
			sieve[i] = true
		}
		done = true
		for i := increment+1; i < sqrLimit; i++ {
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
	return SequentialSiever{sqrLimit:sqrLimit, primes:primes}
}


// Entry method for a thread testing candidate a0 indexes for the given n
func testIndexesThread(start int64, end int64, n int64, primeGrouping *PrimeGrouping, result chan int64, wg *sync.WaitGroup) {
	defer wg.Done()
	var min_i = int64(-1)
	var offset = int64(0)
	var good = false
	for i := start; i < end; i++ {
		if i % 3 != 0 {
			continue
		}
		if i % 5 != 0 && i % 5 != 4 {
			continue 
		}
		offset = i
		good = true
		for j := int64(0); j < n; j++ {
			offset += j
			if primeGrouping.IsPrime(offset) {
				good = false
				break 
			}
		}
		if good {
			min_i = i
			break
		}
	}
	result <- min_i
}

// Parent method for multithreaded testing of candidate a0s in the specified 
// range
func testIndexesThreaded(start int64, end int64, n int64, primeGrouping *PrimeGrouping, n_threads int) int64 {
	var wg sync.WaitGroup
	routine_results := make([]chan int64, n_threads)
	for i := 0; i < n_threads; i++ {
		routine_results[i] = make(chan int64, 1)
	}
	var min_result = int64(-1)
	batch_size := int64(10_000)
	var batches_added = 0
	var stop int64
	for i := start; i < end; i += batch_size {
		if batches_added == n_threads {
			wg.Wait()
			for j := 0; j < batches_added; j++ {
				routine_result := <- routine_results[j]
				if routine_result != -1 {
					if min_result == -1 || min_result > routine_result {
						min_result = routine_result
					}
				}
			}
			if min_result != -1 {
				return min_result
			}
			batches_added = 0
		}
		wg.Add(1)
		if i + batch_size < end+1 {
			stop = i+batch_size
		} else {
			stop = end+1
		}
		
		go testIndexesThread(i, stop, n, primeGrouping, routine_results[batches_added], &wg)
		batches_added += 1
	}
	if batches_added > 0 {
		wg.Wait()
		for j := 0; j < batches_added; j++ {
			routine_result := <- routine_results[j]
			if routine_result != -1 {
				if min_result == -1 || min_result > routine_result {
					min_result = routine_result
				}
			}
		}
		batches_added = 0
	}
	return min_result
}


func A0(n int64, start int64, n_threads int) int64 {
	// special handling for n <= 2
	if n == 1 {
		return 1
	}
	if n == 2 {
		return 8
	}
	// initialize the sequential siever with enough primes to handle n = 1000
	sequentialSiever := NewSequentialSiever(11000)
	var i = start
	primeGrouping := NewPrimeGrouping(i, 10 * ((n * (n-1))/2), &sequentialSiever)
	for true {
		stop := primeGrouping.hi.end - 1 - (n * (n-1))/2
		result := testIndexesThreaded(i, stop, n, &primeGrouping, n_threads)
		if result != -1 {
			return result
		}
		i = stop
		primeGrouping.Advance()
	}
	return -1
}

func getMillis() int64 {
    return time.Now().UnixNano() / int64(time.Millisecond)
}

func main() {
	threadsPtr := flag.Int("t", 4, "Set the number of worker threads")
	nPtr := flag.Int("n", 1000, "Set the value for n")
	startPtr := flag.Int("s", 0, "Set the starting a0 search value")
	flag.Parse()
	if *threadsPtr < 1 {
		fmt.Printf("The entered number of worker threads %d must be greater than zero\n", *threadsPtr)
		flag.Usage()
		return
	}
	if *nPtr < 1 {
		fmt.Printf("The entered n value %d must be greater than zero\n", *nPtr)
		flag.Usage()
		return
	}
	if *startPtr < 0 {
		fmt.Printf("The entered starting a0 search value %d must be non-negative\n", *startPtr)
		flag.Usage()
		return
	}
	
	fmt.Printf("\n######## Ponder This Challenge - March 2024 ########\n\n")
	startTime := getMillis()
	fmt.Printf("Searching for term a_0 of X_%d starting from index %d with %d worker thread(s)...\n", *nPtr, *startPtr, *threadsPtr)
	result := A0(int64(*nPtr), int64(*startPtr), *threadsPtr)
	if result == - 1 {
		fmt.Printf("A result could not be found.\n")
	} else {		 
		fmt.Printf("Result: %d\n", result)
	}
	endTime := getMillis()
	elapsed := endTime - startTime
	fmt.Println(fmt.Sprintf("Elapsed time : %d ms", elapsed))
}
