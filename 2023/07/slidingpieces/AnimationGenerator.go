package slidingpieces

import (
	"golang.org/x/image/font"
    "golang.org/x/image/font/basicfont"
    "golang.org/x/image/math/fixed"
	"image"
	"image/color"
	"image/gif"
	"strconv"
	"fmt"
	"os"
)

type Bitmap struct {
	// bitmap width in pixels
	Width	int
	// bitmap height in pixels
	Height	int
	// pixels in RGBA
	pixels	[][]color.RGBA
}

// AnimationGenerator takes a defined board and valid solution and can output an animated gif
type AnimationGenerator struct {
	board 			Board
	solution 		DijkstraState
	// cached bitmaps of each piece type
	pieceTypeBitmaps	map[int]Bitmap	
	palette			[]color.Color
	outlineColor	color.RGBA
	bgColor			color.RGBA
	cellDim			int
	outlineDim		int
}

// Export an animated gif of the solution to the specified file path
// Each frame includes the accumulated cost to that point displayed in 7x13 fixed width basicfont characters
func (ag *AnimationGenerator) Generate(filePath string, moveFrames int, moveFrameDelay int, moveCompleteDelay int, solutionCompleteDelay int, reverse bool) {
	positions := make([]Coord, len(ag.board.Pieces))
	for i:= 0; i < len(ag.board.Pieces); i++ {
		positions[i] = ag.board.Pieces[i].Start
	}
	cost := 0
	textPaddingTop := 30
	textPaddingBottom := 5
	textPaddingLeft := 10
	textColor := ag.outlineColor
	textPoint := fixed.Point26_6{fixed.I(textPaddingLeft), fixed.I(ag.cellDim * boardDim + textPaddingTop )}
	
	imgWidth := ag.cellDim * boardDim
	imgHeight := ag.cellDim * boardDim + textPaddingTop + 13 + textPaddingBottom
	
	var images []*image.Paletted	// one image per frame of animation
	var delays []int				// one delay per frame of animation
	
	for i:= 0; i < len(ag.solution.Path); i+=2 {
		moveNum := i/2 + 1
		pieceId, _ := strconv.Atoi(string(ag.solution.Path[i]))
		pieceIndex := pieceId - 1
		dir, _ := DirectionFromCharacter(string(ag.solution.Path[i+1]))
		nextPos := positions[pieceId - 1].add(dir.Offset())
		cost += ag.board.Pieces[pieceIndex].Cost
		for j := 0; j <= moveFrames; j++ {
			img := image.NewPaletted(image.Rect(0, 0, imgWidth, imgHeight), ag.palette)
			// initialize the image to the bgColor 
			for y := 0; y < imgHeight; y++ {
				for x := 0; x < imgWidth; x++ {
					img.Set(x,y,ag.bgColor)
				}
			}
			images = append(images, img)
			if j == 0 {
				delays = append(delays, moveCompleteDelay)
			} else {
				delays = append(delays, moveFrameDelay)
			}
			// draw the board and all pieces except the piece currently being moved
			for p:= 0; p < len(ag.board.Pieces); p++ {
				if p == pieceIndex {
					continue
				}
				pX := positions[p].X * ag.cellDim
				pY := positions[p].Y * ag.cellDim
				pTypeId := ag.board.Pieces[p].TypeId
				for bY := 0; bY < ag.pieceTypeBitmaps[pTypeId].Height; bY++ {
					for bX := 0; bX < ag.pieceTypeBitmaps[pTypeId].Width; bX++ {
						// don't overwrite if alpha is zero. Ignore blending
						if(ag.pieceTypeBitmaps[pTypeId].pixels[bY][bX].A == 0x00) {
							continue
						}
						img.Set(pX + bX, pY + bY, ag.pieceTypeBitmaps[pTypeId].pixels[bY][bX])
					}
				}
			}
			
			// draw the current cost
			costStr := fmt.Sprintf("Move %d, Cost: %d", moveNum, cost)
			costDrawer := &font.Drawer{Dst: img, Src: image.NewUniform(textColor), Face: basicfont.Face7x13, Dot: textPoint}
			costDrawer.DrawString(costStr)
			
			// draw the piece being moved, with an interpolated position based on the moveFrame
			movePos := j * ag.cellDim / moveFrames
			moveX := dir.Offset().X * movePos
			moveY := dir.Offset().Y * movePos
			pieceX := positions[pieceIndex].X * ag.cellDim + moveX
			pieceY := positions[pieceIndex].Y * ag.cellDim + moveY
			pieceTypeId := ag.board.Pieces[pieceIndex].TypeId
			for bitmapY := 0; bitmapY < ag.pieceTypeBitmaps[pieceTypeId].Height; bitmapY++ {
				for bitmapX := 0; bitmapX < ag.pieceTypeBitmaps[pieceTypeId].Width; bitmapX++ {
					// don't overwrite if alpha is zero. Ignore blending
					if(ag.pieceTypeBitmaps[pieceTypeId].pixels[bitmapY][bitmapX].A == 0x00) {
						continue
					}
					img.Set(pieceX + bitmapX, pieceY + bitmapY, ag.pieceTypeBitmaps[pieceTypeId].pixels[bitmapY][bitmapX])
				}
			}
		}
		
		positions[pieceIndex] = nextPos
		
	}
	
	// draw final frame
	finalImg := image.NewPaletted(image.Rect(0, 0, imgWidth, imgHeight), ag.palette)
	// initialize the image to the bgColor 
	for y := 0; y < imgHeight; y++ {
		for x := 0; x < imgWidth; x++ {
			finalImg.Set(x,y,ag.bgColor)
		}
	}
	images = append(images, finalImg)
	delays = append(delays, solutionCompleteDelay)
	// draw the board and all pieces
	for p:= 0; p < len(ag.board.Pieces); p++ {
		pX := positions[p].X * ag.cellDim
		pY := positions[p].Y * ag.cellDim
		pTypeId := ag.board.Pieces[p].TypeId
		for bY := 0; bY < ag.pieceTypeBitmaps[pTypeId].Height; bY++ {
			for bX := 0; bX < ag.pieceTypeBitmaps[pTypeId].Width; bX++ {
				// don't overwrite if alpha is zero. Ignore blending
				if(ag.pieceTypeBitmaps[pTypeId].pixels[bY][bX].A == 0x00) {
					continue
				}
				finalImg.Set(pX + bX, pY + bY, ag.pieceTypeBitmaps[pTypeId].pixels[bY][bX])
			}
		}
	}
	// draw the final cost
	costStr := fmt.Sprintf("Move %d, cost: %d", len(ag.solution.Path)/2, cost)
	costDrawer := &font.Drawer{Dst: finalImg, Src: image.NewUniform(textColor), Face: basicfont.Face7x13, Dot: textPoint}
	costDrawer.DrawString(costStr)
	
	// if the reverse flag is set, quickly wind back the entire animation to the start
	if(reverse) {
		frameCount := len(images)
		for i:= frameCount - 1; i > 0; i-- {
			copyFrame := image.NewPaletted(image.Rect(0, 0, imgWidth, imgHeight), ag.palette)
			for y:= 0; y < imgHeight; y++ {
				for x:= 0; x < imgWidth; x++ {
					copyFrame.Set(x,y,images[i].At(x,y))
				}
			}
			images = append(images,copyFrame)
			delays = append(delays, 0)
		}
		
	}
	
	f, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE, 0600)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer f.Close()
	gif.EncodeAll(f, &gif.GIF{
		Image: images,
		Delay: delays,
	})
}

