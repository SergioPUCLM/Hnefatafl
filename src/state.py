import json
import hashlib
import os
import copy
import typing 
import pygame

from board import Board


class State():
    """Class to represent one state of a game"""
    def __init__(self, ID, whites, blacks, king, gamer,type_game, json_string=None):
        # PARAMETERS SAVED ON JSON
        self.ID = ID  # MD5 unique ID of the state
        self.whites = whites  # Position of the white pieces
        self.blacks = blacks  # Position of the black pieces
        self.king = king  # Position of the king piece
        self.gamer = gamer  # Player's turn (0 = black, 1 = white)

        self.selec_piece=None
 
        # OTHER PARAMATERS
        self.type_game = type_game  # Name of game variant
        self.json_string = json_string  # Optional parameter

        self.possible_movements = []  # Succesor states 
        self.last_movements = []  # Store last 8 states

        if json_string is not None:  # Replace parameters with the json string if present (type_game is not included)
            js = json.loads(json_string)  # Load the string as JSON format
            self.ID = js['ID']
            self.whites = js['whites']
            self.blacks = js['blacks']
            self.king = js['king']
            self.gamer = js['gamer']

        if self.ID == '0':  # Generate the ID if none has been given
            self.ID = self.gen_md5_id()
            
        self.last_movements.append(self.ID)
        self.save_in_json('STATES.json')  # Save the state into the JSON


    def gen_md5_id(self):
        """Generate the ID with an md5 sum"""
        md5 = hashlib.md5(str(self.parse_no_ID()).encode()).hexdigest()
        return f'{self.type_game}-{md5}'  # ID = Name-MD5change_turn


    def change_turn(self):
        """Change the player to the opposite"""
        self.gamer = 1 - self.gamer


    def parse_json(self):
        """Convert the state into a json string to save it"""
        state_string = {
            "ID": self.ID,
            "whites": self.whites,
            "blacks": self.blacks,
            "king": self.king,
            "gamer": self.gamer
        }
        return state_string


    def parse_no_ID(self):
        """Convert the state into a json string without ID for the MD5 generation"""
        state_string = {
            "whites": self.whites,
            "blacks": self.blacks,
            "king": self.king,
            "gamer": self.gamer
        }
        return state_string

    
    def save_in_json(self, file):
        """Save the state to a JSON file if it does not exist already"""
        existing_states = []

        if not os.path.exists(file):  # Check if the file exists, if not, create a new one
            with open(file, 'w') as f:
                json.dump([], f)  # Write an empty list to the file
        else:  # If the file exists, load existing states
            with open(file, 'r') as f:
                try:
                    existing_states = json.load(f)
                except json.decoder.JSONDecodeError:
                    existing_states = []  # If the file is empty initialize existing_states as an empty list

        state_ids = [state['ID'] for state in existing_states]  # Get saved states IDs

        if self.ID not in state_ids:  # Check if the state ID already exists in the file
            existing_states.append(self.parse_json())  # Add new state
            with open(file, 'w') as f:  # Update the file
                json.dump(existing_states, f)
                
       
    def generate_successors(self):
        """Generates the successor states o the current state. It is an iterator in this case"""  
        for current_pos, valid_moves in self.mov_valid_list():  # Iterate over the valid moves
            for new_pos in valid_moves:
                current_state_copy = copy.deepcopy(self)  # Create a copy of the current state      
                # Modify the different copies 
                current_state_copy.make_movement(current_pos, new_pos)
                yield (current_pos, new_pos), current_state_copy


    def mov_valid_list(self):
        """Method that returns a list with possible moves"""
        special_squares = Board.square_escapes + [Board.center]

        mov_valid_list = []  # List of movements
        if self.gamer == 0:
            for pos in (self.blacks):
                mov_valid_list.append((pos,self._mov_valid(pos, Board.size, special_squares)))
            return mov_valid_list
        else:
            for pos in (self.whites):
                mov_valid_list.append((pos,self._mov_valid(pos, Board.size, special_squares)))
            mov_valid_list.append((self.king, self.mov_valid_king(self.king, Board.size)))
            return mov_valid_list


    def mov_valid_king(self, origin, size):
        """Calculates valid movement positions for a king on a square board based on its origin."""
        return self._mov_valid(origin, size, special_squares=None)
    
    def _mov_valid(self, origin, size, special_squares=None):
        """Calculates valid movement positions for a piece on a square board based on its origin."""
        destination_list = []  # Initialize the list to hold valid destination positions

        # Calculate positions vertically upwards from the origin
        destination = origin - size
        while destination >= 0:
            if self._is_occupied(destination):
                break   
            if special_squares is None or not destination in special_squares:
                destination_list.append(destination)  
            destination = destination - size 
        
        # Calculate positions vertically downwards from the origin
        destination = origin + size
        while destination < size*size:
            if self._is_occupied(destination):
                break    
            if special_squares is None or not destination in special_squares:
                destination_list.append(destination) 
            destination = destination + size  

        # Calculate positions horizontally to the left from the origin
        destination = origin - 1
        while destination // size == origin // size:
            if self._is_occupied(destination):
                break   
            if special_squares is None or not destination in special_squares:
                destination_list.append(destination)  
            destination = destination - 1    

        # Calculate positions horizontally to the right from the origin
        destination = origin + 1
        while destination // size == origin // size:
            if self._is_occupied(destination):
                break  
            if special_squares is None or not destination in special_squares:
                destination_list.append(destination)  
            destination = destination + 1  
        
        return destination_list  # Return the list of valid destinations
    

    def _is_occupied(self, destination): 
        """Check if the destination is occupied by another piece"""
        return destination in self.whites or destination in self.blacks or destination == self.king
    
    
    def check_valid_move(self, origin, destination):
        return ((((self.gamer == 0 and origin in self.blacks) or 
                 (self.gamer == 1 and origin in self.whites)) and
                 (destination in self._mov_valid(origin, Board.size, Board.square_escapes + [Board.center]))) or 
                 (self.gamer == 1 and origin == self.king) and (destination in self.mov_valid_king(origin, Board.size)))


    def make_movement(self, current_pos, new_pos): 
        """Modify state if necessary. The id of the sate has to be updated and the sate must be stored""" 
       
        if current_pos in self.blacks:
            self.blacks.remove(current_pos)
            self.blacks.append(new_pos)
            self.blacks.sort()
        
        elif current_pos == self.king:
            self.king = new_pos
        
        elif current_pos in self.whites:    
            self.whites.remove(current_pos)
            self.whites.append(new_pos)
            self.whites.sort()
        
        self.capture(new_pos)
        if not self.is_finished():
            self.change_turn()
        
        self.ID = self.gen_md5_id()
        self.last_movements.append((self.ID))
        self._delete_movements()
    
    
    def _delete_movements(self):
        """Delete movements from the list of last movements when it has been stored more than 8 movements """
        if(len(self.last_movements) > 9):
            del self.last_movements[0]
       
    def capture(self, position):
        """Method that captures a piece"""
        special_squares = Board.square_escapes + [Board.center]
        directions = [-1, 1, -Board.size, Board.size]  # Left, Right, Up, Down
        opponent = self.whites + [self.king] if self.gamer == 0 else self.blacks
        player = self.blacks if self.gamer == 0 else self.whites + [self.king]

        def capture_king(position_opponent):
            """Check capture for the king"""
            surrounding = [position_opponent + d for d in directions]
            
            # Check for king capture conditions (surrounding for opponent or opponent and center)
            if (all(pos in player for pos in surrounding)
                or all (pos in player + [Board.center] for pos in surrounding)):
                self.king = None
                #self.win()

        for direction in directions:  # Check all directions
            if ((position % Board.size == 0 and direction == -1) or (position % Board.size == Board.size - 1  and direction == 1)):
                continue
            pos_aday = position + direction
            if (pos_aday == self.king):
                if self.gamer == 0:    
                    capture_king(pos_aday)
            else: 
                # Check if there is an opponent piece in the position
                if pos_aday in opponent:
                    # Check if the adjacent piece can be captured (player+direction is an opponent
                    # and player + 2*direction is a player or special_square)
                    if self.gamer == 0 and self.king == Board.center: # Special case for the center when the center is occupied
                        allies_positions = player + Board.square_escapes
                    else:
                        allies_positions = player + special_squares
                    possible_ally = pos_aday + direction
                    if ((possible_ally % Board.size != 0 and direction != -1) or (possible_ally % Board.size != Board.size - 1  and direction != 1)):
                        if possible_ally in allies_positions:
                        # Check if the opponent piece not are surrounded by player pieces
                        # if not the king but are surrounded by player pieces, the piece not is captured
                            opponent.remove(pos_aday)  # Remove the captured piece from the opponent list
        if self.gamer == 0:    
            self.whites = opponent
            if self.king is not None:
                self.whites.remove(self.king)
        else:
            self.blacks = opponent


    def is_tied(self):
        """Returns true if the current state is the same as the from 8 states ago."""
        return len(self.last_movements) == 9 and self.last_movements[0] == self.last_movements[8]
    
    
    def king_has_escaped(self):
        """Check if the king has escaped"""
        return self.king in Board.square_escapes


    def win(self):
        """Method that checks if the king has escaped"""
        if self.king_has_escaped() or len(self.blacks) <= 1:
            print("The king has escaped")
        else:
            print("Blacks captures the king")


    def is_finished(self):
        """Check whether the game has been finished."""
        # Need to check when the king loses and th tied
        return self.king_has_escaped() or self.is_tied() or self.king == None or len(self.blacks) <= 1
    

    def parse_gamer(self):
        if self.gamer == 0:
            return "BLACKS "
        else:
            return "WHITES "
        

    def handle_click(self, pos):
        tablero = Board()
        margin_size_x = 275
        if self.type_game == 'Brandubh':
            square_size = 100  # Size of the squares
            margin_size_y = 10  # Margin size
        elif self.type_game == 'Tafl':
            square_size = 90  # Size of the squares
            margin_size_y = 5  # Margin siz
        else:
            square_size = 80  # Size of the squares
            margin_size_y = 3
        col = (pos[0] - margin_size_x) // square_size
        row = (pos[1] - margin_size_y) // square_size
        square_num = row * tablero.size + col

        # Check if the turn player has clicked on one of their pieces
        if self.gamer == 0:
            if self.selec_piece is None:
                if square_num in self.blacks:
                    # Update the selected piece             
                    self.selec_piece = square_num
            else:
                if self.check_valid_move(self.selec_piece, square_num):
                    square_num_in = self.selec_piece
                    self.selec_piece = None
                    return square_num_in, square_num
                else:
                    # Reset selec_piece
                    self.selec_piece = None
        else:
            if self.selec_piece is None:
                if square_num in self.whites or square_num == self.king:
                    # Update the selected piece
                    self.selec_piece = square_num
            else:
                if self.check_valid_move(self.selec_piece, square_num):
                    square_num_in = self.selec_piece
                    self.selec_piece = None
                    return square_num_in, square_num
                else:
                    # Reset selec_piece
                    self.selec_piece = None


    def draw_board(self, screen, board_size, square_size, margin_size_x, margin_size_y):
        # Define the colors
        bg_color = (30, 30, 30)  # Color for the margin
        border_color = (0, 0, 0)  # Black color for the square borders
        font = pygame.font.Font(None, 24)  # Define the font for numbering

        # Load images for the squares
        square_images = {
            "sienna": pygame.image.load("images/board/black_square.png"),
            "burlywood": pygame.image.load("images/board/white_square.png")
        }
        # Scale the images to fit the square size
        for color in square_images:
            square_images[color] = pygame.transform.scale(square_images[color], (square_size, square_size))

        # Fill the margin area
        screen.fill(bg_color)

        for row in range(board_size):
            for col in range(board_size):
                # Determine the color of the square based on row and column
                color_name = "sienna" if (row + col) % 2 == 0 else "burlywood"
                square_image = square_images[color_name]

                # Calculate the rectangle for the square with margins
                rect = pygame.Rect(
                    margin_size_x + col * square_size,
                    margin_size_y + row * square_size,
                    square_size,
                    square_size
                )

                # Draw the square image
                screen.blit(square_image, rect)

                # Draw the square border
                pygame.draw.rect(screen, border_color, rect, 1)

        # Draw the numbers after drawing the squares
        for row in range(board_size):
            for col in range(board_size):
                # Calculate the rectangle for the square with margins
                rect = pygame.Rect(
                    margin_size_x + col * square_size,
                    margin_size_y + row * square_size,
                    square_size,
                    square_size
                )

                # Number the square, placing it in the lower right corner
                number = row * board_size + col
                color_name = "sienna" if (row + col) % 2 == 0 else "burlywood"
                text = font.render(str(number), True, (0, 0, 0) if color_name == "burlywood" else (255, 255, 255))
                text_rect = text.get_rect(bottomright=(rect.right - 5, rect.bottom - 5))
                screen.blit(text, text_rect)


    def draw_special_squares(self, screen, board_size, square_size, margin_size_x, margin_size_y):
        # Load the image for the special square
        special_square_image = pygame.image.load("images/board/special.png")
        special_square_image = pygame.transform.scale(special_square_image, (square_size, square_size))

        special_square_center_image = pygame.image.load("images/board/center.png")
        special_square_center_image = pygame.transform.scale(special_square_center_image, (square_size, square_size))

        tablero = Board()
        special_squares = tablero.square_escapes
        special_square_center = tablero.center

        for square_num in special_squares:  # Iterate over all the special squares
            # Calculate the top-left coordinates of the square
            x, y = margin_size_x + (square_num % board_size) * square_size, margin_size_y + (square_num // board_size) * square_size

            # Draw the special square image
            screen.blit(special_square_image, (x, y))

        # Calculate the top-left coordinates of the center square
        x, y = margin_size_x + (special_square_center % board_size) * square_size, margin_size_y + (special_square_center // board_size) * square_size

        # Draw the center square image
        screen.blit(special_square_center_image, (x, y))


    def draw_pieces(self,screen, board_size, square_size, margin_size_x, margin_size_y):
        # Load the images for the pieces
        white_piece_img = pygame.image.load('images/pieces/white_piece.png')
        black_piece_img = pygame.image.load('images/pieces/black_piece.png')
        king_piece_img = pygame.image.load('images/pieces/king_piece.png')

        # Scale the images to fit the square size
        white_piece_img = pygame.transform.scale(white_piece_img, (square_size, square_size))
        black_piece_img = pygame.transform.scale(black_piece_img, (square_size, square_size))
        king_piece_img = pygame.transform.scale(king_piece_img, (square_size, square_size))

        king_pos = self.king
        black_pieces = self.blacks
        white_pieces = self.whites

        # Function to calculate the top-left coordinates of a square given its number
        def calc_square_top_left(square_num):
            row = (square_num ) // board_size
            col = (square_num ) % board_size
            return margin_size_x + col * square_size, margin_size_y + row * square_size

        # Function to draw a single piece
        def draw_piece(piece_img, square_num):
            x, y = calc_square_top_left(square_num)
            screen.blit(piece_img, (x, y))

        # Draw the king
        # If king is not none
        if king_pos is not None:
            draw_piece(king_piece_img, king_pos)

        # Draw the black pieces
        for pos in black_pieces:
            draw_piece(black_piece_img, pos)

        # Draw the white pieces
        for pos in white_pieces:
            draw_piece(white_piece_img, pos)
