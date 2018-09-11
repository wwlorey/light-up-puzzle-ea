import coordinate as coord_class
import copy
import random
import time


class LightUpPuzzle:
    def __init__(self, config, stub_class=False):
        """Initializes the LightUpPuzzle class.

        Where config is a Config object for the light up puzzle problem.

        And where the stub_class parameter is used to signify that a deepcopy is being performed.
        If stub_class is True, only create a "stub class" of this class.
        Otherwise, business as usual.
        """

        def generate_coord_boards():
            """Generates a 2D coordinate board and its transpose.

            These are used when verifying solutions and creating random boards.
            """
            self.coord_board = []

            for x in range(self.num_rows):
                coord_list = []
                for y in range(self.num_cols):
                    coord_list.append(coord_class.Coordinate(x, y))

                self.coord_board.append(coord_list)

            self.transpose_coord_board = [list(l) for l in zip(*self.coord_board)]


        def generate_random_board():
            """Randomly generates a solvable board.

            Solvable boards are generated by iteratively placing black squares (with probability
            dictated by the configuration file) and required bulbs around each square before
            removing the bulbs, leaving a board with at least one solution.

            This function should only be called in __init__
            """
            self.black_squares = {}
            self.bulbs = set([])

            if int(self.config.settings["override_random_board_dimensions"]):
                self.num_rows = int(self.config.settings["override_num_rows"])
                self.num_cols = int(self.config.settings["override_num_cols"])

            else:
                min_dimension = int(self.config.settings["min_random_board_dimension"])
                max_dimension = int(self.config.settings["max_random_board_dimension"])

                self.num_rows = random.randint(min_dimension, max_dimension)
                self.num_cols = random.randint(min_dimension, max_dimension)

            generate_coord_boards()

            # Create a list of shuffled coordinates used in assigning black squares & bulbs
            shuffled_coords = []
            for row in self.coord_board:
                for coord in row:
                    shuffled_coords.append(coord)

            random.shuffle(shuffled_coords)

            # Assign black squares & bulbs to the board
            for coord in shuffled_coords:
                if not coord in self.bulbs: 
                    if random.random() <= float(self.config.settings["black_square_placement_prob"]):
                        adj_coord_list = self.get_adj_coords(coord)
                        num_placed_bulbs = 0

                        # Compute the random max value for this black square
                        max_value = random.choices(list(range(0, int(self.config.settings["adj_value_dont_care"]))), [float(n) for n in self.config.settings["black_square_value_probabilities"].split(',')])[0]

                        # Put a placeholder black square to ensure the maximum amount of bulbs can be placed
                        self.black_squares[coord] = int(self.config.settings["adj_value_dont_care"])

                        # Place bulbs around the square, if allowed
                        for adj_coord in adj_coord_list:
                            if num_placed_bulbs < max_value and self.place_bulb(adj_coord):
                                num_placed_bulbs += 1

                        # Update the real black square value to match the number of adjacent bulbs
                        self.black_squares[coord] = num_placed_bulbs
                    
                    elif random.random() <= float(self.config.settings["bulb_placement_prob"]):
                        # Attempt to place a bulb
                        self.place_bulb(coord)

            if not self.check_valid_solution():
                # Fill non-lit coordinates with black squares of value self.config.settings["adj_value_dont_care"]
                for coord in shuffled_coords:
                    if not coord in self.shined_squares and not coord in self.bulbs and not coord in self.black_squares:
                        self.black_squares[coord] = int(self.config.settings["adj_value_dont_care"])


        def force_adj_bulbs():
            """Places bulbs around black squares where there is only one valid
            bulb placement pattern.
            """
            for black_square in self.black_squares:
                # Get the adjacent coordinates to black_square that are not black
                adj_coords = [s for s in self.get_adj_coords(black_square) if not s in self.black_squares]

                if self.black_squares[black_square] == len(adj_coords):
                    # There is only one way to place bulbs around this square
                    # Place those bulbs
                    for coord in adj_coords:
                        self.place_bulb(coord)


        if stub_class:
            # All allocation will be done by __deepcopy__
            # Return to avoid setting any member variables
            return


        self.black_squares = {}
        self.bulbs = set([])
        self.fitness_ratio = 0
        self.log_str = ''

        self.config = config

        # Seed the random number generator
        self.log_str += 'seed: '
        if int(self.config.settings["use_external_seed"]):
            # Use external seed
            seed_val = float(self.config.settings["seed"])

        else:
            # Default to system time as seed
            seed_val = time.time()

        random.seed(seed_val)
        self.log_str += str(seed_val) + '\n\n'

        if int(self.config.settings["generate_uniform_random_puzzle"]):
            # Generate random initial board state
            generate_random_board()

            # Ensure a valid solution is generated
            while not self.check_valid_solution():
                generate_random_board()

            # Re-initialize the bulb set
            self.bulbs = set([])

            # Use black square adjacency heuristic to force validity
            if int(config.settings['force_validity']):
                force_adj_bulbs()

            self.log_str += 'randomly generated puzzle\n' + \
                            '\tmin_random_board_dimension: ' + str(self.config.settings["min_random_board_dimension"]) + '\n' + \
                            '\tmax_random_board_dimension: ' + str(self.config.settings["max_random_board_dimension"]) + '\n' + \
                            '\toverride_random_board_dimensions: ' + ('True' if int(self.config.settings["override_random_board_dimensions"]) else 'False') + '\n' + \
                            '\toverride_num_rows: ' + str(self.config.settings["override_num_rows"]) + '\n' + \
                            '\toverride_num_cols: ' + str(self.config.settings["override_num_cols"]) + '\n' + \
                            '\tblack_square_value_probabilities: ' + str(self.config.settings["black_square_value_probabilities"]) + '\n' + \
                            '\tblack_square_placement_prob: ' + str(self.config.settings["black_square_placement_prob"]) + '\n\n'

        else:
            # Read initial board state
            with open(self.config.settings["input_file_path"], 'r') as input_file:
                self.log_str += 'puzzle source: ' + self.config.settings["input_file_path"] + '\n\n'

                # Read line 0 (number of columns)
                self.num_cols = int(input_file.readline())

                # Read line 1 (number of rows)
                self.num_rows = int(input_file.readline())

                # Read line 2 to eof (coordinates of black squares and their adjacency values)
                for row in input_file:
                    black_square_data = [int(i) for i in row.split()]
                    self.black_squares[coord_class.Coordinate(black_square_data[1] - 1, black_square_data[0] - 1)] = black_square_data[2]

            # Generate coordinate versions of the board
            generate_coord_boards()


        self.log_str += 'board size (#cols x #rows): ' + str(self.num_cols) + ' x ' + str(self.num_rows) + '\n' + \
                        'enforce_adj_quotas: ' + ('True' if int(self.config.settings["enforce_adj_quotas"]) else 'False') + '\n' + \
                        'adj_value_dont_care: ' + str(self.config.settings["adj_value_dont_care"]) + '\n' + \
                        'max_num_random_bulb_placements: ' + str(self.config.settings["max_num_random_bulb_placements"]) + '\n\n'

        with open(config.settings["log_file_path"], 'a') as log:
            log.write(self.log_str)

        self.num_empty_squares = -1 # This value is updated during solution verification


    def get_random_coord(self):
        """Returns a random coordinate ranging in the space (num_cols, num_rows)."""
        return coord_class.Coordinate(random.randint(0, self.num_rows - 1), random.randint(0, self.num_cols - 1))


    def get_adj_coords(self, coord):
        """Returns a list of coordinates adjacent to coordinate coord"""
        adj_coords = []

        if not coord.x == 0:
            adj_coords.append(coord_class.Coordinate(coord.x - 1, coord.y))

        if not coord.x == self.num_rows - 1:
            adj_coords.append(coord_class.Coordinate(coord.x + 1, coord.y))

        if not coord.y == 0:
            adj_coords.append(coord_class.Coordinate(coord.x, coord.y - 1))

        if not coord.y == self.num_cols - 1:
            adj_coords.append(coord_class.Coordinate(coord.x, coord.y + 1))

        return adj_coords


    def place_bulb(self, coord):
        """Attempts to place a bulb at coord position on the board.

        Returns True on success, False on fail.
        """
        if coord in self.black_squares:
            return False # Can't place a bulb on a black square 

        # Check for cross-shine in the coordinate's row (same x value)
        matching_x_coord_bulbs = [c for c in self.bulbs if c.x == coord.x]
        found_x_delimeter = False if len(matching_x_coord_bulbs) else True

        for bulb_coord in matching_x_coord_bulbs:
            if bulb_coord.x == coord.x:
                min_y = min(bulb_coord.y, coord.y)
                max_y = max(bulb_coord.y, coord.y)

                if max_y - min_y < 2:
                    return False

                for black_coord in [c for c in self.black_squares if c.x == coord.x]:
                    if black_coord.y < max_y and black_coord.y > min_y:
                        found_x_delimeter = True
                        break

        if not found_x_delimeter:
            return False

        # Check for cross-shine in the coordinate's column (same y value)
        matching_y_coord_bulbs = [c for c in self.bulbs if c.y == coord.y]
        found_y_delimeter = False if len(matching_y_coord_bulbs) else True

        for bulb_coord in matching_y_coord_bulbs:
            if bulb_coord.y == coord.y:
                min_x = min(bulb_coord.x, coord.x)
                max_x = max(bulb_coord.x, coord.x)

                if max_x - min_x < 2:
                    return False

                for black_coord in [c for c in self.black_squares if c.y == coord.y]:
                    if black_coord.x < max_x and black_coord.x > min_x:
                        found_y_delimeter = True
                        break

        if not found_y_delimeter:
            return False

        self.bulbs.add(coord)
        return True


    def visualize(self):
        """Prints a string representation of the board.

        '_' Empty white square
        'x' Black square (with 0 <= x <= self.config.settings["adj_value_dont_care"])
        '!' Light bulb
        """
        board = [ [ '_' for col in range(self.num_cols) ] for row in range(self.num_rows) ]

        for coord, value in self.black_squares.items():
            board[coord.x][coord.y] = str(value)

        for coord in self.bulbs:
            board[coord.x][coord.y] = '!'

        for row in board:
            for item in row:
                print(item + ' ', end='')

            print()

        print()


    def get_num_bulbs(self, coord_list):
        """Returns the number of bulbs in coord_list."""
        num_adj_bulbs = 0

        for coord in coord_list:
            if coord in self.bulbs:
                num_adj_bulbs += 1

        return num_adj_bulbs


    def get_num_black_squares(self, coord_list):
        """Returns the number of black squares in coord_list."""
        num_adj_black_squares = 0  

        for coord in coord_list:
            if coord in self.black_squares:
                num_adj_black_squares += 1

        return num_adj_black_squares 


    def check_valid_solution(self):
        """Checks to see if the board is valid.

        Returns True if the following conditions are met:
        1. No bulbs shine on eachother. (guaranteed by place_bulb() function)
        2. Every black square has the required adjacent bulbs. (can be disabled using config file setting)
        """
        # Create and populate set of shined squares
        self.shined_squares = set([])

        for bulb_coord in self.bulbs:
            # Create a list of adjacency lists - used for determining where the bulb shines
            adj_coord_lists = []

            adj_coord_lists.append(self.coord_board[bulb_coord.x][:bulb_coord.y][::-1])           # Row from this column to the left
            adj_coord_lists.append(self.coord_board[bulb_coord.x][bulb_coord.y + 1:])             # Row from this column to the right
            adj_coord_lists.append(self.transpose_coord_board[bulb_coord.y][:bulb_coord.x][::-1]) # Column from this row up
            adj_coord_lists.append(self.transpose_coord_board[bulb_coord.y][bulb_coord.x + 1:])   # Column from this row down

            for coord_list in adj_coord_lists:
                for coord in coord_list:
                    if coord in self.black_squares:
                        break # Shine cannot propagate any further
                    elif coord in self.bulbs:
                        return False # Redundant check for bulb on bulb shining
                    else:
                        self.shined_squares.add(coord)

        # Ensure bulbs count as shined squares
        for bulb_coord in self.bulbs:
            self.shined_squares.add(bulb_coord)

        # Check black square conditions
        if int(self.config.settings["enforce_adj_quotas"]):
            for coord, adj_value in self.black_squares.items():
                if adj_value < int(self.config.settings["adj_value_dont_care"]) and self.get_num_bulbs(self.get_adj_coords(coord)) != adj_value:
                    # Nullify the fitness of this board
                    self.shined_squares = set([])
                    return False

        self.fitness_ratio = self.get_fitness() / (self.num_rows * self.num_cols)

        return True


    def place_bulb_randomly(self):
        """Attempts to put a bulb randomly on the board in a valid location.

        Stops trying to put a bulb after max_num_random_bulb_placements tries.
        Returns True if successful, False otherwise.
        """
        coord = self.get_random_coord()
        count = 0

        while count < int(self.config.settings["max_num_random_bulb_placements"]) and not self.place_bulb(coord):
            coord = self.get_random_coord()
            count += 1

        if count < int(self.config.settings["max_num_random_bulb_placements"]):
            return True

        return False


    def write_to_soln_file(self):
        """Writes problem information to the solution file specified in the configuration file."""
        with open(self.config.settings["soln_file_path"], 'w') as soln_file:
            soln_file.write(str(self.num_cols) + '\n')
            soln_file.write(str(self.num_rows) + '\n')

            for coord in sorted(self.black_squares):
                soln_file.write(str(coord.y) + ' ' + str(coord.x) + ' ' + str(self.black_squares[coord]) + '\n')

            soln_file.write(str(len(self.shined_squares)) + '\n')

            for coord in sorted(self.bulbs):
                soln_file.write(str(coord.y) + ' ' + str(coord.x) + '\n')

            soln_file.write('\n')


    def get_fitness(self):
        """Returns the fitness of the puzzle.

        Fitness is defined as the number of lit squares on the board.
        """
        return len(self.shined_squares)


    def clear_board(self):
        """Clears all bulbs from the board."""
        self.bulbs = set([])

    
    def __deepcopy__(self, memo):
        other = LightUpPuzzle(self.config, stub_class=True)

        other.black_squares = {}
        for s in self.black_squares:
            other.black_squares[s] = self.black_squares[s]

        other.bulbs = set([])
        for b in self.bulbs:
            other.bulbs.add(b)

        other.config = self.config
        other.coord_board = copy.deepcopy(self.coord_board)
        other.fitness_ratio = copy.deepcopy(self.fitness_ratio)
        other.log_str = copy.deepcopy(self.log_str)
        other.num_cols = copy.deepcopy(self.num_cols)
        other.num_empty_squares = copy.deepcopy(self.num_empty_squares)
        other.num_rows = copy.deepcopy(self.num_rows)
        other.shined_squares = copy.deepcopy(self.shined_squares)
        other.transpose_coord_board = copy.deepcopy(self.transpose_coord_board)

        memo = other

        return other