func NewPieceBitmap(piece SlidingPiece, fillColor color.RGBA, outlineColor color.RGBA, cellDim int, outlineDim int) Bitmap {
	// outline is external to cell fill area, so width and height of the bitmap are cell width and cell height of the piece, multiplied by cellDim + 2 * outlineDim 
	width := piece.Bound.X * cellDim + 2 * outlineDim
	height := piece.Bound.Y * cellDim + 2 * outlineDim
	if width == 0 || height == 0 {
		panic(fmt.Sprintf("Piece has invalid bitmap dimension %d x %d", width, height))
	}
	if(cellDim < 1) {
		panic(fmt.Sprintf("Provided cellDim %d is too small (must be at least 1 pixel)", cellDim))
	}
	if(outlineDim < 1) {
		panic(fmt.Sprintf("Provided outlineDim %d is too small (must be at least 1 pixel)", outlineDim))
	}
	if outlineDim >= cellDim {
		panic(fmt.Sprintf("Provided outlineDim %d is greater than cellDim %d", outlineDim, cellDim))
	}
	
	// init the pixels and set all to fully transparent white
	pixels := make([][]color.RGBA, height)
	for y := 0; y < height; y++ {
		pixels[y] = make([]color.RGBA, width)
		for x := 0; x < width; x++ {
			pixels[y][x] = color.RGBA{0xff, 0xff, 0xff, 0x00}
		}
	}
	// draw the cell fills
	for c := 0; c < len(piece.Cells.CoordList); c++ {
		for y:= 0; y < cellDim; y++ {
			for x:= 0; x < cellDim; x++ {
				cX := piece.Cells.CoordList[c].X * cellDim + x + outlineDim
				cY := piece.Cells.CoordList[c].Y * cellDim + y + outlineDim
				pixels[cY][cX] = fillColor
			}
		}
	}
	// draw the cell outlines
	for c := 0; c < len(piece.Cells.CoordList); c++ {
		// add top outline border if no neighboring cells
		topCoord := piece.Cells.CoordList[c].add(Up.Offset())
		if(!piece.Cells.contains(topCoord)) {
			
			startX := 0
			endX := cellDim + outlineDim;
			for x := startX; x < endX; x++ {
				for y := 0; y < outlineDim; y++ {
					oY := piece.Cells.CoordList[c].Y * cellDim + y
					oX := piece.Cells.CoordList[c].X * cellDim + x
					pixels[oY][oX] = outlineColor
				}
			}
		}
		// add bottom outline border if no neighboring cells
		bottomCoord := piece.Cells.CoordList[c].add(Coord{0,1})
		if(!piece.Cells.contains(bottomCoord)) {
			
			startX := 0
			endX := cellDim + outlineDim;
			for x := startX; x < endX; x++ {
				for y := 0; y < outlineDim; y++ {
					oY := piece.Cells.CoordList[c].Y * (cellDim) + cellDim - 1 - y + outlineDim
					oX := piece.Cells.CoordList[c].X * cellDim + x
					pixels[oY][oX] = outlineColor
				}
			}
			
		}
		// add left outline border if no neighboring cells
		leftCoord := piece.Cells.CoordList[c].add(Left.Offset())
		if(!piece.Cells.contains(leftCoord)) {
			startY := 0
			endY := cellDim + outlineDim;
			for y := startY; y < endY; y++ {
				for x := 0; x < outlineDim; x++ {
					oY := piece.Cells.CoordList[c].Y * cellDim + y
					oX := piece.Cells.CoordList[c].X * cellDim + x
					pixels[oY][oX] = outlineColor
				}
			}
			
		}
		// add right outline border if no neighboring cells
		rightCoord := piece.Cells.CoordList[c].add(Right.Offset())
		if(!piece.Cells.contains(rightCoord)) {
			startY := 0
			endY := cellDim + outlineDim;
			for y := startY; y < endY; y++ {
				for x := 0; x < outlineDim; x++ {
					oY := piece.Cells.CoordList[c].Y * cellDim + y
					oX := piece.Cells.CoordList[c].X * (cellDim) + cellDim - 1 - x + outlineDim
					pixels[oY][oX] = outlineColor
				}
			}
		}
	}
	
	return Bitmap{width, height, pixels}
}

