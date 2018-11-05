import os
import sys
import importlib
import inspect
from abc import abstractmethod
import chess
from .types import *


class Player(object):
    """
    The Player class is used to implement a player of Recon Chess. It has methods to implement sensing and moving,
    as well as other methods to get information about the game.

    The intention is to make a class that extends the Player object, and implement each of the methods.

    The order in which each of the methods are called looks roughly like this:

    1. handle_game_start()
    3. handle_opponent_move_result()
    4. choose_sense()
    5. handle_sense_result()
    6. choose_move()
    7. handle_move_result()
    9. handle_game_end()

    Note that the handle_game_start() and handle_game_end() methods are only called at the start and the end of the game
    respectively. The rest are called repeatedly for each of your turns.
    """

    @abstractmethod
    def handle_game_start(self, color: Color, board: chess.Board):
        """
        Called when the game starts. The intent of this function is to provide a place to initialize game wide
        structures like boards and things that depend on what color you are playing as.

        The board is provided to allow starting a game from different board positions.

        :param color: The color that you are playing as.
        :param board: The initial board of the game.
        :return: None
        """
        pass

    @abstractmethod
    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        """
        Called after Player::handle_turn_start() is invoked. Indicates what happened on the opponents turn.

        TODO provide example implementation

        :param captured_my_piece: True if the opponent captured one of your pieces, False otherwise
        :param capture_square: None if captured_my_piece is False, otherwise the square your piece was captured on
        :return: None
        """
        pass

    @abstractmethod
    def choose_sense(self, seconds_left: float, valid_senses: List[Square], valid_moves: List[chess.Move]) -> Square:
        """
        Called when you need to make a sensing action. The return value is the square at the center of the 3x3 sensing
        area. The returned square must be one of the squares in the `valid_senses` parameter.

        Valid moves are provided in case you want to sense based on a potential move.

        TODO provide example implementation

        :param seconds_left: The time in seconds you have left to use in the game.
        :param valid_senses: A `list` containing the valid squares to return.
        :param valid_moves: A `list` containing the valid moves that can be returned in Player::choose_move.
        :return: a Square that is the center of the 3x3 sensing area you want to get information about.
        """
        pass

    @abstractmethod
    def handle_sense_result(self, sense_result: List[Tuple[Square, chess.Piece]]):
        """
        Called after Player::choose_sense() is invoked. This method is used for processing the results of your sense.

        TODO provide example implementation

        :param sense_result: The result of the sense. A `list` of tuples containing a Square and a chess.Piece.
        :return: None
        """
        pass

    @abstractmethod
    def choose_move(self, seconds_left: float, valid_moves: List[chess.Move]) -> chess.Move:
        """
        Called when you need to make a moving action. The return value is the move that you want to take, and must be
        contained in the `valid_moves` parameter.

        TODO provide example implementation

        :param seconds_left: The time in seconds you have left to use in the game.
        :param valid_moves: A `list` containing the valid moves you can make.
        :return: The chess.Move to make.
        """
        pass

    @abstractmethod
    def handle_move_result(self, requested_move: chess.Move, taken_move: chess.Move,
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        """
        Called after Player::choose_move() is invoked. This method is used for processing the results of your move.

        This method can be used to do post processing after your turn ends. Your opponent will be taking their turn
        while this method runs.

        Note that if this method takes a long time, your opponent may finish their turn before this method finishes.
        In that case, this method will count against your time.

        TODO provide example implementation

        :param requested_move: The chess.Move you requested in Player::choose_move().
        :param taken_move: The chess.Move that was actually applied by the game.
        :param captured_opponent_piece: True if the move resulted in a capture, False otherwise
        :param capture_square: None if not captured_piece, otherwise the square that the opponent piece was taken on
        :return: None
        """
        pass

    @abstractmethod
    def handle_game_end(self, winner_color: Optional[Color], senses: List[Square], moves: List[chess.Move],
                        opponent_senses: List[Square], opponent_moves: List[chess.Move]):
        """
        Called when the game ends. This method can be used to process the results of the game.

        :param winner_color: The color of the player who won the game. In the result of a draw, this will be None.
        :param senses: A `list` of senses you made during the game.
        :param moves: A `list` of moves you made during the game.
        :param opponent_senses: A `list` of senses the opponent made during the game.
        :param opponent_moves: A `list` of moves the opponent made during the game.
        :return: None
        """
        pass


def load_player(source_path: str) -> Tuple[str, Type[Player]]:
    """
    Loads a subclass of the Player class that is contained in a python source file. There must only be *1* such
    subclass in the file.

    ex.
    ```python
    name, cls = load_player('my_player.py')
    player = cls()
    ```

    :param source_path: the path to the source file to load
    :return: (name of class, class type)
    """
    # get the path to the main source file
    abs_source_path = os.path.abspath(source_path)

    # insert the directory of the bot source file into system path so we can import it
    # note: insert it first so we know we are searching this first
    sys.path.insert(0, os.path.dirname(abs_source_path))

    # import_module expects a module name, so remove the extension
    package_name = os.path.splitext(os.path.basename(abs_source_path))[0]
    module = importlib.import_module(package_name)
    players = inspect.getmembers(module, lambda o: inspect.isclass(o) and issubclass(o, Player) and o != Player)
    if len(players) == 0:
        raise RuntimeError('{} did not contain any subclasses of {}'.format(source_path, Player))
    elif len(players) > 1:
        raise RuntimeError(
            '{} contained multiple subclasses of {}: {}. Should have exactly 1'.format(source_path, players, Player))
    return players[0]
