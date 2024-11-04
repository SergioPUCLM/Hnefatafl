import json
import hashlib
import datetime
import os

import player as pl
from game import Game


class Server():
    """Creates the games and registers the results of the games"""
    pl_white = None
    pl_black = None
    game = None
    game_id = None
    game_name = None
    winner = None # 0 = Draw, 1 = Player 1, 2 = Player 2

    directory = 'GAMES'  # Directory for the saved games
    if not os.path.exists(directory):  # Create the games directory
            os.makedirs(directory)


    def __init__(self):
        print(f'Server started at {datetime.datetime.now()}')  # Print the server start time


    def new_game(self, game_name):
        """Create a new game with the manager"""
        Server.game_name = game_name  # Name of the game
        Server.game = Game(self.game_name)  # Create the game object
        Server.game_id = self.gen_id() # Generate a unique game id


    def gen_id(self):
        """Generate a unique game id
        """
        date = datetime.datetime.now().date()
        date_string = date.strftime("%Y-%m-%d")  # Output: 'YYYY-MM-DD'
        time = datetime.datetime.now().time()
        time_string = time.strftime("%H:%M:%S")  # Output: 'HH:MM:SS'
        string = f'{Server.game_name}-{date_string}-{time_string}'

        md5 = hashlib.md5(string.encode()).hexdigest()
        return f'{Server.game_name}-{md5}'  # ID = Name-MD5


    def join_game(self, gamer, player_name):
        """Add a player to the game (gamer = 0/1 for black/white, player_name = name of the player or CPU 0-5)
        """
        new_player = None  # New player to be added

        if player_name == "CPU 0": # If the player is the random CPU
            new_player = pl.PlayerRandom(Server.game.current_state, "CPU 0")
        elif player_name == "CPU 1": # If the player is the minimax CPU
            new_player = pl.PlayerMiniMax(Server.game.current_state, 50,"CPU 1")
        elif player_name == "CPU 2": # If the player is the montecarlo CPU
            new_player = pl.PlayerMontecarlo(Server.game.current_state, "CPU 2", 650)
        elif player_name == "CPU 3": # If the player is the qlearning CPU
            new_player = pl.PlayerQLearningBlack(Server.game.current_state, "CPU 3")
        elif player_name == "CPU 4": # If the player is the white qlearning CPU
            new_player = pl.PlayerQLearningWhite(Server.game.current_state, "CPU 4")
        elif player_name == "CPU 5": # If the player is the qlearning CPU
            new_player = pl.PlayerMiniRandom(Server.game.current_state, 2, "CPU 5")
        else:  # If the player is human
            new_player = pl.PlayerHuman(Server.game.current_state, player_name)

        if gamer == 0: # Black
            if Server.pl_black is None:
                Server.pl_black = new_player
                Server.game.black_player = new_player
            else:
                raise Player_Already_Joined(gamer)
        elif gamer == 1: # White
            if Server.pl_white is None:
                Server.pl_white = new_player
                Server.game.white_player = new_player
            else:
                raise Player_Already_Joined(gamer)


    def result(self, winner):
        """Get the results of the game and save them to a JSON"""
        Server.winner = winner  # Set the winner of the game
        results = self.parse_results()

        # Update the player statistics
        if Server.winner == 0:  # Black won
            Server.pl_black.wins += 1
            Server.pl_white.loses += 1
        elif Server.winner == 1:  # White won
            Server.pl_white.wins += 1
            Server.pl_black.loses += 1
            
        # Save new player statistics
        Server.pl_black.save_stats()
        Server.pl_white.save_stats() 

        with open(f'{Server.directory}/{Server.game_id}.json', 'w', encoding='utf-8') as f:
             json.dump(results, f, indent=4, ensure_ascii=False)
        return results
    

    def replay(self, game_data):
        """Replay the game"""
        Server.game_name = game_data[4]
        Server.game = Game(self.game_name)
        Server.game_id = game_data[0]
        Server.game.game_states = game_data[5]
        if game_data[3] == game_data[1]:
            Server.winner = 1
        elif game_data[3] == game_data[2]:
            Server.winner = 2
        else:
            Server.winner = 0
        # Create dummy players
        Server.game.white_player = pl.PlayerReplay(game_data[1], game_data[5][0])
        Server.game.black_player = pl.PlayerReplay(game_data[2], game_data[5][0])
        Server.game.replay(game_data[5], Server.winner)
        return


    def parse_results(self):
        """Parse the results of the game to a JSON string"""
        # Get the winner's name
        if Server.winner == 0:  # Black wins
            winner = Server.pl_black.name
        elif Server.winner == 1:  # White wins
            winner = Server.pl_white.name
        elif Server.winner == 2:  # Draw
            winner = 'None'

        results_string = {
            "game": Server.game_name,
            "pl_black": Server.pl_black.name,
            "pl_white": Server.pl_white.name,
            "winner": winner,
            "game_states": Server.game.game_states
        }
        return results_string


    def reset_server(self):  # Call when a game is over
        """Reset the server
        """
        Server.pl_black = None
        Server.pl_white = None
        Server.game = None
        Server.game_id = None
        Server.game_name = None
        Server.winner = None
        print(f'Server reset at {datetime.datetime.now()}')


    def start_game(self):
        """Method which starts a game
        """
        if Server.pl_black is None or Server.pl_white is None:
            raise Missing_Players()
        else:
           return Server.game.play_game(Server.pl_black, Server.pl_white)


class Player_Already_Joined(Exception):  # There is already a player asigned to that color
    def __init__(self, gamer):
        gamer_color = 'UNKNOWN'
        if gamer == 0:
            gamer_color = 'Black'
        elif gamer == 1:
            gamer_color = 'White'
        self.message = f'Player {gamer_color} already has a player object assigned to it.'
        super().__init__(self.message)


class Missing_Players(Exception):  # There are not 2 players asigned to the game
    def __init__(self):
        self.message = f'Game does not have 2 players assigned to it.'
        super().__init__(self.message)
            