import json
from create_json import createJsonFile
from hashlib import md5

"""
How see the state of the game
Atributes:
    - ID: state id (create a unique id for each state. In this case we use a hash of the JSON state.)
    - white: list of values with the positions of the white pieces
    - black: list of values with the positions of the black pieces
    - king: tuple with the position of the king
    - gamer: 0 if black, 1 if white

If look at the board from the top, the positions are:

00 01 02 03 04 05 06
07 08 09 10 11 12 13
14 15 16 17 18 19 20
21 22 23 24 25 26 27
28 29 30 31 32 33 34
35 36 37 38 39 40 41
42 43 44 45 46 47 48

Methods:
    - change_gamer: change the player
    - __str__: return a string representation of the state
    - to_JSON: return a JSON string representation of the state
    - from_JSON: create a State object from a JSON string
    - save_to_file: save the state to a file
    - load_from_file: load the state from a file
"""
class State:
    """
    Class to represent the state of the game
    """

    def __init__(self, white, black, king, gamer):
        """
        Constructor of the class
        """
        self.ID = 0 # is the default value, it will be changed when the state is saved to a file
        self.white = white # positions list of white pieces
        self.black = black # positions list of black pieces
        self.king = king # position of the king
        self.gamer = gamer # 0 if black, 1 if white
    
    def change_gamer(self):
        self.gamer = 1 - self.gamer
    
    ###################
    ## Other methods ##
    ###################

    def __str__(self):
        """
        Method to return a string representation of the state
        """
        return "State: white=" + str(self.white) + ", black=" + str(self.black) + ", king=" + str(self.king) + ", gamer=" + str(self.gamer)
    
    def to_JSON(self):
        """
        Method to return a JSON string representation of the state
        """
        state_dict = {
            'ID': self.ID,
            'white': self.white,
            'black': self.black,
            'king': self.king,
            'gamer': self.gamer
        }
        return json.dumps(state_dict)
    
    @classmethod
    def from_JSON(cls, json_str):
        """
        Class method to create a State object from a JSON string
        """
        state_dict = json.loads(json_str)
        return cls(state_dict['white'], state_dict['black'], state_dict['king'], state_dict['gamer'])


    def save_to_file(self, filename):
        """
        Method to save the state to a file
        """
        with open(filename, 'w') as f:
            f.write(self.to_JSON())


    def load_from_file(self, filename):
        """
        Method to load the state from a file
        """
        with open(filename, 'r') as f:
            state_dict = json.load(f)
            self.ID = state_dict['ID']
            self.white = state_dict['white']
            self.black = state_dict['black']
            self.king = state_dict['king']
            self.gamer = state_dict['gamer']