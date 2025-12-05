# https://research.ibm.com/haifa/ponderthis/challenges/November2025.html

from dataclasses import dataclass
from copy import deepcopy

# String segment indexes
# s_n = a_n + b_n + c_n
# t_n = a_n + b_n + c_n + c_n + d_n + e_n + f_n
A_INDEX = 0
B_INDEX = 1
C_INDEX = 2
D_INDEX = 3
E_INDEX = 4
F_INDEX = 5

# Indexing for tuples used in expansions of substring terms.
SEGMENT_INDEX = 0
N_INDEX = 1

@dataclass
class SubstringSegment:
    segment_index: int
    n: int
    start_index:int
    stop_index:int

# For each segment in a string, produce the next iteration based on the main or
# bonus rules
def next_string_segments(prior_segments, bonus):
    next_segments = []
    for i in range(len(prior_segments)):
        prior_segment = prior_segments[i]
        next_segment = []
        for j in range(len(prior_segment)):
            if bonus:
                if prior_segment[j] == 'G':
                    next_segment.append('T')
                elif prior_segment[j] == 'T':
                    next_segment.append('C')
                    next_segment.append('A')
                elif prior_segment[j] == 'C':
                    next_segment.append('B')
                    next_segment.append('R')
                elif prior_segment[j] == 'A':
                    next_segment.append('I')
                elif prior_segment[j] == 'R':
                    next_segment.append('B')
                elif prior_segment[j] == 'B':
                    next_segment.append('I')
                    next_segment.append('S')
                elif prior_segment[j] == 'I':
                    next_segment.append('T')
                    next_segment.append('G')
                elif prior_segment[j] == 'S':
                    next_segment.append('C')
            else:
                if prior_segment[j] == 'G':
                    next_segment.append('T')
                elif prior_segment[j] == 'T':
                    next_segment.append('C')
                    next_segment.append('A')
                elif prior_segment[j] == 'C':
                    next_segment.append('T')
                    next_segment.append('G')
                elif prior_segment[j] == 'A':
                    next_segment.append('C')
        next_segments.append("".join(next_segment))
    return next_segments

# Given an index of segment lengths for prior strings, use the recursive 
# relations for s_n or t_n segments to determine segment lengths for the next
# string in the sequence and append the results to the prior_lengths list.
def next_string_lengths(prior_lengths, bonus):
    assert len(prior_lengths) >= 2, "Recursion for next string lengths requires at least the lengths of n=0, n=1"
    next_lengths = []
    if bonus:
        next_lengths = [0] * 6
        next_lengths[A_INDEX] = prior_lengths[-1][C_INDEX]
        next_lengths[B_INDEX] = prior_lengths[-1][D_INDEX]
        next_lengths[C_INDEX] = prior_lengths[-1][D_INDEX] + prior_lengths[-1][F_INDEX]
        next_lengths[D_INDEX] = prior_lengths[-1][E_INDEX] + prior_lengths[-2][E_INDEX]
        next_lengths[E_INDEX] = prior_lengths[-1][A_INDEX] + prior_lengths[-2][A_INDEX] + prior_lengths[-1][B_INDEX]
        next_lengths[F_INDEX] = prior_lengths[-1][A_INDEX] + prior_lengths[-2][A_INDEX]
    else:
        next_lengths = [0] * 3
        next_lengths[A_INDEX] = prior_lengths[-2][A_INDEX] + prior_lengths[-2][B_INDEX] + prior_lengths[-2][C_INDEX]
        next_lengths[B_INDEX] = prior_lengths[-1][A_INDEX]
        next_lengths[C_INDEX] = prior_lengths[-1][A_INDEX] + prior_lengths[-1][B_INDEX]
    prior_lengths.append(next_lengths)

# Perform expansion of portions of s_n or t_n using the recurrence relations 
# found for those strings, discarding any components that lie outside the 
# intended start and stop indexes, until the substring can be expressed 
# entirely in the form of substrings that have been fully calculated.
def recursive_expansion(expansion, bonus, calculated_strings, string_lengths):
    if bonus:
        assert len(calculated_strings) >= 6, f"Bonus recursion requires calculated strings up to n=5 (n={len(calculated_strings) - 1} provided)"
    else:
        assert len(calculated_strings) >= 4, f"Main recursion requires calculated strings up to n=3 (n={len(calculated_strings) - 1} provided)"
    done = True
    for i in range(len(expansion)):
        if expansion[i].n >= len(calculated_strings):
            done = False
            break
    if done:
        result = ''
        for i in range(len(expansion)):
            result += calculated_strings[expansion[i].n][expansion[i].segment_index][expansion[i].start_index:expansion[i].stop_index + 1]
        return result
    next_expansion = []
    term_start_index = 0
    for i in range(len(expansion)):
        # If this term does not require further expansion, copy it over
        if expansion[i].n < len(calculated_strings):
            next_expansion.append(deepcopy(expansion[i]))
            continue
        # Otherwise, expand this term with a recurrence
        n = expansion[i].n
        # expanded_terms gives each term in the expansion as 
        # (segment index, offset from n)
        expanded_terms = []
        if bonus:
            assert expansion[i].segment_index in {A_INDEX, B_INDEX}, f"Bonus expansion for term {expansion[i].segment_index}_{n} unavailable. a/0 or b/1 segments only"
            if expansion[i].segment_index == A_INDEX:
                expanded_terms = [(A_INDEX, -4), (A_INDEX, -5), (B_INDEX, -4), (A_INDEX, -5), (A_INDEX, -6), (B_INDEX, -5), (A_INDEX, -3), (A_INDEX, -4)]
            else:
                expanded_terms = [(A_INDEX, -3), (A_INDEX, -4), (B_INDEX, -3), (A_INDEX, -4), (A_INDEX, -5), (B_INDEX, -4)]
        else:
            assert expansion[i].segment_index == A_INDEX, f"Main expansion for term {expansion[i].segment_index}_{n} unavailable. a/0 segments only"
            expanded_terms = [(A_INDEX, -2), (A_INDEX, -3), (A_INDEX, -3), (A_INDEX, -4)]
        term_length_accumulator = 0
        for j in range(len(expanded_terms)):
            term_len = string_lengths[n + expanded_terms[j][N_INDEX]][expanded_terms[j][SEGMENT_INDEX]]
            term_start_index = term_length_accumulator
            term_stop_index = term_start_index + term_len
            term_length_accumulator += term_len
            # Discard expanded terms that do not overlap our range
            if term_stop_index < expansion[i].start_index:
                continue
            if term_start_index >= expansion[i].stop_index:
                continue
            term_internal_start_index = 0
            term_internal_stop_index = term_len
            if term_stop_index > expansion[i].stop_index:
                term_internal_stop_index = term_len - (term_stop_index - expansion[i].stop_index)
            if term_start_index < expansion[i].start_index:
                term_internal_start_index = (expansion[i].start_index - term_start_index)
            next_expansion.append(SubstringSegment(expanded_terms[j][SEGMENT_INDEX], n + expanded_terms[j][N_INDEX], term_internal_start_index, term_internal_stop_index))
    return recursive_expansion(next_expansion, bonus, calculated_strings, string_lengths)
 
