#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

log_file_paths = ['../output/random_gen_log.txt', '../output/website_puzzle_log.txt']
graph_titles = ['Randomly Generated Puzzles', 'Provided Puzzle']

for q in range(len(log_file_paths)):
    with open(log_file_paths[q], 'r') as log_file:
        # Create a list of lines from the log file, disregarding all config parmeters and empty lines
        log_file = log_file.read().split('\n')
        log_file = [line for line in log_file[log_file.index('Run 1'):] if not line == '']

        evals = []
        curr_evals = []
        fits = []
        curr_fits = []
        best_fits = []
        curr_best_fits = []

        curr_run = 1

        # Segregate data from log file into appropriate lists
        for line in log_file:
            if line[0] == 'R':
                # This line has a run update
                line = line.split()
                run = int(line[1])
                
                if run > curr_run:
                    # A new run has been encountered. Append the curr_* lists
                    curr_run = run
                    evals.append(curr_evals)
                    fits.append(curr_fits)
                    best_fits.append(curr_best_fits)

                    # Reset the curr_* lists
                    curr_evals = []
                    curr_fits = []
                    curr_best_fits = []

            else:
                # This line has eval and fitness data
                line = line.split('\t')

                # Append to the curr_* lists
                curr_evals.append(int(line[0]))
                curr_fits.append(float(line[1]))
                curr_best_fits.append(float(line[2]))
        

        num_entries = len(evals)
        experiment_data = [evals, fits, best_fits]

        # Average all values together
        # Condense the 2D lists into 1D
        for k in range(len(experiment_data)):
            avg = []

            for i in range(len(experiment_data[k][0])):
                summation = 0

                # Sum all data items in the slice of experiment data
                for data_item in experiment_data[k]:
                    summation += data_item[i]
                
                # Average the data
                avg.append(summation / num_entries)
        
            # Replace the original data with the averaged version
            experiment_data[k] = avg


        # Reassign list names for clarity
        evals = experiment_data[0]
        fits = experiment_data[1]
        best_fits = experiment_data[2]

        # Plot the results
        plt.plot(evals, fits, '-ro', linewidth = 2.0)
        plt.plot(evals, best_fits, '-bo', linewidth = 2.0)

        plt.ylim(0, 1)
        plt.xlim(0, evals[-1] + (len(evals) * 20))

        red_patch = mpatches.Patch(color='red', label='Average Local Fitness')
        blue_patch = mpatches.Patch(color='blue', label='Local Best Fitness')
        plt.legend(handles=[blue_patch, red_patch])

        plt.title('Evaluations versus Average Local Fitness and Evaluations versus Local\nBest Fitness for ' + graph_titles[q] + ', Averaged Over All Runs')

        # Include necessary labels
        plt.xlabel('Evaluations')
        plt.ylabel('Fitness\n(ratio of lit white cells to total number of white cells)')

        # Save and close the plot
        plt.savefig(log_file_paths[q][:log_file_paths[q].find('log')] + 'graph.png')
        plt.close()
            