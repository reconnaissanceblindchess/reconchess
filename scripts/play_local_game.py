import argparse
from recon_chess.players import load_player
from recon_chess.game import play_local_game

parser = argparse.ArgumentParser()
parser.add_argument('white_bot_path', help='path to white bot source file')
parser.add_argument('black_bot_path', help='path to black bot source file')
args = parser.parse_args()

white_bot_name, white_player_cls = load_player(args.white_bot_path)
black_bot_name, black_player_cls = load_player(args.black_bot_path)

play_local_game(white_player_cls(), black_player_cls())
