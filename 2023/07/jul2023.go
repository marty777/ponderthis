// https://research.ibm.com/haifa/ponderthis/challenges/July2023.html

package main

import (
	"flag"
	"fmt"
	"time"
	"image/color"
	"jul2023/slidingpieces"
)

// current timestamp in milliseconds
func getMillis() int64 {
    return time.Now().UnixNano() / int64(time.Millisecond)
}

func main() {
	bonusPtr := flag.Bool("b", false, "Find a solution to the bonus challenge")
	verbosePtr := flag.Bool("v", false, "Print the status of each queue step and a trace of each move in a solution when found")
	gifPtr := flag.String("g", "", "Export an animated gif of the solution to the specified `path` when found ")
	
	flag.Parse()
	
	fmt.Println("\n######## Ponder This Challenge - July 2023 ########")
	fmt.Println()
	
	// The board piece start positions are described by piece id in a multiline 
	// string as follows
	challengeBoardString := `
    12234
    12334
    56778
    99888
    .....`
    challengeBoardNumPieces := 9
	// Mapping of piece ids to piece type ids, to handle the equivalence of 
	// pieces with the same shape
    challengeBoardPieceTypes :=  map[int]int{1:1, 2:2, 3:3, 4:1, 5:5, 6:5, 7:7, 8:8, 9:7}
	// Piece colors by type id: 1 - orange, 2 - green, 3 - red, 5 - blue, 7 - yellow, 8 - purple, 
	challengeBoardPieceColors := map[int]color.RGBA{
			1: color.RGBA{0xff, 0x80, 0x00, 0xff},
			2: color.RGBA{0x00, 0x80, 0x00, 0xff},
			3: color.RGBA{0xff, 0x00, 0x00, 0xff},
			5: color.RGBA{0x00, 0x00, 0xff, 0xff},
			7: color.RGBA{0xff, 0xff, 0x00, 0xff},
			8: color.RGBA{0x80, 0x00, 0x80, 0xff},
	}
	var result slidingpieces.DijkstraState
	var err error
	var validateErr error
	var validateCost int
	var animationGenerator slidingpieces.AnimationGenerator
	animationCellSize := 40
	animationOutlineWidth := 1
	animationFramesPerMove := 4
	animationFrameDelay := 1
	animationMoveCompleteDelay := 10
	animationSolutionCompleteDelay := 300
	animationReverse := true
	startTime := getMillis()
	if(*bonusPtr) {
		fmt.Println("Searching for solutions to the bonus challenge...")
		// The goal state is described by piece type ids, not by piece ids, 
		// following the ids layed out in the challengeBoardPieceTypes map 
		// above
		challengeBonusGoalString := `
		.223.
		12338
		1.888
		1..55
		17777`
		challengeBonusBoard := slidingpieces.NewBoard(challengeBoardString, challengeBoardNumPieces, challengeBoardPieceTypes, challengeBonusGoalString)
		result, err = challengeBonusBoard.Dijkstra(150, *verbosePtr)
		if err == nil {
			validateCost, validateErr = challengeBonusBoard.Validate(result.Path, *verbosePtr)
			if validateErr == nil {
				animationGenerator = slidingpieces.NewAnimationGenerator(challengeBonusBoard, result, challengeBoardPieceColors, animationCellSize, animationOutlineWidth)
			}
		}
	} else {
		fmt.Println("Searching for solutions to the main challenge...")
		challengeMainGoalString := `
		77.22
		..321
		.3311
		57718
		.5888`
		challengeMainBoard := slidingpieces.NewBoard(challengeBoardString, challengeBoardNumPieces, challengeBoardPieceTypes, challengeMainGoalString)
		result, err = challengeMainBoard.Dijkstra(100, *verbosePtr)
		if err == nil {
			validateCost, validateErr = challengeMainBoard.Validate(result.Path, *verbosePtr)
			if validateErr == nil {
				animationGenerator = slidingpieces.NewAnimationGenerator(challengeMainBoard, result, challengeBoardPieceColors, animationCellSize, animationOutlineWidth)
			}
		}
	}
	fmt.Println("Result:")
	if err != nil {
		fmt.Println("No solutions found")
	} else if validateErr != nil {
		fmt.Println(fmt.Sprintf("Solution path %s was found but failed validation: %s", result.Path, validateErr))
	} else if validateCost != result.Cost {
		fmt.Println(fmt.Sprintf("Solution path %s was found the cost determined by the search (%d) does not match the cost found in validation (%d) which may indicate an error", result.Path, result.Cost, validateCost))
	} else {
		fmt.Println(fmt.Sprintf("Solution %s reaches the goal state with a cost of %d in %d move(s)", result.Path, result.Cost, len(result.Path)/2))
		
		if(*gifPtr != "") {
			// export an animated gif 
			animationGenerator.Generate(*gifPtr, animationFramesPerMove, animationFrameDelay, animationMoveCompleteDelay, animationSolutionCompleteDelay, animationReverse)
			fmt.Println(fmt.Sprintf("An animation of the solution has been exported to %s", *gifPtr))
		}
	}
	
	endTime := getMillis()
	elapsed := endTime - startTime
	fmt.Println(fmt.Sprintf("Elapsed time : %d ms", elapsed))
}