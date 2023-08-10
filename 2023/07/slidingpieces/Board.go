// SlidingPieces package contains the various structs and methods for finding solutions to the Ponder This July 2023 challenges
package slidingpieces

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
	"math/rand"
)

// The board is fixed as 5x5
const boardDim = 5
// The cost of moving a piece is 5 - size
const costParam = 5

// The Board stores a set of SlidingPieces and the desired goal state of the challenge and handles finding and validating solutions 
type Board struct {
	// Pieces are indexed as piece id - 1
	Pieces	[]SlidingPiece
	Goal	[][]int
}

// The default string representation of a Board
func (b Board) String() string {
	return b.ToString(false, nil)
}

// Returns a string representation of the board with the pieces in the locations specified by the positions argument. 
//
// If byType is true, pieces will be displayed by their associated type id number rather than their piece id number.
func (b Board) ToString(byType bool, positions []Coord) string {
	var sb strings.Builder
	for y := 0; y < boardDim; y++ {
		for x := 0; x < boardDim; x++ {
			foundCell := false
			for p := 0; p < len(b.Pieces); p++ {
				if positions == nil {
					if(b.Pieces[p].HasCellAtCoord(Coord{x,y}, b.Pieces[p].Start)) {
						if byType {
							sb.WriteString(strconv.Itoa(b.Pieces[p].TypeId))
						} else {
							sb.WriteString(strconv.Itoa(b.Pieces[p].Id))
						}
						foundCell = true
						break
					}
				} else {
					if(b.Pieces[p].HasCellAtCoord(Coord{x,y}, positions[p])) {
						if byType {
							sb.WriteString(strconv.Itoa(b.Pieces[p].TypeId))
						} else {
							sb.WriteString(strconv.Itoa(b.Pieces[p].Id))
						}
						foundCell = true
						break
					}
				}
			}
			if !foundCell {
				sb.WriteString(".")
			}
		}
		sb.WriteString("\n")
	}
	return sb.String()
}

// Returns true if the supplied list of positions for pieces match the goal state of the Board
func (b Board) matchesGoal(positions []Coord) bool {
	if positions == nil {
		panic("Nil positions provided to matchesGoal")
	}
	if len(positions) != len(b.Pieces) {
		panic(fmt.Sprintf("Wrong number of positions provided to matchesGoal (required %d, given %d", len(b.Pieces), len(positions)))
	}
	for y:= 0; y < boardDim; y++ {
		for x:= 0; x < boardDim; x++ {
			foundPiece := false
			for p := 0; p < len(b.Pieces); p++ {
				if b.Pieces[p].HasCellAtCoord(Coord{x, y}, positions[p]) {
					foundPiece = true
					if b.Pieces[p].TypeId != b.Goal[y][x] {
						return false
					}
					break
				}
			}
			if !foundPiece && b.Goal[y][x] != 0 {
				return false
			}
		}
	}
	return true
}

// Returns true if coord is within the bounds of the rectangle defined by boundTopLeft and boundBottomRight
func withinBounds(coord Coord, boundTopLeft Coord, boundBottomRight Coord) bool {
    return coord.X >= boundTopLeft.X && coord.X <= boundBottomRight.X && coord.Y >= boundTopLeft.Y && coord.Y <= boundBottomRight.Y
}

// Returns true if the two rectangles defined by topLeft,bottomRight and otherTopLeft,otherBottomRight overlap at any point
func boundsOverlap(topLeft Coord, bottomRight Coord, otherTopLeft Coord, otherBottomRight Coord) bool {
	topRight := Coord{bottomRight.X, topLeft.Y}
	bottomLeft := Coord{topLeft.X, bottomRight.Y}
	otherTopRight := Coord{otherBottomRight.X, otherTopLeft.Y}
	otherBottomLeft := Coord{otherTopLeft.X, otherBottomRight.Y}
    return withinBounds(topLeft, otherTopLeft, otherBottomRight) || withinBounds(topRight, otherTopLeft, otherBottomRight) || withinBounds(bottomLeft, otherTopLeft, otherBottomRight) || withinBounds(bottomRight, otherTopLeft, otherBottomRight) || withinBounds(otherTopLeft, topLeft, bottomRight) || withinBounds(otherTopRight, topLeft, bottomRight) || withinBounds(otherBottomLeft, topLeft, bottomRight) || withinBounds(otherBottomRight, topLeft, bottomRight)
}

