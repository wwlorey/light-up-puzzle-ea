#!/usr/bin/env python3

log_file_paths = ['../output/random_gen_log.txt', '../output/website_puzzle_log.txt']

for q in range(len(log_file_paths)):
    with open(log_file_paths[q], 'r') as log_file:
        # Create a list of lines from the log file, disregarding all config parmeters and empty lines
        log_file = log_file.read().split('\n')
        log_file = [line for line in log_file[log_file.index('Run 30'):] if not line == '']

        fits = []

        # Scrape average fitness data from the log file
        for line in log_file:
            if line[0] != 'R':
                # This line has eval and fitness data
                line = line.split('\t')

                # Append the average fitness
                fits.append(float(line[1]))
        

        # Average the average fitnesses together
        avg_fitness = sum(fits) / len(fits)

        print(avg_fitness)
