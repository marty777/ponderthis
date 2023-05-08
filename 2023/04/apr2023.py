# https://research.ibm.com/haifa/ponderthis/challenges/April2023.html

import argparse
from random import randrange
import copy
from os import path

def initializeBulbGrid(lines):
    if len(lines) == 0:
        print("Supplied bulb grid is empty")
        return None
    for i in range(0,len(lines)):
        stripped_line = lines[i].strip()
        if len(lines) != len(stripped_line):
            print("Supplied bulb grid is not square")
            return None
        # not rigorously verified, but the transformation matrices for 
        # odd-dimensioned bulb grids seem to all be non-involutory so our 
        # solution doesn't work. The matrices might still be invertable.
        if len(lines) % 2 != 0:
            print("Supplied bulb grid has dimensions {} x {}. Bulb grids with even dimensions are required".format( len(lines), len(lines)))
            return None
        for j in range(0, len(stripped_line)):
            if stripped_line[j] != '0' and stripped_line[j] != '1':
                print("Supplied bulb grid has an invalid character '{}' on line {} column {}".format(stripped_line[j], i + 1, j + 1))
                return None
    return BulbGrid(lines)
    
class BulbGrid:
    def __init__(self, lines):
        self.n = len(lines)
        self.n2 = self.n * self.n
        self.transforms = self.all_transforms()
        self.initial_state = []
        for i in range(0, len(lines)):
            # flip the vertical coordinates. (0,0) is the bottom-left corner, not top-left
            line = lines[len(lines) - i - 1]
            for j in range(0, len(line)):
                if line[j] == '\n':
                    continue
                if line[j] == '0':
                    self.initial_state.append(0)
                else:
                    self.initial_state.append(1)
        self.moves = self.required_transforms()
        
    def print_grid(self, moves = []):
        state = copy.deepcopy(self.initial_state)
        for move in moves:
            # don't bother checking for illegal moves here
            for i in range(0, self.n2):
                state[i] ^= self.transforms[move][i]
        for y in range(0, self.n):
            for x in range(0, self.n):
                # flip the vertical coordinates back for display
                print("{} ".format(state[((self.n - 1 - y) * self.n) + x]), end="")
            print()
    
    # Assuming the matrix of transformations is self-inverting, we multiply it 
    # by the vector of net transforms needed to reach an all '1' state. 
    # Any non-zero coefficients on the resulting vector indicate moves that 
    # must be made an odd number of times to reach the desired state, and any 
    # zero coefficients indicate moves that must be made an even number of 
    # times. Ideally there is a minimal solution where each move with non-zero 
    # coefficients is made exactly once and all moves with zero coefficients 
    # are not made. Returns the indexes of all moves with non-zero 
    # coefficients.
    def required_transforms(self):
        net_transform = self.net_transform()
        result = [0] * self.n2
        for i in range(0, self.n2):
            for j in range(0, self.n2):
                result[j] = (result[j] + (net_transform[i] * self.transforms[i][j])) % 2
        moves = []
        for i in range(0, self.n2):
            if result[i] == 1:
                moves.append(i)
        return moves
        
    # The mask of the net transforms needed to change the starting state to all
    # '1's (which is just the starting state, inverted)
    def net_transform(self):
        return list(map(lambda x: (x + 1) % 2, self.initial_state))
        
    # the matrix of transformations for all possible moves
    def all_transforms(self):
        all_t = []
        for i in range(0, self.n2):
            t = []
            for j in range(0, self.n2):
                if j // self.n == i // self.n:
                    t.append(1)
                elif j % self.n == i % self.n:
                    t.append(1)
                else:
                    t.append(0)
            all_t.append(t)
        return all_t
        
    # Attempt to find a randomized solution where each required move is made
    # exactly once while respecting the rule that moves can only be made if the 
    # corresponding bulb is off. Returns False if the end state couldn't be 
    # reached
    def trial_solution(self):
        steps = []
        done = False
        state = copy.deepcopy(self.initial_state)
        while not done:
            if len(steps) == len(self.moves):
                done = True
                continue
            # determine all candidate moves (required moves which haven't been 
            # made yet where the bulb is currently off)
            candidates = []
            for move in self.moves:
                if state[move] != 0:
                    continue
                if move in steps:
                    continue
                candidates.append((move))
            # if no candidate moves are available, this attempt has failed
            if len(candidates) == 0:
                return False
            # select a candidate move at random and apply the transform
            candidate_index = randrange(0, len(candidates))
            steps.append(candidates[candidate_index])
            for i in range(0, self.n2):
                state[i] ^= self.transforms[candidates[candidate_index]][i]
        return steps
        
    # test that the provided list of moves doesn't include any invalid moves on
    # active bulbs and that it reaches a fully lit end state. Return the moves
    # as tuples of coordinates.
    def validate_solution(self, moves):
        # convert into tuples
        tuples = []
        for move in moves:
            col = (move % self.n) + 1
            row = (move // self.n) + 1
            tuples.append((col,row))
        state = copy.deepcopy(self.initial_state)
        for i in range(0, len(tuples)):
            move = (tuples[i][1] - 1) * self.n + (tuples[i][0] - 1)
            if state[move] != 0:
                print("Illegal move made at step {} ({}, {}). Bulb is already lit".format(i + 1, tuples[i][0], tuples[i][1]))
                return False
            for j in range(0, self.n):
                state[((tuples[i][1] - 1) * self.n) + j] ^= 1
                state[((j) * self.n) + (tuples[i][0] - 1)] ^= 1
            state[move] = 1
        offBulbs = 0
        for i in range(0, self.n2):
            if state[i] != 1:
                offBulbs += 1
        if offBulbs > 0:
            print("Resulting state has {} bulb{} unlit.".format(offBulbs, '' if offBulbs == 1 else 's'))
            return False
        return tuples

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="An input text file containing a bulb grid")
    parser.add_argument("-m", "--maxattempts", default=1000, type=int, help="Maximum number of trial solutions to attempt")
    parser.add_argument("-t", "--trace", action="store_true", help="Print a step-by-step trace of a successful solution when found")
    args = parser.parse_args()
    if args.maxattempts < 1:
        print("Specified attempts too small: {}".format(args.maxattempts))
        parser.print_usage()
        exit()
    inputfile = args.inputfile
    if(not path.exists(inputfile)):
        print("Input file '{}' could not be found".format(inputfile))
        parser.print_usage()
        exit()
    f = open(inputfile, 'r')
    lines = f.readlines()
    f.close()
    bulbGrid = initializeBulbGrid(lines)
    if bulbGrid == None:
        print("Input file '{}' could not be parsed as a bulb grid".format(inputfile))
        parser.print_usage()
        exit();
    
    print("\n######## Ponder This Challenge - April 2023 ########\n")
    bulbGrid.print_grid()
    print()
    print("The minimum number of steps to transform the input bulbs to fully on is {}".format(len(bulbGrid.moves)))
    print("Attempting a maximum of {} randomized trial solutions...".format(args.maxattempts))
    for i in range(0, args.maxattempts):
        trial_result = bulbGrid.trial_solution()
        if trial_result != False:
            print("Trial {} of {} succeeded".format(i + 1, args.maxattempts))
            steps = bulbGrid.validate_solution(trial_result)
            if steps != False:
                print(steps)
                if(args.trace):
                    print("Starting solution trace...")
                    bulbGrid.print_grid()
                    for i in range(0, len(steps)):
                        print(steps[i])
                        bulbGrid.print_grid(trial_result[0:i+1])
                    print(steps)
            else:
                print("Trial solution {} failed validation".format(trial_result))
                continue
            exit()
        else:
            print("Trial {} of {} failed".format(i + 1, args.maxattempts))
    print("A solution could not be found in {} attempts".format(args.maxattempts))
    
main()
