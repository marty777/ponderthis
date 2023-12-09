# https://research.ibm.com/haifa/ponderthis/challenges/November2023.html

import argparse
from os import path
from sys import stderr, maxsize
from copy import deepcopy
from random import randrange
import queue

IDA_STAR_NODE_SQUARE_INDEX = 0
IDA_STAR_NODE_MOVE_INDEX = 1

# Reading from lines in an input file, this method should return lists of 
# integers describing the 880 distinct 4x4 magic squares for the integers 0-15, 
# plus all transformation of those squares by rotation and reflection.
# Returns False on error.
def importMagicSquares(lines):
    squares = []
    for i in range(0, len(lines)):
        line = lines[i]
        comment = line.find('#')
        if comment != -1:
            line = line[:comment].strip()
        if len(line) == 0:
            continue
        cols = line.split()
        if len(cols) != 16:
            print("Unable to read magic square on line {}. Incorrect number of columns found".format(i), file=stderr)
            return False
        tiles = []
        for j in range(0,16):
            try:
                column_int = int(cols[j])
                tiles.append(column_int)
            except ValueError:
                print("Unable to read magic square on line {}. The element in column {} ({}) could not be read as an integer".format(i, j, cols[j]), file=stderr)
                return False
        if not isMagic(tiles, False):
            print("Unable to read magic square on line {}. The arrangement does not form a magic square".format(i), file=stderr)
            return False
        # add this set of digits and all transformations to the list of magic 
        # squares. Note that we only need to reflect on one axis when combined
        # with rotation
        for reflect in range(0,2):
            for rotation in range(0,4):
                transformed_tiles = deepcopy(tiles)
                if reflect == 1:
                    transformed_tiles = reflectSquare(transformed_tiles)
                for rot in range(0, rotation):
                    transformed_tiles = rotateSquare(transformed_tiles)
                if not isMagic(transformed_tiles, False):
                    print("An error occurred while producing a transformation for the magic square on line {}. With {} reflections and {} clockwise rotations, the result does not form a magic square".format(i, reflect, rotation), file=stderr)
                    return False
                squares.append(transformed_tiles)
    return squares

# Convert a x,y coord in [0-3],[0-3] to a [0-15] index. Doesn't check bounds.
def index4(x,y):
    return x + (4 * y) 

