import copy
import genotype as genotype_class
import light_up_puzzle as puzzle_class
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
            self.fitness = 0
        

        def init_puzzles_with_bulbs():
            """Randomly places bulbs on each puzzle in population in a uniform manner.
            
            The number of attempted bulb placements is determined by config.
            """
            for genotype_index in range(len(self.population)):
                for bulb_count in range(int(self.config.settings['num_bulbs_to_place'])):
                    self.phenotype.place_bulb_randomly(self.population[genotype_index].bulbs)
        

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


        self.config = config

        # Open the log file and write the header
        # TODO: Wrap this in a log class
        with open(self.config.settings['log_file_path'], 'w') as log:
            log.write('Result Log\n\n')
        
        self.population_size = int(self.config.settings['µ'])
        self.offspring_pool_size = int(self.config.settings['λ'])

        # Create the base puzzle class (phenotype)
        self.phenotype = puzzle_class.LightUpPuzzle(self.config)

        # Create the puzzle population: a list genotypes
        self.population = []
        for _ in range(self.population_size):
            self.population.append(genotype_class.Genotype())

        self.parents = []
        self.children = []


        if int(self.config.settings['force_validity']):
            # Use black square adjacency heuristic to force validity
            force_adj_bulbs()
        
        init_puzzles_with_bulbs()
        init_experiment_variables()


    def init_run_variables(self):
        """Initializes run specific variables.

        This function should be called at the top of each run.
        """
        self.max_run_fitness = 0
        self.eval_count = 1
    
    
    def evaluate(self, population):
        """TODO""" 
        for genotype in population:
            self.phenotype.check_valid_solution(genotype.bulbs)
            genotype.fitness = self.phenotype.get_fitness()
            genotype.fitness_ratio = genotype.fitness / (self.phenotype.num_rows * self.phenotype.num_cols - len(self.phenotype.black_squares))
        
        population.sort(key=lambda x : x.fitness_ratio, reverse=True)


    def select_parents(self):
        """Chooses which parents from the population breed.

        TODO
        """
        if int(self.config.settings['use_fitness_proportional_selection']):
            # Select the top parents for breeding
            num_selected_parents = int(len(self.population) * float(self.config.settings['selection_proportion']))
            self.parents = self.population[:num_selected_parents]

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

        def shuffle_bulb(child_index):
            """Attempts to move the placement of a random bulb to a random position.

            If this cannot be done in a valid way, the child is left unchanged.
            """
            tmp_child = self.children[child_index]

            bulb_index = random.randint(0, len(tmp_child.bulbs) - 1)

            try:
                tmp_child.pop(bulb_index)
            except:
                # No bulbs avail to remove
                pass
            
            shuffled_bulb = False
            for _ in range(int(self.config.settings['max_num_random_bulb_placements_mutation'])):
                if self.phenotype.place_bulb_randomly(tmp_child):
                    shuffled_bulb = True
                    break
            
            if shuffled_bulb:
                self.children[child_index] = tmp_child


        for child_index in range(self.children):
            if random.random() < float(self.config.settings['bulb_shuffle_prob']):
                shuffle_bulb(child_index)


    def select_for_survival(self):
        """Selects which children from the child population will replace parents
        in the general population.

        Keeps µ (population size) constant.
        """
        pass


    def decide_termination(self):
        """Will the experiment terminate?

        True if the program will terminate, False otherwise.
        """
        pass
