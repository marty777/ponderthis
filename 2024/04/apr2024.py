# https://research.ibm.com/haifa/ponderthis/challenges/April2024.html

import math
import copy

# Index constants
MODULUS = 0
REMAINDER = 1
GAME_N = 0
GAME_MOVES = 1

# Calculate a remainder satisfying all given congruences with pairwise coprime
# moduli using the Chinese Remainder Theorem. Congruences are passed as a list 
# of [[modulus, remainder],...]
def crt(congruences):
    sum = 0
    product = 1
    for i in range(len(congruences)):
        product *= congruences[i][MODULUS]
    for i in range(len(congruences)):
        p = product // congruences[i][MODULUS]
        # pow can calculate a multiplicative modular inverse as of Python 3.8
        sum += congruences[i][REMAINDER] * pow(p, -1, congruences[i][MODULUS]) * p 
    return sum % product

# Find a solution, if one exists, satisfying all given conguences with possibly 
# non-pairwise coprime moduli. Congruences are passed as a list of 
# [[modulus, remainder],...]
def non_coprime_crt(congruences):
    # Groups are keyed by base modulus and point to a dictionary of congruences
    # keyed on initial congruence id giving the power the modulus is raised to
    groups = {}
    for i in range(len(congruences)):
        if congruences[i][MODULUS] not in groups.keys():
            groups[congruences[i][MODULUS]] = {}
        groups[congruences[i][MODULUS]][i] = 1
    # Separate out greatest common divisors until no two groups have a GCD > 1
    while True:
        groups_changed = False
        for base_modulus in groups.keys():
            smallest_non_one_gcd = -1
            for other_base_modulus in groups.keys():
                if base_modulus == other_base_modulus:
                    continue
                gcd = math.gcd(base_modulus,other_base_modulus)
                if gcd != 1 and (smallest_non_one_gcd == -1 or gcd < smallest_non_one_gcd):
                    smallest_non_one_gcd = gcd
            if smallest_non_one_gcd == -1:
                continue
            # If this group has a common divisor > 1 with any other groups, 
            # create a new group for the divisor if needed and remove powers of 
            # the divisor from each existing group. Any remaining quotients > 1 
            # after the divisor is removed move to their own groups
            if not smallest_non_one_gcd in groups.keys():
                groups[smallest_non_one_gcd] = {}
            # The number of groups may change while iterating, so get a fixed 
            # list of the current keys
            group_keys = list(groups.keys())
            for other_base_modulus in group_keys:
                if other_base_modulus == smallest_non_one_gcd:
                    continue
                if other_base_modulus % smallest_non_one_gcd == 0:
                    # Remove the group for the other base modulus and add its 
                    # members to groups for the smallest gcd and any remaining 
                    # quotient > 1 after powers of the gcd are divided out.
                    # Note that it's possible for some parts of an initial 
                    # congruence to reach the same group by multiple paths. In 
                    # this case, only one entry for the initial congruence is 
                    # retained in the group, but the powers are summed
                    other_group = copy.deepcopy(groups[other_base_modulus])
                    del groups[other_base_modulus]
                    for congruence_id in other_group.keys():
                        power = 0
                        quotient = other_base_modulus**other_group[congruence_id]
                        while quotient % smallest_non_one_gcd == 0:
                            power += 1
                            quotient //= smallest_non_one_gcd
                        if congruence_id not in groups[smallest_non_one_gcd].keys():
                            groups[smallest_non_one_gcd][congruence_id] = power
                        else:
                            groups[smallest_non_one_gcd][congruence_id] += power
                        if quotient == 1:
                            continue 
                        if not quotient in groups.keys():
                            groups[quotient] = {}
                        if congruence_id not in groups[quotient].keys():
                            groups[quotient][congruence_id] = 1
                        else:
                            groups[quotient][congruence_id] += 1
            groups_changed = True
            break
        if not groups_changed:
            break
    # For each group, determine if all congruences within it have a solution.
    # If not, there is no solution to the original system of congruences.
    # If there is, the group of congruences are all implied by a single
    # congruence which can be added to coprime_congruences to be solved using
    # the CRT
    coprime_congruences = []
    solvable = True
    for base_modulus in groups.keys():
        greatest_power = 0
        greatest_power_remainder = 0
        for congruence_id in groups[base_modulus].keys():
            if groups[base_modulus][congruence_id] > greatest_power:
                greatest_power = groups[base_modulus][congruence_id]
                greatest_power_remainder = congruences[congruence_id][REMAINDER]
        remainder_okay = True
        for congruence_id in groups[base_modulus].keys():
            modulus = base_modulus ** groups[base_modulus][congruence_id]
            remainder = congruences[congruence_id][REMAINDER]
            if greatest_power_remainder % modulus != remainder % modulus:
                remainder_okay = False
                break
        if not remainder_okay:
            solvable = False
            break 
        coprime_congruences.append([base_modulus ** greatest_power, greatest_power_remainder % (base_modulus ** greatest_power)])
    if solvable:
        return crt(coprime_congruences)
    return False

