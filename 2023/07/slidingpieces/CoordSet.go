package slidingpieces

// CoordSet stores a set of Coord objects to enable quick testing for membership in the set and provide an iterable array of Coords in the set.
type CoordSet struct {
	coords		map[Coord]struct{}
	CoordList 	[]Coord
}

// Returns true if the provided Coord is a member of the CoordSet
func (cs CoordSet) contains(c Coord) bool {
	if _,ok := cs.coords[c]; ok {
		return true
	}
	return false
}

// Adds a Coord to the set, if an identical coord is not already present
func (cs *CoordSet) insert(c Coord) {
	if !cs.contains(c) {
		cs.coords[c] = struct{}{}
		cs.CoordList = append(cs.CoordList, c)
	}
}

// Returns a new, empty CoordSet
func NewCoordSet() CoordSet {
	return CoordSet{coords: make(map[Coord]struct{}), CoordList: make([]Coord, 0)}
}