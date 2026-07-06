# https://research.ibm.com/blog/ponder-this-june-2026

import itertools
import math
from copy import deepcopy

# Represents a film where a list of heroes are introduced sequentially and 
# each new hero has an action scene together with the previously introduced 
# heroes.
class Film:

    def __init__(self):
        self.heroes = []

    def __len__(self):
        return len(self.heroes)
    
    def __contains__(self, item):
        return item in self.heroes
    
    def __repr__(self):
        return f"{self.heroes}"

    def add(self, hero):
        self.heroes.append(hero)
    
    def combos(self):
        result = set()
        for i in range(1,len(self.heroes) + 1):
            result.add(frozenset(self.heroes[:i]))
        return result

# Represents a hypercube in boolean "n-hero-space" where a symmetric chain 
# decomposition can be constructed to derive a set of films that contain all 
# hero combinations over the minimal number of action scenes.
class HeroCube:

    def __init__(self, n):
        if n < 3:
            raise ValueError("Not implemented for fewer than 3 heroes")
        if n > 26:
            raise ValueError("Not implemented for more than 26 heroes (not enough letters)")
        self.n = n
        self.coordinate_to_hero_index = {}
        for i in range(n):
            self.coordinate_to_hero_index[i] = chr(i + 65)        
        # Define a symmetric chain decomposition for a boolean lattice 
        # hypercube with 3 dimensions. The chains cover all vertices, are 
        # disjoint, are of minimal number, and are "increasing" in the number 
        # of "true" entries in each successive vertex coordinate.
        three_cube_scd =   [
                            [[0,0,0],[1,0,0],[1,1,0],[1,1,1]],
                            [[0,1,0],[0,1,1]],
                            [[0,0,1],[1,0,1]],
                            ]
        # extend each coordinate in the 3-dimensional SCD to n dimensions
        self.three_cube_scd = []
        for three_chain in three_cube_scd:
            chain = []
            for three_vertex in three_chain:
                vertex = [0] * self.n
                for i in range(3):
                    vertex[i] = three_vertex[i]
                chain.append(vertex)
            self.three_cube_scd.append(chain)

    # Construct a symmetric chain decomposition of this hypercube using the
    # recursive method given by Petr Gregor in 
    # https://ktiml.mff.cuni.cz/~gregor/hypercube/lecture17.pdf,
    # with the pre-defined SCD for a hypercube of order 3 as the lowest level
    # of the recursion. 
    # Return a mapping of the SCD to a list of films covering all possible 
    # combinations of n heroes in the minimal number of scenes, as a compressed
    # string.
    def construct_scd(self):
        # Construct the SCD
        chains = []
        if self.n == 3:
            chains = self.three_cube_scd
        else:
            chains = self.join_scd(self.n - 1, self.construct_scd_recurse(self.n - 1, False), self.construct_scd_recurse(self.n - 1, True))
        # Convert the SCD into a list of films
        films_strings = []        
        for chain in chains:
            heroes = []
            start_index = 0
            # Skip the 0,0,...0 vertex if at the start of this chain
            if chain[start_index].count(1) == 0:
                start_index = 1
            # If the chain starts with a vertex with more than one 1 entry,
            # the heroes represented can start the movie in any order.
            if chain[start_index].count(1) > 1:
                initial_heroes = list(map(lambda i: self.coordinate_to_hero_index[i] ,[i for i, x in enumerate(chain[start_index]) if x == 1]))
                heroes.extend(initial_heroes)
            # If there is only one 1 entry in the initial vertex in the chain,
            # add that hero to the film
            else:
                initial_hero = self.coordinate_to_hero_index[chain[start_index].index(1)]
                heroes.append(initial_hero)
            # Iterate over the chain and add each subsequent hero to the film
            for i in range(start_index + 1, len(chain)):
                heroes.append(self.next_hero(chain[i-1],chain[i]))
            films_strings.append('0' + "".join(heroes))
        # Sort the films by length (not required, but I prefer it) and return 
        # the compressed string
        films_strings.sort(key = lambda x: len(x))
        
        return "".join(films_strings)

    # Given two neighboring vertices in a chain, return the added hero
    def next_hero(self, previous_vertex, current_vertex):
        for i in range(len(current_vertex)):
            if current_vertex[i] != previous_vertex[i]:
                return self.coordinate_to_hero_index[i]
        raise Exception(f"Next hero not found between vertices {previous_vertex} and {current_vertex}. The vertices may not be adjacent")

    # Return True if the end vertex neighbors the start vertex and increases 
    # the number of 1 entries between their coordinates by one.
    def is_increasing_neighbor(self, start_vertex, end_vertex):
        end_vertex_contains_start_vertex = True
        max_start_vertex_hi_dim = 0
        for i in range(len(start_vertex)):
            if start_vertex[i] == 1:
                max_start_vertex_hi_dim = i
        for i in range(max_start_vertex_hi_dim):
            if end_vertex[i] != start_vertex[i]:
                end_vertex_contains_start_vertex = False
                break
        if not end_vertex_contains_start_vertex:
            return False
        return start_vertex.count(1) + 1 == end_vertex.count(1)
    # Given lo and hi SCD chains on sub-cubes of dimension self.n - depth, 
    # remove the final vertex from each chain in the hi cube SCD, add it to a 
    # neighboring chain in the lo cube SCD, and return the union of the two 
    # sets of modified chains. 
    def join_scd(self, depth, lo, hi):
        joined_chains = []
        removed_vertices = []
        # For each hi chain, remove the final vertex and add it to the list of
        # removed vertices. If the remaining chain is non-empty, add it to the
        # list of resulting chains of the join.
        for hi_chain in hi:
            final_vertex = hi_chain.pop()
            removed_vertices.append(final_vertex)
            if len(hi_chain) > 0:
                joined_chains.append(hi_chain)
        # For each lo chain, add a neighboring removed vertex from one of the
        # hi chains. This is always possible due to how the lo and hi cubes 
        # were originally split.
        for lo_chain in lo:
            final_vertex = lo_chain[-1]
            # Find a removed vertex that neighbors the final vertex of this lo
            # chain
            neighbor_found = False
            for i in range(len(removed_vertices)):
                # When a neighboring vertex is found, add it to the end of this
                # chain and remove it from the list of available removed 
                # vertices
                if self.is_increasing_neighbor(final_vertex, removed_vertices[i]):
                    lo_chain.append(removed_vertices[i])
                    del removed_vertices[i]
                    neighbor_found = True
                    break
            # This shouldn't be possible
            if not neighbor_found:
                raise Exception(f"Adjoining neighbor not found between path {lo_chain} with final vertex {final_vertex} and removed high vertices {removed_vertices} at depth {depth}.")
            # Add the incremented lo chain to the list of chains returned in 
            # the join
            joined_chains.append(lo_chain)
        return joined_chains
            
    # Recursively construct an SCD for this hypercube by dividing it in two on 
    # single dimensions until a 3-cube is reached, then join the SCDs for the 
    # sub-cubes together until a full one is reached. 
    def construct_scd_recurse(self, depth, hi):
        chains = []
        # If we've reached the maximum depth of the recursion, use the pre-set 
        # 3-dimensional cube SCD.
        if depth == 3:
            chains = deepcopy(self.three_cube_scd)
        # Otherwise, join the SCDs of the split hi and lo sub-cubes of this
        # hypercube.
        else:
            chains = self.join_scd(depth - 1, self.construct_scd_recurse(depth - 1, False), self.construct_scd_recurse(depth - 1, True))
        # Set hi/lo for the corresponding coordinate of all chains at this depth
        for i in range(len(chains)):
            for j in range(len(chains[i])):
                chains[i][j][depth] = 1 if hi else 0
        return chains

