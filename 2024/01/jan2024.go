// Solver for the [IBM Ponder This Janauary 2024 Challenge]
//
// [IBM Ponder This Janauary 2024 Challenge]: https://research.ibm.com/haifa/ponderthis/challenges/January2024.html
package main

import (
	"flag"
	"fmt"
	"time"
	"sync"
	"strconv"
	"strings"
	"math/rand"
)

// Assigner is a struct to keep track of integer assignments to the board
type Assigner struct {
	assigned	[16]bool
}

// Returns a copy of the given Assigner
func (a *Assigner) Copy() Assigner {
	var copy_assigner = NewAssigner();
	for i:=0; i < 16; i++ {
		copy_assigner.assigned[i] = a.assigned[i]
	} 
	return copy_assigner
}

// Updates the assignment list and returns true if the given integer is in the 
// range [1,16] and has not been previously asssigned. Returns false otherwise.
func (a *Assigner) SetIfValid(i int) bool {
	if i < 1 || i > 16 {
		return false
	}
	if a.assigned[i - 1] {
		return false
	}
	a.assigned[i - 1] = true
	return true
}

// Given a list of integers, updates the assignment list and returns true if 
// all are in the range [1,16] and have not been previously asssigned. Returns 
// false on the first invalid assignment found, if any.
func (a *Assigner) SetIfValidList(indexes []int) bool {
	for i := 0; i < len(indexes); i++ {
		if !a.SetIfValid(indexes[i]) {
			return false;
		}
	}
	return true;
}

// Returns a new assigner with no assignments.
func NewAssigner() Assigner {
	var assigned [16]bool
	for i:=0; i < 16; i++ {
		assigned[i] = false
	}
	return Assigner{assigned}
}

// Returns true if the given board position assignments are a valid solution 
// to the riddle equations. Returns false otherwise.
func validateSolution(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p int) bool {
	assigner := NewAssigner();
	if !assigner.SetIfValidList([]int{a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p}) { return false }
	if a + b - c - d != 5 	{ return false }
	if e + f + g - h != 10 	{ return false }
	if i - j + k + l != 9 	{ return false }
	if m - n + o - p != 0 	{ return false }
	if a + e + i - m != 17 	{ return false }
	if b + f - j - n != 8 	{ return false }
	if c - g - k + o != 11 	{ return false }
	if d + h + l + p != 48 	{ return false }
	return true
}

// Given a partial set of board position assignments, solves for the remaining 
// positions using the riddle equations. Returns the complete list of board 
// positions if the resulting set is a valid solution to the board riddle, nil 
// otherwise.
//
// Labels for board positions:
// a b c d
// e f g h
// i j k l
// m n o p
func solution(a, b, h, j, k, l, m, n, p int) []int {
	assigner := NewAssigner()
	if !assigner.SetIfValidList([]int {a, b, h, j, k, l, m, n, p}) {
		return nil
	}
	i := 9 + j - k - l
	if !assigner.SetIfValid(i) { return nil }
	d := 48 - h - l - p
	if !assigner.SetIfValid(d) { return nil }
	f := 8 - b + j + n
	if !assigner.SetIfValid(f) { return nil }
	c := -(5 - a - b + d)
	if !assigner.SetIfValid(c) { return nil }
	e := 17 - a - i + m
	if !assigner.SetIfValid(e) { return nil }
	g := 10 - e - f + h
	if !assigner.SetIfValid(g) { return nil }
	o := 0 - m + n + p
	if !assigner.SetIfValid(o) { return nil }
	if !validateSolution(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p) {
		return nil;
	}
	return []int{a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p}
}

// Entry method for a worker thread generating possible solutions to the riddle
// board. Given board positions h, l, p, cycles through all possible a, b, j, k, 
// m, n. The remaining positions can be solved for using the riddle equations.
// Returns any valid solutions found via the solutions channel.
//
// Labels for board positions:
// a b c d
// e f g h
// i j k l
// m n o p
func mainChallengeThread(h int, l int, p int, solutions chan [][]int, wg *sync.WaitGroup) {
	defer wg.Done()
	found_solutions := make([][]int, 0)
	// The comparisons to omit duplicate assignments are complicated, but this 
	// runs quite fast
	for a := 1; a <= 16; a++ {
		if a == h || a == l || a == p {
			continue
		}
		for b := 1; b <= 16; b++ {
			if b == h || b == l || b == p || 
				b == a {
				continue
			}
			for j := 1; j <= 16; j++ {
				if j == h || j == l || j == p ||
					j == a || j == b {
						continue;
				}
				for k := 1; k <= 16; k++ {
					if k == h || k == l || k == p ||
						k == a || k == b || k == j {
							continue;
					}
					for m := 1; m <= 16; m++ {
						if m == h || m == l || m == p ||
							m == a || m == b || m == j || 
							m == k {
								continue;
						}
						for n := 1;  n <= 16; n++ {
							if n == h || n == l || n == p ||
							n == a || n == b || n == j || 
							n == k || n == m {
									continue;
							}							
							solution := solution(a, b, h, j, k, l, m, n, p)
							if solution != nil {
								found_solutions = append(found_solutions, solution)
							}						
						}
					}
				}
			}
		}
	}
	solutions <- found_solutions
}

