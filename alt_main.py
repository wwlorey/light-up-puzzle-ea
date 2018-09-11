#!/usr/bin/env python3

import args as args_class
import config as config_class
import ea_driver as ea_driver_class


if __name__ == '__main__':

    # Process command line arguments
    args = args_class.Arguments(1, ['config/default.cfg'])
    config_file = args.get_args()[0]


    # Setup configuration
    config = config_class.Config(config_file)


    # Initialize the EA driver
    ea_driver = ea_driver_class.EADriver(config)


    # Testing
    ea_driver.evaluate(ea_driver.population)
    ea_driver.select_parents()
    ea_driver.recombine()


    for child in ea_driver.children:
        for coord in child.bulbs:
            print(coord)
    
        print(child.fitness_ratio)
        print('\n\n')


    for genotype in ea_driver.population:
        ea_driver.phenotype.visualize(genotype.bulbs)
        print(genotype.fitness_ratio)
        print(genotype.fitness)
    

    # Run the EA
    '''
    for run_count in range(1, int(config.settings["num_experiment_runs"]) + 1):
        ea_driver.init_run_variables()

        for eval_count in range(1, int(config.settings["num_fitness_evaluations"]) + 1):
            print("Run: %i\tEval count: %i" % (run_count, eval_count))

            ea_driver.evaluate(self.puzzle_population)

            ea_driver.select_parents()

            ea_driver.recombine()

            ea_driver.mutate()

            ea_driver.evaluate(self.children)

            ea_driver.select_for_survival()

            if ea_driver.decide_termination():
                break
    '''