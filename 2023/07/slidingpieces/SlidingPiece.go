package slidingpieces

// SlidingPiece stores an id, type id, starting position on the board, cells in the piece and cost of moving a piece.
type SlidingPiece struct {
	Id		int
	TypeId	int
	// Cells are given as a set of coordinates relative to the top-left corner of the piece bounding rectangle
	Cells 	CoordSet
	Cost	int
	// The width and height of the piece used as a bounding rectangle for quicker intersection testing
	Bound	Coord
	// The position of the piece on the board in the starting state, given by the top-left coordinate of its bounding rectangle
	Start	Coord
}

// Returns true if the piece contains a cell at the same location as c when the piece is at the provided position on the board
func (p SlidingPiece) HasCellAtCoord(c Coord, piecePosition Coord) bool {
	// test bounding box for early return
	if c.X < piecePosition.X || c.X > piecePosition.X + p.Bound.X - 1 || c.Y < piecePosition.Y || c.Y > piecePosition.Y + p.Bound.Y - 1 {
		return false
	}
	internalCoord := Coord{c.X - piecePosition.X, c.Y - piecePosition.Y}
	return p.Cells.contains(internalCoord)
}