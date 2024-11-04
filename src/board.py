class Board():
    """
    Class to represent the board of the game
    - size: Size of a board side (nº squares = size^2)
    - square_escapes: List of escape squares    
    - center: Position of the center square
    """
    # CLASS VARIABLES (Accesesd by Board.variable)
    size = 0  # Size of a board side (nº squares = size^2)
    square_escapes = []  # List of escape squares
    center = 0  # Position of the center square

    def initialize(self, size, square_escapes, center):
        """
        Initialize the board (Must be separated from the constructor to allow instancing)
        """
        Board.size = size
        Board.square_escapes = square_escapes
        Board.center = center
        