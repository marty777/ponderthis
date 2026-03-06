# https://research.ibm.com/blog/ponder-this-february-2026

import argparse
from copy import deepcopy
from itertools import product
from collections import defaultdict
from sympy import Rational
from sympy.matrices import Matrix, eye, zeros, ones

NUM_MEN = 5

class Backgammon:
    def __init__(self, dicemax):
        self.dicemax = dicemax
    # Convert positions from a dict to state tuple, with
    # the coordinate zero-based
    def position_normalize(positions):
        min_k = min(positions.keys())
        max_k = max(positions.keys())
        state = [0] * (max_k - min_k + 1)
        for k in positions.keys():
            state[k - min_k] = positions[k]
        return tuple(state)
    # List all distinct rolls of the dice (up to re-ordering) along with the
    # probability of the roll occuring
    def all_rolls_p(self):
        results = {}
        p_roll = Rational(1,self.dicemax * self.dicemax)
        for i in range(1, self.dicemax + 1):
            for j in range (1, self.dicemax + 1):
                roll = tuple(sorted([i,j]))
                if roll not in results:
                    results[roll] = p_roll
                else:
                    results[roll] += p_roll
        return results
    # Test if the given state is detached, meaning it is of the form 
    # (3,0,..,0,2) and the only available non-blot moves occur on double rolls
    # where the front two men are moved forward together.
    def state_is_detached(self, state):
        return state[0] == 3 and state[-1] == 2 and len(state) > 4*self.dicemax + 1
    # Return true if a state is a blot
    def state_is_blot(self, state): return 1 in state
    # List all possible next states, including blots, given a current state and
    # a list of moves provided by a dice roll.
    def all_next_states(self, state, moves):
        start_men = []
        for i in range(len(state)):
            for j in range(state[i]):
                start_men.append(i)
        next_states = set()
        for men_move in product(list(range(len(start_men))), repeat=len(moves)):
            men = deepcopy(start_men)
            for i in range(len(men_move)):
                men[men_move[i]] += moves[i]
            next_positions_by_move = defaultdict(int)
            for i in range(len(men)):
                next_positions_by_move[men[i]] += 1
            next_state = Backgammon.position_normalize(next_positions_by_move)
            next_states.add(next_state)
        return next_states
    # Return a directed graph of possible transitions between non-blot states
    # (excepting detached states of the form (3,...,2) which go off infinitely 
    # on their own)
    def graph(self):
        possible_rolls = self.all_rolls_p()
        graph = {}
        frontier = []
        frontier_next = []
        frontier_next.append(tuple([NUM_MEN]))
        while len(frontier_next) > 0:
            frontier = frontier_next
            frontier_next = []
            while len(frontier) > 0:
                candidate = frontier.pop()
                if candidate in graph:
                    continue
                # Prevent detached states of the form 3,0,...,0,2 with 
                # length > the maximum move distance from being added to the 
                # graph
                if self.state_is_detached(candidate):
                    continue
                next_state_transitions = {}
                for roll in possible_rolls:
                    mismatch = roll[0] != roll[1]
                    if roll[0] == roll[1]:
                        moves = [roll[0], roll[0], roll[1], roll[1]]
                    else:
                        moves = [roll[0], roll[1]]
                    all_next_states = self.all_next_states(candidate, moves)
                    detached_next_states_count = 0
                    for next_state in all_next_states:
                        if self.state_is_blot(next_state):
                            continue
                        if self.state_is_detached(next_state):
                            detached_next_states_count += 1
                        if roll not in next_state_transitions:
                            next_state_transitions[roll] = [next_state]
                        else:
                            next_state_transitions[roll].append(next_state)
                        frontier_next.append(next_state)
                    # If this state/roll has multiple options for next states, 
                    # remove any detached options because they can't be part of
                    # an optimal strategy 
                    if roll in next_state_transitions and detached_next_states_count > 0 and detached_next_states_count < len(next_state_transitions[roll]):
                        for i in range(len(next_state_transitions[roll])):
                            if self.state_is_detached(next_state_transitions[roll][i]):
                                del next_state_transitions[roll][i]
                                break
                graph[candidate] = next_state_transitions
        return graph