# Compute segments of s_n or t_n directly up to n = max_calculated_string_n, 
# then calculate the lengths of subsequent string segments until an n is 
# reached where |a_n| is greater than substring_stop and n is modularly 
# congruent to substring_n (modulus differing in the main and bonus 
# challenges), implying that s_{substring_n} or t_{substring_n} will begin with
# a_n and a_n fully contains the intended substring. Finally, work backward 
# from a_n using expansion rules until the intended substring can be 
# constructed using the directly computed string segments.
# Note that substring_stop is the index of the final character in the required 
# substring.
def challenge(bonus, max_calculated_string_n, substring_n, substring_start, substring_stop):
    assert substring_start <= substring_stop, f"Start of substring index must be <= stop of substring index ({substring_start} and {substring_stop} provided)"
    assert substring_n > 0, "substring n index must be non-negative"
    # Directly produce a lookup of s_n or t_n, organized as segmented 
    # substrings, up to specified max_calculated_string_n
    computed_string_segments = []
    if bonus:
        computed_string_segments.append(['R','A','B','B','I','T','S'])
    else:
        computed_string_segments.append(['C','A','T'])
    for n in range(1, max_calculated_string_n + 1):
        computed_string_segments.append(next_string_segments(computed_string_segments[-1], bonus)) 
    # Compute lengths of string segments for subsequent strings until a string 
    # where the first segment length contains the required substring range is 
    # reached and the index is compatible with the the required substring n 
    # (congruent mod 2 for the main challenge, congruent mod 4 for the bonus 
    # challenge)
    string_segment_lengths = []
    # Initialize segment lengths from directly calculated strings
    for i in range(len(computed_string_segments)):
        segment_lengths = []
        if bonus:
            # Omit the second "B" segment from RABBITS as it will always be 
            # identical to the first and does not need to be recalculated
            segment_lengths = [len(computed_string_segments[i][0]),
                               len(computed_string_segments[i][1]),
                               len(computed_string_segments[i][2]),
                               len(computed_string_segments[i][4]),
                               len(computed_string_segments[i][5]),
                               len(computed_string_segments[i][6])]
        else:
            segment_lengths = [len(computed_string_segments[i][0]),
                               len(computed_string_segments[i][1]),
                               len(computed_string_segments[i][2])]
        string_segment_lengths.append(segment_lengths)
    n = len(computed_string_segments)
    while True:
        # Generate next substring lengths using recursive relations until an 
        # a_n term is found where the length exceeds our stopping index and n 
        # is congruent to our intended n mod 2 for the main challenge or mod 4 
        # for the bonus challenge
        next_string_lengths(string_segment_lengths, bonus)
        if string_segment_lengths[n][A_INDEX] > substring_stop:
            if bonus:
                if substring_n % 4 == n % 4:
                    break
            else:
                if substring_n % 2 == n % 2:
                    break
        n += 1
    # The first string segment at the current n index contains the entirety of 
    # the desired substring. Expand the terms of the segment using recurrence
    # relations with prior string segments, pruning expanded terms that do not 
    # overlap with the desired substring, until the level of directly computed 
    # string segments is reached.
    segment_terms = [SubstringSegment(A_INDEX, n, substring_start, substring_stop)]
    return recursive_expansion(segment_terms, bonus, computed_string_segments, string_segment_lengths)

def main():
    print("\n######## Ponder This Challenge - November 2025 ########\n")
    # Construct a lookup of segments of s_{n} up to n = 4, then use those
    # to find the substring s_{10**100}[10**100:10**100 + 1000]
    print("Main challenge:\n\n{}".format(challenge(bonus=False, 
              max_calculated_string_n=4, 
              substring_n=10**100, 
              substring_start=10**100, 
              substring_stop=10**100 + 999)))
    # Construct a lookup of segments of t_{n} up to n = 5, then use those
    # to find the substring t_{10**100}[10**100:10**100 + 1000]
    print("\nBonus challenge:\n\n{}".format(challenge(bonus=True, 
              max_calculated_string_n=5, 
              substring_n=10**100, 
              substring_start=10**100, 
              substring_stop=10**100 + 999)))

if __name__ == "__main__":
    main()