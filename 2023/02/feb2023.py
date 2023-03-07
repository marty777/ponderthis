# https://research.ibm.com/haifa/ponderthis/challenges/February2023.html

import argparse
from pathlib import Path
from random import randint, choice, shuffle
import copy
from os import path
from datetime import datetime

class KingSolver:
    def __init__(self, queens):
        self.n = len(queens)
        self.queens = copy.deepcopy(queens)
    def queenThreats(self, position):
        threatCount = 0
        for q in self.queens:
            if q[0] == position[0] and q[1] == position[1]:
                continue
            x_diff = abs(position[0] - q[0])
            y_diff = abs(position[1] - q[1])
            if x_diff == 0 or y_diff == 0 or x_diff == y_diff:
                threatCount += 1
        return threatCount
    # given the set of queen positions, list all 'safe' positions on the board
    # i.e. all positions not occupied by a queen and under threat by  exactly 
    # 2 queens.
    def safePositions(self):
        threats = [-1] * self.n * self.n
        for row in range(0, self.n):
            for column in range(0, self.n):
                pos = (column, row)
                if pos in self.queens:
                    continue
                threats[row * self.n + column] = self.queenThreats(pos)
        safe_positions = []
        for column in range(0, self.n):
            for row in range(0, self.n):
                if threats[row * self.n + column] == 2:
                    safe_positions.append((column, row))
        return safe_positions
    # given the set of 'safe' positions, find spatially isolated single 
    # positions or groups of connected positions within king-threatening 
    # distance. Once we have a list of grouped positions, produce a list of 
    # the number of possible arrangements for 0, 1, 2, etc. kings (without 
    # being mutally threatening) within each group and return the full list 
    # of group/king arrangement counts.
    # Example. If there was a single group of 'safe' (S) positions arranged 
    # like:
    #
    # . . S . S . . .
    # . . . S . . . .
    #
    # Then within the group there's:
    #    1 way to arrange 0 kings
    #    3 ways to arrange 1 king
    #    1 way to arrange 2 kings
    #    0 ways to arrange 3 kings
    #    0 ways to arrange 4 kings
    #    etc.
    # Omitting any trailing 0-arrangement possibilities the entry for this 
    # group would be [1,3,1], with the list index corresponding to a number of 
    # kings and the value corresponding to the number of possible ways to 
    # arrange that number of kings.
    def safePositionGroupKingArrangementCounts(self):
        safe_positions = self.safePositions()
        buckets = []
        for i in range(0, len(safe_positions)):
            assigned = False
            for j in range(0, i):
                x_diff = abs(safe_positions[i][0] - safe_positions[j][0])
                y_diff = abs(safe_positions[i][1] - safe_positions[j][1])
                if x_diff <= 1 and y_diff <= 1:
                    # a hit
                    for k in range(0, len(buckets)):
                        if j in buckets[k]:
                            assigned = True
                            buckets[k].append(i)
                            break
                if assigned:
                    break
            if not assigned:
                buckets.append([i])
        # Using the bucket assignment above, it's possible for positions in a 
        # single connected group to be assigned to multiple buckets. Perform 
        # merges of connected groups until no more merges are possible.
        stillMerging = True
        while(stillMerging and len(buckets) > 1):
            bucketsCopy = copy.deepcopy(buckets)
            merges = 0
            # do at most 1 merge per pass
            for i in range(0, len(bucketsCopy)):
                for j in range(0, len(bucketsCopy)):
                    if j == i:
                        continue
                    shouldMerge = False
                    for n in range(0, len(bucketsCopy[i])):
                        for m in range(0, len(bucketsCopy[j])):
                            x_diff = abs(safe_positions[bucketsCopy[i][n]][0] - safe_positions[bucketsCopy[j][m]][0])
                            y_diff = abs(safe_positions[bucketsCopy[i][n]][1] - safe_positions[bucketsCopy[j][m]][1])
                            if x_diff <= 1 and y_diff <= 1:
                                shouldMerge = True
                                break
                        if shouldMerge:
                            break
                    if shouldMerge:
                        # add elements of bucket j to elements of bucket i and 
                        # remove bucket j
                        bucketsCopy[i].extend(bucketsCopy[j])
                        del bucketsCopy[j]
                        merges += 1
                        break
                if merges > 0:
                    break
            if merges == 0:
                stillMerging = False
            else:
                buckets = bucketsCopy
        # Given the groups of safe positions, determine the number of ways to 
        # arrange different amounts of kings for each group
        safe_position_group_king_arrangements = []
        for i in range(0, len(buckets)):
            safe_position_group_king_arrangements.append([])
            for j in range(0, len(buckets[i]) + 1):
                # determine the number of distinct possible j-king arrangements
                # across the safe positions contained in bucket i and add it 
                # to the arrangement count list.
                group_arrangements = self.arrangementsOfKingsInPositionGroupBFS(safe_positions, buckets, i, j)
                safe_position_group_king_arrangements[i].append(group_arrangements)
        # Truncate any group king arrangement counts that have trailing zeroes
        for i in range(0, len(buckets)):
            while(safe_position_group_king_arrangements[i][len(safe_position_group_king_arrangements[i]) - 1] == 0):
                safe_position_group_king_arrangements[i] = safe_position_group_king_arrangements[i][:-1]
        return safe_position_group_king_arrangements
    
    # determine if a given king would threaten a given position, within an 
    # indexed list of safe positions
    def kingThreatensSpace(self, safe_positions, safe_position_group, king_safe_position_group_index, given_safe_position_group_index):
        king_position = safe_positions[safe_position_group[king_safe_position_group_index]]
        given_position = safe_positions[safe_position_group[given_safe_position_group_index]]
        x_diff = abs(given_position[0] - king_position[0])
        y_diff = abs(given_position[1] - king_position[1])
        # this will indicate that a king threatens its own position, but we 
        # aren't using this function that way
        return (x_diff <= 1 and y_diff <= 1)
    
    # Use a BFS to fully examine all possible arrangements of k kings in the 
    # given group of 'safe' positions and return the total number of distinct 
    # arrangements.
    def arrangementsOfKingsInPositionGroupBFS(self, safe_positions, safe_position_groups, index, k_kings):
        # always exactly 1 way to arrange 0 kings in a group of any size, 
        # including empty
        if k_kings == 0:
            return 1
        # if the number of kings exceeds the number of positions, there's 
        # definitely 0 ways to arrange them and we can skip further analysis
        max_positions = len(safe_position_groups[index])
        if max_positions < k_kings:
            return 0
        # state is a set of indexes of positions within the group, not the 
        # indexes of safe positions directly
        no_assignments = [-1] * k_kings
        successes = set()
        frontier = []
        frontier_next = []
        frontier_next.append(no_assignments)
        
        while(len(frontier_next) > 0):
            frontier = copy.deepcopy(frontier_next)
            frontier_next.clear()
            while(len(frontier) > 0):
                state = frontier.pop()
                stateKey = str(state)
                most_recent_king_state_index = -1
                for i in range(0, len(state)):
                    if state[i] == -1:
                        break
                    most_recent_king_state_index = i
                next_king_state_index = most_recent_king_state_index + 1
                # if we've hit an end state
                if next_king_state_index == len(state):
                    successes.add(stateKey)
                    continue
                # given the current state, find all remaining safe position 
                # indexes (within the group)
                remaining_safe_position_group_indexes = []
                for i in range(state[most_recent_king_state_index]+1, len(safe_position_groups[index])):
                    if i in state:
                        continue
                    safe = True
                    for j in range(0, next_king_state_index):
                        if self.kingThreatensSpace(safe_positions, safe_position_groups[index], state[j], i):
                            safe = False
                            break
                    if safe:
                        remaining_safe_position_group_indexes.append(i)
                for i in range(0, len(remaining_safe_position_group_indexes)):
                    nextState = copy.deepcopy(state)
                    nextState[next_king_state_index] = remaining_safe_position_group_indexes[i]
                    nextStateKey = str(nextState)
                    frontier_next.append(nextState)
        return len(successes)
    # Given a list of counts of distinct arrangements of k kings within each 
    # of a set of connected groups of 'safe' positions, determine the total 
    # number of distinct ways to arrange any number of kings on safe spaces on
    # this board. Uses a recursive DFS to examine all possible distributions 
    # of kings between the grouped positions, but exits early if the total 
    # ever exceeds a target value.
    def totalKingArrangements(self, safe_position_group_arrangements, group_index, choices, total_arrangements_target):
        # if we've reached a leaf of the tree
        if group_index == len(safe_position_group_arrangements):
            product = 1
            kings = 0
            for i in range(0, len(safe_position_group_arrangements)):
                product *= safe_position_group_arrangements[i][choices[i]]
                kings += choices[i]
            if kings == self.n:
                return product, True
            else:
                return 0, True
        nodesum = 0
        # determine the maximum possible kings that can be assigned to 
        # subsequent groups and the number of kings that have been previously 
        # assigned
        current_kings = 0
        for i in range(0, group_index):
            current_kings += choices[i]
        remaining_max = 0
        for i in range(group_index + 1, len(safe_position_group_arrangements)):
            remaining_max += len(safe_position_group_arrangements[i]) - 1
        for i in range(0, len(safe_position_group_arrangements[group_index])):
            # if the previous choices plus this one can't possibly reach n 
            # kings ignore the branch
            if(current_kings + i + remaining_max < self.n):
                continue
            nextChoices = copy.deepcopy(choices)
            nextChoices.append(i)
            branchVal, branchOk = self.totalKingArrangements(safe_position_group_arrangements, group_index + 1, nextChoices, total_arrangements_target)
            nodesum += branchVal
            if(nodesum > total_arrangements_target or not branchOk):
                return nodesum, False
        return nodesum, True
    def satisfiesTarget(self, targetDistinctKingArrangements):
        safePositions = self.safePositions()
        groupKingCounts = self.safePositionGroupKingArrangementCounts()
        amount,ok = self.totalKingArrangements(groupKingCounts, 0, [], targetDistinctKingArrangements)
        return (amount == targetDistinctKingArrangements and ok)
    def zeroPossibleNKings(self):
        # there are zero possible ways to arrange n kings if the sum of the 
        # maximum number of kings that can be arranged in each grouping of 
        # 'safe' positions is less than n.
        safePositions = self.safePositions()
        groupKingCounts = self.safePositionGroupKingArrangementCounts()
        total = 0
        for g in groupKingCounts:
            total += len(g) - 1
        return total < self.n
        
