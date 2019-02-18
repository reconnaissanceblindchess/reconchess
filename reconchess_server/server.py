from flask import Flask, request
from reconchess import Game

app = Flask(__name__)

last_game_id = 0
game_by_id = {}


@app.route('/api/player/register')
def api_player_register():
    pass


@app.route('/api/game/new')
def api_game_new():
    """
    Start a game. contents should be json array with name of players the game should be between
    :return: game id
    """
    global last_game_id
    last_game_id += 1
    game_by_id[last_game_id] = Game()
    return last_game_id


@app.route('/api/challenge/get')
def api_challenge_get():
    pass


@app.route('/api/challenge/invite')
def api_challenge_invite():
    pass


@app.route('/api/challenge/accept')
def api_challenge_accept():
    pass


@app.route('/api/game/<game_id>/is_over')
def api_game_is_over(game_id):
    pass


@app.route('/api/game/<game_id>/sense_actions')
def api_game_sense_actions(game_id):
    pass


@app.route('/api/game/<game_id>/move_actions')
def api_game_move_actions(game_id):
    pass


@app.route('/api/game/<game_id>/start_turn')
def api_game_start_turn(game_id):
    pass


@app.route('/api/game/<game_id>/opponent_move_results')
def api_game_opponent_move_results(game_id):
    pass


@app.route('/api/game/<game_id>/sense')
def api_game_sense(game_id):
    pass


@app.route('/api/game/<game_id>/move')
def api_game_move(game_id):
    pass


@app.route('/api/game/<game_id>/end_turn')
def api_game_end_turn(game_id):
    pass


@app.route('/api/game/<game_id>/color')
def api_game_color(game_id):
    pass


@app.route('/api/game/<game_id>/wait_for_turn')
def wait_for_turn(game_id):
    pass
