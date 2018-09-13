import copy
import genotype as genotype_class
import light_up_puzzle as puzzle_class
import log as log_class
import seed as seed_class
import random


class EADriver:
    def __init__(self, config):
        """Initializes the EADriver class.
        
        Where config is a Config object. 
        """

        def init_experiment_variables():
            """Initializes experiment specific variables.
            
            This function should only be called once (at the beginning of the program, 
            by the class' __init__ function).
            """
            self.max_global_fitness = 0
            self.run_count = 1
            self.best_fit_genotype = genotype_class.Genotype()
        

        self.config = config

        # Initialize the seed class
        self.seed = seed_class.Seed(self.config)

        self.population_size = int(self.config.settings['µ'])
        self.offspring_pool_size = int(self.config.settings['λ'])

        init_experiment_variables()
        self.init_run_variables()

        # Initialize the log file class
        self.log = log_class.Log(self.config, self.seed, self.phenotype, overwrite=True)


    def init_run_variables(self):
        """Initializes run specific variables.

        This function should be called before each run.
        """

        def force_adj_bulbs():
            """Places bulbs around black squares where there is only one valid
            bulb placement pattern.
            """
            bulbs = set([])

            # Determine where to place bulbs
            for black_square in self.phenotype.black_squares:
                # Get the adjacent coordinates to black_square that are not black
                adj_coords = [s for s in self.phenotype.get_adj_coords(black_square) if not s in self.phenotype.black_squares]

                if self.phenotype.black_squares[black_square] == len(adj_coords):
                    # There is only one way to place bulbs around this square
                    # Place those bulbs
                    for coord in adj_coords:
                        self.phenotype.place_bulb(coord, bulbs)
            
            # Save bulb placements to each genotype
            for genotype in self.population:
                genotype.bulbs = copy.deepcopy(bulbs)


        def init_puzzles_with_bulbs():
            """Randomly places bulbs on each puzzle in population in a uniform manner.
            
            The number of attempted bulb placements is determined by config.
            """
            for genotype_index in range(len(self.population)):
                # Place bulbs until num_bulb_placement_failures failures are reached
                failure_count = 0
                while failure_count < int(self.config.settings['num_bulb_placement_failures']):
                    if not self.phenotype.place_bulb_randomly(self.population[genotype_index].bulbs):
                        failure_count += 1


        self.max_run_fitness = 0
        self.eval_count = 1
        self.avg_fitness_ratio = 0.0
        self.total_fitnesses_seen = 0
        self.total_fitness_ratio_sum = 0

        # Create/reset the base puzzle class (phenotype)
        self.phenotype = puzzle_class.LightUpPuzzle(self.config)

        # Create/reset the puzzle population: a list genotypes
        self.population = []
        for _ in range(self.population_size):
            self.population.append(genotype_class.Genotype())

        self.parents = []
        self.children = []

        if int(self.config.settings['force_validity']):
            # Use black square adjacency heuristic to force validity
            force_adj_bulbs()
        
        init_puzzles_with_bulbs()

    
    def evaluate(self, population, log_run=False):
        """TODO""" 
        for genotype in population:
            self.phenotype.check_valid_solution(genotype.bulbs)
            genotype.fitness = self.phenotype.get_fitness()
            genotype.fitness_ratio = genotype.fitness / (self.phenotype.num_rows * self.phenotype.num_cols - len(self.phenotype.black_squares))

            # Calculate average fitness
            self.total_fitness_ratio_sum += genotype.fitness_ratio
            self.total_fitnesses_seen += 1
            self.avg_fitness_ratio = self.total_fitness_ratio_sum / self.total_fitnesses_seen

            # Determine if this fitness is the new best fitness
            if genotype.fitness > self.best_fit_genotype.fitness:
                self.best_fit_genotype = genotype
                # TODO: write to solution file
        
        self.eval_count += len(population)

        if log_run:
            self.log.write_run_header(self.run_count)
            self.log.write_run_data(self.eval_count, self.avg_fitness_ratio, self.best_fit_genotype.fitness_ratio)


    def select_parents(self):
        """Chooses which parents from the population breed.

        TODO
        """
        if int(self.config.settings['use_fitness_proportional_selection']):
            # Select parents for breeding using the fitness proportional "roulette wheel" method (with replacement)
            self.parents = random.choices(self.population, weights=[(g.fitness_ratio * 100) / float(len(self.population)) for g in self.population], k=int(self.config.settings['parent_population_size']))

        else:
            # TODO: Perform a k-tournament selection
            pass


    def recombine(self):
        """Breeds λ (offspring_pool_size) children from the existing parent population.
        
        TODO
        """

        def breed(parent_a, parent_b):
            """Breeds two parent genotypes together to produce a child genotype.

            Returns the child genotype.
            """
            a_bulbs = list(parent_a.bulbs)
            b_bulbs = list(parent_b.bulbs)

            # Perform a n-point crossover on the parent's bulbs
            n = int(self.config.settings['n_point_crossover'])

            min_crossover_index = 0
            max_crossover_index = min(len(a_bulbs) - 1, len(b_bulbs) - 1)

            crossover_indices = []
            rand_start = min_crossover_index 
            for _ in range(n):
                crossover_indices.append(random.randint(rand_start, max_crossover_index))
                rand_start = crossover_indices[-1]
            
            # Ensure the entire parent is copied during crossover
            crossover_indices.append(max_crossover_index + 1)

            child_bulbs = set([])
            prev_crossover_index = 0
            for crossover_index in crossover_indices:
                if random.random() < float(self.config.settings['parent_selection_weight']):
                    # Choose parent_a's substring
                    for bulb in a_bulbs[prev_crossover_index:crossover_index]:
                        child_bulbs.add(bulb)

                else:
                    # Choose parent_b's substring
                    for bulb in b_bulbs[prev_crossover_index:crossover_index]:
                        child_bulbs.add(bulb)
                
                prev_crossover_index = crossover_index
            
            return genotype_class.Genotype(child_bulbs)


        self.children = []

        for _ in range(self.offspring_pool_size):
            # Select parents with replacement
            parent_a = self.parents[random.randint(0, len(self.parents) - 1)]
            parent_b = self.parents[random.randint(0, len(self.parents) - 1)]

            # Produce a child
            self.children.append(breed(parent_a, parent_b))
        
    
    def mutate(self):
        """Performs mutation on each child in the child population.
        
        TODO
        """

        def shuffle_bulb(child):
            """Attempts to move the placement of a random bulb to a random position.

            If this cannot be done in a valid way, the child is left unchanged.
            """
            tmp_child = copy.deepcopy(child)
            rand_bulb_index = random.randint(0, len(tmp_child.bulbs) - 1)

            try:
                tmp_child.pop(rand_bulb_index)
            except:
                # No bulbs available to remove
                pass
            
            shuffled_bulb = False
            fail_count = 0
            while fail_count < int(self.config.settings['num_bulb_placement_failures_mutation']):
                if self.phenotype.place_bulb_randomly(tmp_child.bulbs):
                    shuffled_bulb = True
                    break
                else:
                    fail_count += 1
            
            if shuffled_bulb:
                child = copy.deepcopy(tmp_child)


        for child in self.children:
            if random.random() < float(self.config.settings['mutation_probability']):
                shuffle_bulb(child)


    def select_for_survival(self):
        """Selects which children from the child population will replace parents
        in the general population.

        Keeps µ (population size) constant.
        """
        if int(self.config.settings['use_truncation']):
            # Use truncation for survival selection
            combined_generations = self.population + self.children
            self.sort_genotypes(combined_generations)

            self.population = combined_generations[:self.population_size]
        
        else:
            # Use k-tournament for survival selection
            pass


    def decide_termination(self):
        """Will the experiment terminate?

        Returns True if the program will terminate, False otherwise.
        """
        if self.best_fit_genotype.fitness_ratio == 1.0:
            # The board has been completely solved
            return True
        
        # TODO: Implement stagnant solution growth timeout

        return False


    def sort_genotypes(self, genotype_list):
        """Sorts the given genotype list from most fit to least fit by each
        element's fitness ratio.
        """
        genotype_list.sort(key=lambda x : x.fitness_ratio, reverse=True)


    def print_update(self):
        """Prints a run count and eval count update to the screen."""
        print('Run: %i\tEval count: %i' % (self.run_count, self.eval_count))
        print('Avg Fitness: %f\tBest Fitness (Ratio): %f' % (self.avg_fitness_ratio, self.best_fit_genotype.fitness_ratio))
        print()


    def increment_run_count(self):
        """Increments the run count."""
        self.run_count += 1
