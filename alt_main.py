#!/usr/bin/env python3

import args as args_class
import config as config_class
import ea_driver as ea_driver_class


if __name__ == '__main__':

    # Process command line arguments
    script_args = args_class.Arguments(1, ['config/default.cfg'])
    config_file = script_args.get_args()[0]


    # Setup configuration
    config = config_class.Config(config_file)


    # Initialize the EA driver
    ea_driver = ea_driver_class.EADriver(config)


    # Testing
    ea_driver.evaluate()
    for puzzle in ea_driver.puzzle_population:
        puzzle.visualize()
        print(ea_driver.puzzle_population[puzzle])


    # Run the EA
    '''
    for run_count in range(1, int(config.settings["num_experiment_runs"]) + 1):
        ea_driver.init_run_variables()

        for eval_count in range(1, int(config.settings["num_fitness_evaluations"]) + 1):
            print("Run: %i\tEval count: %i" % (run_count, eval_count))

            ea_driver.evaluate()

            ea_driver.select_parents()

            ea_driver.recombine()

            ea_driver.mutate()

            ea_driver.evaluate_offspring()

            ea_driver.select_for_survival()

            if ea_driver.decide_termination():
                break
    '''