# Given the graph and a particular set of branch choices as a strategy, 
# construct an absorbing Markov model and return the expected number of dice 
# rolls until absorption (representing a blot and the game ending) as a 
# Rational. Note that this amount includes the final dice roll, so 1 should be 
# subtracted from the result.
def absorbing_markov(graph, all_rolls_p, node_roll_strategy_index, strategies, strategy_index, use_rationals=True):
    p_doubles = Rational(0,1)
    p_non_doubles = Rational(0,1)
    for roll in all_rolls_p:
        if roll[0] == roll[1]:
            p_doubles += all_rolls_p[roll]
        else:
            p_non_doubles += all_rolls_p[roll]

    node_keys = list(graph.keys())
    node_indexes = {node_keys[i]: i for i in range(len(node_keys))}
    start_node_index = node_indexes[tuple([NUM_MEN])]
    # The detached case is states of the form (3,0,...,0,2) where the 
    # distance between the two groups of men is greater than 4 times the 
    # maximum dice face, meaning only the 2 group can be advanced on double 
    # rolls and no non-double moves can be made that don't result in a blot.
    # If a game reaches this state, it can only transition to a similar state
    # and the absorbing state, so only one node is used to represent all 
    # states of this type.
    detached_node_index = len(node_keys)
    absorbing_node_index = detached_node_index + 1
    # Build the transition matrix
    transition_array = []
    for i in range(len(node_keys)):
        node = node_keys[i]
        row = []
        for j in range(absorbing_node_index + 1):
            if use_rationals:
                row.append(Rational(0,1))
            else:
                row.append(0)
        for roll in all_rolls_p:
            p_roll = all_rolls_p[roll]
            if roll not in graph[node]:
                row[absorbing_node_index] += p_roll if use_rationals else float(p_roll)
                continue
            next_node = graph[node][roll][0]
            # If this node and roll has multiple choices of next non-blot state
            # take the branch indicated by the current choice index
            if((node, roll) in node_roll_strategy_index):
                next_node_index = strategies[strategy_index][node_roll_strategy_index[(node, roll)]]
                next_node = graph[node][roll][next_node_index]
            # Indicated next states that don't appear in the graph are the 
            # detached cases of (3,0,...,0,2)
            if next_node not in node_indexes:
                row[detached_node_index] += p_roll if use_rationals else float(p_roll)
            else:
                row[node_indexes[next_node]] += p_roll if use_rationals else float(p_roll)
        transition_array.append(row)
    # Add the detached node row - transitions to itself on double rolls and 
    # to the absorbing node on non-double rolls.
    detached_row = []
    for j in range(absorbing_node_index + 1):
        if use_rationals:
            detached_row.append(Rational(0,1))
        else:
            detached_row.append(0)
    detached_row[detached_node_index] += p_doubles if use_rationals else float(p_doubles)
    detached_row[absorbing_node_index] += p_non_doubles if use_rationals else float(p_non_doubles)
    transition_array.append(detached_row)
    # Add the absorbing node row - only transitions to itself
    absorbing_row = []
    for j in range(absorbing_node_index + 1):
        if use_rationals:
            absorbing_row.append(Rational(0,1))
        else:
            absorbing_row.append(0)
    absorbing_row[absorbing_node_index] += Rational(1) if use_rationals else 1
    transition_array.append(absorbing_row)
    # Using SymPy, construct the transition matrix, take the Q submatrix and 
    # find the inverse of (I - Q) to determine the expected number of turns 
    # before absorption
    transition_matrix = Matrix(transition_array)
    # Q is the square submatrix of the transition matrix containing the 
    # transitions between all non-absorbing nodes (include the detached node 
    # in this case).
    q_matrix = transition_matrix[0:(len(node_keys) + 1), 0:(len(node_keys) + 1)]
    i_minus_q = eye(len(node_keys) + 1) - q_matrix
    # N = (I - Q)^{-1}
    n_matrix = i_minus_q.inv()
    # N*1 gives a vector of the expected turns before absorption starting from
    # any node.
    one_vec = ones((len(node_keys) + 1), 1)
    expected_turns_before_absorption_vec =  n_matrix * one_vec
    # Return the value for the start node.
    return expected_turns_before_absorption_vec[start_node_index]

# List all combinations of choices that can be made on nodes where there are 
# multiple options for next state on some dice rolls. The challenges don't
# contain any states with more than 2 options per roll, so this is overkill.
def branch_combinations(node_branch_counts):
    options = []
    node_roll_index = {}
    for node_roll in node_branch_counts:
        index = len(options)
        node_roll_index[node_roll] = index
        node_roll_options = []
        for i in range(node_branch_counts[node_roll]):
            node_roll_options.append(i)
        options.append(node_roll_options)
    combinations = list(product(*options))
    return node_roll_index, combinations

