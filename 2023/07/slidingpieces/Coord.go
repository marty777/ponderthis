package slidingpieces

import (
	"fmt"
)

// A Coord stores a position on the Board in x and y
type Coord struct {
	X	int
	Y	int
}

// Returns a new Coord as the sum of this Coord and the provided other Coord.
func (c Coord) add(other Coord) Coord {
	return Coord { X: c.X + other.X, Y: c.Y + other.Y}
}

// Returns the default string representation of the Coord
func (c Coord) String() string {
	return fmt.Sprintf("(%d, %d)", c.X, c.Y)
}

