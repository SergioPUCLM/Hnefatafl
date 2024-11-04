import os
import pygame

from state import State
from board import Board
from game import Game
from server import Server
from interface import main_menu


if __name__ == '__main__':
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # Make the screen centered [DO NOT DELETE OR GRAPHICS WILL GLITCH]
    pygame.init()  # Initiate pygame
    game_manager = Server()  # Start the server
    main_menu(game_manager)  # Load the menu
