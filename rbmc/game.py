import chess
from abc import abstractmethod
from datetime import datetime
from .types import *
from .player import Player


class Game(object):
    @abstractmethod
    def valid_senses(self) -> List[Square]:
        pass

    @abstractmethod
    def valid_moves(self) -> List[chess.Move]:
        pass

    @abstractmethod
    def get_seconds_left(self) -> float:
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def opponent_move_results(self) -> Optional[Square]:
        pass

    @abstractmethod
    def sense(self, square: Square) -> List[Tuple[Square, chess.Piece]]:
        pass

    @abstractmethod
    def move(self, requested_move: chess.Move) -> Tuple[chess.Move, chess.Move, Optional[Square]]:
        pass

    @abstractmethod
    def end_turn(self):
        pass

    @abstractmethod
    def is_over(self):
        pass

    @abstractmethod
    def get_winner_color(self) -> Optional[Color]:
        pass

    @abstractmethod
    def get_sense_history_for(self, color: Color) -> List[Square]:
        pass

    @abstractmethod
    def get_move_history_for(self, color: Color) -> List[chess.Move]:
        pass


class LocalGame(Game):
    """Would implement all logic and use a chess.Board() object as the truth board"""

    def __init__(self, seconds_per_player: float = 900):
        self.turn = chess.WHITE
        self.board = chess.Board()

        self.seconds_left_by_color = {chess.WHITE: seconds_per_player, chess.BLACK: seconds_per_player}
        self.current_turn_start_time = None

    def start(self):
        """
        Starts off the clock for the first player.
        :return: None.
        """
        self.current_turn_start_time = datetime.now()

    def get_seconds_left(self) -> float:
        """
        :return: The amount of seconds left for the current player.
        """
        if self.current_turn_start_time:
            elapsed_since_turn_start = (datetime.now() - self.current_turn_start_time).total_seconds()
            return self.seconds_left_by_color[self.turn] - elapsed_since_turn_start
        else:
            return self.seconds_left_by_color[self.turn]

    def valid_senses(self) -> List[Square]:
        """
        :return: List of squares that are in the inside 6x6 square in the board.
        """
        return [i for i in chess.SQUARES if not (i % 8 == 0 or i % 8 == 7 or i < 8 or i >= 56)]

    def end_turn(self):
        """
        Used for bookkeeping. Does the following:

        #. Updates the time used for the current player
        #. Ends the turn for the current player
        #. Starts the timer for the next player

        :return: None
        """
        elapsed = datetime.now() - self.current_turn_start_time
        self.seconds_left_by_color[self.turn] -= elapsed.total_seconds()

        self.turn = not self.turn
        self.current_turn_start_time = datetime.now()


class RemoteGame(Game):
    """A pass through object, would implement the methods as making a request to the game server"""

    def __init__(self, game_id):
        super().__init__()
        self.game_id = game_id
        self.latest_status = None

    def get_player_color(self, name):
        """Would request the color of the player from the server"""
        return chess.WHITE

    def get_starting_board(self):
        return chess.Board()

    def wait_for_turn(self, name):
        """
        Would request turn information from the server, and return when its the player's turn.
        Could either do:
        1. Busy wait, where server instantly returns response indicating the turn
        2. Server wait, where server doesn't send response until its the turn. Not sure if this would run into timeout
        issues.
        """
        pass


def play_local_game(white_player: Player, black_player: Player) \
        -> Tuple[Optional[Color], List[Square], List[chess.Move], List[Square], List[chess.Move]]:
    players = [black_player, white_player]

    game = LocalGame()

    white_player.handle_game_start(chess.WHITE, game.board.copy())
    black_player.handle_game_start(chess.BLACK, game.board.copy())
    game.start()

    while not game.is_over():
        play_turn(game, players[game.turn])

    winner_color = game.get_winner_color()
    white_senses = game.get_sense_history_for(chess.WHITE)
    white_moves = game.get_move_history_for(chess.WHITE)
    black_senses = game.get_sense_history_for(chess.BLACK)
    black_moves = game.get_move_history_for(chess.BLACK)

    white_player.handle_game_end(winner_color, white_senses, white_moves, black_senses, black_moves)
    black_player.handle_game_end(winner_color, black_senses, black_moves, white_senses, white_moves)

    return winner_color, white_senses, white_moves, black_senses, black_moves


def play_remote_game(name, game_id, player: Player):
    game = RemoteGame(game_id)

    color = game.get_player_color(name)

    player.handle_game_start(color, game.get_starting_board())
    game.start()

    while not game.is_over():
        game.wait_for_turn(name)
        play_turn(game, player)

    player.handle_game_end(game.get_winner_color(), game.get_sense_history_for(color), game.get_move_history_for(color),
                           game.get_sense_history_for(not color), game.get_move_history_for(not color))


def play_turn(game: Game, player: Player):
    # ally captured
    opt_capture_square = game.opponent_move_results()
    player.handle_opponent_move_result(opt_capture_square is not None, opt_capture_square)

    valid_senses = game.valid_senses()
    valid_moves = game.valid_moves()

    # sense
    sense = player.choose_sense(game.get_seconds_left(), valid_senses, valid_moves)
    sense_result = game.sense(sense)
    player.handle_sense_result(sense_result)

    # move
    move = player.choose_move(game.get_seconds_left(), valid_moves)
    requested_move, taken_move, opt_enemy_capture_square = game.move(move)
    player.handle_move_result(requested_move, taken_move,
                              opt_enemy_capture_square is not None, opt_enemy_capture_square)

    # end turn
    game.end_turn()
