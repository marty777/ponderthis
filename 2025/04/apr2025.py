# https://research.ibm.com/haifa/ponderthis/challenges/April2025.html

from dataclasses import dataclass
from math import isqrt
from random import choice
from copy import deepcopy
import argparse

DIRS = {'U':(0, -1), 'R': (1, 0), 'D': (0, 1), 'L': (-1, 0)}

MAIN_MAX_STEPS = 500
BONUS_MAX_STEPS = 150

MAIN_BOARD = """ 0  0  1  5  1  0  0  0  0  0  1 19  0  7  4  2  7 12  7  1
                 2  6  0  0  1  8  0  8  1  2  1  0  8  9  1  7 10 13 10  6
                 4 11  6  7  5  5 14  1 12  1  0  2  0  2  2  5  1 10  0 14
                15 12  2  5 18  6 19 16 18 11 14  3  1  2  3  3  8  2  1  9
                 5  6  8 18  4 17  7 16 14 13  4 13  8  1  2  2  7  5 11 12
                 6  7 13 16  1 14  7 17 18  9 14  6 16 10  0  3  2  0  6  5
                11  5 11  3 14 19 19  4 17 16  3 12 17 17  1  2 12  6  7 11
                18  6  6  3 19 13  7  9  5 13  4  4  2 13  2  0  0  5  4  6
                17 19  7  2  4  3  4  1 16  9 13 17 17 15  6  9  1  5  2  0
                 8  8 17 18 10 12 10  0  0 13 13 10  8  0  0  7 18 10  6  3
                13  3 19  3  5  9 17 16 12  2 19  9  1 17  3  0 10 11  4 19
                14  5 11 13 15  6  5 10  6  1  7  3  4 15 10 10 13  4  9  7
                 2 12  5  7  7 16  3  2 18 14 11 18 12 15  4  2 12 15 10  6
                12  5  2 15  8  9 18  9  5  1 17 17  1  0  8  9  5  6  8 13
                 9 13  5  3  9  8 18 15 10  6 12 18 11 15  2 12  6  8 12 15
                14  4  2  0 13  2 18 12 16  2  4 13  0  3 16 15 15 16  7  7
                 6 12  1 14  4 12  8 14 10  0 15 16 13  4  5 12  5  2 16 12
                 5  5  3  0  8  0  5 16 11  4 17 13 18 17  0  9  8 16 13  6
                15 13 13  5  6  7  9 15 12 18  2 12 19  4  9  5  6  8  9  3
                12 10 11  2  5  8 11  7 16 12  0 14 10  5  9  0 15  4 11  3"""

