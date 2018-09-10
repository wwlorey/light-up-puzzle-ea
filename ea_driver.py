import light_up_puzzle as puzzle_class


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


        # Open the log file and write the header
        # TODO: Wrap this in a log class
        with open(config.settings['log_file_path'], 'w') as log:
            log.write('Result Log\n\n')
        
        self.config = config
        self.population_size = int(config.settings['µ'])
        self.offspring_pool_size = int(config.settings['λ'])

        # key: light up puzzle, value: (num lit cells) / (total num cells)
        # Note: the key is initialized to zero to begin with
        self.puzzle_population = {}
        for _ in range(self.population_size):
            self.puzzle_population[puzzle_class.LightUpPuzzle(config)] = 0
        
        init_experiment_variables()


    def init_run_variables(self):
        """Initializes run specific variables.

        This function should be called at the top of each run.
        """
        self.max_run_fitness = 0
        self.eval_count = 1
    
    
    def evaluate(self):
        """TODO""" 
        for puzzle in self.puzzle_population:
            puzzle.check_valid_solution()
            self.puzzle_population[puzzle] = puzzle.get_fitness() / (puzzle.num_rows * puzzle.num_cols)


    def select_parents(self):
        """Chooses which parents survive from the population.

        TODO
        """
        


    def recombine(self):
        """Breeds λ children from the existing parent population.
        
        TODO
        """
        pass
        
    
    def mutate(self):
        """Performs mutation on each child in the child population.
        
        TODO
        """
        pass


    def evaluate_offspring(self):
        """TODO"""
        pass


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
