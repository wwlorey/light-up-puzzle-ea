#!/usr/bin/env python3

import copy
import ea.ea_driver as ea_driver_class
import ea.genotype as genotype_class
import util.args as args_class
import util.config as config_class


if __name__ == '__main__':

    # Process command line arguments
    args = args_class.Arguments(1, ['config/default.cfg'])
    config_file = args.get_args()[0]


    # Setup configuration
    config = config_class.Config(config_file)


    # Initialize the EA driver and its run variables
    # Even though it will be used in performing a random search
    ea_driver = ea_driver_class.EADriver(config)


    # Perform the random search
    while ea_driver.run_count <= int(config.settings["num_experiment_runs"]):
        while ea_driver.eval_count <= int(config.settings['num_fitness_evaluations']):
            ea_driver.eval_count += 1

            genotype = genotype_class.Genotype()

            # Place bulbs until num_bulb_placement_failures failures are reached
            failure_count = 0
            while failure_count < int(ea_driver.config.settings['num_bulb_placement_failures']):
                if not ea_driver.phenotype.place_bulb_randomly(genotype.bulbs):
                    failure_count += 1
            
            ea_driver.phenotype.check_valid_solution(genotype.bulbs)
            genotype.fitness = ea_driver.phenotype.get_fitness()
            genotype.fitness_ratio = genotype.fitness / (ea_driver.phenotype.num_rows * ea_driver.phenotype.num_cols - len(ea_driver.phenotype.black_squares))
            
            if ea_driver.best_fit_local_genotype.fitness_ratio < genotype.fitness_ratio:
                ea_driver.best_fit_local_genotype = copy.deepcopy(genotype)

            ea_driver.log.write_run_header(ea_driver.run_count)
            ea_driver.log.write_run_data(ea_driver.eval_count, 0, ea_driver.best_fit_local_genotype.fitness_ratio)

        ea_driver.init_run_variables()
        ea_driver.increment_run_count()
          