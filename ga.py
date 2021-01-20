# coding: utf-8
#
# ga.py
#
#            Copyright (C) 2021 Keisuke Ueda
#
from collections import deque
import itertools
import json
import time
import numpy as np

from reversi import play


SIZE = 8
GENE_LENGTH = 10


# Convert a 10-variable array into a 8x8 matrix
#   arg:    (10, ) np.array
#   return: (8, 8) np.array
def generate_eb(array):
    return np.array([list(array[[0,1,2,3,3,2,1,0]]),
                    list(array[[1,4,5,6,6,5,4,1]]),
                    list(array[[2,5,7,8,8,7,5,2]]),
                    list(array[[3,6,8,9,9,8,6,3]]),
                    list(array[[3,6,8,9,9,8,6,3]]),
                    list(array[[2,5,7,8,8,7,5,2]]),
                    list(array[[1,4,5,6,6,5,4,1]]),
                    list(array[[0,1,2,3,3,2,1,0]])])

# An evaluation-board generated randomly
e_random = generate_eb(np.random.normal(0, 10, GENE_LENGTH))



class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)



class GA:
    def __init__(self, parameter):
        self.max_generation = parameter[0]
        self.num_population = parameter[1]
        self.num_parents = parameter[2]
        self.blx_alpha = parameter[3]
        self.mut_prob = parameter[4]
        self.data_path = parameter[5]
        self.num_generation = 0
        self.population = np.array([])
        self.parents = np.array([])
        with open(self.data_path) as f:
            self.data = json.load(f)
        
    def make_genes(self):
        self.population = np.random.normal(0, 10, (self.num_population, GENE_LENGTH))
    
    # return: True if load can be done, else False
    def load_genes(self):
        if list(self.data.keys()):
            latest = str(np.max([int(k) for k in list(self.data.keys())]))
            self.population = np.array(self.data[latest]["population"])
            self.parents = np.array(self.data[latest]["selected"])
            self.num_generation = int(latest)
            return True
        else: return False
            
    def select(self):
        start = time.time()
        q = deque(self.population)
        print("--- SELECT ---")
        while len(q) > self.num_parents:
            e1, e2 = q.popleft(), q.popleft()
            result = play(generate_eb(e1), generate_eb(e2), debug_mode=False)
            winner = e1 if result==-1 else e2
            q.append(winner)
            print("X", end='')
        # Generate the next generation
        self.parents = np.array(q)
        end = time.time()
        print("\n--- Complete {:6.1f} seconds ---".format(end-start))
    
    # Just for debug (Check if this GA algorithm itself work correctly)
    def select_debug(self):
        start = time.time()
        q = deque(self.population)
        print("--- SELECT ---")
        while len(q) > self.num_parents:
            e1, e2 = q.popleft(), q.popleft()
            result = np.sum(e1 - e2)
            winner = e1 if result>0 else e2
            q.append(winner)
            print("X", end='')
        # Generate the next generation
        self.parents = np.array(q)
        end = time.time()
        print("\n--- Complete {:6.1f} seconds ---".format(end-start))
        
    
    # looking at the justification of selected genes.
    # here, match with random genes.
    def test(self):
        print("----- Test Match -----")
        result = play(generate_eb(self.parents[0]), e_random, debug_mode=False)
        if result==-1: print("-- WIN --")
        elif result==1: print("-- LOSE --")
        else: print("-- DRAW --")
    
    # BLX-alpha Crossover
    def blx(self, x, y):
        alpha = self.blx_alpha
        max_p, min_p = np.max(x, axis=0), np.min(y, axis=0)
        diff = max_p - min_p
        max_c, min_c = max_p+alpha*diff, min_p-alpha*diff
        return choose_rand(min_c, max_c, 2)
    
    # Crossover
    def crossover(self):
        population = self.parents.copy()
        for comb in itertools.combinations(self.parents, 2):
            population = np.concatenate([population, self.blx(comb[0], comb[1])])
        self.population = population
    
    # Mutation
    def mutation(self):
        probability = self.mut_prob
        for i in range(self.num_population):
            rand = np.random.rand()
            if rand < probability / 3:
                target = np.random.randint(0, GENE_LENGTH)
                self.population[i][target] += np.random.normal(0, 20)
            elif rand < probability * 2 / 3:
                target = np.random.randint(0, GENE_LENGTH)
                self.population[i][target] *= -1
            elif rand < probability:
                target1, target2 = np.random.randint(0, GENE_LENGTH, 2)
                tmp = self.population[i][target1]
                self.population[i][target1] = self.population[i][target2]
                self.population[i][target2] = tmp
                
    # Normalize the parameter of genes
    def normalize(self):
        self.population -= np.mean(self.population, axis=1, keepdims=True)
        self.population = self.population / np.max(np.abs(self.population), axis=1, keepdims=True) * 100
        
    # Saving the data into JSON file.
    def save_data(self):
        print("--- SAVING DATA ---")
        self.data[str(self.num_generation)] = {
                                            "population": list(self.population), 
                                            "selected"  : list(self.parents)
                                        }
        with open(self.data_path, 'w') as f:
            json.dump(self.data, f, indent=4, cls=MyEncoder)
        print("--- Complete ---")
    
    # Total flow of genetic algorithm
    def evolve(self):
        if self.load_genes(): pass
        else:
            print("----- Generation:    0 -----")
            self.make_genes()
            self.normalize()
            self.select()
            self.save_data()
        self.num_generation += 1
        while (self.num_generation <= self.max_generation):
            print("----- Generation: {:3d} -----".format(self.num_generation))
            self.test()
            self.crossover()
            self.mutation()
            self.normalize()
            self.select()
            self.save_data()
            self.num_generation += 1
            print()

# Choose one point randomly in the specified number dimensional rectangular.            
def choose_rand(mini, maxi, num):
    arr = np.random.rand(num, 10)
    arr = arr * (maxi-mini) + mini
    return arr