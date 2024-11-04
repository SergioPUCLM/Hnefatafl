import pygame
import sys
import json
import os

from server import Server
from state import State
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def open_file_browser(starting_location=None):
    """Open a file browser to select a file"""
    file_types = [("JSON files", "*.json")]

    # Create a hidden Tkinter root window
    root = tk.Tk()
    root.withdraw()

    if starting_location is None:
        starting_location = '.'

    # Open file dialog for selecting a file
    file_path = filedialog.askopenfilename(initialdir=starting_location, title='Elije un archivo de jugador', filetypes=file_types)

    # Check if a file was selected
    if file_path:
        return file_path
    else: 
        return None


def process_player_file(file_path):
    """Process a player file"""
    with open(file_path, 'r') as file:
        player_data = json.load(file)
        # Check it is a player file
        try:  # Extract the data 
            name = player_data['name']
            wins = player_data['wins']
            loses = player_data['loses']
            data = (name, wins, loses)
        except KeyError:
            print('Error: Invalid player file')
            return None
    return data


def process_game_file(file_path):
    """Process a game file"""
    with open(file_path, 'r') as file:
        game_data = json.load(file)
        # Check it is a game file
        try:  # Extract the data
            id = file_path.split('/')[-1].split('.')[0]
            game = game_data['game']
            pl_white = game_data['pl_white']
            player_black = game_data['pl_black']
            winner = game_data['winner']
            states_data = game_data['game_states']
            states = []
            if not os.path.exists('STATES.json'):  # Check if the states file exists
                # Display a warning message box
                root = tk.Tk()
                root.withdraw()
                messagebox.showwarning("Error", "STATES.json not found. Play at least one game to create it.", icon=messagebox.ERROR)
                return None
            else:  # Find the states in STATES.json [WARNING: IF STATES IS DELETED, ALL PREVIOUS GAMES WILL BE INVALID]
                with open('STATES.json', 'r') as f:
                    states_json = json.load(f)
                    for state_id in states_data:  # Load the states into a list
                        for item in states_json:
                            if item['ID'] == state_id:
                                state = State(None, None, None, None, None, game, json.dumps(item))
                                states.append(state)
                                break
            data = (id, pl_white, player_black, winner, game, states)
            if states:
                return data
            else:
                print('Error: Invalid game file')
                return None
        except KeyError as e:
            print('Error: Invalid game file')
            return None


def main_menu(game_manager):
    """Show the main menu"""
    # Define colors
    c_white = pygame.Color(255, 255, 255)
    c_black = pygame.Color(0, 0, 0)
    c_textbox_inactive = pygame.Color(230, 230, 230)
    c_textbox_active = pygame.Color(180, 180, 170)
    c_red = pygame.Color(255, 0, 0)
    c_background = pygame.Color(30, 30, 30)

    # Set up display
    screen_width, screen_height = 620, 480
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_icon(pygame.transform.scale(pygame.image.load("images/icons/icon.png"), (32, 32)))
    pygame.display.set_caption('Hnefatafl - Menu Principal')

    # Load fonts
    font_face = 'Consolas'

    font_size = 14
    font = pygame.font.SysFont(font_face, font_size)

    font_size_title = 42
    font_title = pygame.font.SysFont(font_face, font_size_title, True)

    font_size_subtitle = 24
    font_subtitle = pygame.font.SysFont(font_face, font_size_subtitle)

    # Labels 
    label_title_text = 'Hnefatafl'
    label_title_surface = font_title.render(label_title_text, True, c_white)
    label_title_position = (screen_width/2 - label_title_surface.get_width()/2, 15)

    # Buttons
    play_button = pygame.Rect(screen_width/2 - 150, screen_height/2 - 30, 300, 100)
    play_button_text = 'Jugar'
    play_button_surface = font_title.render(play_button_text, True, c_black)
    play_button_position = (play_button.x + play_button.width/2 - play_button_surface.get_width()/2, play_button.y + play_button.height/2 - play_button_surface.get_height()/2)
    pl_color_normal = c_white
    pl_color_hover = c_textbox_inactive
    pl_color_click = c_textbox_active
    pl_color = pl_color_normal

    stats_button = pygame.Rect(screen_width/2 - 150, screen_height/2 - 145, 300, 100)
    stats_button_text = 'Estadísticas'
    stats_button_surface = font_title.render(stats_button_text, True, c_black)
    stats_button_position = (stats_button.x + stats_button.width/2 - stats_button_surface.get_width()/2, stats_button.y + stats_button.height/2 - stats_button_surface.get_height()/2)
    st_color_normal = c_white
    st_color_hover = c_textbox_inactive
    st_color_click = c_textbox_active
    st_color = st_color_normal

    replay_button = pygame.Rect(screen_width/2 - 150, screen_height/2 + 85, 300, 100)
    replay_button_text = 'Repeticiones'
    replay_button_surface = font_title.render(replay_button_text, True, c_black)
    replay_button_position = (replay_button.x + replay_button.width/2 - replay_button_surface.get_width()/2, replay_button.y + replay_button.height/2 - replay_button_surface.get_height()/2)
    rp_color_normal = c_white
    rp_color_hover = c_textbox_inactive
    rp_color_click = c_textbox_active
    rp_color = rp_color_normal

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Check if mouse is clicked
                if play_button.collidepoint(event.pos): 
                    pl_color = pl_color_click
                if stats_button.collidepoint(event.pos):
                    st_color = st_color_click
                if replay_button.collidepoint(event.pos):
                    rp_color = rp_color_click
            if event.type == pygame.MOUSEBUTTONUP:
                if play_button.collidepoint(event.pos):
                    pl_color = pl_color_normal
                    play_menu(game_manager)
                if stats_button.collidepoint(event.pos):
                    st_color = st_color_normal
                    stats_menu(game_manager)
                if replay_button.collidepoint(event.pos):
                    rp_color = rp_color_normal
                    replay_menu(game_manager)
            if event.type == pygame.MOUSEMOTION:  # Check if click is released
                if play_button.collidepoint(event.pos):
                    pl_color = pl_color_hover
                else:
                    pl_color = pl_color_normal
                if stats_button.collidepoint(event.pos):
                    st_color = st_color_hover
                else:
                    st_color = st_color_normal
                if replay_button.collidepoint(event.pos):
                    rp_color = rp_color_hover
                else:
                    rp_color = rp_color_normal

        screen.fill((30, 30, 30))

        # Draw title
        screen.blit(label_title_surface, label_title_position)

        # Draw buttons
        pygame.draw.rect(screen, pl_color, play_button, 0)
        screen.blit(play_button_surface, play_button_position)
        pygame.draw.rect(screen, st_color, stats_button, 0)
        screen.blit(stats_button_surface, stats_button_position)
        pygame.draw.rect(screen, rp_color, replay_button, 0)
        screen.blit(replay_button_surface, replay_button_position)

        pygame.display.flip()


