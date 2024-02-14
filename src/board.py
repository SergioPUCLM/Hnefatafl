"""
Atributtes:
    - size: size of the board
    - square_escape: position of the escape squares
    - throne: position of the throne square
    - state: current state of the board
Methods:
    - mov_valid: check if the piecemove is valid
    - obtain_valid_moves: obtain the valid moves for the current state
    - human_representation: return a string representation of the board
    - hash_state: return the hash of the state in md5
    - winner: print the winner of the game and exit the program
"""
import json
import sys
from hashlib import md5
from state import State


class Board:
    """
    Class to represent the board of the game
    """

    def __init__(self, size, square_escape, throne, state):
        """
        Constructor of the class
        """
        self.size = size # variable with the size of the board
        self.square_escape = square_escape  # list with tuples with the position of the escape squares
        self.throne = throne # position of the throne square
        self.state = State() # actual state of the board
        self.five_move =[] # list with the hash last five moves

    def init_state_JSON(self, file):
        """
        Method to initialize the state of the board from a JSON file
        """
        with open(file, 'r') as f:
            data = json.load(f)
            self.state = State(white=data['white'], black=data['black'], king=data['king'], gamer=data['gamer'])
            self.state.ID = self.hash_state(self.state)
            self.five_move.append(self.state.ID)

    def init_state(self, type_game)
        """
        Method to initialize the  state of the board 
        default type is (Brandubh) )
        """
        if (type_game == "Brandubh" or type_game is None):
            self.state = State(white=[17,23,25,31],
                            black = [3,10,21,22,26,27,38,45], 
                            king= 24, gamer=0) # initial state of the board)
        else:
            print("Error: Incorrect type of game")
            sys.exit(1)
        # create the hash of the state and set it to the state
        self.state.ID = type_game+"-"+self.hash_state(self.state)    
        self.state.to_JSON()

        


    def create_state(self, type_game, white, black, king, gamer):
        """
        Method to create a instance of the state
        """ 
        self.state = State(white, black, king, gamer)
        if len(self.five_move) == 5:
            self.five_move.pop(0)
        self.state.ID = type_game+"-"+self.hash_state(self.state)
        self.five_move.append(self.state.ID)
        self.state.to_JSON()


    def human_representation(self):
        """
        Method to return a string representation of the board
        """
        board = ""
        for i in range(self.size*self.size):
            if i in self.state.get_black():
                board += "B"
            elif i in self.state.get_white():
                board += "W"
            elif i == self.state.get_king():
                board += "K"
            else:
                board += " "
            if (i+1) % self.size == 0:
                board += "\n"
        return board

    def mov_valid(self,origin, destination,type_piece ):
        """
        Function to check if a move is valid
            - state: current state of the board
            - origin
            - destination
            - type_piece: type of the piece (0=black, 1=white, 2=king)

        """

        # Check if the move is in the same position
        if (origin == destination):
            return False
        
        # Check if the move is inside the board
        if (destination < 0 or destination > self.size*self.size-1):
            return False
        
        # Check vertical move and horizontal move
        if (destination % self.size != origin % self.size) and (destination // self.size != origin // self.size):
            return False
        
        # check if the square is free
        if (destination in self.state.get_black() or 
            destination in self.state.get_white() or
            destination == self.state.get_king()):
            return False
        
        # check if the square is an escape square or the throne
        if (destination in self.square_escape or destination == self.throne):
                # check if the piece is the king
                if type_piece == 2:
                    self.winner(2) # white wins
        return False    
        
        ### añadir codigo de la captura de piezas (mejor ponerlo en otra función y llamarla)

    def  hash_state(state):
        """
        Function to return the hash of the state in md5
        """
        return md5((state.to_JSON_noID()).encode('utf-8')).hexdigest()
    
    def winner(winnerValue):
        """
        Method to print the winner of the game and exit the program
        """
        if winnerValue == 0:
            print ("The winner is Black")
            sys.exit(0)
        else:
            print ("The winner is White")
            sys.exit(0)

        