package slidingpieces

import (
	"fmt"
	"errors"
)

// Direction represents a possible direction to move a SlidingPiece on the Board (up, down, left and right)
type Direction int

const (
	Up Direction = iota
	Down
	Left
	Right		
)

// Returns a single-character string representing the direction.
func (d Direction) String() string {
	switch d {
		case Up:
			return "U"
		case Down:
			return "D"
		case Left:
			return "L"
		case Right:
			return "R"
	}
	return "undefined direction"
}

// Returns a Coord representing the vector of a movement on the Board by one space in the Direction.
func (d Direction) Offset() Coord {
	switch d {
		case Up:
			return Coord{0,-1}
		case Down:
			return Coord{0,1}
		case Left:
			return Coord{-1,0}
		case Right:
			return Coord{1,0}
	}
	fmt.Println("WARNING: No offset found for direction ", d)
	return Coord{0,0}
}

// Returns a Direction given a single-character string representing that direction, or a non-nil error if a matching string was not provided.
func DirectionFromCharacter(dirChar string) (Direction, error) {
	switch dirChar {
		case "U":
			return Up, nil
		case "D":
			return Down, nil
		case "L":
			return Left, nil
		case "R":
			return Right, nil
	}
	return Up, errors.New(fmt.Sprintf("Undefined direction string %s", dirChar))
}	