import json
from hashlib import md5

class Board:  #TODO: Initialize the board
    name = ''
    size = 0
    escape = []
    center = 0
    def _init_(self, name, size, escape, center):
        Board.name = name
        Board.size = size
        Board.escape = escape
        Board.center = center