class QueenGenerator:
    def __init__(self, n):
        self.n = n
    # returns the number of threats from queens to a given position. 
    def positionThreat(self, queens, position):
        threatCount = 0
        for q in queens:
            if q[0] == position[0] and q[1] == position[1]:
                continue
            x_diff = abs(position[0] - q[0])
            y_diff = abs(position[1] - q[1])
            if x_diff == 0 or y_diff == 0 or x_diff == y_diff:
                threatCount += 1
        return threatCount
    def solved(self, queens):
        worst_threat = 0
        for i in range(0, len(queens)):
            threat = self.positionThreat(queens, queens[i])
            if threat > worst_threat:
                worst_threat = threat
        return worst_threat == 0
    # generates a single n-queen arrangement using iterative repair.
    # this may require multiple attempts and is not guaranteed to reach a 
    # solution.
    def solve(self, maxAttempts, maxMovesPerAttempt, verbose = False):
        attempt = 0
        finished = False
        solution = []
        while not finished:
            if attempt > maxAttempts:
                break
            result = self.generateQueens(maxMovesPerAttempt, verbose)
            if result != False:
                solution = result
                finished = True
            attempt += 1
        if not finished:
            if(verbose):
                print("No {}-queen arrangement found after {} attempts".format(self.n, attempt))
            return False
        return solution
    
    # returns a list of tuples giving the coordinates of n queens, or False 
    # if no solution can be found within maxMoves.
    def generateQueens(self, maxMoves, verbose=False):
        max_attempts = 50
        # initialize queen positions to a random column, 1 per row
        n = self.n;
        queens = []
        seen = set()
        # initialize queen positions to 1 per column in random rows
        for i in range(0, n):
            queens.append([i,randint(0, n - 1)])
        finished = False;
        moves = 0
        # Find the most-threatened queen that can be moved to a less 
        # threatened position in the same column, maximizing the reduction in 
        # threat, such that we do not repeat a queen arrangement that has been 
        # previously seen.
        # Exit if the number of attempted moves exceeds maxMoves and a 
        # solution has not been found.
        while not finished:
            stateKey = str(queens)
            seen.add(stateKey)
            if verbose:
                print("Move {}:\t{}".format(moves, queens))
            if self.solved(queens):
                finished = True
                break
            if moves > maxMoves:
                break
            candidates = []
            for q in queens:
                # no need to consider safe queens
                queenThreat = self.positionThreat(queens, q)
                if queenThreat == 0:
                    continue
                # consider each space in the same column as a possible 
                # destination for the queen
                for i in range(0,self.n):
                    if i == q[1]:
                        continue
                    # minus 1 to exclude the threat from the queen in the same 
                    # column
                    positionThreat = self.positionThreat(queens, [q[0], i]) - 1
                    # record the candidate position and difference between the
                    # threat to the current queen position and the threat to
                    # the candidate position.
                    # no need to consider candidate positions that are worse.
                    if positionThreat < queenThreat:
                        candidates.append((q[0], i, queenThreat - positionThreat))
            # given a list of candidates, sort from best to worst improvement
            sorted_candidates = sorted(candidates, key=lambda c: c[2], reverse=True)
            moveFound = False
            # try candidate moves in sorted order until a state that hasn't been 
            # previously tried is found. If no move is found, this attempt has 
            # failed.
            for c in sorted_candidates:
                nextQueens = copy.deepcopy(queens)
                nextQueens[c[0]] = [c[0], c[1]]
                nextQueensKey = str(nextQueens)
                if nextQueensKey not in seen:
                    if verbose:
                        print("\tMoving queen from {} to {}".format(queens[c[0]], nextQueens[c[0]]))
                    queens = nextQueens
                    moveFound = True
                    break
            if not moveFound:
                if verbose:
                    print("\tNo possible moves found.")
                break
            moves += 1
        if(finished):
            # return positions as a list of tuples, rather than a list of lists
            return list(map(lambda q: (q[0], q[1]), queens))
        else:
            return False