def challenge(dicemax, calculate_strategy=False):
    bg = Backgammon(dicemax)
    # Get all distinct combinations of dice rolls and corresponding 
    # probabilities
    all_rolls_p = bg.all_rolls_p()
    # Generate a graph of distinct states of men and the transitions between 
    # them (truncating at the detached cases)
    graph = bg.graph()
    # Determine the nodes in the graph that have multiple choices for non-blot
    # next nodes. Choices that go to detached nodes are omitted because they
    # can't be part of an optimal strategy.
    branches = {}
    for node in graph:
        for roll in graph[node]:
            if len(graph[node][roll]) > 1:
                branches[(node, roll)] = len(graph[node][roll])
    # List all possible strategies
    strategy_node_roll_index, strategies = branch_combinations(branches)
    # If calculate_strategy is True (or the maximum value of the dice is not
    # one we have a pre-calculated optimal strategy for), iterate over all 
    # possible strategies and calculate the expected number of turns of each 
    # to determine the optimal strategy.
    if (dicemax not in [2,6]) or calculate_strategy:
        best_strategy_index = 0
        choice_expected_turns = []
        for strategy_index in range(len(strategies)):
            expected_turns = absorbing_markov(graph,all_rolls_p, strategy_node_roll_index, strategies, strategy_index)
            if strategy_index == 0 or choice_expected_turns[best_strategy_index] < expected_turns:
                best_strategy_index = strategy_index
            choice_expected_turns.append(expected_turns)
        return choice_expected_turns[best_strategy_index]
    # Use pre-computed optimal strategies for the main or bonus challenges and
    # return the expected number of dice rolls
    else:
        main_optimal_strategies = [(0, 1, 1, 1, 0)]
        main_node_roll_index = {((3, 0, 0, 0, 2), (1, 1)): 0, ((3, 0, 0, 0, 2), (2, 2)): 1, ((3, 0, 2), (1, 1)): 2, ((3, 0, 2), (2, 2)): 3, ((3, 2), (1, 1)): 4}
        bonus_optimal_strategies = [(0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1)]
        bonus_node_roll_index = {((3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2), (3, 3)): 0, ((3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2), (6, 6)): 1, ((3, 0, 2), (2, 2)): 2, ((3, 0, 2), (1, 1)): 3, ((3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2), (5, 5)): 4, ((3, 0, 0, 0, 0, 0, 0, 0, 2), (2, 2)): 5, ((3, 0, 0, 0, 0, 0, 0, 0, 2), (4, 4)): 6, ((3, 0, 0, 0, 0, 0, 2), (3, 3)): 7, ((3, 0, 0, 0, 0, 0, 2), (6, 6)): 8, ((3, 0, 0, 0, 2), (2, 2)): 9, ((3, 0, 0, 0, 2), (4, 4)): 10, ((3, 0, 0, 0, 2), (1, 1)): 11, ((3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2), (4, 4)): 12, ((3, 2), (1, 1)): 13, ((3, 0, 0, 0, 0, 2), (5, 5)): 14, ((3, 0, 0, 2), (3, 3)): 15}
        if dicemax == 2:
            return absorbing_markov(graph,all_rolls_p, main_node_roll_index, main_optimal_strategies, 0)
        else:
            return absorbing_markov(graph,all_rolls_p, bonus_node_roll_index, bonus_optimal_strategies, 0)

def main():
    parser = argparse.ArgumentParser(prog='feb2026')
    parser.add_argument("-s", "--strategy", action="store_true", help="search for the optimal strategy for each challenge rather than using a pre-computed result")
    args = parser.parse_args()
    print("\n######## Ponder This Challenge - February 2026 ########\n")
    main_expected_turns = challenge(2, calculate_strategy=args.strategy)
    main_expected_turns_minus_one = main_expected_turns - 1
    print(f"Main challenge solution:\n\n\t{main_expected_turns_minus_one} ({float(main_expected_turns_minus_one):.6f})")
    
    bonus_expected_turns = challenge(6, calculate_strategy=args.strategy)
    bonus_expected_turns_minus_one = bonus_expected_turns - 1
    print(f"\nBonus challenge solution:\n\n\t{bonus_expected_turns_minus_one} ({float(bonus_expected_turns_minus_one):.6f})")

if __name__ == "__main__":
    main()