// Returns true if the SlidingPiece with pieceId can be legally moved 1 space in the specified direction given the current positions of all pieces on the Board. 
// Tests if any part of the piece would leave the board or collide with any other pieces.
func (b Board) canMove(pieceId int, direction Direction, positions []Coord) bool {
	if positions == nil {
		panic("Nil positions provided to canMove")
	}
	if len(positions) != len(b.Pieces) {
		panic(fmt.Sprintf("Wrong number of positions provided to canMove (required %d, given %d", len(b.Pieces), len(positions)))
	}
	if pieceId > len(positions) || pieceId < 1 || pieceId > len(b.Pieces) {
		panic(fmt.Sprintf("Invalid piece id %d provided to canMove", pieceId))
	}
	
	pieceIndex := pieceId - 1
	offset := direction.Offset()
	piecePosition := positions[pieceIndex].add(offset)
	// test if piece moves outside the board
	if piecePosition.X < 0 || piecePosition.X + b.Pieces[pieceIndex].Bound.X - 1 >= boardDim || piecePosition.Y < 0 || piecePosition.Y + b.Pieces[pieceIndex].Bound.Y - 1 >= boardDim {
		return false
	}
	topLeft := piecePosition
	bottomRight := topLeft.add(Coord{b.Pieces[pieceIndex].Bound.X - 1, b.Pieces[pieceIndex].Bound.Y - 1})
	// test if offset piece position would overlap other pieces
	for otherIndex := 0; otherIndex < len(b.Pieces); otherIndex++ {
		if otherIndex == pieceIndex {
			continue 
		}
		// skip per-cell testing if the bounding boxes don't overlap
		otherPieceTopLeft := positions[otherIndex]
		otherPieceBottomRight := otherPieceTopLeft.add(Coord{b.Pieces[otherIndex].Bound.X - 1, b.Pieces[otherIndex].Bound.Y - 1})
		if !boundsOverlap(topLeft, bottomRight, otherPieceTopLeft, otherPieceBottomRight) {
			continue
		}
		for i := 0; i < len(b.Pieces[pieceIndex].Cells.CoordList); i++ {
			cellPosition := b.Pieces[pieceIndex].Cells.CoordList[i].add(piecePosition)
			for j := 0; j < len(b.Pieces[otherIndex].Cells.CoordList); j++ {
				otherCellPosition := b.Pieces[otherIndex].Cells.CoordList[j].add(positions[otherIndex])
				if otherCellPosition == cellPosition {
					return false
				}
			}
		}
	}
	return true
}

// Returns a string representing the state of SlidingPieces on the board, given by type id rather than piece id. 
// Used as an associative key for a map of reached board states in the Dijkstra method.
func (b Board) stateKey(positions []Coord) string {
	buffer := make([]int, boardDim * boardDim)
	for p := 0; p < len(b.Pieces); p++ {
		for c := 0; c < len(b.Pieces[p].Cells.CoordList); c++ {
			offsetPos := b.Pieces[p].Cells.CoordList[c].add(positions[p])
			index := offsetPos.X + offsetPos.Y * boardDim
			buffer[index] = b.Pieces[p].TypeId
		}
	}
	var sb strings.Builder
	for i := 0; i < boardDim * boardDim; i++ {
		sb.WriteString(strconv.Itoa(buffer[i]))
	}
	return sb.String()
}

// Returns a string representing the goal state of the board, with the same format as the stateKey method.
func (b Board) goalKey() string {
	var sb strings.Builder
	for y := 0; y < boardDim; y++ {
		for x := 0; x < boardDim; x++ {
			sb.WriteString(strconv.Itoa(b.Goal[y][x]))
		}
	}
	return sb.String()
}

// Stores an intermediate state of a set of moves on the Board, giving the positions of all pieces, the accumulated cost of the moves and a string indicating the sequence of moves used to reach the state.
type DijkstraState struct {
	positions []Coord
	Cost int
	Path string
}