// Parent method for setting up worker threads searching for board solutions. 
// Over each possible assignment of the board positions h, l and p, spawns a 
// thread to test all possible remaining board position assignments and return 
// any that correspond to valid solutions to the board.
//
// The system of linear equations will produce a unique solution for
// c, d, e, f, g, i, o if the terms a, b, h, j, k, l, m, n, p are provided. 
// There may be a faster version of this approach where only 8 terms need to be 
// varied instead of 9, but I wasn't able to find one. 
//
// Labels for board positions:
// a b c d
// e f g h
// i j k l
// m n o p
func mainChallengeThreaded(n_threads int) [][]int {
	var wg sync.WaitGroup
	solutions := make([][]int, 0)
	routine_results := make([]chan [][]int, n_threads)
	for i := 0; i < n_threads; i++ {
		routine_results[i] = make(chan [][]int, 1)
	}
	var batchCount = 0
	var numAdded = 0
	// For each thread in a batch, pick variables h, l, and p. Note that h, l 
	// and p must be >= 3. Each of d,h,l,p must be greater than 2 to satisfy 
	// d + h + l + p = 48
	for h := 3; h <= 16; h++ {
		for l := 3; l <= 16; l++ {
			if l == h {
				continue
			}
			for p := 3; p <= 16; p++ {
				if p == h || p == l {
					continue
				}
				if(numAdded == n_threads) {
					wg.Wait()
					for i:=0; i < numAdded; i++ {
						result_solutions := <- routine_results[i]
						for index := 0; index < len(result_solutions); index++ {
							solutions = append(solutions, result_solutions[index])
						}
					}
					numAdded = 0
					batchCount += 1
				}
				wg.Add(1)
				go mainChallengeThread(h,l,p, routine_results[numAdded], &wg)
				numAdded += 1
			}
		}
	}
	// wait for any remaining threads
	if(numAdded > 0) {
		wg.Wait()
		for i:=0; i < numAdded; i++ {
			result_solutions := <- routine_results[i]
			for index := 0; index < len(result_solutions); index++ {
				solutions = append(solutions, result_solutions[index])
			}
		}
	}
	return solutions
}

// Returns a formatted string of the integers representing a solution to the 
// board
func solutionKey (input []int) string {
	list := make([]string, 0)
	for i:=0; i < len(input); i++ {
		list = append(list, strconv.Itoa(input[i]))
	} 
	return fmt.Sprintf("[%s]", strings.Join(list, ","))
}

// Given coefficients to the horizontal and vertical equations in the board
// return them as a string formatted for the bonus challenge answer.
func bonusCoefficientsKey(coefficients [24]int) string {
	coefficient_strings := make([]string, 0)
	for i := 0; i < 24; i++ {
		if coefficients[i] == -1 {
			coefficient_strings = append(coefficient_strings, "-")
		} else {
			coefficient_strings = append(coefficient_strings, "+")
		}
	}
	return fmt.Sprintf("[%s]", strings.Join(coefficient_strings, ","))
}

// Given two solutions and a set of horizontal and vertical coefficients 
// returns true if both solutions sum to the same numbers across all rows and 
// columns, false otherwise.
func bonusTestPairWithCoefficients(a []int, b []int, coefficients [24]int)  bool {
	for row := 0; row < 4; row++ {
		var sum_a = a[4 * row]
		var sum_b = b[4 * row]
		for col := 1; col < 4; col++ {
			sum_a += coefficients[(col - 1) + 7*row] * a[4*row + col]
			sum_b += coefficients[(col - 1) + 7*row] * b[4*row + col]
		}
		if sum_a != sum_b {
			return false;
		}
	}
	for col := 0; col < 4; col++ {
		var sum_a = a[col]
		var sum_b = b[col]
		for row := 1; row < 4; row++ {
			sum_a += coefficients[3 + (row-1)*7 + col] * a[4*row + col]
			sum_b += coefficients[3 + (row-1)*7 + col] * b[4*row + col]
		}
		if sum_a != sum_b {
			return false;
		} 
	}
	return true
}

