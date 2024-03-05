# https://research.ibm.com/haifa/ponderthis/challenges/February2024.html

# Calculate the probability that Alice wins the game requiring N consecutive 
# rounds won with the given round outcome probabilities.
def game_win_probability(p_round_alice_win, p_round_bob_win, N):
    p_round_draw = 1.0 - p_round_alice_win - p_round_bob_win
    
    # Build a Markov model of game states based on consecutive wins for Alice 
    # and Bob
    # 0 - State D -   0/0 -         Draw
    # 1 - State A -   [1,N-1]/0 -   Alice has consecutive wins but has not won
    # 2 - State B -   0/[1,N-1] -   Bob has consecutive wins but has not won
    # 3 - State A_N - N/0 -         Alice has won
    # 4 - State B_N - 0/N -         Bob has won
    
    # Calculate transition probabilities between states
    p_A_to_D = 0    # Cumulative probabilty of transition from Alice winning consecutive rounds to a draw round 
    p_A_to_B = 0    # Cumulative probabilty of transition from Alice winning consecutive rounds to a Bob round win
    p_B_to_D = 0    # Cumulative probabilty of transition from Bob winning consecutive rounds to a draw round
    p_B_to_A = 0    # Cumulative probabilty of transition from Bob winning consecutive rounds to an Alice round win
    p_A_to_A_N = pow(p_round_alice_win,(N-1))   # Probability of transition from Alice winning consecutive rounds to Alice winning the game
    p_B_to_B_N = pow(p_round_bob_win,(N-1))     # Probability of transition from Bob winning consecutive rounds to Bob winning the game
    for i in range(0, N-1):
        alice_pow = pow(p_round_alice_win,i)
        bob_pow = pow(p_round_bob_win,i)
        p_A_to_D += alice_pow
        p_A_to_B += alice_pow
        p_B_to_D += bob_pow
        p_B_to_A += bob_pow
    p_A_to_D *= p_round_draw
    p_A_to_B *= p_round_bob_win
    p_B_to_D *= p_round_draw
    p_B_to_A *= p_round_alice_win
    
    # Set up the transition matrix for the Markov model
    transitions = [ [p_round_draw,  p_round_alice_win,  p_round_bob_win,    0.0,        0.0], 
                    [p_A_to_D,      0.0,                p_A_to_B,           p_A_to_A_N, 0.0],   
                    [p_B_to_D,      p_B_to_A,           0.0,                0.0,        p_B_to_B_N],
                    [0.0,           0.0,                0.0,                1.0,        0.0],
                    [0.0,           0.0,                0.0,                0.0,        1.0] ]
    
    # Run the system forward for m steps to reach stable ratios between the A, 
    # B and D states. 
    m = 1000
    steps = 0
    values = [0.0, 0.0, 0.0, 0.0, 0.0]
    next_values = [1.0, 0.0, 0.0, 0.0, 0.0]
    while steps < m:
        steps += 1
        values = next_values
        next_values = [0.0]*5
        for i in range(0, 5):
            for j in range(0,5):
                next_values[i] += values[j] * transitions[j][i]
    
    # Approximate the probability that Alice wins the game based on the 
    # probabilities that have accumulated in the states of the model.
    A_value = next_values[1]
    B_value = next_values[2]
    A_N_value = next_values[3]
    B_N_value = next_values[4]
    p_alice_win = A_N_value + ((A_value * p_A_to_A_N) * (1.0 - A_N_value - B_N_value) / ((A_value * p_A_to_A_N) + (B_value * p_B_to_B_N))) 
    return p_alice_win

# Calculate the probabilities of Alice and Bob winning a round of the game
def round_probabilities(bonus):
	# the maximum possible roll of the dice is 59
	primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59]
	dice = [[1,4],[1,6],[1,8],[0,9],[1,12],[1,20]]
	outcomes = [0] * 60
	# Run through all rolls of the dice and record counts of outcomes
	dice_recursion(0, 0, dice, outcomes)
	total = sum(outcomes)
	alice_total = 0
	bob_total = 0
	for i in range(0, len(primes)):
		alice_total += outcomes[primes[i]]
	if bonus:
		# Bob wins if a non-prime odd number
		for i in range(1, len(outcomes), 2):
			if i in primes:
				continue
			bob_total += outcomes[i]
	else:
		# Bob wins if a non-prime even number
		for i in range(0, len(outcomes), 2):
			if i in primes:
				continue
			bob_total += outcomes[i]
	return alice_total/total, bob_total/total

# Given a list of dice, recurse through all possible rolls and update the 
# outcomes list
def dice_recursion(index, accumulated_sum, dice, outcomes):
	if index == len(dice):
		outcomes[accumulated_sum] += 1
		return 
	for i in range(dice[index][0], dice[index][1] + 1):
		dice_recursion(index + 1, accumulated_sum + i, dice, outcomes)

def main():
    print("\n######## Ponder This Challenge - February 2024 ########\n")
    a_main, b_main = round_probabilities(False)
    print("Main challenge:\t\t{:.18f}".format(game_win_probability(a_main, b_main, 13)))
    a_bonus, b_bonus = round_probabilities(True)
    print("Bonus challenge:\t{:.18f}".format(game_win_probability(a_bonus, b_bonus, 300)))
	
if __name__ == "__main__":
    main()