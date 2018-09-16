#!/usr/bin/env python3

import ea.ea_driver as ea_driver_class
import util.config as config_class
import util.args as args_class


if __name__ == '__main__':

    # Process command line arguments
    args = args_class.Arguments(1, ['config/default.cfg'])
    config_file = args.get_args()[0]


    # Setup configuration
    config = config_class.Config(config_file)

    # Get configuration parameters
    config = config_class.LightUpPuzzleConfig(config_file)


    for run_count in range(1, config.settings["num_experiment_runs"] + 1):
      # Create a new puzzle instance for this run
      puzzle = puzzle_class.LightUpPuzzle(config) 
      max_run_fitness = 0
      fitness = 0
      eval_count = 1

      # Open the log file
      with open(config.settings["log_file_path"], 'a') as log:

        for eval_count in range(1, config.settings["num_fitness_evaluations"] + 1):
          print("Run: %i\tEval count: %i" % (run_count, eval_count))

          if not puzzle.place_bulb_randomly():
            # There are no more options for placing bulbs. Clear the board of bulbs
            puzzle.clear_board()

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
        
        log.write('---------------------------\n\n')