BONUS_BOARD = """0  1  0  0  0  5 16  8 15  4  5  5 17 17  7 11 18  4 16 15  9 17  1  3 19  6  4 16  3  7
                 6  3 13 11  1  5 10 18  8 18  8  8  3 10 18  4  2  8  3  1 11 12 11 15 12  8 14  5  4  9
                 9  0 15  4  1 11  1 11 17  8  4  6  4 12 16 19  9  8  4  2 18 12  1  4  4 10 10  4  9  2
                10 10  2  9  1 19 19 16 19 18  2  4 17  6  8  1 14  9 13  4  1  4 10  2 11  2  7  8 10 15
                11  6 14  1  0  8  4  9  3 16  6  6 14  9  5 19 13  5  5  0 17 18  8 17  6  4  5 17  5 15
                 0  1  0  0  7  1  8  0  4  3  3  5 10 16  2  9 18 17 17  6 14 15 13 12  1  8 15  1  9  1
                 0  1  1  0 19  4  1  0 13  4  4  6  3 11 11  1 19 17 12  7 16 17  0 18  0 14 17 18 17 18
                16 14  5  1  3  0 18 12 15  7  2  0  2  2  8 13  3  9 13 13 18  3  1 12 18 19  1  6 16  0
                 7 13 15  9  0  1  4 15  8  3 19 12  4  0  2  1 11 19  6  3  0 14  5 15  7  4  3 15 10 15
                19 16 11  8  3  2 10 13 10 14 11 12 10 18  6  2  7  9 11 10  4 14 10  6 11  4 12  5 17 10
                 9  0 10 19 19 11 14 19 17  3  4  8 11  4  3  6  8 12  4  8  4  3 16 10  4 10 12 10 19  0
                18 17  1 17 19  5  3 10 10 19 17  6  6 14  3  2  8  5  1  2  8 10  7  4 18 10  5  3  9  6
                10 16  0 17 11 10 14  1 11  1  2 14 16  4  8  2 10  2  8  8 18 12 18 13 18  1 17 18  8  2
                 2 11  8 11 12 15  0  5  8  3  4  6  6  7  6 15  7  7 13 18 13 12 14  9 15  0 15  8  1  7
                 2  6 17 14  5 14  0  8  1 11 13 13 19 13  5  1  8  9 18  5  1 16 14 11  9  2 12 18 10 19
                15  2 15 17  8  5 11 18 16 10  7  1 17 18 19  9  4 13 12  6  3  2  4  5  0 13 13 17 19 12
                17  4  4 17  8 14  6 12 18 14 13  7 17  5 19 18  9 11 11 10  6 17 19  6 13 19  7  0 14  5
                 8  9 10  2 19  3  7 10  9 14 16  3  6  4  1 15 13  8  5  0 14  8  6  0  1  3 14  1 13 10
                12  3 10 18  5 19 17 16  5 12 14 19  6 13 15  3  1 15 15  4 10  9 12  2 19  3 10 13 12  2
                19 18 17 19  2 18 16  5  6  4 12 10  0  1  5 12 10 18  3  0  3 12 14  2 16 13  9 15 10 15
                17  5 19 16 14  6  2 15  9 14 19 15  7 15 16  6 12  1  8 12  2 14 12 18  4  4  4 12 12 17
                 6 12  7 17  0 11 17 11  5 12 13  6  4 13 15 16  9 16 15  3 13 11  3 17 14  9  5  5  5 12
                 3  0  4 15 16  4 17  2  2 16  0  1  7  4  3  0  4  2  9 13 13  4 15 10 16  0  1  5  1  2
                 6  1  9  6  9  9  8 18  2  5  2  9 19  0 12  7  0 17  4  3 19 10 12 14 10  8  6  6 10 19
                 6 11 13  2 17 11  3  1 18 13 12  0 11  7  2 12  9  3 13  8  2  1 17 19 11 19  5  0  2 15
                13 19 12 17  9 18 13  9  1 12  6  9 15 13  9  3  4  4  0 15 15  4 16  9 16 13  1 13  4  6
                17  5 11  3  3 15  9 16  8  1 15 14  9 12 13  8 17  1 16  7 15 17 18  8 11 16 19 14  7  8
                 6 10 18 16  4 10  2 14  6  2  1  1 18  0  6 17  6 15 17  0  5 13 11  4  8 10  8  1 10 13
                13  0  3  2  9 14  3  5 14 11  4 13  0  8  5 14 14  8 19  7 14 10 16 14  8 19 19  2  6 19
                 5  3  4  5 10 19  2  5  8 10  9  6 11  4  4 12 10 15 17 15  8  9  5 19 14 16 12 16 16  5"""

def add_coord(c1, c2): return (c1[0] + c2[0], c1[1] + c2[1])

def manhattan_dist(c1, c2): return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1])

def in_bounds(pos, dim): return not (pos[0] < 0 or pos[1] < 0 or pos[0] >= dim or pos[1] >= dim)

