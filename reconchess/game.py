from abc import abstractmethod
from datetime import datetime
from .utilities import *
from .history import GameHistory


class Game(object):
    """
    Abstract class that represents an instantiation of a Reconnaissance Chess Game. See :class:`LocalGame`
    and :class:`RemoteGame`
    for implementations.
    """

    @abstractmethod
    def sense_actions(self) -> List[Square]:
        """
        :return: List of :class:`Square` that the player can choose for sense phase.
        """
        pass

    @abstractmethod
    def move_actions(self) -> List[chess.Move]:
        """
        :return: List of :class:`chess.Move` that the player can choose for move phase.
        """
        pass

    @abstractmethod
    def get_seconds_left(self) -> float:
        """
        :return: float indicating the seconds the player has left to play.
        """
        pass

    @abstractmethod
    def start(self):
        """
        Starts the game and the timers for each player.
        """
        pass

    @abstractmethod
    def opponent_move_results(self) -> Optional[Square]:
        """
        :return: :class:`Square` where opponent captured a piece last turn if they did, otherwise `None`.
        """
        pass

    @abstractmethod
    def sense(self, square: Square) -> List[Tuple[Square, Optional[chess.Piece]]]:
        """
        Execute a sense action and get the sense result.

        An example result returned from sensing `B7` at the beginning of the game: ::

            [
                (A8, Piece(ROOK, BLACK)), (B8, Piece(KNIGHT, BLACK)), (C8, Piece(BISHOP, BLACK)),
                (A7, Piece(PAWN, BLACK)), (B7, Piece(PAWN, BLACK)), (C7, Piece(PAWN, BLACK)),
                (A6, None), (B6, None), (C8, None)
            ]

        :param square: The :class:`Square` to sense.
        :return: A list of tuples, where each tuple contains a :class:`Square` in the sense, and if there was a piece
            on the square, then the corresponding :class:`chess.Piece`, otherwise `None`.
        """
        pass

    @abstractmethod
    def move(self, requested_move: Optional[chess.Move]) \
            -> Tuple[Optional[chess.Move], Optional[chess.Move], Optional[Square]]:
        """
        Execute a move action and get the result.

        :param requested_move: The :class:`chess.Move` to execute.
        :return: A tuple containing the requested :class:`chess.Move`, the taken :class:`chess.Move`,
            and the :class:`Square` that a capture occurred on if one occurred.
        """
        pass

    @abstractmethod
    def end_turn(self):
        """
        End the current player's turn.
        """
        pass

    @abstractmethod
    def is_over(self) -> bool:
        """
        The game is over if either player has run out of time, or if either player's King has been captured.

        This will always return `True` after :meth:`end()` has been called.

        :return: Returns `True` if the game is over, otherwise `False`.
        """
        pass

    @abstractmethod
    def get_winner_color(self) -> Optional[Color]:
        """
        Returns the color of the player who won the game. If the game is not over, or is over but does not have a winner
        (i.e. :meth:`end()` has been called), then this will return `None`.

        :return: :class:`Color` of the winner if the game has ended and has a winner, otherwise `None`.
        """
        pass

    @abstractmethod
    def get_win_reason(self) -> Optional[WinReason]:
        """
        Returns the reason the player who won won the game. If the game is not over, or is over but does not have a
        winner (i.e. :meth:`end()` has been called), then this will return `None`.

        :return: :class:`WinReason` of the winner if the game has ended and has a winner, otherwise `None`.
        """
        pass

    @abstractmethod
    def get_game_history(self) -> Optional[GameHistory]:
        """
        Get the history of the game.

        :return: :class:`GameHistory` if the game is over, otherwise `None`.
        """
        pass


