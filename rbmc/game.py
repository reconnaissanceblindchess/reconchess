import chess
from abc import abstractmethod
from datetime import datetime
from .types import *
from .player import Player
from .utilities import *
from .history import GameHistory


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
    def sense(self, square: Square) -> List[Tuple[Square, Optional[chess.Piece]]]:
        pass

    @abstractmethod
    def move(self, requested_move: Optional[chess.Move]) \
            -> Tuple[Optional[chess.Move], Optional[chess.Move], Optional[Square]]:
        pass

    @abstractmethod
    def end_turn(self):
        pass

    @abstractmethod
    def is_over(self) -> bool:
        pass

    @abstractmethod
    def get_winner_color(self) -> Optional[Color]:
        pass

    @abstractmethod
    def get_game_history(self) -> Optional[GameHistory]:
        pass

class LocalGame(Game):
    """Would implement all logic and use a chess.Board() object as the truth board"""

    def __init__(self, seconds_per_player: float = 900, store_game_history: bool = True):
        self.turn = chess.WHITE
        self.board = chess.Board()

        self.store_game_history = store_game_history
        self.__game_history = GameHistory() if self.store_game_history else None
        self.seconds_left_by_color = {chess.WHITE: seconds_per_player, chess.BLACK: seconds_per_player}
        self.current_turn_start_time = None

        self.move_results = None

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
        :return: List of all squares on the board.
        """
        return chess.SQUARES

    def valid_moves(self) -> List[chess.Move]:
        """
        :return: List of moves that are possible with only knowledge of your pieces
        """
        return moves_without_opponent_pieces(self.board) + pawn_capture_moves_on(self.board)

    def opponent_move_results(self) -> Optional[Square]:
        return self.move_results

    def sense(self, square: Square) -> List[Tuple[Square, Optional[chess.Piece]]]:
        if square not in self.valid_senses():
            raise ValueError('LocalGame::sense({}): {} is not a valid square.'.format(square, square))

        rank, file = chess.square_rank(square), chess.square_file(square)
        sense_result = []
        for delta_rank in [1, 0, -1]:
            for delta_file in [-1, 0, 1]:
                if 0 <= rank + delta_rank <= 7 and 0 <= file + delta_file <= 7:
                    sense_square = chess.square(file + delta_file, rank + delta_rank)
                    sense_result.append((sense_square, self.board.piece_at(sense_square)))
        
        if self.store_game_history:
            self.__game_history.store_sense(self.board.fullmove_number, self.turn, square, sense_result)

        return sense_result

    def move(self, requested_move: Optional[chess.Move]) \
            -> Tuple[Optional[chess.Move], Optional[chess.Move], Optional[Square]]:
        if requested_move is None:
            # pass move
            taken_move = None

            # doesn't capture anything
            opt_capture_square = None
        else:
            # add in a queen promotion if the move doesn't have one but could have one
            move = add_pawn_queen_promotion(self.board, requested_move)
            if move not in self.valid_moves():
                raise ValueError('Requested move {} was not in valid_moves()'.format(requested_move))

            # calculate taken move
            taken_move = self._revise_move(move)

            # calculate capture square
            opt_capture_square = capture_square_of_move(self.board, taken_move)

        # store move information before the move is pushed, as pushing a move
        # will change the turn over to the opponent
        if self.store_game_history:
            self.__game_history.store_move(self.board.fullmove_number, self.turn, 
                                        requested_move, taken_move, opt_capture_square)
            self.__game_history.store_opponent_move_results(self.board.fullmove_number, 
                                        not self.turn, opt_capture_square)

        # apply move
        self.board.push(taken_move if taken_move is not None else chess.Move.null())

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
        if not self.is_over() or not self.store_game_history:
            return None
        else:
            return self.__game_history

    def is_over(self) -> bool:
        no_time_left = self.seconds_left_by_color[chess.WHITE] <= 0 or self.seconds_left_by_color[chess.BLACK] <= 0
        king_captured = self.board.king(chess.WHITE) is None or self.board.king(chess.BLACK) is None
        return no_time_left or king_captured


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
    game_history = game.get_game_history()

    white_player.handle_game_end(winner_color, game_history)
    black_player.handle_game_end(winner_color, game_history)

    return winner_color, game_history


def play_remote_game(name, game_id, player: Player):
    game = RemoteGame(game_id)

    color = game.get_player_color(name)

    player.handle_game_start(color, game.get_starting_board())
    game.start()

    while not game.is_over():
        game.wait_for_turn(name)
        play_turn(game, player)

    player.handle_game_end(game.get_winner_color(), game.get_game_history())


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