class KlumpBoard:
    def __init__(self, board_string, bonus):
        # Parse the board
        lines = board_string.split("\n")
        dim = len(lines)
        cells = {}
        total_gp = 0
        for y in range(len(lines)):
            row = list(map(lambda x: int(x), lines[y].strip().split()))
            for x in range(len(row)):
                cells[(x, y)] = row[x]
                total_gp += row[x]
        # Pre-calculate sets of sets of positions for each possible size of the 
        # Klumpengeist such that there exists a path from the top left corner 
        # of the board to that position that doesn't pass through any larger 
        # items
        size_zones = []
        size_zones.append(set())
        max_size = isqrt(total_gp)
        for size in range(1, max_size+1):
            start_pos = (0,0)
            reached = set()
            queue = []
            next_queue = []
            next_queue.append(start_pos)
            while len(next_queue) > 0:
                queue = next_queue
                next_queue = []
                while len(queue) > 0:
                    pos = queue.pop()
                    if pos in reached:
                        continue
                    reached.add(pos)
                    for direction in DIRS:
                        next_pos = add_coord(pos, DIRS[direction])
                        if next_pos in reached:
                            continue
                        if in_bounds(next_pos, dim) and cells[next_pos] <= size:
                            next_queue.append(next_pos)
            size_zones.append(reached)  
        self.dim = dim
        self.cells = cells
        self.size_zones = size_zones
        self.bonus = bonus
    
    # Flood fill using the size_zones sets to find uneaten/unempty positions 
    # that can be reached and devoured by the Klumpengeist at its current size 
    # and position without passing through other uneaten positions. Returns a 
    # dictionary of minimal paths to reach each position
    def available_positions(self, klumpstate):
        size = isqrt(klumpstate.growth_points)
        reached = {}
        seen = {}
        queue = []
        queue_next = []
        queue_next.append((klumpstate.pos, ''))
        while len(queue_next) > 0:
            queue = queue_next
            queue_next = []
            while len(queue) > 0:
                pos, path = queue.pop()
                if pos in seen and len(seen[pos]) <= len(path):
                    continue
                seen[pos] = path
                if pos in self.size_zones[size] and pos not in klumpstate.eaten:
                    reached[pos] = path
                    continue
                for d in DIRS:
                    next_pos = add_coord(pos, DIRS[d])
                    if next_pos not in self.size_zones[size]:
                        continue
                    next_path = path + d
                    queue_next.append((next_pos, next_path))
        return reached
    
@dataclass
class KlumpState:
    growth_points: int
    pos: tuple
    eaten: set
    path: str
    def __repr__(self):
        return f"Klumpstate pos {self.pos} GP {self.growth_points} eaten {len(self.eaten)} path len {len(self.path)}"
    def __str__(self):
        return self.__repr__()
    def devour(self, pos, path_segment, klumpboard):
        size = isqrt(self.growth_points)
        assert pos not in self.eaten, f"The Klumpengeist attempted to devour an item at position {pos} that has already been consumed"
        assert size >= klumpboard.cells[pos], f"The Klumpengeist attempted to devour an item of size {klumpboard.cells[pos]} at position {pos} while at size {size} (GP {self.growth_points})"
        self.path += path_segment
        self.pos = pos
        self.growth_points += klumpboard.cells[pos]
        self.eaten.add(pos)

# Traverse the board with the Klumpengeist using a simple heuristic over 
# repeated trials: Randomly pick one of the closest available uneaten items to 
# move to next. 
def klumpengeist(klumpboard):
    max_tries = 1000
    start_eaten = set()
    # Add all zero positions to the initial eaten list
    for x in range(klumpboard.dim):
        for y in range(klumpboard.dim):
            if klumpboard.cells[(x,y)] == 0:
                start_eaten.add((x,y))
    # Attempt semi-random walks until a successful path is found.
    # At each step, find all closest uneaten items and pick one at random to 
    # move to next. 
    for i in range(max_tries):
        klumpstate = KlumpState(1, (0,0), deepcopy(start_eaten), '')
        solved = True
        while True:
            if klumpboard.bonus:
                if len(klumpstate.path) > BONUS_MAX_STEPS:
                    solved = False
                    break
                if klumpstate.growth_points >= 30*30:
                    break
            else:
                if len(klumpstate.path) > MAIN_MAX_STEPS:
                    solved = False
                    break
                if len(klumpstate.eaten) == klumpboard.dim * klumpboard.dim:
                    break
            candidates = klumpboard.available_positions(klumpstate)
            if len(candidates) == 0:
                solved = False
                break
            # Find the minimal distance to reach any candidate item and pick 
            # the next destination randomly from the items at that distance
            min_dist = None
            for pos in candidates:
                dist = manhattan_dist(klumpstate.pos, pos)
                if min_dist is None or min_dist > dist:
                    min_dist = dist
            nearest_candidates = [pos for pos in candidates if manhattan_dist(klumpstate.pos, pos) == min_dist]
            next_pos = choice(nearest_candidates)
            klumpstate.devour(next_pos, candidates[next_pos], klumpboard)
        if solved:
            return klumpstate                     
    return None

