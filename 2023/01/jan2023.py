# https://research.ibm.com/haifa/ponderthis/challenges/January2023.html

from random import randrange, random, choice, choices
from copy import deepcopy

def set_at_pos(string, position, character):
    return string[:position] + character + string[position + 1:]

# A first stab at a solution and a useful debugging check on the recursive method. BFS exploration of possible moves on the input string
# to find a minimal route to all 'G's. The search space becomes unworkably large above about 7 characters.
class BFSGeneSolver:
    def __init__(self):
        self.cache = {"G": 0, "A": 1, "C": 1, "T": 1}
    def updateCache(self, string, steps):
        if(string not in self.cache.keys() or self.cache[string] > steps):
            self.cache[string] = steps
    def canSetToA(self, string, position):
        if(string[position] == 'A'):
            return False
        if(position == 0):
            return True
        if(string[position] == 'C'):
            if(string[position - 1] != 'C'):
                return False
            if(position - 1 == 0):
                return True
            i = position - 2
            allAs = True 
            while(allAs and i >= 0):
                if(string[i] != 'A'):
                    allAs = False
                i-=1
            return allAs
        return False
    def canSetToC(self, string, position):
        if(string[position] == 'C'):
            return False
        if(position == 0):
            return True
        if(string[position] == 'T'):
            i = position - 1
            allCs = True 
            while(allCs and i >= 0):
                if(string[i] != 'C'):
                    allCs = False
                i-=1
            return allCs
        if(string[position] == 'A'):
            if(string[position - 1] != 'C'):
                return False
            if(position - 1 == 0):
                return True
            i = position - 2
            allAs = True 
            while(allAs and i >= 0):
                if(string[i] != 'A'):
                    allAs = False
                i-=1
            return allAs
        return False
    def canSetToT(self, string, position):
        if(string[position] == 'T'):
            return False
        if(position == 0):
            return True
        if(string[position] == 'C'):
            i = position - 1
            allTs = True 
            while(allTs and i >= 0):
                if(string[i] != 'T'):
                    allTs = False
                i-=1
            return allTs
        if(string[position] == 'G'):
            i = position - 1
            allTs = True 
            while(allTs and i >= 0):
                if(string[i] != 'T'):
                    allTs = False
                i-=1
            return allTs
        return False
    def canSetToG(self, string, position):
        if(string[position] == 'G'):
            return False
        if(position == 0):
            return True
        if(string[position] == 'T'):
            if(string[position - 1] != 'C'):
                return False
            if(position - 1 == 0):
                return True
            i = position - 2
            allAs = True 
            while(allAs and i >= 0):
                if(string[i] != 'A'):
                    allAs = False
                i-=1
            return allAs
        return False
    def bfs(self, input):
        string = input
        while(len(string) > 0 and string[len(string) - 1] == 'G'):
            string = string[:-1]
        if len(string) == 0:
            return 0
        if(string in self.cache.keys()):
            return self.cache[string]
        explored = {}
        frontier = {}
        frontier_next = {string:0}
        min = -1
        while len(frontier_next) > 0:
            frontier = frontier_next.copy()
            frontier_next.clear()
            for k in frontier.keys():
                steps = frontier[k] 
                if(k[len(k) - 1] == 'G'):
                    result = steps + self.bfs(k)
                    if min == -1 or result < min:
                        min = result
                if(k not in explored.keys() or steps < explored[k]):
                    explored[k] = steps
                    for i in range(len(k)):
                        if self.canSetToG(k,i):
                            nextK = set_at_pos(k,i,'G')
                            if((nextK not in explored.keys() or steps + 1 < explored[nextK]) and nextK not in frontier_next.keys()):
                                frontier_next[nextK] = steps + 1
                        if self.canSetToT(k,i):
                            nextK = set_at_pos(k,i,'T')
                            if((nextK not in explored.keys() or steps + 1 < explored[nextK]) and nextK not in frontier_next.keys()):
                                frontier_next[nextK] = steps + 1
                        if self.canSetToA(k,i):
                            nextK = set_at_pos(k,i,'A')
                            if((nextK not in explored.keys() or steps + 1 < explored[nextK]) and nextK not in frontier_next.keys()):
                                frontier_next[nextK] = steps + 1
                        if self.canSetToC(k,i):
                            nextK = set_at_pos(k,i,'C')
                            if((nextK not in explored.keys() or steps + 1 < explored[nextK]) and nextK not in frontier_next.keys()):
                                frontier_next[nextK] = steps + 1

        self.updateCache(string, min)
        return min
    def solve(self, input):
        return self.bfs(input)

