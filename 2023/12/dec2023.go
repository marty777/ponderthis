// https://research.ibm.com/haifa/ponderthis/challenges/December2023.html
package main

import (
	"flag"
	"time"
	"fmt"
	"math"
	"sync"
)

// Determines the number of distinct circles with m < r < m+1 by searching a  
// 60 degree arc of the triangular grid for points that lie between the 
// bounding circles and storing a set of all distinct squared vector lengths 
// found.
func f(m int) int {
	c := math.Sqrt(0.75) 										// constant height of a row of triangles, sqrt(3/4)
	m0 := float64(m)	 										// radius of interior circle
    m1 := float64(m + 1)										// radius of exteror circle
    m0_2 := m0*m0												// radius of interior circle squared
    m1_2 := m1*m1												// radius of exterior circle squared
	
	// v_max, the highest row number to examine, the floor of (the y coord of 
	// the intersection of the line y=x/sqrt(3/4) and radius of the exterior 
	// circle) / the height of a row
	// m1^2 = x^2 + y^2 
	//	-> y^2 = m1^2 - x^2 = x^2/(3/4)
	// 	-> x^2*(4/3 + 1) = m1^2
	//	-> x^2 = m1^2 * 3/7
	//	-> y = sqrt(m1^2 * 3/7)/sqrt(3/4)
	//	-> y = sqrt(m1^2 * 3/7 * 4/3 * 3/4)/sqrt(3/4)
	//	-> y = sqrt(m1^2 * 12/21) = m1 * sqrt(12/21)
	// 	-> v_max = y / sqrt(3/4) = m1 * sqrt(48/63)
	v_max := int(math.Floor(m1 * math.Sqrt(48.0/63.0)))
    radii2 := make(map[float64]bool, 0)							// set of distinct circles found, given by radius squared
	var v int = 1 												// current grid row index
	for v <= v_max {
		y := float64(v) * c										// cartesian y coordinate of the row
		x0 := math.Sqrt((m0 * m0) - (y * y))					// cartesian x coordinate of the point on the interior circle at y
		x1 := math.Sqrt((m1 * m1) - (y * y))					// cartesian x coordinate of the point on the exterior circle at y
		var x float64 = 0										// storage for cartesian coord of each point on the grid at height y within the bounding circles
		if v % 2 == 1 {
			x = math.Floor(x0) + 0.5
		} else {
			x = math.Floor(x0)
		}
		for x < x1 {
			r2 := (x * x) + (float64(v * v) * float64(0.75))	// squared length of the vector between the origin and the grid point
			if r2 > m0_2 && r2 < m1_2 {
				_, exists := radii2[r2]
				if !exists {
					radii2[r2] = true
				}
			}
			x += 1.0
		}
		v += 1
	}
	return len(radii2);
}

// Struct for passing batch run result information over a channel
type fResult struct {
	m int
	result int
}

func f_thread(m int, c chan fResult, wg *sync.WaitGroup) {
	defer wg.Done()
	result := f(m)
	c <- fResult{m:m, result:result}
}

// Parent method for multithreading batch jobs. Will examine all f(m) for m in 
// the range [min,max] by passing the jobs off to a maximum of n_threads 
// threads. Any m where f(m) = 1,000,000 will be recorded and returned in an 
// array.
func f_threaded(min int, max int, n_threads int, verbose bool) []int {
	fmt.Println(fmt.Sprintf("Searching for m such that f(m) = 1,000,000 in the range %d - %d with %d worker threads", min, max, n_threads))
	var wg sync.WaitGroup
	routine_results := make([]chan fResult, n_threads)
	for i := 0; i < n_threads; i++ {
		routine_results[i] = make(chan fResult, 1)
	}
	var millions = make([]int, 0)
	var numAdded = 0
	var index = min
	var batchNum = 0
	var maxBatch = int(math.Ceil(float64(max - min))/float64(n_threads))
	for index <= max {
		if numAdded == n_threads {
			wg.Wait()
			for i:= 0; i < numAdded; i++ {
				result := <- routine_results[i]
				if result.result == 1_000_000 {
					millions = append(millions, result.m)
					if verbose {
						fmt.Println(fmt.Sprintf("FOUND\tm: %d\tf(m): %d", result.m, result.result))
					}
				} else if verbose {
					fmt.Println(fmt.Sprintf("\tm: %d\tf(m): %d", result.m, result.result))
				}
			}
			if verbose {
				fmt.Println(fmt.Sprintf("Batch %d of %d complete ( %.2f %% )", batchNum + 1, maxBatch + 1, 100.0 * float64(batchNum + 1)/float64(maxBatch + 1)))
			}
			batchNum += 1
			numAdded = 0
		}
		wg.Add(1)
		go f_thread(index, routine_results[numAdded], &wg)
		numAdded += 1
		index += 1
	}
	// Resolve any remaining queued threads
	if numAdded > 0 {
		wg.Wait()
		for i:=0; i < numAdded; i++ {
			result := <- routine_results[i]
			if result.result == 1_000_000 {
				millions = append(millions, result.m)
				if verbose {
					fmt.Println(fmt.Sprintf("FOUND\tm: %d\tf(m): %d", result.m, result.result))
				}
			} else if verbose {
				fmt.Println(fmt.Sprintf("\tm: %d\tf(m): %d", result.m, result.result))
			}
		}
		if verbose {
			fmt.Println(fmt.Sprintf("Batch %d of %d complete ( %.2f %% ) ", batchNum + 1, maxBatch + 1, 100.0 * float64(batchNum + 1)/float64(maxBatch + 1)))
		}
		numAdded = 0
	}
	return millions
}

func getMillis() int64 {
    return time.Now().UnixNano() / int64(time.Millisecond)
}

func main() {
	
	minMPointer := flag.Int("min", 4310900, "The minimum in the range of m values to test")
	maxMPointer := flag.Int("max", 4314000, "The maximum in the range of m values to test")
	threadsPtr  := flag.Int("t", 4, "The number of worker thread to run")
	verbosePtr  := flag.Bool("v", false, "Print progress")
	flag.Parse()
	
	if(*minMPointer < 1) {
		fmt.Printf("The entered mimimum value for m %d is too small and must be greater than 1\n", *minMPointer)
		flag.Usage()
		return
	}
	if(*maxMPointer < *minMPointer) {
		fmt.Printf("The enterd maximum m value %d cannot be less than the entere minimum m value %d\n", *maxMPointer, *minMPointer)
		flag.Usage()
		return
	}
	if *threadsPtr < 1 {
		fmt.Printf("The entered number of worker threads %d must be greater than zero\n", *threadsPtr)
		flag.Usage()
		return
	}
	fmt.Printf("\n######## Ponder This Challenge - December 2023 ########\n\n")
	startTime := getMillis()
	millions := f_threaded(*minMPointer, *maxMPointer, *threadsPtr, *verbosePtr)
	if len(millions) == 0 {
		fmt.Println("No results found")
	} else {
		fmt.Println(fmt.Sprintf("%d result(s) found:", len(millions)))
		for i:=0; i < len(millions); i++ {
			fmt.Println(millions[i])
		}
	}
	endTime := getMillis()
	elapsed := endTime - startTime
	fmt.Println(fmt.Sprintf("Elapsed time : %d ms", elapsed))
}