# Verify that a given list of tiles describes a magic square with the 
# integers 0-15
def isMagic(tiles, verbose):
    expected = 30
    if len(tiles) != 16:
        if verbose:
            print("Incorrect length of tiles {} (expected {})".format(len(tiles), 16))
        return False
    for i in range(0,16):
        if tiles[i] < 0 or tiles[i] > 15:
            if verbose:
                print("Unexpected value {} at position ({},{}). Tiles must be in the range [0,15]".format(i, i % 4, i // 4))
            return False
    for x in range(0,4):
        col_sum = 0
        for y in range(0,4):
            col_sum += tiles[index4(x, y)]
        if col_sum != expected:
            if verbose:
                print("Column sum {} is {} (expected {})".format(x, col_sum, expected))
            return False
    for y in range(0,4):
        row_sum = 0
        for x in range(0,4):
            row_sum += tiles[index4(x, y)]
        if row_sum != expected:
            if verbose:
                print("Row sum {} is {} (expected {})".format(y, row_sum, expected))
            return False
    diag_sum1 = tiles[index4(0,0)] + tiles[index4(1,1)] + tiles[index4(2,2)] + tiles[index4(3,3)]
    if diag_sum1 != expected:
        if verbose:
            print("TLBR Diagonal sum {} is {} (expected {})".format(y, diag_sum1, expected))
        return False
    diag_sum2 = tiles[index4(3,0)] + tiles[index4(2,1)] + tiles[index4(1,2)] + tiles[index4(0,3)] 
    if diag_sum2 != expected:
        if verbose:
            print("TRBL Diagonal sum {} is {} (expected {})".format(y, diag_sum2, expected))
        return False
    return True


# Return a copy of the elements of the square with the positions reflected 
# horizontally
def reflectSquare(tiles):
    result = [0] * 16
    for x in range(0,4):
        for y in range(0,4):
            result[index4(3-x,y)] = tiles[index4(x,y)]
    return result 
    
# Return a copy of the elements of the square with the positions rotated 90 
# degrees clockwise
def rotateSquare(tiles):
    rotation = [12,8,4,0,13,9,5,1,14,10,6,2,15,11,7,3]
    result = [0] * 16
    for i in range(0, 16):
        result[i] = tiles[rotation[i]]
    return result

def stringSquare(tiles):
    result = ""
    for y in range(0,4):
        for x in range(0,4):
            result += "{:02d} ".format(tiles[index4(x,y)])
        result += "\n"
    result += "\n"
    return result

def printSquare(tiles):
    print(stringSquare(tiles))

# Stores the state of a 15-puzzle board.
# This is probably unnecessarily compact. My initial approach to the solution
# was much more memory-contrained. Tiles of the square and a lookup of tile 
# positions are packed into 64-bit integers, 4 bits per value. I'm not entirely
# clear on how much python abstracts integer representation, but this may
# prevent the script from running on 32-bit or big-endian architectures if not
# modified.
class Puzzle15State:
    def __init__(self, tiles):
        self.tiles = 0
        self.indexes = 0
        for i in range(0, 16):
            self.tiles |= tiles[i] << (4 * i)
            self.indexes |= i << (4 * tiles[i])
        self.goalid = 1 # all squares are solvable to one of two goal states.
    def __str__(self):
        result = ""
        tile_values = self.getTiles()
        for y in range(0,4):
            for x in range(0,4):
                if tile_values[index4(x,y)] > 9:
                    result += "{} ".format(tile_values[index4(x,y)])
                else:
                    result += "{}  ".format(tile_values[index4(x,y)])
            result += "\n"
        return result
    def getTiles(self):
        result = [0] * 16
        for i in range(0, 16):
            result[i] = (self.tiles >> (4 * i)) & 0xf
        return result
    def getIndexes(self):
        result = [0] * 16
        for i in range(0, 16):
            result[i] = (self.indexes >> (4 * i)) & 0xf
        return result
    def indexOfTile(self, tile):
        return self.indexes >> (4 * tile) & 0xf
    def tileAtIndex(self, index):
        return self.tiles >> (4 * index) & 0xf
    # Swaps the positions of two tiles, given by value.
    def swap(self, tile1, tile2):
        allBits = 0xffffffffffffffff
        index1 = self.indexOfTile(tile1)
        index2 = self.indexOfTile(tile2)
        # update the positions of tile1 and tile2 in the packed tiles
        self.tiles &= (0xf << (4 * index1)) ^ allBits
        self.tiles &= (0xf << (4 * index2)) ^ allBits
        self.tiles |= tile2 << (4 * index1)
        self.tiles |= tile1 << (4 * index2)
        # update the indexes for tile1 and tile1
        self.indexes &= (0xf << (4 * tile1)) ^ allBits
        self.indexes &= (0xf << (4 * tile2)) ^ allBits
        self.indexes |= index2 << (4 * tile1)
        self.indexes |= index1 << (4 * tile2)
    # Similar to swap, but includes checks for legal moves. Returns True on 
    # success.
    def safeSwap(self, tile1, tile2):
        index1 = self.indexOfTile(tile1)
        index2 = self.indexOfTile(tile2)
        x1 = index1 % 4
        x2 = index2 % 4
        y1 = index1 // 4
        y2 = index2 // 4
        if x1 == x2:
            if abs(y2 - y1) != 1:
                return False
        elif y1 == y2:
            if abs(x2 - x1) != 1:
                return False
        else:
            return False
        self.swap(tile1, tile2)
        return True

class Puzzle15:
    def __init__(self):
        # two possible goal states, 1-15 + 0 in order, and the same but with 14
        # and 15 swapped, to handle the two possible parities of all 15 puzzle
        # states.
        self.goal1 = Puzzle15State([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0])
        self.goal2 = Puzzle15State([1,2,3,4,5,6,7,8,9,10,11,12,13,15,14,0])
        print("Building index of Walking Distances for the 15-puzzle...")
        self.wdlookup = self.buildWalkingDistances()
    
    def inversionCount(self, square, goalsquare):
        inversions = 0
        # for each tile in the base square, count how many tiles appear after it (left-to-right, top-to-bottom)
        # that should appear before it in the goal square
        for i in range(0, 16):
            # horizontal
            tile = square.tileAtIndex(i)
            if tile == 0:
                continue
            src_index = i
            dst_index = goalsquare.indexOfTile(tile)
            i_inversions = 0
            for j in range(i+1, 16):
                tile2 = square.tileAtIndex(j)
                if tile2 == 0:
                    continue
                if goalsquare.indexOfTile(tile2) < dst_index:
                    i_inversions += 1
            inversions += i_inversions
        return inversions
    
    # See https://mathworld.wolfram.com/15Puzzle.html
    # For an NxN puzzle if N is odd, the goal is reachable if the number of 
    # inversions is even
    # For an NxN puzzle if N is even: 
    #   if the blank is on row 1 or 3 (0-indexed) and the number of inversions 
    #       is even, the goal is reachable
    #   if the blank is on row 0 or 2 and the nubmber of inversions is odd the 
    #       goal is reachable
    # All possible states of the 15-puzzle will be reachable from any other 
    # 15-puzzle state of the same parity, and no possible states of the 
    # opposite parity are reachable.
    def solvable(self, square, goalsquare):
        inversions = self.inversionCount(square, goalsquare)
        row0 = square.indexOfTile(0) // 4
        if row0 % 2 == 1 and inversions % 2 == 0:
            return True
        if row0 % 2 == 0 and inversions % 2 == 1:
            return True
        return False
    
    # keystring for the walking distances lookup
    def walkingDistanceKey(self, positions):
        group1 = sorted(positions[0])
        group2 = sorted(positions[1])
        group3 = sorted(positions[2])
        group4 = sorted(positions[3])
        return "[" + "[" + ",".join(map(str, group1))+"]," + "[" + ",".join(map(str, group2))+"]," + "[" + ",".join(map(str, group3))+"]," + "[" + ",".join(map(str, group4))+"]" + "]"
        
    # Construct the lookup of walking distances for all possible board states
    # using a BFS.
    # Note that the same lookup is used for the horizontal and vertical walking
    # distance of a puzzle state, with the tiles mapped to a walking distance 
    # horizontally or vertically
    def buildWalkingDistances(self):
        goal = [[1,1,1,1],[2,2,2,2],[3,3,3,3],[4,4,4,0]]
        goalKey = self.walkingDistanceKey(goal)
        seen = {}
        # queue elements are state, row index of 0, steps
        queue = []
        queueNext = []
        queueNext.append([goal,3,0])
        seen[goalKey] = 0
        rounds = 0
        while len(queueNext) > 0:
            rounds += 1
            queue = queueNext
            queueNext = []
            while len(queue) > 0:
                state = queue.pop()
                # for up and down moves of 0, find all distinct elements that 
                # can be swapped. 
                # up elements
                rows = state[0]
                blank_row_index = state[1]
                steps = state[2]
                if blank_row_index > 0:
                    unique_elements = set(rows[blank_row_index-1])
                    for unique_element in unique_elements:
                        nextRows = deepcopy(rows)
                        nextRows[blank_row_index].remove(0)
                        nextRows[blank_row_index-1].remove(unique_element)
                        nextRows[blank_row_index].append(unique_element)
                        nextRows[blank_row_index-1].append(0)
                        nextKey = self.walkingDistanceKey(nextRows)
                        if nextKey in seen:
                            continue
                        nextSteps = steps + 1
                        seen[nextKey] = nextSteps
                        nextBlankIndex = blank_row_index-1
                        queueNext.append([nextRows,nextBlankIndex, nextSteps])
                # down elements
                if blank_row_index < 3:
                    unique_elements = set(rows[blank_row_index+1])
                    for unique_element in unique_elements:
                        nextRows = deepcopy(rows)
                        nextRows[blank_row_index].remove(0)
                        nextRows[blank_row_index+1].remove(unique_element)
                        nextRows[blank_row_index].append(unique_element)
                        nextRows[blank_row_index+1].append(0)
                        nextKey = self.walkingDistanceKey(nextRows)
                        if nextKey in seen:
                            continue
                        nextSteps = steps + 1
                        seen[nextKey] = nextSteps
                        nextBlankIndex = blank_row_index+1
                        queueNext.append([nextRows,nextBlankIndex, nextSteps])
        return seen
        
    # Determine the walking distance between a puzzle state and a goal state. 
    # Developed by Ken'ichiro Takahashi, see 
    # https://www.mdpi.com/2073-431X/12/1/11 for an explanation of the walking 
    # distance heuristic, among others applicable to the 15-puzzle.
    # This is a a relaxed constraint heuristic. Rather than following the exact
    # rules of the puzzle, we calculate the horizontal walking distance by 
    # grouping tiles by row, where the order does not matter. At each step, 
    # the blank position can be exchanged with any tile in a neighboring row, 
    # continuing until all tiles are in the corresponding goal row. The same 
    # can be done for columns in the vertical walking distance. 
    # The total walking distance is the sum of the horizontal + vertical 
    # distances.
    # This method builds the horizontal and vertical walking distance keys for 
    # the provided square, determines the values from a pre-built lookup of all
    # possible walking distance states, and returns the horizontal + vertical
    # sum.
    def walkingDistance(self, square, goalsquare):
        wd_rows = []
        wd_cols = []
        for i in range(0,4):
            wd_rows.append([0] * 4)
            wd_cols.append([0] * 4)
        for row in range(0,4):
            for i in range(0,4):
                tile = square.tileAtIndex(index4(i,row))
                if tile == 0:
                    wd_rows[row][i] = 0
                else:
                    wd_rows[row][i] = (goalsquare.indexOfTile(tile) // 4) + 1
        for col in range(0,4):
            for i in range(0,4):
                tile = square.tileAtIndex(index4(col,i))
                if tile == 0:
                    wd_cols[col][i] = 0
                else:
                    wd_cols[col][i] = (goalsquare.indexOfTile(tile) % 4) + 1
        wd_row_key = self.walkingDistanceKey(wd_rows)
        wd_col_key = self.walkingDistanceKey(wd_cols)
        wd_row_val = self.wdlookup[wd_row_key]
        wd_col_val = self.wdlookup[wd_col_key]
        return  wd_row_val+wd_col_val 
    
    # Find all neighbors of the blank position on the board and returns a list
    # of tile values that can be swapped.
    def availableMoves(self, square):
        index = square.indexOfTile(0)
        x = index % 4
        y = index // 4
        moves = []
        if x > 0:
            moves.append(square.tileAtIndex(index4(x-1, y)))
        if x < 3:
            moves.append(square.tileAtIndex(index4(x+1, y)))
        if y > 0:
            moves.append(square.tileAtIndex(index4(x, y-1)))
        if y < 3:
            moves.append(square.tileAtIndex(index4(x, y+1)))
        return moves
    
    # Perform an iterative deepinging A* (IDA*) search to find a path between 
    # the provided square and one of the two possible goal states. Return the 
    # path if found or False if the path is not reachable within the provided
    # max_cost
    def ida_star(self, start_square, max_cost):
        goal = self.goal1
        # if goal1 can't reach start_square by parity check, use goal2
        if not self.solvable(start_square, goal):
            goal = self.goal2
        # estimate initial depth to search to
        bound = self.walkingDistance(start_square, goal)
        if bound > max_cost:
            return False
        # Nodes in the list contain two parameters: a square state and the 
        # value of the tile moved to reach the state from the previous state. 
        # The start state has no move to reach it.
        nodes = [[start_square, -1]]
        while True:
            cost_to_goal = self.ida_star_search(nodes, 0, bound, goal, max_cost)
            # if the goal is reached, the node list will include the list of 
            # moves and states that reach if from the start state. Skip the 
            # first node in the list, as the start state did not require a move
            # to reach it.
            if cost_to_goal == 0:
                moves = []
                for i in range(1, len(nodes)):
                    moves.append(nodes[i][IDA_STAR_NODE_MOVE_INDEX])
                return moves
            # if the goal is unreachable within max_cost, return False    
            if cost_to_goal == -1:
                return False 
            # if we haven't reached to goal or determined that it's unreachable
            # expand the bounds of the DFS based on the best heuristic estimate
            # and repeat
            bound = cost_to_goal
    
    # Perform the recursive DFS portion of the IDA* search. Return -1 if the 
    # goal state is not estimated to be reachable from the current list of 
    # states within max_cost, 0 if the goal is reached within the current 
    # bounds of the search depth, and the estimated cost to reach the goal 
    # otherwise. If the goal is reached, the list nodes should contain
    # the list of states and moves that reach the goal.
    def ida_star_search(self, nodes, cost, bound, goal, max_cost):   
        # If we've exceeded the maximum cost, assume the goal is unreachable
        # and search no deeper
        if cost > max_cost:
            return -1
        node = nodes[-1]
        estimated_cost = cost + self.walkingDistance(node[0], goal)
        # Since the heuristic cannot overestimate cost (it may underestimate)
        # take the goal to be unreachable if the estimated cost exceeds
        # the maximum cost and search no deeper
        if estimated_cost > max_cost:
            return -1
        # If estimated cost exceeds the current bounding depth of the DFS,
        # return it so the bound can be expanded.
        if estimated_cost > bound:
            return estimated_cost
        # If we have reached the goal, the cost is 0
        if node[IDA_STAR_NODE_SQUARE_INDEX].tiles == goal.tiles:
            return 0
        # Test each possible next move from this state for the best estimated 
        # cost. If no moves reach a previously unseen state, take the goal to be
        # unreachable.
        min_cost_to_goal = -1
        moves = self.availableMoves(node[IDA_STAR_NODE_SQUARE_INDEX])
        for move in moves:
            next_square = deepcopy(node[IDA_STAR_NODE_SQUARE_INDEX])
            next_square.swap(0,move)
            # Skip this move if we've previously reached this state in the 
            # current node list
            already_in_nodes = False
            for i in range(0, len(nodes) - 1):
                if nodes[len(nodes) - 1 - i][IDA_STAR_NODE_SQUARE_INDEX].tiles == next_square.tiles:
                    already_in_nodes = True
                    break
            if already_in_nodes:
                continue
            nodes.append([next_square, move])
            cost_to_goal = self.ida_star_search(nodes, cost + 1, bound, goal, max_cost)
            # If the goal has been reached within this branch of the DFS the 
            # current list of nodes will include the full path of states to it.
            # Return 0 indicating that the goal is reached.
            if cost_to_goal == 0:
                return 0
            # If the goal is estimated to be reachable within max_cost from this branch
            # but the DFS does not currently search deep enough, update the min_cost 
            # if it is unset or greater than the estimate.
            if cost_to_goal != -1:
                if min_cost_to_goal == -1 or min_cost_to_goal > cost_to_goal:
                    min_cost_to_goal = cost_to_goal
            # Remove this move from the node list and try the next
            nodes.pop()
        return min_cost_to_goal   
    # Ensure that we can reach the solutionsquare from one of the two starting states 
    # using the provided sequence of moves, that all the moves are legal,
    # and that the goal state is a magic square
    def verify(self, moves, solutionsquare, printstates):
        statesquare = deepcopy(self.goal1)
        if not self.solvable(solutionsquare, statesquare):
            statesquare = deepcopy(self.goal2)
        startstate = deepcopy(statesquare)
        for i in range(0, len(moves)):
            move = moves[i]
            okay = statesquare.safeSwap(move, 0)
            if not okay:
                return False
        if solutionsquare.getTiles() != statesquare.getTiles():
            return False
        if not isMagic(statesquare.getTiles(), True):
            return False
        if printstates:
            print("\nSolution found with {} moves ".format(len(moves)))
            print(moves)
            print("\nInitial state:")
            print(startstate)
            print("Final state:")
            print(statesquare)
        return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="a provided file listing all 880 distinct 4x4 magic squares")
    parser.add_argument("-m", "--maxdepth", default=50, type=int, help="maximum move depth to explore for solutions")
    args = parser.parse_args()
    # Handle maxdepth argument
    maximum_solution_length = args.maxdepth
    if maximum_solution_length < 35:
        print("Specified maximum move depth {} is too small. There are no solutions with fewer than 35 moves.".format(maximum_solution_length), file=stderr)
        parser.print_usage()
        exit()
    if maximum_solution_length > 80:
        print("Specified maximum move depth {} is too large. There are no optimal solutions to the 15 Puzzle that exceed 80 moves. Maximum move depth set to 80.".format(maximum_solution_length))
        maximum_solution_length = 80
    # Handle input file
    inputfile = args.inputfile
    if(not path.exists(inputfile)):
        print("Input file '{}' could not be found".format(inputfile), file=stderr)
        parser.print_usage()
        exit()
    f = open(inputfile, 'r')
    lines = f.readlines()
    f.close()
    squares = importMagicSquares(lines)
    if squares == False:
        print("Unable to import magic squares file {}.".format(inputifle),file=stderr)
        parser.print_usage()
        exit()
    print("Loaded {} magic squares, including those produced by rotation and reflection, from input file {}".format(len(squares), inputfile))
    
    puzzle = Puzzle15()
    print("Attempting to find solutions to reach a magic square from a sorted 15-puzzle state with no more than {} steps...".format(maximum_solution_length))
    remaining_squares = deepcopy(squares)
    attempts = 0
    # pick a magic square at random from the list and attempt to find a 
    # solution to a sorted start state in no more than 
    # maximum_solution_length moves
    while len(remaining_squares) > 0:
        attempts += 1
        square_index = randrange(0, len(remaining_squares))
        # load the elements of the square into a Puzzle15State object
        square = Puzzle15State(remaining_squares[square_index])
        print("Attempt {} ({} possible magic squares remaining)".format(attempts, len(remaining_squares)))
        solution = puzzle.ida_star(square, maximum_solution_length)
        if solution != False:
            # we've found the path from the square to the sorted state, so reverse the path
            solution.reverse()
            print("Verifying solution {}...".format(solution))
            if not puzzle.verify(solution, square, True):
                print("Solution did not pass verification")
                printSquare(square)
                return
            else:
                exit()
        del remaining_squares[square_index]
    print("No solutions found.")
    
if __name__ == "__main__":
    main()