func NewAnimationGenerator(board Board, solution DijkstraState, pieceColors map[int]color.RGBA, cellDim int, outlineDim int) AnimationGenerator {
	_,validateErr :=  board.Validate(solution.Path, false)
	if(validateErr != nil) {
		panic(fmt.Sprintf("Provided solution does not pass validation %s", validateErr))
	}
	for p:= 0; p < len(board.Pieces); p++ {
		_, ok := pieceColors[board.Pieces[p].TypeId]
		if(!ok) {
			panic(fmt.Sprintf("pieceColors does not include a color assignment for piece type %d", board.Pieces[p].TypeId))
		}
	}
	// assuming no duplicate colors are included in the piece colors map, include each of them, plus black and white
	var palette []color.Color
	for _,color := range pieceColors {
		palette = append(palette, color)
	}
	
	outlineColor := color.RGBA{0x00,0x00,0x00,0xff}	// black
	bgColor := color.RGBA{0xff,0xff,0xff,0xff}		// white
	
	palette = append(palette, outlineColor) 
	palette = append(palette, bgColor) 
	// pre-build piece bitmaps
	pieceBitmaps := make(map[int]Bitmap, len(board.Pieces))
	for p := 0; p < len(board.Pieces); p++ {
		_,exists := pieceBitmaps[board.Pieces[p].TypeId]
		if !exists {
			pieceBitmaps[board.Pieces[p].TypeId] = NewPieceBitmap(board.Pieces[p], pieceColors[board.Pieces[p].TypeId], outlineColor, cellDim, outlineDim)
		}
	}
	return AnimationGenerator{board, solution, pieceBitmaps, palette, outlineColor, bgColor, cellDim, outlineDim}
}