def stats_menu(game_manager):
    """View stats of a player"""
    # Define colors
    c_white = pygame.Color(255, 255, 255)
    c_black = pygame.Color(0, 0, 0)
    c_textbox_inactive = pygame.Color(230, 230, 230)
    c_textbox_active = pygame.Color(180, 180, 170)
    c_red = pygame.Color(255, 0, 0)
    c_background = pygame.Color(30, 30, 30)

    # Set up display
    screen_width, screen_height = 780, 380
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_icon(pygame.transform.scale(pygame.image.load("images/icons/icon.png"), (32, 32)))
    pygame.display.set_caption('Hnefatafl - Estadísticas')

    # Load fonts
    font_face = 'Consolas'

    font_size = 14
    font = pygame.font.SysFont(font_face, font_size)

    font_size_title = 42
    font_title = pygame.font.SysFont(font_face, font_size_title, True)

    font_size_subtitle = 24
    font_subtitle = pygame.font.SysFont(font_face, font_size_subtitle)

    # Labels
    title_label_text = 'Estadísticas de jugadores'
    title_label_surface = font_title.render(title_label_text, True, c_white)
    title_label_position = (screen_width/2 - title_label_surface.get_width()/2, 15)

    name_label_text = 'Nombre del jugador: '
    name_label_surface = font_subtitle.render(name_label_text, True, c_white)
    name_label_position = (20, 70)

    wins_label_text = 'Victorias: '
    wins_label_surface = font_subtitle.render(wins_label_text, True, c_white)
    wins_label_position = (20, 120)

    losses_label_text = 'Derrotas: '
    losses_label_surface = font_subtitle.render(losses_label_text, True, c_white)
    losses_label_position = (20, 170)

    c_name_label_text = 'Nan'
    c_name_label_surface = font_subtitle.render(c_name_label_text, True, c_white)
    c_name_label_position = (name_label_position[0] + name_label_surface.get_width() + 10, 70)

    c_wins_label_text = 'NaN'
    c_wins_label_surface = font_subtitle.render(c_wins_label_text, True, c_white)
    c_wins_label_position = (wins_label_position[0] + wins_label_surface.get_width() + 10, 120)

    c_losses_label_text = 'NaN'
    c_losses_label_surface = font_subtitle.render(c_losses_label_text, True, c_white)
    c_losses_label_position = (losses_label_position[0] + losses_label_surface.get_width() + 10, 170)

    # Buttons
    select_button = pygame.Rect(screen_width/2 - 150, screen_height/2 + 50, 300, 50)
    select_button_text = 'Seleccionar Jugador'
    select_button_surface = font_subtitle.render(select_button_text, True, c_black)
    select_button_position = (select_button.x + select_button.width/2 - select_button_surface.get_width()/2, select_button.y + select_button.height/2 - select_button_surface.get_height()/2)
    sl_color_normal = c_white
    sl_color_hover = c_textbox_inactive
    sl_color_click = c_textbox_active
    sl_color = sl_color_normal

    back_button = pygame.Rect(20, screen_height - 50, 70, 30)
    back_button_text = 'Menú'
    back_button_surface = font.render(back_button_text, True, c_black)
    back_button_position = (back_button.x + back_button.width/2 - back_button_surface.get_width()/2, back_button.y + back_button.height/2 - back_button_surface.get_height()/2)
    bk_color_normal = c_red
    bk_color_hover = c_textbox_inactive
    bk_color_click = c_textbox_active
    bk_color = bk_color_normal

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Check if mouse is clicked
                if select_button.collidepoint(event.pos):
                    sl_color = sl_color_click
                if back_button.collidepoint(event.pos):
                    bk_color = bk_color_click

            if event.type == pygame.MOUSEBUTTONUP:  # Check if click is released
                if select_button.collidepoint(event.pos):
                    sl_color = sl_color_normal
                    file = open_file_browser('./PLAYERS/')
                    if file:  # Check a file was selected
                        player_data = process_player_file(file)
                        if player_data:  # Check the file is a valid player file
                            c_name_label_text = player_data[0]
                            c_wins_label_text = str(player_data[1])
                            c_losses_label_text = str(player_data[2])
                            c_name_label_surface = font_subtitle.render(c_name_label_text, True, c_white)
                            c_wins_label_surface = font_subtitle.render(c_wins_label_text, True, c_white)
                            c_losses_label_surface = font_subtitle.render(c_losses_label_text, True, c_white)
                        else:  # Inform of wrong json format
                            root = tk.Tk()
                            root.withdraw()
                            # Show a warning message box
                            messagebox.showwarning("Error", "Formato de archivo inválido!", icon=messagebox.ERROR)
                if back_button.collidepoint(event.pos):
                    bk_color = bk_color_normal
                    main_menu(game_manager)

            if event.type == pygame.MOUSEMOTION:  # Check if mouse is hovered over an object
                if select_button.collidepoint(event.pos):
                    sl_color = sl_color_hover
                else:
                    sl_color = sl_color_normal
                if back_button.collidepoint(event.pos):
                    bk_color = bk_color_hover
                else:
                    bk_color = bk_color_normal

        # Background color
        screen.fill(c_background)

        # Draw labels
        screen.blit(title_label_surface, title_label_position)
        screen.blit(name_label_surface, name_label_position)
        screen.blit(wins_label_surface, wins_label_position)
        screen.blit(losses_label_surface, losses_label_position)
        screen.blit(c_name_label_surface, c_name_label_position)
        screen.blit(c_wins_label_surface, c_wins_label_position)
        screen.blit(c_losses_label_surface, c_losses_label_position)

        # Draw buttons
        pygame.draw.rect(screen, sl_color, select_button, 0)
        screen.blit(select_button_surface, select_button_position)

        pygame.draw.rect(screen, bk_color, back_button, 0)
        screen.blit(back_button_surface, back_button_position)

        pygame.display.flip()



