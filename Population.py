from random import shuffle, choice, sample, random
from operator import  attrgetter
import numpy as np
import pandas as pd
from project.game import main
from copy import deepcopy
from utils import *
import os

from selection import *
from crossover import  *
from mutation import *

def create_weights():
    first_layer = np.random.rand(16,16) * np.random.choice([-3,3])
    second_layer = np.random.rand(16,) * np.random.choice([-3,3])
    third_layer = np.random.rand(16,64) * np.random.choice([-3,3])
    fourth_layer = np.random.rand(64,)* np.random.choice([-3,3])
    fifth_layer = np.random.rand(64,4)* np.random.choice([-3,3])
    sixth_layer = np.random.rand(4,)* np.random.choice([-3,3])
    return np.array((first_layer, second_layer, third_layer, fourth_layer, fifth_layer, sixth_layer))

class Individual:
    def __init__(
        self,
        fitness_type,
        representation=None,
    ):
        self.fitness_type = fitness_type
        if representation is None:
            self.representation = flatten(create_weights())
        else:
            self.representation = representation
        self.fitness = self.evaluate()

    def evaluate(self):
        game_score = main(unflatten(self.representation), display_graphics=True)
        self.game_score = game_score
        return self.game_score[self.fitness_type]

    def __len__(self):
        return len(self.representation)

    def __getitem__(self, position):
        return self.representation[position]

    def __setitem__(self, position, value):
        self.representation[position] = value

    def __repr__(self):
        return f"Individual(size={len(self.representation)}); Fitness: {self.fitness}"


class Population:
    def __init__(self, size, optim, fitness_type):
        self.individuals = []
        self.size = size
        self.optim = optim
        self.fitness_type = fitness_type
        for _ in range(size):
            self.individuals.append(
                Individual(
                    self.fitness_type
                )
            )
            
    def evolve(self, gens, select, elitism, mutate, crossover, mu_p, co_p, export_data = True):
        csv_row=[]

        for gen in range(gens):
            new_pop = []
            if elitism == True:
                if self.optim == 'max':
                    elite = deepcopy(max(self.individuals, key=attrgetter('fitness')))
                elif self.optim == 'min':
                    elite = deepcopy(min(self.individuals, key=attrgetter('fitness')))

            while len(new_pop) < self.size:

                parent1, parent2 = select(self), select(self)
                # Crossover
                if random() < co_p:
                    offspring1, offspring2 = crossover(parent1, parent2)
                else:
                    offspring1, offspring2 = parent1, parent2
                # Mutation
                if random() < mu_p:
                    offspring1 = mutate(offspring1)
                if random() < mu_p:
                    offspring2 = mutate(offspring2)

                new_pop.append(Individual(representation=offspring1, fitness_type=self.fitness_type))
                if len(new_pop) < self.size:
                    new_pop.append(Individual(representation=offspring2, fitness_type=self.fitness_type))

            if elitism == True:
                if self.optim == 'max':
                    least = min(new_pop, key=attrgetter('fitness'))
                elif self.optim == 'min':
                    least = max(new_pop, key=attrgetter('fitness'))
                new_pop.append(elite)
                new_pop.pop((new_pop.index(least)))

            self.individuals = new_pop

            print(f'Best member of gen {gen+1}')

            if self.optim == 'max':
                champion = max(self, key=attrgetter("fitness"))
                if export_data:
                    csv_row.append(champion.fitness)
                print(champion.game_score)
            elif self.optim == 'min':
                champion = min(self, key=attrgetter("fitness"))
                if export_data:
                    csv_row.append(champion.fitness)
                print(champion.game_score)
        return csv_row

    def __len__(self):
        return len(self.individuals)

    def __getitem__(self, position):
        return self.individuals[position]

    def __repr__(self):
        return f"Population(size={len(self.individuals)}, individual_size={len(self.individuals[0])})"



if __name__=='__main__':

    # Get current directory to save data to
    wd=os.getcwd()
    path=os.path.join(wd, "Geometric_xo_mu_2.csv")
    # Create an empty list which will be used to save the GAs data
    to_csv=[]

    # n_gens = choice([50, 100, 200])
    # select = choice([tournament, fps, rank])


    # Iterate over n runs to test the parameters
    for i in range(1):

        # Each time, create a brand new population with the same parameters
        pop = Population(
            size=30,
            optim = 'max',
            fitness_type = 'score'
        )

        # And evolve it
        to_csv.append(pop.evolve(
            gens=100, 
            select= tournament, 
            crossover= geometric_co,
            mutate=geometric_mutation,
            co_p=1,
            mu_p=0.05,
            elitism=True,
            export_data=True
        ))

    # If we chose to export data in the pop parameters, to_csv will have data in it, which we will save 
    if len(to_csv) > 0:
        df_to_csv=pd.DataFrame(data=to_csv)
        df_to_csv.to_csv(path)
