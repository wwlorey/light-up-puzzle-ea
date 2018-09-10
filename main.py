#!/usr/bin/env python3

import sys
import light_up_puzzle as puzzle_class
import light_up_puzzle_config as config_class


if __name__ == '__main__':

    # Command line argument processing
    if len(sys.argv) == 1:
        # No config file provided, use default
        config_file = 'config/default.cfg'
  
    else:
        # Use the provided config file
        config_file = sys.argv[1]


    # Configuration setup
    config = config_class.LightUpPuzzleConfig(config_file)


    # Open the log file and write the header
    with open(config.settings["log_file_path"], 'w') as log:
        log.write('Result Log\n\n')


    # Variable initialization
    max_global_fitness = 0
    fitness = 0

    with open(config.settings["log_file_path"], 'w') as log:
        puzzle = puzzle_class.LightUpPuzzle(config) 


    # Run the EA
    for run_count in range(1, int(config.settings["num_experiment_runs"]) + 1):
        max_run_fitness = 0
        eval_count = 1

        for eval_count in range(1, int(config.settings["num_fitness_evaluations"]) + 1):
            print("Run: %i\tEval count: %i" % (run_count, eval_count))

            # TODO: Place bulbs to fill an entire board here
            # TODO: Run EA logic here

            if puzzle.check_valid_solution():
                fitness = puzzle.get_fitness()

                if fitness > max_run_fitness:
                    max_run_fitness = fitness

                    # This is the best fitness we've found for this run
                    # Write it to the log file
                    log.write("Run %i\n" % run_count)
                    log.write("%i\t%i\n\n" % (eval_count, fitness))
            
                if fitness > max_global_fitness:
                    max_global_fitness = fitness

                    # This is the best fitness we've found overall
                    # Write it to the solution file
                    puzzle.write_to_soln_file()