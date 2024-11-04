import json
import pygame
import sys
import os
import time

from board import Board
from state import State
from board import Board


class Game():
    """
    Class to represent a game
    - type_game: Name of the game variant to play from json
    """
    def __init__(self, type_game):
        self.type_game = type_game  # Name of the game variant
        self.board = None # Board object
        self.current_state = None # Current game state. 
        self.game_states = [] # Store all the movements of a game.
        self.black_player = None
        self.white_player = None
        
        with open('INITSTATES.json', 'r', encoding='utf-8') as file:
            games = json.load(file)

            for game in games:
                if (game['name'] == self.type_game):  # Pick the game
                    size = game['size']
                    escape = game['escape']
                    center = game['center']
                    self.board = Board()  # Create the board
                    self.board.initialize(size, escape, center)  # Initialize the board

                    state_dict = game['init_state']
                    state_json_string = json.dumps(state_dict)  # Convert the dict to a JSON string
                    self.current_state = State(None, None, None, None, None, game['name'], state_json_string)  # Create the initial state
                    break
            self.store_movement()

    
    def graphic_board(self, current_player, screen, board_size, square_size, margin_size_x, margin_size_y):
        """
        Method that draws the board of the game
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill((0, 0, 0))  # Fill the screen with a black background

        # Draw the board, special squares, and pieces at the calculated positions
        current_player.state.draw_board(screen, board_size, square_size, margin_size_x, margin_size_y)
        current_player.state.draw_special_squares(screen, board_size, square_size, margin_size_x, margin_size_y)
        current_player.state.draw_pieces(screen, board_size, square_size, margin_size_x, margin_size_y)

        pygame.display.flip()
        
        time.sleep(0.05)

    def play_game(self, black_player, white_player):
        """Launch a game of Hnefatafl"""
        winner = None
        
        board_size = Board.size  # Size of the board
        margin_size_x = 275  # Margin size in x
        if self.type_game == 'Brandubh':
            square_size = 100  # Size of the squares
            margin_size_y = 10  # Margin size in y
        elif self.type_game == 'Tafl':
            square_size = 90  # Size of the squares
            margin_size_y = 5  # Margin size in y
        else:
            square_size = 80  # Size of the squares
            margin_size_y = 3  # Margin size in y
        window_size_x = board_size * square_size + 2 * margin_size_x
        window_size_y = board_size * square_size + 2 * margin_size_y

        screen = pygame.display.set_mode((window_size_x, window_size_y))
        pygame.display.set_icon(pygame.transform.scale(pygame.image.load("images/icons/icon.png"), (32, 32)))
        pygame.display.set_caption(f'Hnefatalf - Partida en curso ({self.type_game})')

        # Colors
        c_white = (255, 255, 255)
        c_red = (255, 0, 0)
        c_black = (0, 0, 0)
        
        # Load fonts
        font_face = 'Consolas'

        font_size = 15
        font = pygame.font.SysFont(font_face, font_size)

        font_big_size = 25
        font_big = pygame.font.SysFont(font_face, font_big_size)

        # Labels
        turn_label_text = 'Turno'
        turn_label_surface = font_big.render(turn_label_text, True, c_white)
        turn_label_position = (margin_size_x - 10 - turn_label_surface.get_width() - 10, window_size_y/2 - turn_label_surface.get_height())

        turn_player_text = black_player.name  # Default value, change each turn to current player's turn
        turn_player_surface = font.render(turn_player_text, True, c_white)
        turn_player_position = (margin_size_x - 10 - turn_player_surface.get_width() - 10, window_size_y/2 + turn_label_surface.get_height())

        w_player_tag_text = 'Jugador Blancas'
        w_player_tag_surface = font_big.render(w_player_tag_text, True, c_white)
        w_player_tag_position = (window_size_x - margin_size_x + 10, window_size_y/2 - w_player_tag_surface.get_height() - 100)


        w_player_text = white_player.name
        w_player_surface = font.render(w_player_text, True, c_white)
        w_player_position = (window_size_x - margin_size_x + 10, window_size_y/2 + w_player_tag_surface.get_height()- 100)

        b_player_tag_text = 'Jugador Negras'
        b_player_tag_surface = font_big.render(b_player_tag_text, True, c_white)
        b_player_tag_position = (window_size_x - margin_size_x + 10, window_size_y/2 - b_player_tag_surface.get_height() + 100)

        b_player_text = black_player.name
        b_player_surface = font.render(b_player_text, True, c_white)
        b_player_position = (window_size_x - margin_size_x + 10, window_size_y/2 + b_player_tag_surface.get_height() + 100)

        while not self.is_game_over():
            current_player =  black_player if self.current_state.gamer == 0 else white_player
            
            self.graphic_board(current_player,screen,board_size,square_size,margin_size_x,margin_size_y)

            # Draw labels
            turn_player_text = f'{current_player.name}'
            turn_player_surface = font.render(turn_player_text, True, c_white)

            screen.blit(turn_label_surface, turn_label_position)
            screen.blit(turn_player_surface, turn_player_position)

            screen.blit(w_player_tag_surface, w_player_tag_position)
            screen.blit(w_player_surface, w_player_position)

            screen.blit(b_player_tag_surface, b_player_tag_position)
            screen.blit(b_player_surface, b_player_position)

            pygame.display.flip()

            current_player.make_movement()  # Stop everything untill the player (or bot) makes a movement
            self.store_movement()  # Store the movement

            if self.is_game_over():
                if self.current_state.is_tied():
                    winner = 2
                else:
                    winner = self.current_state.gamer

                if  not (self.current_state.parse_gamer() == 'BLACKS '):
                    black_player.info(self.current_state) 
                else:
                    white_player.info(self.current_state)        
                self.graphic_board(current_player,screen,board_size,square_size,margin_size_x,margin_size_y)

                # Show a winner tag
                if winner == 0 or winner == 1: # If there is a winner
                    winner_text_1 = 'Enhorabuena'
                    winner_text_2 = f'{current_player.name}'
                    winner_text_3 = f'Has ganado la partida'
                    winner_text_4 = 'Presiona cualquier tecla para continuar'
                else: 
                    winner_text_1 = 'Tablas!'
                    winner_text_2 = ''
                    winner_text_3 = 'Nadie ha ganado la partida'
                    winner_text_4 = 'Presiona cualquier tecla para continuar'

                winner_surface_1 = font_big.render(winner_text_1, True, c_red)
                winner_surface_2 = font_big.render(winner_text_2, True, c_red)
                winner_surface_3 = font_big.render(winner_text_3, True, c_red)
                winner_surface_4 = font.render(winner_text_4, True, c_red)

                winner_position_1 = (window_size_x/2 - winner_surface_1.get_width()/2, window_size_y/2 - winner_surface_1.get_height() - 50)
                winner_position_2 = (window_size_x/2 - winner_surface_2.get_width()/2, window_size_y/2 - winner_surface_2.get_height())
                winner_position_3 = (window_size_x/2 - winner_surface_3.get_width()/2, window_size_y/2)
                winner_position_4 = (window_size_x/2 - winner_surface_4.get_width()/2, window_size_y/2 + winner_surface_3.get_height() + 50)

                # Rectangle to draw the text on
                box_width = max(winner_surface_1.get_width(), winner_surface_2.get_width(), winner_surface_3.get_width(), winner_surface_4.get_width()) + 60
                box_height = winner_surface_1.get_height() + winner_surface_2.get_height() + winner_surface_3.get_height() + winner_surface_4.get_height() + 100
                box_x = (window_size_x - box_width) / 2
                box_y = (window_size_y - box_height) / 2

                # Rectangle border (10 px)
                rect_width = box_width + 20
                rect_height = box_height + 20
                rect_x = box_x - 10
                rect_y = box_y - 10

                # Draw the box
                pygame.draw.rect(screen, c_black, (rect_x, rect_y, rect_width, rect_height))
                pygame.draw.rect(screen, c_white, (box_x, box_y, box_width, box_height))
                
                # Draw the text
                screen.blit(winner_surface_1, winner_position_1)
                screen.blit(winner_surface_2, winner_position_2)
                screen.blit(winner_surface_3, winner_position_3)
                screen.blit(winner_surface_4, winner_position_4)

                pygame.display.update()
                pygame.display.flip()

                # Wait for any kind of user input
                end_game = False
                while not end_game:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            end_game = True

            pygame.display.update() 
            pygame.display.flip() 

        return winner
            
    def store_movement(self):
        """Method that store the different movements of the players during a game 
        """
        self.game_states.append(self.current_state.gen_md5_id())
        self.current_state.save_in_json('STATES.json')


    def is_game_over(self):
        return self.current_state.is_finished()
     
    def replay(self, game_states, winner):
        """Replay a loaded game"""
        board_size = Board.size  # Size of the board
        margin_size_x = 275  # Margin size in x
        if self.type_game == 'Brandubh':
            square_size = 100  # Size of the squares
            margin_size_y = 10  # Margin size
        elif self.type_game == 'Tafl':
            square_size = 90  # Size of the squares
            margin_size_y = 5  # Margin siz
        else:
            square_size = 80  # Size of the squares
            margin_size_y = 3
        window_size_x = board_size * square_size + 2 * margin_size_x
        window_size_y = board_size * square_size + 2 * margin_size_y

        screen = pygame.display.set_mode((window_size_x, window_size_y))
        pygame.display.set_icon(pygame.transform.scale(pygame.image.load("images/icons/icon.png"), (32, 32)))
        pygame.display.set_caption(f'Hnefatalf - Repetición en curso ({self.type_game})')

        # Colors
        c_white = (255, 255, 255)
        c_red = (255, 0, 0)
        c_black = (0, 0, 0)
        
        # Load fonts
        font_face = 'Consolas'

        font_size = 15
        font = pygame.font.SysFont(font_face, font_size)

        font_big_size = 25
        font_big = pygame.font.SysFont(font_face, font_big_size)

        # Labels
        turn_label_text = 'Turno'
        turn_label_surface = font_big.render(turn_label_text, True, c_white)
        turn_label_position = (margin_size_x - 10 - turn_label_surface.get_width() - 10, window_size_y/2 - turn_label_surface.get_height())

        turn_player_text = self.black_player.name  # Default value, change each turn to current player's turn
        turn_player_surface = font.render(turn_player_text, True, c_white)
        turn_player_position = (margin_size_x - 10 - turn_player_surface.get_width() - 10, window_size_y/2 + turn_label_surface.get_height())

        w_player_tag_text = 'Jugador Blancas'
        w_player_tag_surface = font_big.render(w_player_tag_text, True, c_white)
        w_player_tag_position = (window_size_x - margin_size_x + 10, window_size_y/2 - w_player_tag_surface.get_height() - 100)


        w_player_text = self.white_player.name
        w_player_surface = font.render(w_player_text, True, c_white)
        w_player_position = (window_size_x - margin_size_x + 10, window_size_y/2 + w_player_tag_surface.get_height()- 100)

        b_player_tag_text = 'Jugador Negras'
        b_player_tag_surface = font_big.render(b_player_tag_text, True, c_white)
        b_player_tag_position = (window_size_x - margin_size_x + 10, window_size_y/2 - b_player_tag_surface.get_height() + 100)

        b_player_text = self.black_player.name
        b_player_surface = font.render(b_player_text, True, c_white)
        b_player_position = (window_size_x - margin_size_x + 10, window_size_y/2 + b_player_tag_surface.get_height() + 100)

        for state in game_states:
            self.current_state = state
            if self.current_state.gamer == 0:
                current_player = self.black_player
            else:
                current_player = self.white_player

            current_player = self.black_player if self.current_state.gamer == 0 else self.white_player

            current_player.state = self.current_state

            # Draw the board, special squares, and pieces at the calculated positions
            self.current_state.draw_board(screen, board_size, square_size, margin_size_x, margin_size_y)
            self.current_state.draw_special_squares(screen, board_size, square_size, margin_size_x, margin_size_y)
            self.current_state.draw_pieces(screen, board_size, square_size, margin_size_x, margin_size_y)

            # Draw labels
            turn_player_text = f'{current_player.name}'
            turn_player_surface = font.render(turn_player_text, True, c_white)

            screen.blit(turn_label_surface, turn_label_position)
            screen.blit(turn_player_surface, turn_player_position)

            screen.blit(w_player_tag_surface, w_player_tag_position)
            screen.blit(w_player_surface, w_player_position)

            screen.blit(b_player_tag_surface, b_player_tag_position)
            screen.blit(b_player_surface, b_player_position)

            pygame.display.flip()

            time.sleep(1)

        # Show a winner tag
        if winner == 0 or winner == 1: # If there is a winner
            winner_text_1 = 'Repetición finalizada'
            winner_text_2 = f'{current_player.name}'
            winner_text_3 = f'Gano la partida'
            winner_text_4 = 'Presiona cualquier tecla para continuar'
        else:
            winner_text_1 = 'Repetición finalizada'
            winner_text_2 = 'Tablas!'
            winner_text_3 = 'Nadie ha ganado la partida'
            winner_text_4 = 'Presiona cualquier tecla para continuar'

        winner_surface_1 = font_big.render(winner_text_1, True, c_red)
        winner_surface_2 = font_big.render(winner_text_2, True, c_red)
        winner_surface_3 = font_big.render(winner_text_3, True, c_red)
        winner_surface_4 = font.render(winner_text_4, True, c_red)

        winner_position_1 = (window_size_x/2 - winner_surface_1.get_width()/2, window_size_y/2 - winner_surface_1.get_height() - 50)
        winner_position_2 = (window_size_x/2 - winner_surface_2.get_width()/2, window_size_y/2 - winner_surface_2.get_height())
        winner_position_3 = (window_size_x/2 - winner_surface_3.get_width()/2, window_size_y/2)
        winner_position_4 = (window_size_x/2 - winner_surface_4.get_width()/2, window_size_y/2 + winner_surface_3.get_height() + 50)

        # Rectangle to draw the text on
        box_width = max(winner_surface_1.get_width(), winner_surface_2.get_width(), winner_surface_3.get_width(), winner_surface_4.get_width()) + 60
        box_height = winner_surface_1.get_height() + winner_surface_2.get_height() + winner_surface_3.get_height() + winner_surface_4.get_height() + 100
        box_x = (window_size_x - box_width) / 2
        box_y = (window_size_y - box_height) / 2

        # Rectangle border (10 px)
        rect_width = box_width + 20
        rect_height = box_height + 20
        rect_x = box_x - 10
        rect_y = box_y - 10

        # Draw the box
        pygame.draw.rect(screen, c_black, (rect_x, rect_y, rect_width, rect_height))
        pygame.draw.rect(screen, c_white, (box_x, box_y, box_width, box_height))
                
        # Draw the text
        screen.blit(winner_surface_1, winner_position_1)
        screen.blit(winner_surface_2, winner_position_2)
        screen.blit(winner_surface_3, winner_position_3)
        screen.blit(winner_surface_4, winner_position_4)

        pygame.display.update()
        pygame.display.flip()

        # Wait for any kind of user input
        end_game = False
        while not end_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    end_game = True
        return
