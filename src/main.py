import json
from hashlib import md5

from state import State, Node
from create_json import createJsonFile


def getInitialState(filename, game):  #TODO: <-- Maybe make this get called when creating the board?
    """Get the initial state from a JSON file."""
    with open(filename, 'r') as f:
        variants = json.load(f)
        
    for variant in variants:
        if variant["name"] == game:
            init_state = variant["init_state"]
            return State(
                ID=init_state.get("ID", 0),
                whites=init_state.get("white", []),
                blacks=init_state.get("black", []),
                king=init_state.get("king", 0),
                turn=init_state.get("gamer", 0)
            )
    raise ValueError("Game variant not found in the JSON file.")


def main():
    # Files where variants and states will be 
    GAMESFILE = 'INITSTATES.json'  # File where the gamemodes will be stored
    STATESFILE = 'STATES.json'  # File where the states will be saved

    createJsonFile(GAMESFILE)  # Create the JSON file
    game = 'Brandubh'  # Chosen game
    initialState = getInitialState(GAMESFILE, game)  # Create the initial state
    initialState.toString()
    print()
    initialState.drawBoard()


if __name__ == main():
    main()