def replay_menu(game_manager):
    FILE = None  # File to replay

    """Watch replay of a game"""
    # Define colors
    c_white = pygame.Color(255, 255, 255)
    c_black = pygame.Color(0, 0, 0)
    c_textbox_inactive = pygame.Color(230, 230, 230)
    c_textbox_active = pygame.Color(180, 180, 170)
    c_red = pygame.Color(255, 0, 0)
    c_background = pygame.Color(30, 30, 30)
    
    # Set up display
    screen_width, screen_height = 720, 480
    screen = pygame.display.set_mode((screen_width, screen_height))

    # Set the window icon and caption
    pygame.display.set_icon(pygame.transform.scale(pygame.image.load("images/icons/icon.png"), (32, 32)))
    pygame.display.set_caption('Hnefatafl - Repeticiones')

    # Load fonts
    font_face = 'Consolas'

    font_size = 14
    font = pygame.font.SysFont(font_face, font_size)

    font_size_title = 42
    font_title = pygame.font.SysFont(font_face, font_size_title, True)

    font_size_subtitle = 24
    font_subtitle = pygame.font.SysFont(font_face, font_size_subtitle)

    # Labels
    title_label_text = 'Repeticiones de partidas'
    title_label_surface = font_title.render(title_label_text, True, c_white)
    title_label_position = (screen_width/2 - title_label_surface.get_width()/2, 15)

    replay_file_title_text = 'Archivo:'
    replay_file_title_surface = font_subtitle.render(replay_file_title_text, True, c_white)
    replay_file_title_position = (10, title_label_position[1] + title_label_surface.get_height() + 20)

    replay_file_text = '<Ningun archivo seleccionado>'
    replay_file_surface = font.render(replay_file_text, True, c_black)
    replay_file_position = (replay_file_title_surface.get_width() + 15, replay_file_title_position[1] + 5)

    replay_file_rect = replay_file_surface.get_rect()
    replay_file_rect.topleft = (replay_file_position[0], replay_file_position[1] - 5)
    replay_file_rect.width = screen_width - 207
    replay_file_rect.height = replay_file_title_surface.get_height()

    id_text = 'ID:'
    id_surface = font_subtitle.render(id_text, True, c_white)
    id_position = (10 , replay_file_title_position[1] + replay_file_title_surface.get_height() + 15)

    id_p_text = 'NaN'
    id_p_surface = font_subtitle.render(id_p_text, True, c_white)
    id_p_position = (id_position[0] + id_surface.get_width() + 10, id_position[1])

    gamemode_text = 'Modo de juego:'
    gamemode_surface = font_subtitle.render(gamemode_text, True, c_white)
    gamemode_position = (10, id_position[1] + id_surface.get_height() + 15)

    gamemode_g_text = 'NaN'
    gamemode_g_surface = font_subtitle.render(gamemode_g_text, True, c_white)
    gamemode_g_position = (gamemode_position[0] + gamemode_surface.get_width() + 10, gamemode_position[1])

    w_player_text = 'Blancas: '
    w_player_surface = font_subtitle.render(w_player_text, True, c_white)
    w_player_position = (10, gamemode_position[1] + gamemode_surface.get_height() + 15)

    w_player_p_text = 'NaN'
    w_player_p_surface = font_subtitle.render(w_player_p_text, True, c_white)
    w_player_p_position = (w_player_position[0] + w_player_surface.get_width() + 10, w_player_position[1])

    b_player_text = 'Negras: '
    b_player_surface = font_subtitle.render(b_player_text, True, c_white)
    b_player_position = (10, w_player_p_position[1] + w_player_p_surface.get_height() + 15)

    b_player_p_text = 'NaN'
    b_player_p_surface = font_subtitle.render(b_player_p_text, True, c_white)
    b_player_p_position = (b_player_position[0] + b_player_surface.get_width() + 10, b_player_position[1])

    winner_text = 'Ganador:'
    winner_surface = font_subtitle.render(winner_text, True, c_white)
    winner_position = (10, b_player_p_position[1] + b_player_p_surface.get_height() + 15)

    winner_p_text = 'NaN'
    winner_p_surface = font_subtitle.render(winner_p_text, True, c_white)
    winner_p_position = (winner_position[0] + winner_surface.get_width() + 10, winner_position[1])

    # Buttons
    back_button = pygame.Rect(20, screen_height - 50, 70, 30)
    back_button_text = 'Menu'
    back_button_surface = font.render(back_button_text, True, c_black)
    back_button_position = (back_button.x + back_button.width/2 - back_button_surface.get_width()/2, back_button.y + back_button.height/2 - back_button_surface.get_height()/2)
    bk_color_normal = c_red
    bk_color_hover = c_textbox_inactive
    bk_color_click = c_textbox_active
    bk_color = bk_color_normal

    select_button = pygame.Rect(screen_width - 80, title_label_position[1] + replay_file_rect.topleft[1] - replay_file_rect.height + 6, 70, 30)
    select_button_text = 'Buscar'
    select_button_surface = font.render(select_button_text, True, c_black)
    select_button_position = (select_button.x + select_button.width/2 - select_button_surface.get_width()/2, select_button.y + select_button.height/2 - select_button_surface.get_height()/2)
    sl_color_normal = c_white
    sl_color_hover = c_textbox_inactive
    sl_color_click = c_textbox_active
    sl_color = sl_color_normal

    play_button = pygame.Rect(screen_width/2 - 150, screen_height/2 + 85, 300, 100)
    play_button_text = 'Reproducir'
    play_button_surface = font_title.render(play_button_text, True, c_black)
    play_button_position = (play_button.x + play_button.width/2 - play_button_surface.get_width()/2, play_button.y + play_button.height/2 - play_button_surface.get_height()/2)
    pl_color_normal = c_white
    pl_color_hover = c_textbox_inactive
    pl_color_click = c_textbox_active
    pl_color = pl_color_normal

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Check if mouse is clicked
                if select_button.collidepoint(event.pos):
                    sl_color = sl_color_click
                if play_button.collidepoint(event.pos):
                    pl_color = pl_color_click
                if back_button.collidepoint(event.pos):
                    bk_color = bk_color_click
            if event.type == pygame.MOUSEBUTTONUP:  # Check if click is released
                if select_button.collidepoint(event.pos):
                    sl_color = sl_color_normal
                    # Reset all labels when opening
                    FILE = None
                    replay_file_text = '<Ningún archivo seleccionado>'
                    replay_file_surface = font.render(replay_file_text, True, c_black)
                    id_p_text = 'NaN'
                    id_p_surface = font_subtitle.render(id_p_text, True, c_white)
                    gamemode_g_text = 'NaN'
                    gamemode_g_surface = font_subtitle.render(gamemode_g_text, True, c_white)
                    w_player_p_text = 'NaN'
                    w_player_p_surface = font_subtitle.render(w_player_p_text, True, c_white)
                    b_player_p_text = 'NaN'
                    b_player_p_surface = font_subtitle.render(b_player_p_text, True, c_white)
                    winner_p_text = 'NaN'
                    winner_p_surface = font_subtitle.render(winner_p_text, True, c_white)
                    file = open_file_browser('./GAMES/')
                    if file:
                        game_data = process_game_file(file)  # Process the file data
                        if game_data:
                            replay_file_text = file.split('/')[-2] + '/' + file.split('/')[-1]
                            replay_file_surface = font.render(replay_file_text, True, c_black)
                            id_p_text = game_data[0]
                            id_p_surface = font_subtitle.render(id_p_text, True, c_white)
                            gamemode_g_text = game_data[4]
                            gamemode_g_surface = font_subtitle.render(gamemode_g_text, True, c_white)
                            w_player_p_text = game_data[1]
                            w_player_p_surface = font_subtitle.render(w_player_p_text, True, c_white)
                            b_player_p_text = game_data[2]
                            b_player_p_surface = font_subtitle.render(b_player_p_text, True, c_white)
                            winner_p_text = game_data[3]
                            winner_p_surface = font_subtitle.render(winner_p_text, True, c_white)
                            FILE = file  # Once data is checked, set the file
                        else:
                            root = tk.Tk()
                            root.withdraw()
                            # Show a warning message box
                            messagebox.showwarning("Error", "Formato de archivo inválido!", icon=messagebox.ERROR)
                if play_button.collidepoint(event.pos):
                    pl_color = pl_color_normal
                    if FILE:
                        game_manager.replay(game_data)  # Replay the game
                        main_menu(game_manager)
                    else:
                        root = tk.Tk()
                        root.withdraw()
                        # Show a warning message box
                        messagebox.showwarning("Error", "Selecciona un archivo válido!", icon=messagebox.ERROR)
                if back_button.collidepoint(event.pos):
                    bk_color = bk_color_normal
                    main_menu(game_manager)
            if event.type == pygame.MOUSEMOTION:  # Check if mouse is hovered over an object
                if select_button.collidepoint(event.pos):
                    sl_color = sl_color_hover
                else:
                    sl_color = sl_color_normal
                if play_button.collidepoint(event.pos):
                    pl_color = pl_color_hover
                else:
                    pl_color = pl_color_normal
                if back_button.collidepoint(event.pos):
                    bk_color = bk_color_hover
                else:
                    bk_color = bk_color_normal

        screen.fill(c_background)

        # Draw labels
        screen.blit(title_label_surface, title_label_position)
        screen.blit(replay_file_title_surface, replay_file_title_position)
        pygame.draw.rect(screen, c_white, replay_file_rect, 0)
        screen.blit(replay_file_surface, replay_file_position)
        screen.blit(w_player_surface, w_player_position)
        screen.blit(w_player_p_surface, w_player_p_position)
        screen.blit(b_player_surface, b_player_position)
        screen.blit(b_player_p_surface, b_player_p_position)
        screen.blit(gamemode_surface, gamemode_position)
        screen.blit(gamemode_g_surface, gamemode_g_position)
        screen.blit(winner_surface, winner_position)
        screen.blit(winner_p_surface, winner_p_position)
        screen.blit(id_surface, id_position)
        screen.blit(id_p_surface, id_p_position)
        
        # Draw buttons
        pygame.draw.rect(screen, sl_color, select_button, 0)
        screen.blit(select_button_surface, select_button_position)

        pygame.draw.rect(screen, pl_color, play_button, 0)
        screen.blit(play_button_surface, play_button_position)

        pygame.draw.rect(screen, bk_color, back_button, 0)
        screen.blit(back_button_surface, back_button_position)

        pygame.display.flip()


