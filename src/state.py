import json
from create_json import createJsonFile
from hashlib import md5

class State:
    def _init_(self, ID = 0, whites = [], blacks = [], king = 0, turn = 0):
        """Generate a state"""
        self.ID = ID
        self.whites = whites
        self.blacks = blacks
        self.king = king
        self.turn = turn

        if self.ID == 0:  # Only initial states brought from the INITSTATES.json will have ID = 0
            md5 = self.calculateMD5(self.parseNoID())  # Get an MD5 hash from the state
            self.ID = Board.name + '-' + md5
            #TODO: Get the board name data from the Board class once implemented

    
    def saveState(self):
        """Save the state into the JSON"""


    def parse(self):
        """Convert the state into a json string"""
        state_string = {
            "ID": self.ID,
            "whites": self.whites,
            "blacks": self.blacks,
            "king": self.king,
            "turn": self.turn
        }
        return state_string


    def parseNoID(self):
        """Convert the state into a json string without ID for t"""
        state_string = {
            "whites": self.whites,
            "blacks": self.blacks,
            "king": self.king,
            "turn": self.turn
        }
        return state_string


    def calculateMD5(string):
        return hashlib.md5(input_string.encode()).hexdigest()


    def drawBoard(self):
        """Display the state in human-readable form"""


    def toString(self):
        """Display a state as a single json string"""
        print(f'{self.parse}')


class Node:
    pass