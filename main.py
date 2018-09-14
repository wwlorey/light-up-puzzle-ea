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


    # Initialize the EA driver and its run variables
    ea_driver = ea_driver_class.EADriver(config)


    # Run the EA
    while ea_driver.run_count <= int(config.settings["num_experiment_runs"]):

        while True:
            ea_driver.evaluate(ea_driver.population, log_run=True)

            ea_driver.select_parents()

            ea_driver.recombine()

            ea_driver.mutate()

            ea_driver.evaluate(ea_driver.children)

            ea_driver.select_for_survival()

            if ea_driver.decide_termination():
                break
            
        ea_driver.init_run_variables()
        ea_driver.increment_run_count()