def saveOutput(outputdir, filename, output):
    outputpath = path.join(outputdir, filename)
    f = open(outputpath, "a")
    f.write(str(output) + '\n')
    f.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("outputdir", help="The directory to store successful solutions")
    parser.add_argument("-b", "--bonus", action="store_true", help="Attempt to solve the bonus problem for 26 queens")
    parser.add_argument("-m", "--maxattempts", default=100, type=int, help="Maximum number of solutions to attempt")
    args = parser.parse_args()
    outputdir = args.outputdir
    if(not path.isdir(outputdir) or  not path.exists(outputdir)):
        print("Output directory '{}' could not be found".format(outputdir))
        parser.print_usage()
        exit()
    if args.maxattempts < 1:
        print("Specified attempts too small: {}".format(args.maxattempts))
        parser.print_usage()
        exit()
    print("\n######## Ponder This Challenge - February 2023 ########\n")
    if(args.bonus):
        print("Bonus problem: Attempting to find 26-queen solutions that permit no placements\nof 26 kings on 'safe' positions.")
    else:
        print("Attempting to find 20-queen solutions that permit exactly 48 possible\nplacements of 20 kings on 'safe' positions.")
    print("A maximum of {} queen arrangement(s) will be generated and tested.".format(args.maxattempts))
    print("Satisfying queen arrangements will be saved to the directory '{}'".format(args.outputdir))
    # maximum attempt parameters for using iterative repair to generate n-queen 
    # arrangements
    maxQueenAttempts = 20
    maxQueenMovesPerAttempt = 250
    successes = 0
    if(args.bonus):
        n = 26
        queenGenerator = QueenGenerator(n)
        queens = False
        # until maxattempts is exceeded, generate a 26 queen arrangement and 
        # test if it has no possible ways to arrange 26 mutually 
        # unthreatening kings in the 'safe' positions.
        # If an arrangement satisfies the condition, save it to a text file in 
        # the output directory.
        for i in range(0, args.maxattempts):
            print("Attempt {}/{}".format(i + 1, args.maxattempts))
            queens = False
            
            while queens == False:
                queens = queenGenerator.solve(maxQueenAttempts, maxQueenMovesPerAttempt, False)
            kingSolver = KingSolver(queens)
            if kingSolver.zeroPossibleNKings():
                print("Satisfying arrangement found! ".format(n))
                print(queens)
                outputfilename = datetime.now().strftime('%Y_%m_%d__%H_%M_%S_BONUS.txt')
                saveOutput(outputdir, outputfilename, str(queens))
                print("Saving result to {}".format(path.join(outputdir, outputfilename)))
                successes += 1
    else:
        n = 20
        targetKingArrangements = 48
        queenGenerator = QueenGenerator(n)
        queens = False
        # until maxattempts is exceeded, generate a 20 queen arrangement and 
        # test if it has 48 possible ways to arrange 20 mutually unthreatening 
        # kings in the 'safe' positions.
        # If an arrangement satisfies the condition, save it to a text file in 
        # the output directory.
        for i in range(0, args.maxattempts):
            print("Attempt {}/{}".format(i + 1, args.maxattempts))
            queens = False
            while queens == False:
                queens = queenGenerator.solve(maxQueenAttempts, maxQueenMovesPerAttempt, False)
            kingSolver = KingSolver(queens)
            if kingSolver.satisfiesTarget(targetKingArrangements):
                print("Satisfying arrangement found! ".format(n))
                print(queens)
                outputfilename = datetime.now().strftime('%Y_%m_%d__%H_%M_%S_MAIN.txt')
                saveOutput(outputdir, outputfilename, str(queens))
                print("Saving result to {}".format(path.join(outputdir, outputfilename)))
                successes += 1
    print("{} matching queen solution(s) found in {} attempts".format(successes, args.maxattempts))
    
main()
