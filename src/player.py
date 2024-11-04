import json
import os
import random
import hashlib
import copy
import numpy as np
import math
import pygame
import time
from abc import ABC, abstractmethod

from state import State
from typing import Optional
from board import Board


class Player(ABC):  
    """Base class for the player"""
    def __init__(self, state):
        self.state = state  # State representation of the game
        self.directory = 'PLAYERS'
        

    def info(self,state):
        """Used for q-learning player class"""
        pass


    def load_stats(self):
        """Load the player statistics from a json file"""
        stats = None
        with open(f'{self.directory}/{self.name}.json', 'r', encoding='utf-8') as f:
            js = json.load(f)
            self.name = js['name']
            self.wins = js['wins']
            self.loses = js['loses']


    def save_stats(self):
        """Save the player statistics to a json file"""
        with open(f'{self.directory}/{self.name}.json', 'w', encoding='utf-8') as f:
            json.dump(self.parse_stats(), f)


    def parse_stats(self):
        """Parse the player statistics to a json string"""
        stats_string = {
            "name": self.name,
            "wins": self.wins,
            "loses": self.loses
        }
        return stats_string


    def md5_id(self):
        """Generate the MD5 id of the player"""
        return hashlib.md5(self.name.encode()).hexdigest()


    def make_movement(self):
        """Method which update the current state of the game."""
        current_position, new_position = self._next_movement()
        self.state.make_movement(current_position, new_position)


    @abstractmethod
    def _next_movement(self):
       """Method which returns the following following position that the algorithm has chosen ."""


class PlayerReplay(Player):  # ONLY USED FOR REPLAYS (NO STATS NO WINS NO LOSES)
    def __init__(self, name, state):
        super().__init__(state)
        self.name = name  # Name loaded from replay file


    def _next_movement(self):
        """Do nothing. This exists to make python stop complaining about the abstract method not being there"""
        pass