class RecursiveGeneSolver:
    def __init__(self):
        self.allAsCache = {"A": 0, "C": 1, "G": 1, "T": 1}
        self.allCsCache = {"C": 0, "A": 1, "G": 1, "T": 1}
        self.allTsCache = {"T": 0, "A": 1, "G": 1, "C": 1}
        self.allGsCache = {"G": 0, "A": 1, "T": 1, "C": 1}
        self.AsAndCCache = {"C": 0, "A": 1, "G": 1, "T": 1}
    # build array of 'C' of length size
    def allCs(self, size):
        return ['C'] * size
    # build array of 'T' of length size
    def allTs(self, size):
        return ['T'] * size
    # build array of 'A', 'A', ...,'C' of total length size
    def anC(self, size):
        result = ['A'] * (size - 1)
        result.append('C')
        return result
     
    # the number of steps to convert the given array to AA...A
    def toAllAs(self, array):
        if(len(array)) == 0:
            return 0
        key = ''.join(array)
        # early return if previously determined
        if(key in self.allAsCache.keys()):
            return self.allAsCache[key]
        steps = 0
        allAs = True
        for i in range(len(array)):
            if array[i] != 'A':
                allAs = False
                break
        if(allAs):
            self.allAsCache[key] = 0
            return 0
        # find the first non-A character from the right
        top = len(array) - 1
        while top >= 0:
            if array[top] != 'A':
                break
            top -= 1
        # if only the first character is non-A, it takes one step to finish
        if(top == 0):
            return 1
        # all characters before the first non-A character
        topslice = array[:top]
        toplen = len(topslice)
        # C -> A
        if array[top] == 'C':
            steps = self.toAsAndCs(topslice) + 1 + self.toAllAs(self.anC(toplen))
        # T -> C -> A
        elif array[top] == 'T':
            steps = self.toAllCs(topslice) + 1 + self.toAsAndCs(self.allCs(toplen)) + 1 + self.toAllAs(self.anC(toplen))
        # G -> T -> C -> A
        elif array[top] == 'G':
            steps = self.toAllTs(topslice) + 1 + self.toAllCs(self.allTs(toplen)) + 1 + self.toAsAndCs(self.allCs(toplen)) + 1 + self.toAllAs(self.anC(toplen))
        self.allAsCache[key] = steps
        return steps

    # the number of steps to convert the given array to CC...C
    def toAllCs(self, array):
        if(len(array)) == 0:
            return 0
        key = ''.join(array)
        # early return if previously determined
        if(key in self.allCsCache.keys()):
            return self.allCsCache[key]
        steps = 0
        allCs = True
        for i in range(len(array)):
            if array[i] != 'C':
                allCs = False
                break
        if(allCs):
            self.allCsCache[key] = 0
            return 0
        # find the first non-C character from the right
        top = len(array) - 1
        while top >= 0:
            if array[top] != 'C':
                break
            top -= 1
        # if only the first character is non-C, it takes one step to finish
        if(top == 0):
            self.allCsCache[key] = 1
            return 1
        # all characters before the first non-C character
        topslice = array[:top]
        toplen = len(topslice)
        # A -> C
        if array[top] == 'A':
            steps = self.toAsAndCs(topslice) + 1 + self.toAllCs(self.anC(toplen))
        # T -> C
        elif array[top] == 'T':
            steps = self.toAllCs(topslice) + 1
        # G -> T -> C
        elif array[top] == 'G':
            steps = self.toAllTs(topslice) + 1 + self.toAllCs(self.allTs(toplen)) + 1
        self.allCsCache[key] = steps
        return steps

    # the number of steps to convert the given array to TT..T
    def toAllTs(self, array):
        if(len(array)) == 0:
            return 0
        key = ''.join(array)
        
        if(key in self.allTsCache.keys()):
            return self.allTsCache[key]
        steps = 0
        allTs = True
        for i in range(len(array)):
            if array[i] != 'T':
                allTs = False
                break
        if(allTs):
            self.allTsCache[key] = 0
            return 0
        # find the first non-C character from the right
        top = len(array) - 1
        while top >= 0:
            if array[top] != 'T':
                break
            top -= 1
        # if only the first character is non-T, it takes one step to finish
        if(top == 0):
            self.allTsCache[key] = 1
            return 1
        # all characters before the first non-T character
        topslice = array[:top]
        toplen = len(topslice)
        # A -> C -> T
        if array[top] == 'A':
            steps = self.toAsAndCs(topslice) + 1 + self.toAllTs(self.anC(toplen )) + 1
        # C -> T
        elif array[top] == 'C':
            steps = self.toAllTs(topslice) + 1
        # G -> T
        elif array[top] == 'G':
            steps = self.toAllTs(topslice) + 1
        self.allTsCache[key] = steps
        return steps

    # the number of steps to convert the given array to AA...AC
    def toAsAndCs(self, array):
        if(len(array)) == 0:
            return 0
        key = ''.join(array)
        if(key in self.AsAndCCache.keys()):
            return self.AsAndCCache[key]
        steps = 0
        hasEndingC = False
        if(array[len(array) - 1] == 'C'):
            hasEndingC = True
            remainingAs = 0
            for i in range(len(array) - 2, -1, -1):
                if array[i] != 'A':
                    break
                else:
                    remainingAs += 1
            # already of the form A...AC. 0 steps
            if remainingAs == len(array) - 1:
                self.AsAndCCache[key] = 0
                return 0
            # only the first character differs from the form A...AC
            # so 1 step
            elif remainingAs == len(array) - 2:
                self.AsAndCCache[key] = 1
                return 1
        top = len(array) - 1
        # all characters before the top character (always the final character in the input in this case)
        topslice = array[:top]
        toplen = len(topslice)
        if hasEndingC:
            steps = self.toAllAs(topslice)
        else:
            # A -> C
            if array[top] == 'A':
                 steps = self.toAsAndCs(topslice) + 1 + self.toAllAs(self.anC(toplen))
            # T -> C
            elif array[top] == 'T':
                steps = self.toAllCs(topslice) + 1 + self.toAllAs(self.allCs(toplen))
            # G -> T -> C
            elif array[top] == 'G':
                steps = self.toAllTs(topslice) + 1 + self.toAllCs(self.allTs(toplen)) + 1 + self.toAllAs(self.allCs(toplen))
        self.AsAndCCache[key] = steps
        return steps

    # the number of steps to convert the given array to GG..G
    def toAllGs(self, array):
        if(len(array)) == 0:
            return 0
        key = ''.join(array)
        if(key in self.allGsCache.keys()):
            return self.allGsCache[key]
        steps = 0
        allGs = True
        for i in range(len(array)):
            if array[i] != 'G':
                allGs = False
                break
        if(allGs):
            self.allGsCache[key] = 0
            return 0
        top = len(array) - 1
        while top >= 0:
            if array[top] != 'G':
                break
            top -= 1
        # if only the first character is non-G, it takes one step to finish
        if(top == 0):
            self.allGsCache[key] = 1
            return 1
        # all characters before the first non-G character
        topslice = array[:top]
        toplen = len(topslice)
        # A -> C -> T -> G
        if array[top] == 'A':
            steps = self.toAsAndCs(topslice) + 1 + self.toAllTs(self.anC( toplen )) + 1 + self.toAsAndCs(self.allTs( toplen  )) + 1 + self.toAllGs(self.anC( toplen ))# damn
        # C -> T -> G
        elif array[top] == 'C':
            steps = self.toAllTs(topslice) + 1 +  self.toAsAndCs(self.allTs( toplen )) + 1 + self.toAllGs(self.anC( toplen ))
        elif array[top] == 'T':
            steps = self.toAsAndCs(topslice) + 1 + self.toAllGs(self.anC(toplen))
        self.allGsCache[key] = steps
        return steps
    
    def solve(self, array):
        return self.toAllGs(array)