// Returns a DijkstraState object containing a valid sequence of moves to reach the goal state of the Board from the starting state without exceeding maxCost, or a non-nil error on failure. 
// Passing verbose as true will print the size of the queue at each step.
func (b Board) Dijkstra(maxCost int, verbose bool) (DijkstraState, error) {
	directions := []Direction{Up, Left, Down, Right}
	goalKey := b.goalKey()
	startPositions := make([]Coord, len(b.Pieces))
	for p := 0; p < len(b.Pieces); p++ {
		startPositions[p] = b.Pieces[p].Start
	}
	seen := make(map[string]int)
	reached := make([]DijkstraState,0)
	queue := make([]DijkstraState,0)
	queueNext := make([]DijkstraState, 0)
	queueNext = append(queueNext, DijkstraState{startPositions, 0, ""})
	
	step := 1
	for len(queueNext) > 0 {
		if(verbose) {
			fmt.Println(fmt.Sprintf("Step %d: \t%d paths in queue", step, len(queueNext)))
		}
		step += 1
		queue = queueNext
		queueNext = make([]DijkstraState, 0)
		for i := 0; i < len(queue); i++ {
			seenKey := b.stateKey(queue[i].positions)
			seenCost, found := seen[seenKey]
			if !found || seenCost >= queue[i].Cost {
				seen[seenKey] = queue[i].Cost
			} else {
				continue
			}
			for p := 0; p < len(b.Pieces); p++ {
				for d := 0; d < len(directions); d++ {
					if(b.canMove(b.Pieces[p].Id, directions[d], queue[i].positions)) {
						nextCost := queue[i].Cost + b.Pieces[p].Cost
						if nextCost > maxCost {
							continue
						}
						nextPositions := make([]Coord, len(b.Pieces))
						copy(nextPositions, queue[i].positions)
						nextPositions[p] = nextPositions[p].add(directions[d].Offset())
						nextPath := queue[i].Path + strconv.Itoa(b.Pieces[p].Id) + directions[d].String()
						nextSeenKey := b.stateKey(nextPositions)
						if nextSeenKey == goalKey {
							reached = append(reached, DijkstraState{nextPositions, nextCost, nextPath})
							continue
						}
						seenCost, found = seen[nextSeenKey]
						if !found || seenCost > nextCost {
							seen[nextSeenKey] = nextCost
							queueNext = append(queueNext, DijkstraState{nextPositions, nextCost, nextPath})
						}
					}
				}
			}
		}
	}
	if(len(reached) > 0) {
		return reached[rand.Int() % len(reached)], nil
	}
	return DijkstraState{nil, 0, ""}, errors.New("No results found")
}

// Returns the total move cost of provided solution string on the Board or a non-nil error if the solution is not valid. 
// Passing trace as true will print the state of the board after each move in the solution is made.
func (b Board) Validate(path string, trace bool) (int,error) {
	if trace {
		fmt.Println(fmt.Sprintf("\nValidating solution: %s", path))
	}
	// Initial testing for a valid-looking path string
	if len(path) % 2 != 0 {
		return 0, errors.New(fmt.Sprintf("Provided path is not of even length (%d)", len(path)))
	}
	for i:=0; i < len(path); i+=2 {
		pieceId, err := strconv.Atoi(string(path[i]))
		if err != nil {
			return 0, errors.New(fmt.Sprintf("Non-numeric character %s at position %d", string(path[i]), i))
		}
		if pieceId == 0 || pieceId > len(b.Pieces) {
			return 0, errors.New(fmt.Sprintf("Invalid piece id %s at position %d (%d pieces on this board)", string(path[i]), i, len(b.Pieces)))
		}
		_,err = DirectionFromCharacter(string(path[i+1]))
		if err != nil {
			return 0, errors.New(fmt.Sprintf("Unrecognized direction %s at position %d", string(path[i]), i))
		}
	}
	// Perform all moves in sequence while testing for invalid moves
	positions := make([]Coord, len(b.Pieces))
	for i:= 0; i < len(b.Pieces); i++ {
		positions[i] = b.Pieces[i].Start
	}
	cost := 0
	if trace {
		fmt.Println(fmt.Sprintf("\nStarting state"))
		fmt.Print(b.ToString(false, positions))
		fmt.Println(fmt.Sprintf("Accumulated cost: %d\n", cost))
	}
	for i:= 0; i < len(path); i+=2 {
		moveNum := i/2 + 1
		pieceId, _ := strconv.Atoi(string(path[i]))
		dir, _ := DirectionFromCharacter(string(path[i+1]))
		nextPos := positions[pieceId - 1].add(dir.Offset())
		// Test if the move takes the piece of the board
		for c := 0; c < len(b.Pieces[pieceId - 1].Cells.CoordList); c++ {
			cell_pos := b.Pieces[pieceId - 1].Cells.CoordList[c].add(nextPos)
			if cell_pos.X < 0 || cell_pos.X >= boardDim || cell_pos.Y < 0 || cell_pos.Y >= boardDim {
				return 0, errors.New(fmt.Sprintf("Move %d (%s) takes piece %d off of the board", moveNum, path[i:i+2], pieceId))
			}
		}
		// Test if the move collides with other pieces
		for pOther := 0; pOther < len(b.Pieces); pOther++ {
			if pOther == pieceId - 1 {
				continue
			}
			pOtherPos := positions[pOther]
			for c := 0; c < len(b.Pieces[pieceId - 1].Cells.CoordList); c++ {
				cPos := b.Pieces[pieceId - 1].Cells.CoordList[c].add(nextPos)
				for cOther := 0; cOther < len(b.Pieces[pOther].Cells.CoordList); cOther++ {
					cOtherPos := b.Pieces[pOther].Cells.CoordList[cOther].add(pOtherPos)
					if cOtherPos == cPos {
						return 0, errors.New(fmt.Sprintf("Move %d (%s) has a collision between pieces %d and %d", moveNum, path[i:i+2], pieceId, pOther + 1))
					}
				}
			}
		}
		cost += b.Pieces[pieceId - 1].Cost
		positions[pieceId - 1] = nextPos
		if trace {
			fmt.Println(fmt.Sprintf("Step %d: %s", (i / 2) + 1, path[i:i+2]))
			fmt.Print(b.ToString(false, positions))
			fmt.Println(fmt.Sprintf("Accumulated cost: %d\n", cost))
		}
	}
	// Verify we match the goal state
	if(!b.matchesGoal(positions)) {
		return 0, errors.New(fmt.Sprintf("Solution does not reach the goal state\n"))
	}
	if trace {
		fmt.Println(fmt.Sprintf("Solution reaches the goal state with cost %d\n", cost))
	}
	return cost, nil
}