# Perform a single move instruction on a game state
def act(rods, move, verbose = False):
    if move == 0:
        # Find disk 1 
        disk1_rod = -1
        for i in range(0,3):
            if len(rods[i]) > 0 and rods[i][0] == 1:
                disk1_rod = i
                break
        assert disk1_rod >= 0, "Bad index of disk 1 rod on move 0"
        dest_rod = (disk1_rod + 1) % 3
        rods[disk1_rod].pop(0)
        rods[dest_rod].insert(0, 1)
        if verbose: print("Move 0: Disk 1 moved from rod {} to rod {}".format(disk1_rod, dest_rod))
    elif move == 1:
        # Find disk 1 
        disk1_rod = -1
        for i in range(0,3):
            if len(rods[i]) > 0 and rods[i][0] == 1:
                disk1_rod = i
                break
        assert disk1_rod >= 0, "Bad index of disk 1 rod on move 1"
        dest_rod = (disk1_rod - 1) % 3
        rods[disk1_rod].pop(0)
        rods[dest_rod].insert(0, 1)
        if verbose: print("Move 1: Disk 1 moved from rod {} to rod {}".format(disk1_rod, dest_rod))
    else:
        # If possible, move a disk that is not 1 to another rod. There is 
        # guanteed to be at most 1 way to do this
        move_found = False
        for i in range(0, 3):
            if len(rods[i]) == 0 or rods[i][0] == 1:
                continue
            # Move the top disk of this rod clockwise
            if len(rods[(i + 1) % 3]) == 0 or rods[i][0] <  rods[(i+1)%3][0]:
                disk = rods[i].pop(0)
                rods[(i + 1) % 3].insert(0, disk)
                if verbose: print("Move 2: Disk {} moved from rod {} to rod {}".format(disk, i, (i + 1) % 3))
                move_found = True
                break
            # Move the top disk of this rod counter-clockwise
            elif len(rods[(i - 1) % 3]) == 0 or rods[i][0] <  rods[(i-1)%3][0]:
                disk = rods[i].pop(0)
                rods[(i - 1) % 3].insert(0, disk)
                if verbose: print("Move 2: Disk {} moved from rod {} to rod {}".format(disk, i, (i - 1) % 3))
                move_found = True
                break
        if not move_found:
            if verbose: print("Move 2: No disk moved")

# Determine if all disks are on the winning rod
def in_win_state(rods): return len(rods[0]) == 0 and len(rods[2]) == 0

# Determine if all disks are on the starting rod
def in_start_state(rods): return len(rods[1]) == 0 and len(rods[2]) == 0

# Play the game with the given n and move string until a cycle is found and 
# return each step where the game was in a win state along with the cycle 
# length
def hanoi(n, move_string):
    # Process the move string into a list of integers
    moves = list(map(lambda x: int(x), list(move_string)))
    # Set up the rods and add all disks to the starting rod
    rods = [[],[],[]]
    for i in range(0, n):
        rods[0].append(i+1)
    win_states = []
    move_count = 0
    done = False
    # Play the game using the move list until a cycle is found
    while True:
        act(rods, moves[move_count % len(moves)])
        if in_start_state(rods) and move_count % len(moves) == len(moves) - 1:
            break
        if in_win_state(rods):
            win_states.append(move_count + 1)
        move_count += 1
    return win_states, move_count + 1

# Given a list of games, find the cycle lengths and steps with win states for
# each, then test combinations of win states from each game to see if there is 
# a solution to the system of modular congruences. Returns the smallest 
# solution found from any of the combinations, or False if there are no 
# solutions.
def challenge(games):
    remainders = []
    moduli = []
    for g in games:
        wins, cycle_length = hanoi(g[GAME_N], g[GAME_MOVES])
        remainders.append(wins)
        moduli.append(cycle_length)
    candidates = []
    challenge_recurse(remainders, moduli, [], candidates)
    if len(candidates) == 0:
        return False
    return min(candidates)

# Update the list of candidate solutions by recursively trying all combinations 
# of win states between games as systems of modular congruences
def challenge_recurse(remainders, moduli, selected, candidates):
    if len(selected) == len(moduli):
        congruences = []
        for index in range(len(selected)):
            congruences.append([moduli[index], selected[index]])
        solution = non_coprime_crt(congruences)
        if solution != False:
            candidates.append(solution)
    else:
        for remainder in remainders[len(selected)]:
            next_selected = copy.deepcopy(selected)
            next_selected.append(remainder)
            challenge_recurse(remainders, moduli, next_selected, candidates)

def main():
    print("\n######## Ponder This Challenge - April 2024 ########\n")
    main_result = challenge(
        [[7, '12021121120020211202121'], 
        [10, '0211202112002']]
        )
    print("Main challenge: {}".format(main_result if main_result != False else 'No solution found'))
    bonus_result = challenge(
        [[7, '12021121120020211202121'], 
        [10, '0211202112002'], 
        [9,'20202020021212121121202120200202002121120202112021120020021120211211202002112021120211200212112020212120211']]
        )
    print("Bonus challenge: {}".format(bonus_result if bonus_result != False else 'No solution found'))

if __name__ == "__main__":
    main()