# Given a list of films, return all combinations of heroes that appear over all
# scenes
def films_combos(films):
    result = set()
    for film in films:
        result = result.union(film.combos())
    return result

# Given a set of heroes, return the set of all possible combinations (excluding
# the empty combination).
def hero_combos(heroes):
    sets = set()
    for i in range(1, len(heroes) + 1):
        for combo in itertools.combinations(heroes, i):
            hero_combo = frozenset(combo)
            sets.add(hero_combo)
    return sets

# Returns true if the film string covers all combos of the listed heroes and
# does so with the minimal number of scenes and films
def films_valid(films_string):
    # Parse the films and heroes
    films_split = filter(lambda x: len(x) > 0, films_string.split("0"))
    films = []
    heroes = set()
    for film_string in films_split:
        film = Film()
        for h in list(film_string):
            heroes.add(h)
            film.add(h)
        films.append(film)
    # Given n, determine the minimal number of films and scenes
    n = len(heroes)
    minimal_films = math.comb(n, math.floor(n/2))
    minimal_scenes = 0
    for i in range(math.ceil(n/2), n+1):
        num_films = math.comb(n, i) - math.comb(n, i+1)
        minimal_scenes += i * num_films
    if len(films) != minimal_films:
        return False
    if sum(map(lambda x: len(x), films)) != minimal_scenes:
        return False
    # Test if all possible combinations are covered by the films
    all_combos = hero_combos(list(heroes))
    all_film_combos = films_combos(films)
    remaining_combos = all_combos.difference(all_film_combos)
    if len(remaining_combos) > 0:
        return False
    return True

# Based on the recursive method of symmetric chain decomposition (SCD) given in 
# https://ktiml.mff.cuni.cz/~gregor/hypercube/lecture17.pdf on page 2,
# construct a symmetric chain decompostion for the boolean lattice hypercube 
# of order n to produce a set of disjoint chains where all vertices are covered,
# the number of chains is minimal, and each chain is "increasing". Return the 
# mapping of the SCD to a set of films covering all combinations of n-heroes in
# the minimal number of scenes.
def hero_symmetric_chain_decomposition(n):
    # Initialize a hypercube of order n in "n-hero-space" and find an SCD using
    # the recursive construction method.
    hypercube = HeroCube(n)
    films_string = hypercube.construct_scd()
    if not films_valid(films_string):
        return None
    return films_string

def main():
    print("\n######## Ponder This Challenge - June 2026 ########\n")
    print("Main challenge:\n")
    main_solution = hero_symmetric_chain_decomposition(6)
    if main_solution is None:
        print("\tNo solution found")
    else:
        print("\t", main_solution)
    print("\nBonus challenge:\n")
    bonus_solution = hero_symmetric_chain_decomposition(10)
    if bonus_solution is None:
        print("\tNo solution found")
    else:
        print("\t", bonus_solution)
    print()

if __name__ == "__main__":
    main()