// Parses a multi-line string describing the initial positions and shapes of all pieces on a Board and returns a 2D array of ints for futher processing.
func parseBoardString(boardString string) ([][]int, error) {
	lines := strings.Split(boardString, "\n")
	result := make([][]int, boardDim)
	for i:=0; i < boardDim; i++ {
		result[i] = make([]int, boardDim)
	}
	rowIndex := 0
	for i:= 0; i < len(lines); i++ {
		line := strings.TrimSpace(lines[i])
		if len(line) == 0 {
			continue
		}
		if rowIndex >= boardDim {
			return nil,errors.New("The provided board string contains too many rows")
		}
		if len(line) != boardDim {
			return nil, errors.New(fmt.Sprintf("The provided board string contains too many characters on row %d", i + 1))
		}
		for j:=0; j < len(line); j++ {
			if line[j] == '.' {
				result[rowIndex][j] = 0
			} else {
				val,err := strconv.Atoi(line[j:j+1])
				if err != nil {
					return nil, errors.New(fmt.Sprintf("The provided board string contains an invalid character at row %d column %d", rowIndex, j))
				}
				result[rowIndex][j] = val
			}
		}
		rowIndex += 1
	}
	return result, nil
}

// Returns a new Board object given a multi-line string describing the positions and shapes of the pieces on the Board, the total number of pieces,a map of piece id numbers to type id numbers (to handle identically shaped pieces being treated as equivalent) and a multi-line string describing the goal state of the board t. 
// Panics under various conditions if the provided board and piece information is invalid.
func NewBoard(boardString string, numPieces int, typeMap map[int]int, goalString string) Board {
	if numPieces == 0 || numPieces > 9 {
		panic(fmt.Sprintf("Unable to handle piece id numbers outside of 1-9 (%d pieces provided)", numPieces))
	}
	// boardString and goalString will have an empty first line
	boardCells, err := parseBoardString(boardString)
	if err != nil {
		panic(err)
	}
	goalCells, err := parseBoardString(goalString)
	if err != nil {
		panic(err)
	}
	
	pieces := make([]SlidingPiece, numPieces)
	for p := 1; p <= numPieces; p++ {
		if typeMap[p] == 0 {
			panic(fmt.Sprintf("No type id provided for piece id %d", p))
		}
		cellList := []Coord{}
		minX := -1
		maxX := -1
		minY := -1
		maxY := -1
		for y := 0; y < boardDim; y++ {
			for x := 0; x < boardDim; x++ {
				if boardCells[y][x] == p {
					cellList = append(cellList, Coord{x, y})
					if minX == -1 || minX > x {
						minX = x
					}
					if maxX == -1 || maxX < x {
						maxX = x
					}
					if minY == -1 || minY > y {
						minY = y
					}
					if maxY == -1 || maxY < y {
						maxY = y
					}
				}
			}
		}
		cells := NewCoordSet()
		for i:= 0; i < len(cellList); i++ {
			cells.insert(Coord {X:cellList[i].X - minX, Y:cellList[i].Y - minY})
		}
		piece := SlidingPiece{ Id: p, TypeId: typeMap[p], Cells: cells, Cost: costParam - len(cellList), Bound: Coord{maxX - minX + 1, maxY - minY + 1}, Start: Coord{minX, minY} }
		pieces[p - 1] = piece
	}
	return Board {pieces, goalCells}
}