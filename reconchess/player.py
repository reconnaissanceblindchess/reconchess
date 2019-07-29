import os
import sys
import importlib
import inspect
from abc import abstractmethod
import chess
from .types import *
from .history import GameHistory


class Player(object):
    """
    Base class of a player of Recon Chess. Implementation of a player is done by sub classing this class, and
    implementing each of the methods detailed below. For examples see `examples`.

    The order in which each of the methods are called looks roughly like this:

    #. :meth:`handle_game_start()`
    #. :meth:`handle_opponent_move_result()`
    #. :meth:`choose_sense()`
    #. :meth:`handle_sense_result()`
    #. :meth:`choose_move()`
    #. :meth:`handle_move_result()`
    #. :meth:`handle_game_end()`

    Note that the :meth:`handle_game_start()` and :meth:`handle_game_end()` methods are only called at the start and
    the end of the game respectively. The rest are called repeatedly for each of your turns.
    """

    @abstractmethod
    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        """
        Provides a place to initialize game wide structures like boards, and initialize data that depends on what
        color you are playing as.

        Called when the game starts.

        The board is provided to allow starting a game from different board positions.

        :param color: The color that you are playing as. Either :data:`chess.WHITE` or :data:`chess.BLACK`.
        :param board: The initial board of the game. See :class:`chess.Board`.
        :param opponent_name: The name of your opponent.
        """
        pass

    @abstractmethod
    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        """
        Provides information about what happened on the opponents turn.

        Called at the start of your turn.

        Example implementation: ::

            def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
                if captured_my_piece:
                    self.board.remove_piece_at(capture_square)

        :param captured_my_piece: If the opponent captured one of your pieces, then `True`, otherwise `False`.
        :param capture_square: If a capture occurred, then the :class:`Square` your piece was captured on,
            otherwise `None`.
        """
        pass

    @abstractmethod
    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        """
        The method to implement your sensing strategy. The chosen sensing action should be returned from this function.
        I.e. the value returned is the square at the center of the 3x3 sensing area you want to sense. The returned
        square must be one of the squares in the `sense_actions` parameter.

        You can pass instead of sensing by returning `None` from this function.

        Move actions are provided through `move_actions` in case you want to sense based on a potential move.

        Called after :meth:`handle_opponent_move_result()`.

        Example implementation: ::

            def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
                return random.choice(sense_actions)

        :param sense_actions: A :class:`list` containing the valid squares to sense over.
        :param move_actions: A :class:`list` containing the valid moves that can be returned in :meth:`choose_move()`.
        :param seconds_left: The time in seconds you have left to use in the game.
        :return: a :class:`Square` that is the center of the 3x3 sensing area you want to get information about.
        """
        pass

    @abstractmethod
    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        """
        Provides the result of the sensing action. Each element in `sense_result` is a square and the corresponding
        :class:`chess.Piece` found on that square. If there is no piece on the square, then the piece will be `None`.

        Called after :meth:`choose_sense()`.

        Example implementation: ::

            def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
                for square, piece in sense_result:
                    if piece is None:
                        self.board.remove_piece_at(square)
                    else:
                        self.board.set_piece_at(square, piece)

        :param sense_result: The result of the sense. A `list` of :class:`Square` and an optional :class:`chess.Piece`.
        """
        pass

    @abstractmethod
    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        """
        The method to implement your movement strategy. The chosen movement action should be returned from this function.
        I.e. the value returned is the move to make. The returned move must be one of the moves in the `move_actions`
        parameter.

        The pass move is legal, and is executed by returning `None` from this method.

        Called after :meth:`handle_sense_result()`.

        Example implementation: ::

            def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
                return random.choice(move_actions)

        :param move_actions: A `list` containing the valid :class:`chess.Move` you can choose.
        :param seconds_left: The time in seconds you have left to use in the game.
        :return: The :class:`chess.Move` to make.
        """
        pass

    @abstractmethod
    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        """
        Provides the result of the movement action. The `requested_move` is the move returned from :meth:`choose_move()`,
        and is provided for ease of use. `taken_move` is the move that was actually performed. Note that `taken_move`,
        can be different from `requested_move`, due to the uncertainty aspect.

        Called after :meth:`choose_move()`.

        Example implementation: ::

                def handle_move_result(self, requested_move: chess.Move, taken_move: chess.Move,
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
                    if taken_move is not None:
                        self.board.push(taken_move)

        Note: In the case of playing games on a server, this method is invoked during your opponents turn. This means
        in most cases this method will not use your play time. However if the opponent finishes their turn before
        this method completes, then time will be counted against you.

        :param requested_move: The :class:`chess.Move` you requested in :meth:`choose_move()`.
        :param taken_move: The :class:`chess.Move` that was actually applied by the game if it was a valid move,
            otherwise `None`.
        :param captured_opponent_piece: If `taken_move` resulted in a capture, then `True`, otherwise `False`.
        :param capture_square: If a capture occurred, then the :class:`Square` that the opponent piece was taken on,
            otherwise `None`.
        """
        pass

    @abstractmethod
    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        """
        Provides the results of the game when it ends. You can use this for post processing the results of the game.

        :param winner_color: If the game was a draw, then `None`, otherwise, the color of the player who won the game.
        :param win_reason: If the game was a draw, then `None`, otherwise the reason the game ended specified as
            :class:`WinReason`
        :param game_history: :class:`GameHistory` object for the game, from which you can get the actions
            each side has taken over the course of the game.
        """
        pass


