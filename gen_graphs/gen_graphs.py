#!/usr/bin/env python3

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

log_files = ['../output/random_gen_log.txt', '../output/website_puzzle_log.txt']

for log_file in log_files:
    with open(log_file, 'r') as file:
        file = file.read().split('\n')
        file = [line for line in file[file.index('Run 1'):] if not line == '']
        evals = []
        fitnesses = []
        best_fitnesses = []

        curr_evals = []
        curr_fitnesses = []
        curr_best_fitnesses = []

        curr_run = 1

        for line in file:
            if line[0] == 'R':
                line = line.split()
                run = int(line[1])
                
                if run > curr_run:
                    curr_run = run
                    evals.append(curr_evals)
                    fitnesses.append(curr_fitnesses)
                    best_fitnesses.append(curr_best_fitnesses)

                    curr_evals = []
                    curr_fitnesses = []
                    curr_best_fitnesses = []

            else:
                line = line.split('\t')

                curr_evals.append(int(line[0]))
                curr_fitnesses.append(float(line[1]))
                curr_best_fitnesses.append(float(line[2]))
        
        num_entries = len(evals)
        lists = [evals, fitnesses, best_fitnesses]

        # Average all values together
        # Condense the 2D lists into 1D
        for l in range(len(lists)):
            new = []

            for i in range(len(lists[l][0])):
                summation = 0

                for sub_l in lists[l]:
                    summation += sub_l[i]
                
                new.append(summation / num_entries)
        
            lists[l] = new

        eval_list = lists[0]
        fitness_list = lists[1]
        best_fitness_list = lists[2]

        # Graph the result
        plt.plot(eval_list, fitness_list, '-ro', linewidth = 2.0)
        plt.plot(eval_list, best_fitness_list, '-bo', linewidth = 2.0)

        plt.ylim(0, 1)
        plt.xlim(0, eval_list[-1] + (len(eval_list) * 20))

        red_patch = mpatches.Patch(color='red', label='Average Fitness')
        blue_patch = mpatches.Patch(color='blue', label='Average Best Fitness')
        plt.legend(handles=[blue_patch, red_patch])

        # Include necessary labels
        plt.xlabel('Evaluations')
        plt.ylabel('Fitness\n(ratio of lit cells to all white cells)')

        # Save and close the plot
        plt.savefig(log_file[:log_file.find('log')] + 'graph.png')
        plt.close()
            