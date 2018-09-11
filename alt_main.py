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

    for genotype in ea_driver.population:
        ea_driver.phenotype.visualize(genotype.bulbs)
        print(genotype.fitness_ratio)
        print(genotype.fitness)

    ea_driver.select_parents()
    ea_driver.recombine()
    ea_driver.mutate()
    ea_driver.evaluate(ea_driver.children)
    ea_driver.select_for_survival()

    print('\n\n\n')

    for genotype in ea_driver.population:
        ea_driver.phenotype.visualize(genotype.bulbs)
        print(genotype.fitness_ratio)
        print(genotype.fitness)


    # Run the EA
    while ea_driver.run_count <= int(config.settings["num_experiment_runs"]):
        ea_driver.init_run_variables()

        while ea_driver.eval_count <= int(config.settings['num_fitness_evaluations']):
            ea_driver.print_update()

            ea_driver.evaluate(ea_driver.population, log_run=True)

            ea_driver.select_parents()

            ea_driver.recombine()

            ea_driver.mutate()

            ea_driver.evaluate(ea_driver.children)

            ea_driver.select_for_survival()

            # if ea_driver.decide_termination():
            #     break
            
        ea_driver.increment_run_count()