def validate_print(pos, gp, eaten, empty, klumpboard, move, step_num, eaten_item=None):
    print(f"Step {step_num+1}")
    if eaten_item is not None:
        print(f"The Klumpengeist moves {move} to position {pos} and devours an item of size {eaten_item}.")
    else:
        print(f"The Klumpengeist moves {move} to position {pos}.")
        
    print(f"Klumpengeist GP:\t{gp} (size {isqrt(gp)})\nItem(s) eaten:\t\t{len(eaten)}\nItem(s) remaining:\t{(klumpboard.dim * klumpboard.dim) - len(eaten) - len(empty)}")
    print()
    for y in range(klumpboard.dim):
        for x in range(klumpboard.dim):
            p = (x,y)
            if p == pos:
                print(" []", end='')
                continue
            if p in eaten or p in empty:
                print("  .", end='')
            else:
                if klumpboard.cells[p] > 9:
                    print(f" {klumpboard.cells[p]}", end='')
                else:
                    print(f"  {klumpboard.cells[p]}", end='')
        print()
    print()
    
# Test if the given path satisfies the challenge constraints
def validate(path, klumpboard, verbose):
    if klumpboard.bonus: 
        if len(path) > BONUS_MAX_STEPS: 
            if verbose: print(f"Path {path} ({len(path)} steps) is too long for a bonus solution")
            return False
    else:
        if len(path) > MAIN_MAX_STEPS: 
            if verbose: print(f"Path {path} ({len(path)} steps) is too long for a main solution")            
            return False
    path_directions = list(path)
    pos = (0,0)
    growth_points = 1
    empties = set()
    for x in range(klumpboard.dim):
        for y in range(klumpboard.dim):
            if klumpboard.cells[(x,y)] == 0:
                empties.add((x,y))
    eaten = set()
    for i in range(len(path_directions)):
        next_pos = add_coord(pos, DIRS[path_directions[i]])
        eaten_item = None
        if not (next_pos in eaten or next_pos in empties):
            if klumpboard.cells[next_pos] * klumpboard.cells[next_pos] > growth_points:
                if verbose: print(f"Path {path} ({len(path)} steps) contains an attempt to move to a cell with size {klumpboard.cells[next_pos]} at {next_pos} from {pos} in direction {path_directions[i]} at step {i} with GP {growth_points}")
                return False
            growth_points += klumpboard.cells[next_pos]
            eaten.add(next_pos)
            eaten_item = klumpboard.cells[next_pos]
        pos = next_pos
        if verbose: validate_print(pos, growth_points, eaten, empties, klumpboard, path_directions[i], i, eaten_item)
    if verbose: print(f"Reached end of path {path} ({len(path)} steps) at pos {pos} with {len(eaten)} eaten, {len(empties)} empty ({len(eaten) + len(empties)} total) and GP {growth_points} (size {isqrt(growth_points)})\n")
    if klumpboard.bonus: return isqrt(growth_points) >= 30
    else: return len(eaten) + len(empties) == klumpboard.dim * klumpboard.dim
    
def main():
    parser = argparse.ArgumentParser(
                    prog='apr2025')
    parser.add_argument("-b", "--bonus", action="store_true", help="solve the bonus challenge")
    parser.add_argument("-v", "--verbose", action="store_true", help="print each solution step")
    args = parser.parse_args()
    
    print("\n######## Ponder This Challenge - April 2025 ########\n")
    description = "Bonus" if args.bonus else "Main"
    klumpboard = KlumpBoard(BONUS_BOARD, bonus=True) if args.bonus else KlumpBoard(MAIN_BOARD, bonus=False)
    solution = klumpengeist(klumpboard)
    
    if solution is not None:
        if validate(solution.path, klumpboard, args.verbose):
            print(f"{description} result:\n{solution.path} ({len(solution.path)} steps)\n")
        else:
            print(f"{description} result:\nFailed validation for path {solution.path} ({len(solution.path)} steps)\n")
    else:
        print(f"{description} result: A path could not be found.")
    
        
if __name__ == "__main__":
    main()