# A genetic algorithm for finding a gene that can reach an all-G state
# within the specified range of steps.
class GeneticAlgorithmGeneSearch:
    def __init__(self, recursiveSolver, minSteps, maxSteps):
        self.recursiveSolver = recursiveSolver
        self.minSteps = minSteps
        self.maxSteps = maxSteps
        self.geneLength = 20
        self.populationSize = 30
        self.maxGenerations = 20
        self.mutationChance = 0.1
        self.crossoverChance = 0.7
    # randomized instance of a gene of 'A's and 'C's 
    def randomGene(self):
        gene = []
        for i in range(self.geneLength):
            if(random() > 0.5):
                gene.append('C')
            else:
                gene.append('A')
        return gene
    # GA fitness measure
    def fitness(self, gene):
        steps = self.recursiveSolver.solve(gene)
        if steps < self.minSteps:
            return float(self.minSteps - steps)
        elif steps > self.maxSteps:
            return float(steps - self.maxSteps)
        else:
            return 0.0
    # GA crossover: swap characters between two randomly selected indexes in
    # each parent chromosome and return the updated versions
    def crossover(self, gene1, gene2):
        index1 = randrange(self.geneLength)
        index2 = randrange(self.geneLength)
        char1 = gene1[index1]
        char2 = gene2[index2]
        childGene1 = deepcopy(gene1)
        childGene2 = deepcopy(gene2)
        childGene2[index2] = char1
        childGene1[index1] = char2
        return childGene1, childGene2
    # GA mutation. For one randomly selected element,
    # flip it between 'A' and 'C'
    def mutation(self, gene):
        index = randrange(self.geneLength)
        if gene[index] == 'A':
            gene[index] = 'C'
        else:
            gene[index] = 'A'
        return gene
    # pick 2 chromosomes via tournament selection.
    # select n chromosomes from the total population and return the fittest two
    def tournamentSelection(self, population, n):
        if len(population) < n:
            raise Exception("Population of size {0} too small to select {1} elements".format(len(population), n))
        if n < 2:
            raise Exception("Selection of size {0} too small to produce two parents".format(n))
        selection = choices(population, k = n)
        sortedSelection = sorted(selection, key=lambda c: self.fitness(c))
        return deepcopy(sortedSelection[0]), deepcopy(sortedSelection[1])
    def reproduceAndReplacePopulation(self, population):
        nextPopulation = []
        selectionSize = len(population) // 2
        while(len(nextPopulation) < len(population)):
            parentGene1, parentGene2 = self.tournamentSelection(population, selectionSize)
            if(random() < self.crossoverChance):
                childGene1, childGene2 = self.crossover(parentGene1, parentGene2)
                nextPopulation.append(childGene1)
                nextPopulation.append(childGene2)
            else:
                nextPopulation.append(parentGene1)
                nextPopulation.append(parentGene2)
        # because the result will always be even, remove the last element if 
        # we need an odd result
        if(len(nextPopulation) > len(population)):
            nextPopulation.pop()
        return nextPopulation
    def mutatePopulation(self, population):
        nextPopulation = []
        for i in range(len(population)):
            nextGene = deepcopy(population[i])
            if(random() < self.mutationChance):
                nextPopulation.append(self.mutation(nextGene))
            else:
                nextPopulation.append(nextGene)
        return nextPopulation
    
    def run(self):
        population = []
        for i in range(self.populationSize):
            population.append(self.randomGene())
        # attempting to find fitness no larger than 0
        best = min(population, key = lambda c: self.fitness(c))
        for g in range(self.maxGenerations):
            # early return if we find a match
            if(self.fitness(best) == 0.0):
                print("Satisfactory gene found at start of generation {0}".format(g))
                return best
            avg = sum(map(self.fitness, population))/len(population)
            print("Generation {0} population {1} best fitness {2} average {3}".format(g, len(population), self.fitness(best), avg))
            population = self.reproduceAndReplacePopulation(population)
            population = self.mutatePopulation(population)
            highest = min(population, key = lambda c: self.fitness(c))
            if(self.fitness(highest) < self.fitness(best)):
                best = highest
        if self.fitness(best) == 0.0:
             print("Satisfactory gene found after generation {0}".format(self.maxGenerations - 1))
        else:
            print("No satisfactory gene found after {0} generations. Best fitness found: {1}".format(self.maxGenerations, self.fitness(best)))
        return best

