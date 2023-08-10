 package main
 
 import (
	"testing"
	"jul2023/slidingpieces"
 )
 
 // Test simple example of piece movement off the board and finding the shortest path to some goals
 func TestPieceMovement(t *testing.T) {
	exampleBoardString := `
    ...1.
    ...1.
    ..11.
    .....
    .....`
	exampleBoardNumPieces := 1
	exampleBoardPieceTypes := map[int]int { 1:1 }
	exampleGoalString1D1D := `
    .....
    .....
    ...1.
    ...1.
    ..11.`
	exampleGoalString1L1L1D1D := `
    .....
    .....
    .1...
    .1...
    11...`
	exampleBoard1U := slidingpieces.NewBoard(exampleBoardString, exampleBoardNumPieces, exampleBoardPieceTypes, exampleBoardString)
	_, err1U := exampleBoard1U.Validate("1U", false)
	// Moving piece 1 up by one position should produce an error 
	if err1U == nil {
		t.Fatalf("Movement test 1U did not produce an error expected from moving off the board")
	}
	if err1U.Error() != "Move 1 (1U) takes piece 1 off of the board" {
		t.Fatalf("Movement test 1U did not produce the expected error expected from moving off the board: %s", err1U)
	}
	exampleBoard1D1D := slidingpieces.NewBoard(exampleBoardString, exampleBoardNumPieces, exampleBoardPieceTypes, exampleGoalString1D1D)
	result1D1D, err1D1D := exampleBoard1D1D.Dijkstra(2, false)
	if err1D1D != nil {
		t.Fatalf("Movement test 1D1D did not find a result")
	}
	if result1D1D.Path != "1D1D" {
		t.Fatalf("Movement test 1D1D did not find the correct path: %s", result1D1D.Path)
	}
	cost1D1D, errValidate1D1D := exampleBoard1D1D.Validate(result1D1D.Path, false)
	if errValidate1D1D != nil {
		t.Fatalf("Validation of test 1D1D produced an error: %s", errValidate1D1D)
	}
	if cost1D1D != 2 {
		t.Fatalf("Validated cost %d of test 1D1D did not match expected cost %d", cost1D1D, 2)
	}
		
	exampleBoard1L1L1D1D := slidingpieces.NewBoard(exampleBoardString, exampleBoardNumPieces, exampleBoardPieceTypes, exampleGoalString1L1L1D1D)
	result1L1L1D1D, err1L1L1D1D := exampleBoard1L1L1D1D.Dijkstra(4, false)
	if err1L1L1D1D != nil {
		t.Fatalf("Movement test 1L1L1D1D did not find a result")
	}
	if result1L1L1D1D.Cost != 4 {
		t.Fatalf("Movement test 1L1L1D1D did not find the shortest path: %s", result1L1L1D1D.Path)
	}
	cost1L1L1D1D, errValidate1L1L1D1D := exampleBoard1L1L1D1D.Validate(result1L1L1D1D.Path, false)
	if errValidate1L1L1D1D != nil {
		t.Fatalf("Validation of test 1L1L1D1D produced an error: %s", errValidate1L1L1D1D)
	}
	if cost1L1L1D1D != 4 {
		t.Fatalf("Validated cost %d of test 1L1L1D1D did not match expected cost %d", cost1L1L1D1D, 4)
	}
 }
 
 // Test collision detection between pieces
 func TestPieceCollision(t * testing.T) {
	 exampleBoardString := `
    .....
    .2213
    ..11.
    .....
    ..44.`
	exampleBoardNumPieces := 4
	exampleBoardPieceTypes := map[int]int { 1:1, 2:2, 3:3, 4:4 }
	exampleGoalString := `
    .....
    .2213
    ..11.
    .....
    ..44.`
	exampleGoalString1D1L := `
    .....
    .22.3
    ..1..
    .11..
    ..44.`
	exampleGoalString1D1R := `
    .....
    .22.3
    ....1
    ...11
    ..44.`
	test1U := "1U"
	test1L := "1L"
	test1R := "1R"
	test1D1L := "1D1L"
	test1D1R := "1D1R"
	test1D1D := "1D1D"
	exampleBoard := slidingpieces.NewBoard(exampleBoardString, exampleBoardNumPieces, exampleBoardPieceTypes, exampleGoalString)
	exampleBoard1D1L := slidingpieces.NewBoard(exampleBoardString, exampleBoardNumPieces, exampleBoardPieceTypes, exampleGoalString1D1L)
	exampleBoard1D1R := slidingpieces.NewBoard(exampleBoardString, exampleBoardNumPieces, exampleBoardPieceTypes, exampleGoalString1D1R)
	_,err1U := exampleBoard.Validate(test1U, false)
	if err1U == nil {
		t.Fatalf("Collision test 1U does not procuce an error")
	}
	if err1U.Error() != "Move 1 (1U) has a collision between pieces 1 and 2" {
		t.Fatalf("Collision test 1U does not procuce the expected error: %s", err1U)
	}
	_,err1L := exampleBoard.Validate(test1L, false)
	if err1L == nil {
		t.Fatalf("Collision test 1L does not procuce an error")
	}
	if err1L.Error() != "Move 1 (1L) has a collision between pieces 1 and 2" {
		t.Fatalf("Collision test 1L does not procuce the expected error: %s", err1L)
	}
	_,err1R := exampleBoard.Validate(test1R, false)
	if err1R == nil {
		t.Fatalf("Collision test 1R does not procuce an error")
	}
	if err1R.Error() != "Move 1 (1R) has a collision between pieces 1 and 3" {
		t.Fatalf("Collision test 1R does not procuce the expected error: %s", err1R)
	}
	_,err1D1L := exampleBoard1D1L.Validate(test1D1L, false)
	if err1D1L != nil {
		t.Fatalf("Non-collision test 1D1L produces an unexpected error: %s", err1D1L)
	}
	_,err1D1R := exampleBoard1D1R.Validate(test1D1R, false)
	if err1D1R != nil {
		t.Fatalf("Non-collision test 1D1R produces an unexpected error: %s", err1D1R)
	}
	_,err1D1D := exampleBoard.Validate(test1D1D, false)
	if err1D1D == nil {
		t.Fatalf("Collision test 1D1D does not procuce an error")
	}
	if err1D1D.Error() != "Move 2 (1D) has a collision between pieces 1 and 4" {
		t.Fatalf("Collision test 1D1D does not procuce the expected error: %s %s", err1D1D, test1D1D)
	}
 }
 
 // Test the sample board from the challenge specification
 func TestExampleBoard(t *testing.T) {
	exampleBoardString := `
    .112.
    .122.
    34556
    74666
    .....`
    exampleBoardNumPieces := 7
    exampleBoardPieceTypes := map[int]int { 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:3 }
    exampleGoalString := `
    11..2
    14.22
    34556
    .3666
    .....`
	exampleBoard := slidingpieces.NewBoard(exampleBoardString, exampleBoardNumPieces, exampleBoardPieceTypes, exampleGoalString)
	exampleResult, exampleErr := exampleBoard.Dijkstra(12, false)

	if exampleErr != nil {
		t.Fatalf("Solving the sample board returned an error: %s", exampleErr)
	}
	exampleCost, exampleValidateErr := exampleBoard.Validate(exampleResult.Path, false)
	if exampleValidateErr != nil {
		t.Fatalf("Validating the solution to the sample board returned an error: %s", exampleValidateErr)
	}
	if exampleCost != 11 {
		t.Fatalf("Sample board found an incorrect cost %d (%d expected)", exampleCost, 11)
	}
 }