// Given two solutions that differ in all places, tests all possible flips of at
// least 12 +/- operators in the horizontal and vertical equations. If any 
// result in the same sums for both solutions in each row and column, returns a 
// formatted string with the two solutions and the +/- assignment.
// Returns an empty string otherwise.
func bonusTestPair(a []int, b []int) string {
	if len(a) != 16 || len(b) != 16 {
		panic(fmt.Sprintf("Incorrect array sizes in bonusTestPair %d, %d", len(a), len(b)))
	}
	initial_coefficients := [24]int{1 , -1, -1, 1, 1, -1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1, -1, -1, 1, 1, -1, 1, -1}
	test_coefficients := [24]int{0}
	// There's probably a quicker way to traverse all possible arrangements 
	// that differ in 12 or more positions, but this works
	for i:=0; i < 16777216; i++ {
		var bits = 0
		for j := 0; j < 24; j++ {
			if (i >> j) & 0x01 == 1 {
				bits += 1
			}
		}
		if bits < 12 {
			continue
		}
		for j := 0; j < 24; j++ {
			if (i >> j) & 0x01 == 1 {
				test_coefficients[j] = initial_coefficients[j] * -1
			} else {
				test_coefficients[j] = initial_coefficients[j]
			}
		}
		if bonusTestPairWithCoefficients(a, b, test_coefficients) {
			return fmt.Sprintf("%s\n%s\n%s\n", solutionKey(a), solutionKey(b), bonusCoefficientsKey(test_coefficients))
		}
	}
	return ""
}

// Entry method for a worker thread that tests the board solution at the given 
// index together with each subsequent solution in the list for pairs that 
// provide a bonus challenge solution. If one is found, returns a formatted 
// string of the two solutions along with the reassigned +/- signs via the 
// result channel. Returns an empty string on the result channel if no bonus
// solution is found.
func bonusChallengeThread(index int, solutions [][]int, result chan string, wg *sync.WaitGroup) {
	defer wg.Done()
	for j := index + 1; j < len(solutions); j++ {
		var different = true
		for k:=0; k < 16; k++ {
			if solutions[index][k] == solutions[j][k] {
				different = false
				break
			}
		}
		if different {
			test_result := bonusTestPair(solutions[index], solutions[j])
			if test_result != "" {
				result <- test_result
				return
			}
		}
	}
	result <- ""
}

// Parent method for setting up worker threads searching for bonus challenge 
// solutions. Given the complete list of board solutions, spawns threads to 
// test each possible pair of board solutions in order to find a pair that 
// satisfies the bonus challenge. If a bonus solution is found, prints it and 
// returns true. Returns false otherwise.
func bonusChallengeThreaded(n_threads int, solutions [][]int ) bool {
	var wg sync.WaitGroup
	
	// shuffle the solutions array to not get the same answer every time
	shuffled_solutions := make([][]int, 0)
	for i := range solutions {
		shuffled_solutions = append(shuffled_solutions, solutions[i])
	}
	for i := range shuffled_solutions {
		j := rand.Intn(i+1)
		shuffled_solutions[i], shuffled_solutions[j] = shuffled_solutions[j], shuffled_solutions[i]
	}
	
	routine_results := make([]chan string, n_threads)
	for i := 0; i < n_threads; i++ {
		routine_results[i] = make(chan string, 1)
	}
	var batchCount = 0
	var numAdded = 0
	for index := 0; index < len(shuffled_solutions) - 1; index++ {
		if(numAdded == n_threads) {
			wg.Wait()
			for i:=0; i < numAdded; i++ {
				result_solution := <- routine_results[i]
				// if a solution was found, print it and return
				if result_solution != "" {
					fmt.Println(result_solution)
					return true
				}
			}
			numAdded = 0
			batchCount += 1
		}
		wg.Add(1)
		go bonusChallengeThread(index, shuffled_solutions, routine_results[numAdded], &wg)
		numAdded += 1
	}
	// wait for any remaining threads
	if(numAdded > 0) {
		wg.Wait()
		for i:=0; i < numAdded; i++ {
			result_solution := <- routine_results[i]
			if result_solution != "" {
				fmt.Println(result_solution)
				return true
			}
		}
	}
	return false
}

func getMillis() int64 {
    return time.Now().UnixNano() / int64(time.Millisecond)
}

func main() {
	threadsPtr := flag.Int("t", 4, "The number of worker threads used to find solutions.")
	flag.Parse();
	if *threadsPtr < 1 {
		fmt.Printf("The entered number of worker threads %d must be greater than zero\n", *threadsPtr)
		flag.Usage()
		return
	} 
	fmt.Printf("\n######## Ponder This Challenge - January 2024 ########\n\n")
	startTime := getMillis()
	
	
	fmt.Printf("Main challenge:\n")
	solutions := mainChallengeThreaded(*threadsPtr)
	if len(solutions) == 0 {
		fmt.Printf("No solutions found\n")
		return
	}
	fmt.Println(solutionKey(solutions[rand.Intn(len(solutions))]))
	fmt.Println(len(solutions))
	fmt.Println("\nBonus challenge:")
	if !bonusChallengeThreaded(*threadsPtr, solutions) {
		fmt.Println("No solutions to the bonus challenge found")
	}
	endTime := getMillis()
	elapsed := endTime - startTime
	fmt.Println(fmt.Sprintf("\nElapsed time : %d ms", elapsed))
}	