class PlayerHuman(Player):
    def __init__(self, state, name):
        super().__init__(state)
        self.name = name  # Unique player name
        self.wins = 0
        self.loses = 0

        if not os.path.exists(self.directory):  # Create the players directory
            os.makedirs(self.directory)
        try:
            self.load_stats()  # Load the player statistics if the player exists
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
            self.save_stats()  # Create the player statistics file if it doesn't exist

        
    def _next_movement(self):
        """Make a movement to a specific postion"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    move = self.state.handle_click(pos)
                    if move is not None:
                        self.state.selec_piece = None
                        return move
        
        
class PlayerRandom(Player):  # USE CPU 0 AS NAME IN SERVER
    def __init__(self, state, name=None):
        super().__init__(state)
        self.name = name
        self.wins = 0
        self.loses = 0

        if not os.path.exists(self.directory):  # Create the players directory
            os.makedirs(self.directory)
        try:
            self.load_stats()  # Load the player statistics if the player exists
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
            self.save_stats()  # Create the player statistics file if it doesn't exist


    def _next_movement(self):
        """Make a random movement from the list of possible movements. Returns the current postion and the new position"""
        selected_movement = random.choice(self.state.mov_valid_list())
        while (len(selected_movement[1]) == 0 ):
            selected_movement = random.choice(self.state.mov_valid_list())
        current_position = selected_movement[0]
        new_position = random.choice(selected_movement[1])
        return current_position, new_position


class PlayerMiniMax(Player):  # USE CPU 1 AS NAME IN SERVER
    def __init__(self, state, max_depth, name):
        super().__init__(state)
        self.name = name
        self.wins = 0
        self.loses = 0
        self.max_depth = max_depth

        if not os.path.exists(self.directory):  # Create the players directory
            os.makedirs(self.directory)
        try:
            self.load_stats()  # Load the player statistics if the player exists
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
            self.save_stats()  # Create the player statistics file if it doesn't exist

    def evaluate_state(self, current_state): 
        """Evaluates the value of the sate of a game for the current player."""
        # The heuristic to evaluate the values is followed is for the remaining pieces
        if current_state.is_finished():  # If the game is finished
            if not current_state.is_tied():  # If the game is not tied
                if current_state.gamer == self.state.gamer:  # If the current player is the winner
                    return 1
                return -1
            return 0
        num_blacks = len(current_state.blacks)
        num_whites = len(current_state.whites) + 1
        diff_pieces = num_blacks - num_whites 
        if current_state.gamer == 0: 
            return diff_pieces
        else: 
            return -diff_pieces 

    
    def max_value(self, current_state, alpha, beta, depth): 
        """Computes value for player that is maximizing"""
        if depth == 0 or current_state.is_finished():
            return self.evaluate_state(current_state)  # Evaluate the state of the game
        
        val = float("-inf")  # Negative infinity
        for _ ,successor in current_state.generate_successors():  # For each successor of the current state
            val = max(val, self.min_value(successor, alpha, beta, depth - 1))
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return val


    def min_value(self, current_state, alpha, beta, depth): 
        """Computes value for player that is minimizing"""
        if depth == 0 or current_state.is_finished():  
            return self.evaluate_state(current_state)  # Evaluate the state of the game

        val = float("inf")
        for _ ,successor in current_state.generate_successors():  # For each successor of the current state
            val = min(val, self.max_value(successor, alpha, beta, depth - 1))
            beta = min(beta, val)
            if alpha >= beta: 
                break   
        return val


    def search_alpha_beta(self):
        """Make a movement using the minimax algorithm (using alpha-beta pruning)"""
        if self.state.is_finished(): 
            return None
        
        best_val = float("-inf")
        beta = float("inf")
        best_positions = None
        
        for pos_tuple, successor in self.state.generate_successors():  # For each successor of the current state
            val = self.min_value(successor, best_val, beta, self.max_depth)  # Compute the value of the successor
            if val > best_val:  # If the value is better than the current best value
                best_val = val
                best_positions = pos_tuple
        return best_positions
    

    def _next_movement(self):
        current_pos, new_pos = self.search_alpha_beta()
        return current_pos, new_pos


class MonteCarloTreeNode: 
    """Class in charge of defining a Montecarlo Tree Node"""
    def __init__(self, state, parent = None, parent_position = None, state_position = None) -> None:
        self.state = state # The state of the current node
        self.parent = parent # Parent of the node 
        self.parent_position = parent_position # current_position for the movement
        self.state_position = state_position # new_position
        self.visits = 0
        self.accumulated_rewards = 0 # This is for the wins and the losses. It could be added two parameters instead
        self.expanded_children = [] # Represents all the possible actions of the current node 
        self.sucessors_iterator = self.state.generate_successors()
    
    
    def expand_node(self):
        """Expand a node and returns its child"""
        next_successor = next(self.sucessors_iterator, None)  # Get the next successor
        if next_successor is None:  # If there are no more successors
            return None  # Return None
        positions_tuple, successor = next_successor # Get the positions tuple and the successor
        child_node = MonteCarloTreeNode(successor, self, positions_tuple[0], positions_tuple[1])  # Create a new node
        self.expanded_children.append(child_node)  # Add the new node to the expanded children
        return child_node
        

    def calculate_uct_value(self):
        """Calculate the upper confidence bound for trees"""
        if self.parent is None:
            raise ValueError("Not possible to obtain the evaluation of node")
        return self.average_win_ratio() + 2/math.sqrt(2) * math.sqrt((2*math.log(self.parent.visits,2))/self.visits)
        

    def average_win_ratio(self):
        """Returns the average reward of a node (C).This corresponds to (accumulated_rewards)/(visits)"""
        if self.visits != 0:
            return self.accumulated_rewards / self.visits 
    

    def is_terminal(self):
        """Check whether it is a terminal state in where the game is finished"""
        return self.state.is_finished()


    def best_child(self):
        """Returns the child node with the highest uct value"""
        best_child = None
        best_uct_value = float('-inf')
    
        for child_node in self.expanded_children:  # For each child node
            uct_value = child_node.calculate_uct_value()  # Calculate the UCT value
            if uct_value > best_uct_value:  # If the UCT value is better than the current best UCT value
                best_uct_value = uct_value
                best_child = child_node
        return best_child


class MonteCarloTreeSearch:
    """ Class in charge of traversing the tree"""
    def __init__(self, state):     
        self.state = state
        self.root_node = MonteCarloTreeNode(self.state)  # Create the root node
        self.current_gamer = self.root_node.state.gamer  # Get the current gamer
    

    def no_children(self):
        """Returns true if the root node does not have any children"""
        return len(self.root_node.expanded_children) == 0
    

    def best_node(self):
        """Returns node with highest highest average value. Run iterations called once so that it has a child """
        if self.no_children():
            raise ValueError("The root does not have any children")
    
        max_child = None
        max_average_reward = float('-inf')

        for child in self.root_node.expanded_children:  # For each child node
            average_reward = child.average_win_ratio()
            if average_reward > max_average_reward:  # If the average reward is better than the current best average reward
                max_average_reward = average_reward
                max_child = child
        return max_child


    def simulate_iterations(self): 
        """Steps that must be followed for the MonteCarlo algorithm to add a node to the tree""" 
        chosen_node = self.tree_policy()  # Choose the node that is going to be expanded
        chosen_node_state = chosen_node.state
        reward = self.default_policy(copy.deepcopy(chosen_node_state), self.current_gamer)  # Simulate a game to get the reward
        self.backpropagate_results(chosen_node, reward)  


    def tree_policy(self): 
        """Chooses the node that is going to be expanded"""
        current_montecarlo_node = self.root_node
        while not current_montecarlo_node.is_terminal():  # While the node is not terminal
            expanded_child = current_montecarlo_node.expand_node()  # Expand the node
            if expanded_child is not None: 
                return expanded_child
            current_montecarlo_node = current_montecarlo_node.best_child()
        return current_montecarlo_node
    

    @staticmethod
    def default_policy(state, current_gamer):
        """It randomly simulate a game and return a reward depending on the result"""
        # Carry out random simulations
        # Check that the state that has been passed is updated
        random_player = PlayerRandom(state) # Taking into account random simulations
        while not state.is_finished():  # While the game is not finished
            random_player.make_movement()  # Make a random movement
        if state.is_tied():  # If the game is tied
            return 0
        if state.gamer == current_gamer:
            return 1  # Current gamer wins. It is added one to the accumulated_rewards
        return -1 # Current gamer losses. It is subtracted one to the accumulated_rewards 
   

    def backpropagate_results(self, montecarlo_node, reward):
        """Propagate reward obtained for node until root is reached."""
        while montecarlo_node is not None: 
            montecarlo_node.visits += 1 # add one to the number of total visists
            montecarlo_node.accumulated_rewards += reward # Add the reward to the corresponding node
            montecarlo_node = montecarlo_node.parent # Update the current node to its parent
               

class PlayerMontecarlo(Player):  # USE CPU 2 AS NAME IN SERVER
    def __init__(self, state, name, number_iterations):
        super().__init__(state)
        self.name = name
        self.montecarlo_tree = None
        self.number_iterations = number_iterations
        self.wins = 0
        self.loses = 0

        if not os.path.exists(self.directory):  # Create the players directory
            os.makedirs(self.directory)
        try:
            self.load_stats()  # Load the player statistics if the player exists
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
            self.save_stats() # Create the player statistics file if it doesn't exist


    def _next_movement(self):
        """Make a movement using the Monte Carlo Tree Search algorithm
        """
        self.montecarlo_tree = MonteCarloTreeSearch(self.state)

        for _ in range(self.number_iterations):  
            self.montecarlo_tree.simulate_iterations()
            
        return self.montecarlo_tree.best_node().parent_position, self.montecarlo_tree.best_node().state_position


class PlayerMiniRandom(Player):  # USE CPU 5 AS NAME IN SERVER
    def __init__(self, state, max_depth, name):
        super().__init__(state)
        self.name = name
        self.wins = 0
        self.loses = 0
        self.max_depth = max_depth
        self.start_time = time.time()
        self.max_time = 5

        if not os.path.exists(self.directory):  # Create the players directory
            os.makedirs(self.directory)
        try:
            self.load_stats()  # Load the player statistics if the player exists
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
            self.save_stats()  # Create the player statistics file if it doesn't exist


    def evaluate_state(self, current_state): 
        """Evaluates the value of the sate of a game for the current player"""
        # The heuristic to evaluate the values is followed is for the remaining pieces
        if current_state.is_finished():
            if not current_state.is_tied():
                if current_state.gamer == self.state.gamer:
                    return 1
                return -1
        if self.state.gamer == 0:
            return 0.5  
        return 0
    

    def max_value(self, current_state, alpha, beta, depth): 
        """Computes value for player that is maximizing"""
        if depth == 0:
            return self.evaluate_state(current_state)
        
        if current_state.is_finished():  # If the game is finished
            return self.evaluate_state(current_state)
        
        val = float("-inf")
        for _ ,successor in current_state.generate_successors():  # For each successor of the current state
            val = (max(val, self.min_value(successor, alpha, beta, depth - 1)))
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return val / 2
    

    def min_value(self, current_state, alpha, beta, depth): 
        """Computes value for player that is minimizing"""
        if depth == 0:
            return self.evaluate_state(current_state)
        
        if current_state.is_finished():  # If the game is finished
            return self.evaluate_state(current_state)
        
        val = float("inf")
        for _ ,successor in current_state.generate_successors():  # For each successor of the current state
            val = (min(val, self.max_value(successor, alpha, beta, depth - 1)))
            beta = min(beta, val)
            if alpha >= beta: 
                break   
        return val / 2


    def search_alpha_beta(self):
        """Make a movement using the minimax algorithm (using alpha-beta pruning)"""
        if self.state.is_finished(): 
            return None
        
        best_val = float("-inf")
        beta = float("inf")
        best_positions = None
        
        succesors = self.state.generate_successors()
        succesors_list = list(succesors)
        succesors_list_cero = []
        succesors_list_mayor_cero = []
        for pos_tuple, successor in succesors_list:  # For each successor of the current state
            val = self.min_value(successor, best_val, beta, self.max_depth)  # Value is the minimum value of the successor
            if val > best_val:  # If the value is better than the current best value
                best_val = val
                best_positions = pos_tuple
                succesors_list_mayor_cero = []
            if val == 0:  # If the value is 0, we can choose a random movement (not negative)
                succesors_list_cero.append(pos_tuple)
            if val == best_val:  # If the value is the same as the best value
                succesors_list_mayor_cero.append(pos_tuple)

        if best_positions is None or best_val == 0:
            best_positions = random.choice(succesors_list_cero)  
            return best_positions
        if succesors_list_mayor_cero != []:  # If there are movements with a value greater than 0
            best_positions = random.choice(succesors_list_mayor_cero)  
            return best_positions
        return best_positions


    def _next_movement(self):
        """Make a movement using the minimax algorithm (using alpha-beta pruning)"""
        self.start_time = time.time()
        current_pos, new_pos = self.search_alpha_beta()
        return current_pos, new_pos


class PlayerQLearningWhite(Player): # cpu 4
    def __init__(self, state, name, learning_rate=0.4, discount_factor=1, exploration_rate=0.9):
        super().__init__(state)
        self.name = name
        self.wins = 0
        self.loses = 0
        self.learning_rate = learning_rate 
        self.discount_factor = discount_factor 
        self.exploration_rate = exploration_rate
        self.q_table = {} # Q table, which maps states to actions and their respective Q values
        self.previous_state_key = None  # previous state of the game
        self.previous_index = None  # Index of the action taken in the previous state
        self.previous_subindex = None  # Subndex of the action taken in the previous state
        self.next_state_key = None  # Next state of the game
        self.iteraciones = 0 # Number of iterations

        try:
            self.load_stats()  # Load the player statistics if the player exists
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
            self.save_stats()  # Create the player statistics file if it doesn't exist
        try:
            self.load_q_table()  # Cargar la tabla Q si existe
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
            print("No se pudo cargar la tabla Q")
            self.save_q_table()  # Crear la tabla Q si no existe

    def info(self,state):
        """
        The player receives the result of the game and evaluates the previous state on 
        which he moved based on the finalresult and updates the Q table
        """
        if (state.is_tied()):
            reward = -50
        else:
            reward = -100
        self.update_q_table( reward)
        self.save_q_table()


    def load_q_table(self):
        with open(f'q_table/q_tableWhites2Prof.json', 'r', encoding='utf-8') as f:
            self.q_table = json.load(f)


    def save_q_table(self):
        with open(f'q_table/q_tableWhites2Prof.json', 'w', encoding='utf-8') as f:
            json.dump(self.q_table, f)


    def _next_movement(self):
        current_state_key = str(self.state.ID)

        if current_state_key not in self.q_table:
            self.q_table[current_state_key] = [(i, [0]*len(move[1])) for i, move in enumerate(self.state.mov_valid_list())]
            # If the king id in a edge square, the value of the escape square is set to 100
            for i in range(len(self.state.mov_valid_list())):
                    if (self.state.mov_valid_list()[i][0] == self.state.king):
                        for j in range(len(self.state.mov_valid_list()[i][1])):
                            if (self.state.mov_valid_list()[i][1][j] in Board.square_escapes):
                                self.q_table[current_state_key][i][1][j] = 100

        valid_moves = self.state.mov_valid_list()

        if not valid_moves:
            raise Exception("No valid moves available")

        if random.random() < self.exploration_rate:
            # Exploración: elegir una acción aleatoria
            action_index = random.randint(0, len(valid_moves) - 1)
            current_position, possible_positions = valid_moves[action_index]
            while len(possible_positions) == 0:
                action_index = random.randint(0, len(valid_moves) - 1)
                current_position, possible_positions = valid_moves[action_index]

            # Select a random position among the possible positions
            new_position = random.choice(possible_positions)
            self.previous_subindex = possible_positions.index(new_position)
        else:
            # Select the action with the highest Q value among the possible actions
            q_values = [np.max(q_values) for _, q_values in self.q_table[current_state_key] if len(q_values) > 0]
            if not q_values:
                action_index = random.randint(0, len(valid_moves) - 1)
            else:
                action_index = np.argmax(q_values)

            current_position, possible_positions = valid_moves[action_index]
            while len(possible_positions) == 0:
                action_index = random.randint(0, len(valid_moves) - 1)
                current_position, possible_positions = valid_moves[action_index]

            q_values = self.q_table[current_state_key][action_index][1]
            self.previous_subindex = np.argmax(q_values)

            new_position = possible_positions[self.previous_subindex]

        self.previous_index = action_index
        return current_position, new_position


    def update_q_table(self,reward):
        # learning from experience
        state_key = self.previous_state_key
        next_state_key = self.next_state_key
        action_index = self.previous_index

        current_q_value = self.q_table[state_key][action_index][1][self.previous_subindex]
        next_max_q_value = max([np.max(q_values) for _, q_values in self.q_table[next_state_key]]) if next_state_key in self.q_table else 0
        updated_q_value = current_q_value + self.learning_rate * (reward + self.discount_factor * next_max_q_value - current_q_value)
        self.q_table[state_key][action_index][1][self.previous_subindex] = updated_q_value


    def make_movement(self):
        """Make the q-learning movement"""
        self.previous_state_key = str(self.state.ID)
        current_position, new_position = self._next_movement()
        self.state.make_movement(current_position, new_position)
        self.next_state_key = str(self.state.ID)
        self.iteraciones += 1
        fin = False

        if self.state.is_finished() and not (self.state.is_tied()):  # If the game is finished and there is a winner
            if self.iteraciones >= 50:  # If the number of iterations is greater than 50
                reward = 50  # Give a reward of 50
            elif self.iteraciones >= 30 and self.iteraciones < 50:  # If the number of iterations is greater than 30 and less than 50
                reward = 80  # Give a reward of 80
            elif self.iteraciones < 30 and self.iteraciones >= 15:  # If the number of iterations is less than 30 and greater than 15
                reward = 100  # Give a reward of 100
            elif self.iteraciones < 15 and self.iteraciones >= 5:  # If the number of iterations is less than 15 and greater than 5
                reward = 150  # Give a reward of 150
            elif self.iteraciones < 5:  # If the number of iterations is less than 5
                reward = 200  # Give a reward of 200
            fin = True
        elif self.state.is_finished():  # If the game is finished and there is a tie
            reward = -100  # Give a reward of -100
            fin = True
        else:  # If the game is not finished
            if (self.q_table[self.previous_state_key][self.previous_index][1][self.previous_subindex] == 0):  # If the king is in a corner square
                reward = self.policyhatediagonal()  # Get the reward based on the policy
            else:  # If the king is not in a corner square
                reward = 0  # Set the reward to 0

        self.update_q_table(reward)  # Update the Q table
        if fin:
            self.save_q_table()  # Save the Q table at the end


    def policy(self):
        king_position = self.state.king
        size = Board.size
        x1, y1 = king_position // size, king_position % size

        max_distance = 8.48528137423857
        distance_list = []

        for scape in Board.square_escapes:
            x2, y2 = scape // size, scape % size
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            distance_list.append(distance)
        distance = min(distance_list)
        reward = 100 * (1 - distance / max_distance)
        return reward


    def policyhatediagonal(self):
        king_position = self.state.king
        size = Board.size
        x1, y1 = king_position // size, king_position % size

        max_distance = 8.48528137423857

        distance_list = []
        for scape in Board.square_escapes:  # For each escape square
            x2, y2 = scape // size, scape % size
            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  # Calculate the distance between the king and the escape square
            distance_list.append(distance)
        distance = min(distance_list)

        if (x1 == y1 and (x1 != 0 and x1 != size - 1)) or (x1 + y1 == size - 1 and (x1 != 0 and x1 != size - 1 and y1 != 0 and y1 != size - 1)):
            reward = -100 * (distance / max_distance)
        elif x1 == 0 or x1 == size - 1 or y1 == 0 or y1 == size - 1:
            reward = 100 * (1 - distance / max_distance)
        else:
            reward = 0

        return reward


class PlayerQLearningBlack(Player): # cpu 3
    def __init__(self, state, name, learning_rate=0.4, discount_factor=1, exploration_rate=0.9):
        super().__init__(state)
        self.name = name
        self.wins = 0
        self.loses = 0
        self.learning_rate = learning_rate 
        self.discount_factor = discount_factor 
        self.exploration_rate = exploration_rate
        self.q_table = {} # Q table, which maps states to actions and their respective Q values
        self.previous_state_key = None  # previous state of the game
        self.previous_index = None  # Index of the action taken in the previous state
        self.previous_subindex = None  # Subndex of the action taken in the previous state
        self.next_state_key = None  # Next state of the game
        self.iteraciones = 0 # Number of iterations

        try:
            self.load_stats()  # Load the player statistics if the player exists
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
            self.save_stats()  # Create the player statistics file if it doesn't exist
        try:
            self.load_q_table()  # Cargar la tabla Q si existe
        except (FileNotFoundError, PermissionError, json.JSONDecodeError, KeyError):
            print("No se pudo cargar la tabla Q")
            self.save_q_table()  # Crear la tabla Q si no existe

    def info(self,state):
        """
        The palayer receives the result of the game and evaluates the previous state in which he moved 
        based on the final result and updates the Q table
        """

        if (state.is_tied()):
            reward = 50 # In black player, the tied reward is positive
        else:
            reward = -100
        self.update_q_table(reward)
        self.save_q_table()


    def load_q_table(self):
        """Load the Q table from a json file"""
        with open(f'q_table/q_tableBlacks2Prof.json', 'r', encoding='utf-8') as f:
            self.q_table = json.load(f)


    def save_q_table(self):
        """Save the Q table to a json file"""
        with open(f'q_table/q_tableBlacks2Prof.json', 'w', encoding='utf-8') as f:
            json.dump(self.q_table, f)


    def _next_movement(self):
        current_state_key = str(self.state.ID)
        if current_state_key not in self.q_table:
            self.q_table[current_state_key] = [(i, [0]*len(move[1])) for i, move in enumerate(self.state.mov_valid_list())]
        valid_moves = self.state.mov_valid_list()

        if not valid_moves:
            raise Exception("No valid moves available")

        if random.random() < self.exploration_rate:
            # Exploración: elegir una acción aleatoria
            action_index = random.randint(0, len(valid_moves) - 1)
            current_position, possible_positions = valid_moves[action_index]
            while len(possible_positions) == 0:
                action_index = random.randint(0, len(valid_moves) - 1)
                current_position, possible_positions = valid_moves[action_index]

            # Select a random position among the possible positions
            new_position = random.choice(possible_positions)
            self.previous_subindex = possible_positions.index(new_position)
        else:
            # Select the action with the highest Q value among the possible actions
            q_values = [np.max(q_values) for _, q_values in self.q_table[current_state_key] if len(q_values) > 0]
            if not q_values:
                action_index = random.randint(0, len(valid_moves) - 1)
            else:
                action_index = np.argmax(q_values)

            current_position, possible_positions = valid_moves[action_index]
            while len(possible_positions) == 0:
                action_index = random.randint(0, len(valid_moves) - 1)
                current_position, possible_positions = valid_moves[action_index]

            q_values = self.q_table[current_state_key][action_index][1]
            self.previous_subindex = np.argmax(q_values)

            new_position = possible_positions[self.previous_subindex]

        self.previous_index = action_index
        return current_position, new_position


    def update_q_table(self,reward):
        # learning from experience
        state_key = self.previous_state_key
        next_state_key = self.next_state_key
        action_index = self.previous_index

        current_q_value = self.q_table[state_key][action_index][1][self.previous_subindex]
        next_max_q_value = max([np.max(q_values) for _, q_values in self.q_table[next_state_key]]) if next_state_key in self.q_table else 0
        updated_q_value = current_q_value + self.learning_rate * (reward + self.discount_factor * next_max_q_value - current_q_value)
        self.q_table[state_key][action_index][1][self.previous_subindex] = updated_q_value


    def make_movement(self):
        self.previous_state_key = str(self.state.ID)
        current_position, new_position = self._next_movement()
        self.state.make_movement(current_position, new_position)
        self.next_state_key = str(self.state.ID)
        self.iteraciones += 1
        fin = False

        if self.state.is_finished():  # If the game is finished
            if self.iteraciones >= 50:  # If the number of iterations is greater than 50
                reward = 50  # Give a reward of 50
            elif self.iteraciones >= 30 and self.iteraciones < 50:  # If the number of iterations is greater than 30 and less than 50
                reward = 80  # Give a reward of 80
            elif self.iteraciones < 30 and self.iteraciones >= 15:  # If the number of iterations is less than 30 and greater than 15
                reward = 100  # Give a reward of 100
            elif self.iteraciones < 15 and self.iteraciones >= 5:  # If the number of iterations is less than 15 and greater than 5
                reward = 150  # Give a reward of 150
            elif self.iteraciones < 5:  # If the number of iterations is less than 5
                reward = 200  # Give a reward of 200
            fin = True
        elif self.state.is_finished() and (self.state.is_tied()):  # If the game is finished and there is a tie
            reward = 50  # Give a reward of 50
            fin = True
        else:  # If the game is not finished
            reward = 0  # Set the reward to 0

        self.update_q_table(reward)
        if fin:
            self.save_q_table()