def play_menu(game_manager):
    """Show the game configuration menu"""
    WHITEPLAYER = None
    BLACKPLAYER = None
    GAME = None

    # Define colors
    c_white = pygame.Color(255, 255, 255)
    c_black = pygame.Color(0, 0, 0)
    c_textbox_inactive = pygame.Color(230, 230, 230)
    c_textbox_active = pygame.Color(180, 180, 170)
    c_red = pygame.Color(255, 0, 0)
    c_background = pygame.Color(30, 30, 30)
    
    # Set up display
    screen_width, screen_height = 720, 480
    screen = pygame.display.set_mode((screen_width, screen_height))

    # Set the window icon and caption
    pygame.display.set_icon(pygame.transform.scale(pygame.image.load("images/icons/icon.png"), (32, 32)))
    pygame.display.set_caption('Hnefatafl - Ajustes de partida')

    # Load fonts
    font_face = 'Consolas'

    font_size = 14
    font = pygame.font.SysFont(font_face, font_size)

    font_size_title = 42
    font_title = pygame.font.SysFont(font_face, font_size_title, True)

    font_size_subtitle = 24
    font_subtitle = pygame.font.SysFont(font_face, font_size_subtitle)

    # Labels
    title_label_text = 'Parámetros de partida'
    title_label_surface = font_title.render(title_label_text, True, c_white)
    title_label_position = (screen_width/2 - title_label_surface.get_width()/2, 15)

    white_label_text = 'Jugador blancas'
    white_label_surface = font_subtitle.render(white_label_text, True, c_white)
    white_label_position = (20, 70)

    black_label_text = 'Jugador negras'
    black_label_surface = font_subtitle.render(black_label_text, True, c_white)
    black_label_position = (screen_width - 20 - black_label_surface.get_width(), 70)

    w_type_label_text = 'Tipo Blancas'
    w_type_label_surface = font_subtitle.render(w_type_label_text, True, c_white)
    w_type_label_position = (20, 150)

    b_type_label_text = 'Tipo Negras'
    b_type_label_surface = font_subtitle.render(b_type_label_text, True, c_white)
    b_type_label_position = (screen_width - 20 - b_type_label_surface.get_width(), 150)

    board_type_label_text = 'Modo de juego'
    board_type_label_surface = font_subtitle.render(board_type_label_text, True, c_white)
    board_type_label_position = (screen_width/2 - board_type_label_surface.get_width()/2, 150)

    warning_name_text = 'CPU no puede tener nombre'

    warning_name_surface_w = font.render(warning_name_text, True, c_red)
    warning_name_position_w = (20, 105)

    warning_name_surface_b = font.render(warning_name_text, True, c_red)
    warning_name_position_b = (screen_width - 20 - warning_name_surface_b.get_width(), 105)

    warning_game_text = 'Q-Learning solo disponible en Brandubh'
    warning_game_text_2 = 'Se usará CPU random por defecto'

    warning_game_surface = font.render(warning_game_text, True, c_red)
    warning_game_position = (screen_width/2 - warning_game_surface.get_width()/2, 270)

    warning_game_surface_2 = font.render(warning_game_text_2, True, c_red)
    warning_game_position_2 = (screen_width/2 - warning_game_surface_2.get_width()/2, warning_game_position[1] + 15)

    # Text boxes
    white_name_box = pygame.Rect(10, 100, 300, font_size+8) # Left, Top, Width, Height
    white_name_active = False
    white_name_color = c_textbox_inactive
    white_name_text = ''
    white_name_txt = font.render(white_name_text, True, c_black)
        
    black_name_box = pygame.Rect(screen_width-310, 100, 300, font_size+8) # Left, Top, Width, Height
    black_name_active = False
    black_name_color = c_textbox_inactive
    black_name_text = ''
    black_name_txt = font.render(black_name_text, True, c_black)

    # Radio buttons
    player_type_rb_height, player_type_rb_width = font_size+8, 100
    player_type_rb_text = ['Humano', 'Random', 'MiniMax', 'Montecarlo', 'MiniRandom', 'Q-Learning']
    board_types = ['Brandubh', 'Tafl', 'Fetlar']
    option_separation = 25

    w_player_type_rb = [pygame.Rect(20, (white_name_box.top + 80) + i * option_separation, player_type_rb_width, player_type_rb_height) for i in range(6)]
    w_player_type_rb_checked = [True, False, False, False, False, False]

    b_player_type_rb = [pygame.Rect(screen_width - 20 - player_type_rb_width, (black_name_box.top + 80) + i * option_separation, player_type_rb_width, player_type_rb_height) for i in range(6)]
    b_player_type_rb_checked = [True, False, False, False, False, False]

    board_type_rb = [pygame.Rect(screen_width/2 - player_type_rb_width/2, (black_name_box.top + 80) + i * option_separation, player_type_rb_width, player_type_rb_height) for i in range(3)]
    board_type_rb_checked = [True, False, False]

    # Buttons
    play_button = pygame.Rect(screen_width/2 - 100, screen_height/2 + 75, 200, 100)
    play_button_text = 'Jugar'
    play_button_surface = font_title.render(play_button_text, True, c_black)
    play_button_position = (play_button.x + play_button.width/2 - play_button_surface.get_width()/2, play_button.y + play_button.height/2 - play_button_surface.get_height()/2)
    pl_color_normal = c_white
    pl_color_hover = c_textbox_inactive
    pl_color_click = c_textbox_active
    pl_color = pl_color_normal

    back_button = pygame.Rect(20, screen_height - 50, 70, 30)
    back_button_text = 'Menú'
    back_button_surface = font.render(back_button_text, True, c_black)
    back_button_position = (back_button.x + back_button.width/2 - back_button_surface.get_width()/2, back_button.y + back_button.height/2 - back_button_surface.get_height()/2)
    bk_color_normal = c_red
    bk_color_hover = c_textbox_inactive
    bk_color_click = c_textbox_active
    bk_color = bk_color_normal

    
    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check for window closed
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:  # Check if mouse is clicked
                # Check colision with the white name box
                if white_name_box.collidepoint(event.pos) and w_player_type_rb_checked[0]:
                    white_name_active = True
                    white_name_color = c_textbox_active
                else:
                    white_name_active = False
                    white_name_color = c_textbox_inactive
                # Check colision with the white name box
                if black_name_box.collidepoint(event.pos) and b_player_type_rb_checked[0]:  
                    black_name_active = True
                    black_name_color = c_textbox_active
                else:
                    black_name_active = False
                    black_name_color = c_textbox_inactive
                # Check colision with the white player type radio buttons
                for i, rect in enumerate(w_player_type_rb):
                    if rect.collidepoint(event.pos):
                        w_player_type_rb_checked = [False] * len(w_player_type_rb_checked)  # Deselect all
                        w_player_type_rb_checked[i] = True  # Select the clicked one
                # Check colision with the black player type radio buttons
                for i, rect in enumerate(b_player_type_rb):
                    if rect.collidepoint(event.pos):
                        b_player_type_rb_checked = [False] * len(b_player_type_rb_checked) # Deselect all
                        b_player_type_rb_checked[i] = True  # Select the clicked one
                # Check colision with the board type radio buttons
                for i, rect in enumerate(board_type_rb):
                    if rect.collidepoint(event.pos):
                        board_type_rb_checked = [False] * len(board_type_rb_checked) # Deselect all
                        board_type_rb_checked[i] = True  # Select the clicked one
                # Check colision with the play button
                if play_button.collidepoint(event.pos):
                    pl_color = pl_color_click
                if back_button.collidepoint(event.pos):
                    bk_color = bk_color_click

            if event.type == pygame.MOUSEBUTTONUP:  # Check if click is released
                if play_button.collidepoint(event.pos):
                    pl_color = pl_color_normal
                    # Get the white player
                    if w_player_type_rb_checked[0]:  # If white player is human
                        if white_name_text == '':  # If white player name is empty
                                WHITEPLAYER = 'Anonimo (Blancas)'
                        else:  # If white player name is not empty
                            WHITEPLAYER = white_name_text
                    elif w_player_type_rb_checked[1]:  # If white player is random
                        WHITEPLAYER = 'CPU 0'
                    elif w_player_type_rb_checked[2]:  # If white player is minimax
                        WHITEPLAYER = 'CPU 1'
                    elif w_player_type_rb_checked[3]:  # If white player is montecarlo
                        WHITEPLAYER = 'CPU 2'
                    elif w_player_type_rb_checked[4]:  # If white player is MiniRandom
                        WHITEPLAYER = 'CPU 5'
                    elif w_player_type_rb_checked[5]:  # If white player is Q-Learning (white)
                        # If the game is not Brandubh, the black player is the random and a warning message is shown
                        if not board_type_rb_checked[0]:
                            WHITEPLAYER = 'CPU 0'
                            print('Warning: Q-Learning is not available for this game type, use Brandubh instead')
                            print('WHITE CPU Level set to Random')
                        WHITEPLAYER = 'CPU 4'
                    # Get the black player
                    if b_player_type_rb_checked[0]:  # If black player is human
                        if black_name_text == '':  # If black player name is empty
                            BLACKPLAYER = 'Anonimo (Negras)'
                        else:  # If black player name is not empty
                            BLACKPLAYER = black_name_text
                    elif b_player_type_rb_checked[1]:  # If black player is random
                        BLACKPLAYER = 'CPU 0'
                    elif b_player_type_rb_checked[2]:  # If black player is minimax
                        BLACKPLAYER = 'CPU 1'
                    elif b_player_type_rb_checked[3]:  # If black player is montecarlo
                        BLACKPLAYER = 'CPU 2'
                    elif b_player_type_rb_checked[4]:  # If black player is MiniRandom
                        BLACKPLAYER = 'CPU 5'
                    elif b_player_type_rb_checked[5]:  # If black player is Q-Learning (black)
                        # If the game is not Brandubh, the black player is the random and a warning message is shown
                        if not board_type_rb_checked[0]:
                            BLACKPLAYER = 'CPU 0'
                            print('Warning: Q-Learning is not available for this game type, use Brandubh instead')
                            print('BLACK CPU Level set to Random')
                        else:
                            BLACKPLAYER = 'CPU 3'
                    # Get the game type
                    if board_type_rb_checked[0]:  # If the game is Brandubh
                        GAME = 'Brandubh'
                    elif board_type_rb_checked[1]:  # If the game is Tafl
                        GAME = 'Tafl'
                    elif board_type_rb_checked[2]:  # If the game is Fetlar
                        GAME = 'Fetlar'
                    start_game(WHITEPLAYER, BLACKPLAYER, GAME, game_manager)  # Start the game
                    pygame.display.flip()
                    main_menu(game_manager)
                    
                if back_button.collidepoint(event.pos):
                    bk_color = bk_color_normal
                    main_menu(game_manager)

            if event.type == pygame.MOUSEMOTION:  
                # Check colision with the play button
                if play_button.collidepoint(event.pos):
                    pl_color = pl_color_hover
                else:
                    pl_color = pl_color_normal 
                if back_button.collidepoint(event.pos):
                    bk_color = bk_color_hover
                else:
                    bk_color = bk_color_normal      
                    
            # Check for key presses
            if event.type == pygame.KEYDOWN:
                # Check if the white name box is active
                if white_name_active:
                    if event.key == pygame.K_BACKSPACE:  # Delete a chat
                        white_name_text = white_name_text[:-1]
                    elif event.key == pygame.K_RETURN:  # Unfous the text box
                        white_name_active = False
                        white_name_color = c_textbox_inactive
                    else:
                        if len(white_name_text) < 30 and w_player_type_rb_checked[0]:  # Max 30 characters and human player
                            white_name_text += event.unicode
                    # Re-render the text
                    white_name_txt = font.render(white_name_text, True, c_black)
                # Check if the black name box is active
                if black_name_active: 
                    if event.key == pygame.K_BACKSPACE:  # Delete a chat
                        black_name_text = black_name_text[:-1]
                    elif event.key == pygame.K_RETURN:  # Unfous the text box
                        black_name_active = False
                        black_name_color = c_textbox_inactive
                    else:
                        if len(black_name_text) < 30:  # Max 30 characters
                            black_name_text += event.unicode
                    # Re-render the text
                    black_name_txt = font.render(black_name_text, True, c_black)


        # Background color
        screen.fill(c_background)  

        # Draw text boxes
        pygame.draw.rect(screen, white_name_color, white_name_box, 0)
        pygame.draw.rect(screen, black_name_color, black_name_box, 0)

        screen.blit(white_name_txt, (white_name_box.x + 5, white_name_box.y + 5))
        screen.blit(black_name_txt, (black_name_box.x + 5, black_name_box.y + 5))

        # Draw labels
        screen.blit(title_label_surface, title_label_position)
        screen.blit(white_label_surface, white_label_position)
        screen.blit(black_label_surface, black_label_position)
        screen.blit(w_type_label_surface, w_type_label_position)
        screen.blit(b_type_label_surface, b_type_label_position)
        screen.blit(board_type_label_surface, board_type_label_position)
        if not w_player_type_rb_checked[0]:  # If white player is not human
            screen.blit(warning_name_surface_w, warning_name_position_w)
        if not b_player_type_rb_checked[0]:  # If black player is not human
            screen.blit(warning_name_surface_b, warning_name_position_b)
        if not board_type_rb_checked[0] and (w_player_type_rb_checked[5] or b_player_type_rb_checked[5]):  # If the game is not Brandubh and a Q-Learning player is selected
            screen.blit(warning_game_surface, warning_game_position)
            screen.blit(warning_game_surface_2, warning_game_position_2)

        # Draw radio buttons
        for i, rect in enumerate(w_player_type_rb):  # Draw white player radio buttons
            pygame.draw.rect(screen, c_white, rect, 0)
            if w_player_type_rb_checked[i]:
                pygame.draw.rect(screen, c_red, rect, 2)
            text = font.render(player_type_rb_text[i], True, c_black)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
        for i, rect in enumerate(b_player_type_rb):  # Draw black player radio buttons
            pygame.draw.rect(screen, c_white, rect, 0)
            if b_player_type_rb_checked[i]:
                pygame.draw.rect(screen, c_red, rect, 2)
            text = font.render(player_type_rb_text[i], True, c_black)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
        for i, rect in enumerate(board_type_rb):  # Draw board type radio buttons
            pygame.draw.rect(screen, c_white, rect, 0)
            if board_type_rb_checked[i]:
                pygame.draw.rect(screen, c_red, rect, 2)
            text = font.render(board_types[i], True, c_black)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
        # Handle radio buttons text interaction (CPU can't have a name so it is cleared)
        if not w_player_type_rb_checked[0]:  # If white player is not human
            white_name_text = ''  # Clear the name
            white_name_txt = font.render(white_name_text, True, c_black)  # Re-render the text
        if not b_player_type_rb_checked[0]:  # If black player is not human
            black_name_text = ''  # Clear the name
            black_name_txt = font.render(black_name_text, True, c_black)  # Re-render the text

        # Draw buttons
        pygame.draw.rect(screen, pl_color, play_button, 0)
        screen.blit(play_button_surface, play_button_position)
        pygame.draw.rect(screen, bk_color, back_button, 0)
        screen.blit(back_button_surface, back_button_position)
        
        pygame.display.flip()  # Update the display

def start_game(player_white, player_black, game_type, game_manager):
    """Start a game"""
    game_manager.new_game(game_type)  # Create a new game
    # Add the players
    game_manager.join_game(0,player_black) 
    game_manager.join_game(1, player_white)
    winner = game_manager.start_game()  # Play the game
    game_manager.result(winner)  # Save the results
    game_manager.reset_server()  # Reset the server