def load_player(source_path: str) -> Tuple[str, Type[Player]]:
    """
    Loads a subclass of the Player class that is contained in a python source file or python module.
    There should only be 1 such subclass in the file or module. If there are more than 1 subclasses, then you have
    to define a function named `get_player` in the same module that returns the subclass to use.

    Example of single class definition: ::

        # this will import fine
        class MyBot(Player):
            ...

    Example of multiple class definition: ::

        class MyBot1(Player):
            ...

        class MyBot2(Player):
            ...

        # need to define this function!
        def get_player():
            return MyBot1

    Example of another situation where you may need to define `get_player`: ::

        from my_helper_module import MyPlayerBaseClass

        class MyBot1(MyPlayerBaseClass):
            ...

        # you need to define this because both MyBot1 and MyPlayerBaseClass are subclasses of Player
        def get_player():
            return MyBot1

    Example usage: ::

        name, cls = load_player('my_player.py')
        player = cls()

        name, cls = load_player('reconchess.bots.random_bot')
        player = cls()

    :param source_path: the path to the source file to load
    :return: Tuple where the first element is the name of the loaded class, and the second element is the class type
    """
    if os.path.exists(source_path):
        # get the path to the main source file
        abs_source_path = os.path.abspath(source_path)

        # insert the directory of the bot source file into system path so we can import it
        # note: insert it first so we know we are searching this first
        sys.path.insert(0, os.path.dirname(abs_source_path))

        # import_module expects a module name, so remove the extension
        module_name = os.path.splitext(os.path.basename(abs_source_path))[0]
    else:
        module_name = source_path

    module = importlib.import_module(module_name)
    players = inspect.getmembers(module, lambda o: inspect.isclass(o) and issubclass(o, Player) and o != Player)
    get_player_fns = inspect.getmembers(module, lambda o: inspect.isfunction(o) and o.__name__ == 'get_player')
    if len(players) == 0:
        raise RuntimeError('{} did not contain any subclasses of {}'.format(source_path, Player))
    elif len(players) > 1 and len(get_player_fns) != 1:
        msg = '{} contained multiple subclasses of {}: {}'.format(source_path, Player, players)
        msg += ', but no get_player function was defined. See documentation for reconchess.load_player'
        raise RuntimeError(msg)

    if len(players) == 1:
        return players[0]
    else:
        _, get_player_fn = get_player_fns[0]
        cls = get_player_fn()
        return cls.__name__, cls