# use the trustworthy-but-slow BFS solver to validate the trickier-but-fast recursive solver
def validation():
    print("Starting validation")
    bfsSolver = BFSGeneSolver()
    recursiveSolver = RecursiveGeneSolver()
    # test the provided sample
    sample = "CTTGG"
    sampleExpected = 8
    print("Testing sample gene " + sample)
    sampleBFSSteps = bfsSolver.solve(sample)
    sampleRecursiveSteps = recursiveSolver.solve(sample)
    if(sampleBFSSteps != sampleRecursiveSteps):
        print("Sample {0}:\tBFS {1}\tRecursive {2}".format(sample, sampleBFSSteps, sampleRecursiveSteps))
        return False
    if(sampleRecursiveSteps != sampleExpected):
        print("Sample {0}:\tBFS {1}\tRecursive {2} expected {3}".format(sample, sampleBFSSteps, sampleRecursiveSteps, sampleExpected))
        return False
    sample2 = "ACAC"
    sample2Expected = 25
    print("Testing sample gene " + sample2)
    sample2BFSSteps = bfsSolver.solve(sample2)
    sample2RecursiveSteps = recursiveSolver.solve(sample2)
    if(sample2BFSSteps != sample2RecursiveSteps):
        print("Sample {0}:\tBFS {1}\tRecursive {2}".format(sample2, sample2BFSSteps, sample2RecursiveSteps))
        return False
    if(sample2RecursiveSteps != sample2Expected):
        print("Sample {0}:\tBFS {1}\tRecursive {2} expected {3}".format(sample2, sample2BFSSteps, sample2RecursiveSteps, sample2Expected))
        return False
    # test random sequences of varying lengths
    letters = ['T', 'G', 'A', 'C']
    randomSequenceMax = 5
    errorFound = False
    print("Testing random sequences up to {0} characters...".format(randomSequenceMax))
    for i in range(100):
        test = []
        for j in range(randomSequenceMax):
            test.append(choice(letters))
            bfsSteps = bfsSolver.solve(''.join(test))
            recursiveSteps = recursiveSolver.solve(test)
            if(bfsSteps != recursiveSteps):
                print("Sample {0}\tBFS {1} Recursive {2}".format(''.join(test), bfsSteps, recursiveSteps))
                errorFound = True
    if not errorFound:
        print("Validation completed with no errors")
    else:
        print("Errors found in validation")
    return not errorFound
    
def main():
    
    print("\n######## Ponder This Challenge - January 2023 ########\n")
    # Validation disabled.
    #if not validation():
    #    exit(0)
    print("Searching for satisfactory gene...")
    recursiveSolver = RecursiveGeneSolver()
    geneSearch = GeneticAlgorithmGeneSearch(recursiveSolver, 880000,  890000)
    result = geneSearch.run()
    if(geneSearch.fitness(result) != 0.0):
        print("Could not find a satisfying gene in {0} generations. Best match can be completed in {1} steps".format(geneSearch.maxGenerations, recursiveSolver.solve(result)))
        return
    print("Result:")
    print(result)
    print(recursiveSolver.solve(result))

    hundredTs = ['T'] * 100
    print("\nReaching the all-'G' state from an all-'T' state, for n=100 letters:\n{0}".format(recursiveSolver.solve(hundredTs)))


main()