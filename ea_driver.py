import copy
import light_up_puzzle as puzzle_class
import random


class EADriver:
    def __init__(self, config):
        """Initializes the EADriver class.
        
        Where config is a Config object. 
        """

        def init_experiment_variables():
            """Initializes experiment specific variables.
            
            This function should only be called once (at the beginning of the program).
            """
            self.max_global_fitness = 0
            self.fitness = 0
        

        def init_puzzles_with_bulbs():
            for puzzle_index in range(len(self.puzzle_population)):
                for bulb_count in range(int(self.config.settings['num_bulbs_to_place'])):
                    self.puzzle_population[puzzle_index].place_bulb_randomly()
        

        # Open the log file and write the header
        # TODO: Wrap this in a log class
        with open(config.settings['log_file_path'], 'w') as log:
            log.write('Result Log\n\n')
        
        self.config = config
        self.population_size = int(config.settings['µ'])
        self.offspring_pool_size = int(config.settings['λ'])

        base_puzzle = puzzle_class.LightUpPuzzle(config)
        self.puzzle_population = []
        for _ in range(self.population_size):
            self.puzzle_population.append(copy.deepcopy(base_puzzle))

        self.parents = []
        self.children = []
        
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
        for puzzle in population:
            puzzle.check_valid_solution()
        
        population.sort(key = lambda x : x.fitness_ratio, reverse = True)


    def select_parents(self):
        """Chooses which parents breed.

        TODO
        """
        if int(self.config.settings['use_fitness_proportional_selection']):
            # Select the top parents for breeding
            num_selected_parents = int(len(self.puzzle_population) * float(self.config.settings['selection_proportion']))
            self.parents = self.puzzle_population[:num_selected_parents]

        else:
            # TODO: Perform a k-tournament selection
            pass


    def recombine(self):
        """Breeds λ children from the existing parent population.
        
        TODO
        """
        # TODO: This should be reworked...
        self.children = self.parents
        
    
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
                if tmp_child.place_bulb_randomly():
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