class LocalGame(Game):
    """
    The local implementation of :class:`Game`. Used to run games locally instead of remotely via a server.
    """

    def __init__(self, seconds_per_player: float = 900):
        self.turn = chess.WHITE
        self.board = chess.Board()

        self.__game_history = GameHistory()

        self._is_finished = False
        self.seconds_left_by_color = {chess.WHITE: seconds_per_player, chess.BLACK: seconds_per_player}
        self.current_turn_start_time = None

        self.move_results = None

    def start(self):
        """
        Starts off the clock for the first player.

        :return: None.
        """
        self.current_turn_start_time = datetime.now()

    def end(self):
        """
        Ends the game.
        :return: None.
        """
        self.seconds_left_by_color[self.turn] = self.get_seconds_left()
        self._is_finished = True

    def get_seconds_left(self) -> float:
        """
        :return: The amount of seconds left for the current player.
        """
        if not self._is_finished and self.current_turn_start_time:
            elapsed_since_turn_start = (datetime.now() - self.current_turn_start_time).total_seconds()
            return self.seconds_left_by_color[self.turn] - elapsed_since_turn_start
        else:
            return self.seconds_left_by_color[self.turn]

    def sense_actions(self) -> List[Square]:
        """
        :return: List of all squares on the board.
        """
        return None if self._is_finished else list(chess.SQUARES)

    def move_actions(self) -> List[chess.Move]:
        """
        :return: List of moves that are possible with only knowledge of your pieces
        """
        return None if self._is_finished else moves_without_opponent_pieces(self.board) + pawn_capture_moves_on(self.board)

    def opponent_move_results(self) -> Optional[Square]:
        return self.move_results

    def sense(self, square: Square) -> List[Tuple[Square, Optional[chess.Piece]]]:
        if square not in self.sense_actions():
            raise ValueError('LocalGame::sense({}): {} is not a valid square.'.format(square, square))

        rank, file = chess.square_rank(square), chess.square_file(square)
        sense_result = []
        for delta_rank in [1, 0, -1]:
            for delta_file in [-1, 0, 1]:
                if 0 <= rank + delta_rank <= 7 and 0 <= file + delta_file <= 7:
                    sense_square = chess.square(file + delta_file, rank + delta_rank)
                    sense_result.append((sense_square, self.board.piece_at(sense_square)))

        self.__game_history.store_sense(self.turn, square, sense_result)

        return sense_result

    def move(self, requested_move: Optional[chess.Move]) \
            -> Tuple[Optional[chess.Move], Optional[chess.Move], Optional[Square]]:
            
        if self._is_finished:
            return requested_move, None, None
        if requested_move is None:
            # pass move
            taken_move = None

            # doesn't capture anything
            opt_capture_square = None
        else:
            # add in a queen promotion if the move doesn't have one but could have one
            move = add_pawn_queen_promotion(self.board, requested_move)
            if move not in self.move_actions():
                raise ValueError('Requested move {} was not in move_actions()'.format(requested_move))

            # calculate taken move
            taken_move = self._revise_move(move)

            # calculate capture square
            opt_capture_square = capture_square_of_move(self.board, taken_move)

        # store move information before the move is pushed, as pushing a move
        # will change the turn over to the opponent
        self.__game_history.store_move(self.turn, requested_move, taken_move, opt_capture_square)
        self.__game_history.store_fen_before_move(self.turn, self.board.fen())

        # apply move
        self.board.push(taken_move if taken_move is not None else chess.Move.null())

        self.__game_history.store_fen_after_move(self.turn, self.board.fen())

        # store results of move for notifying other player
        self.move_results = opt_capture_square

        return requested_move, taken_move, opt_capture_square

    def _revise_move(self, move):
        # if its a legal move, don't change it at all. note that board.generate_psuedo_legal_moves() does not
        # include psuedo legal castles
        if move in self.board.generate_pseudo_legal_moves() or is_psuedo_legal_castle(self.board, move):
            return move

        # note: if there are pieces in the way, we DONT capture them
        if is_illegal_castle(self.board, move):
            return None

        # if the piece is a sliding piece, slide it as far as it can go
        piece = self.board.piece_at(move.from_square)
        if piece.piece_type in [chess.PAWN, chess.ROOK, chess.BISHOP, chess.QUEEN]:
            move = slide_move(self.board, move)

        return move if move in self.board.generate_pseudo_legal_moves() else None

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

    def get_game_history(self) -> Optional[GameHistory]:
        return self.__game_history if self.is_over() else None

    def is_over(self) -> bool:
        if self._is_finished:
            return True

        no_time_left = self.seconds_left_by_color[chess.WHITE] <= 0 or self.seconds_left_by_color[chess.BLACK] <= 0
        king_captured = self.board.king(chess.WHITE) is None or self.board.king(chess.BLACK) is None
        return no_time_left or king_captured

    def get_winner_color(self) -> Optional[Color]:
        if not self.is_over():
            return None

        if self.seconds_left_by_color[chess.WHITE] <= 0:
            return chess.BLACK
        elif self.seconds_left_by_color[chess.BLACK] <= 0:
            return chess.WHITE

        if self.board.king(chess.WHITE) is None:
            return chess.BLACK
        elif self.board.king(chess.BLACK) is None:
            return chess.WHITE

        return None

    def get_win_reason(self) -> Optional[WinReason]:
        if not self.is_over():
            return None

        if self.seconds_left_by_color[chess.WHITE] <= 0 or self.seconds_left_by_color[chess.BLACK] <= 0:
            return WinReason.TIMEOUT
        elif self.board.king(chess.WHITE) is None or self.board.king(chess.BLACK) is None:
            return WinReason.KING_CAPTURE

        return None


class RemoteGame(Game):
    """
    The remote implementation of :class:`Game`. Used to play games remotely via a server.

    All the methods implemented are pass-throughs to the server. Each method submits a HTTP request to the corresponding
    end point on the server.
    """

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
