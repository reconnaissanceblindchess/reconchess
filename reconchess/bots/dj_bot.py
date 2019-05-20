import chess.engine
import random
from reconchess import *
import os
# from stockfish import Stockfish

class DJBot(Player):

    # GENERAL STRATEGY:

    # - Each piece has a score; Ally pieces are negative score
    # - Count each captured piece as the game 'score'
    # - Dynamically minimax to figure out best moves
    # - Dynamically populate list of instakill movesets

    # TODO:
    # - maintain belief state of pieces


    def __init__(self):
        self.board = None
        self.belief = None
        self.color = None
        self.my_piece_captured_square = None
        self.lastMove = None
        # self.stockfish = Stockfish()
        self.space_conversions = {
        'a1': chess.A1,'a2': chess.A2,'a3': chess.A3,'a4': chess.A4,'a5': chess.A5,'a6': chess.A6,'a7': chess.A7,'a8': chess.A8,
        'b1': chess.B1,'b2': chess.B2,'b3': chess.B3,'b4': chess.B4,'b5': chess.B5,'b6': chess.B6,'b7': chess.B7,'b8': chess.B8,
        'c1': chess.C1,'c2': chess.C2,'c3': chess.C3,'c4': chess.C4,'c5': chess.C5,'c6': chess.C6,'c7': chess.C7,'c8': chess.C8,
        'd1': chess.D1,'d2': chess.D2,'d3': chess.D3,'d4': chess.D4,'d5': chess.D5,'d6': chess.D6,'d7': chess.D7,'d8': chess.D8,
        'e1': chess.E1,'e2': chess.E2,'e3': chess.E3,'e4': chess.E4,'e5': chess.E5,'e6': chess.E6,'e7': chess.E7,'e8': chess.E8,
        'f1': chess.F1,'f2': chess.F2,'f3': chess.F3,'f4': chess.F4,'f5': chess.F5,'f6': chess.F6,'f7': chess.F7,'f8': chess.F8,
        'g1': chess.G1,'g2': chess.G2,'g3': chess.G3,'g4': chess.G4,'g5': chess.G5,'g6': chess.G6,'g7': chess.G7,'g8': chess.G8,
        'h1': chess.H1,'h2': chess.H2,'h3': chess.H3,'h4': chess.H4,'h5': chess.H5,'h6': chess.H6,'h7': chess.H7,'h8': chess.H8,
        }

    def handle_game_start(self, color: Color, board: chess.Board):
        self.board = board
        self.color = color
        # self.belief = board
        # self.stockfish.set_fen_position(self.board.fen());

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # if the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)
        # self.stockfish.set_fen_position(self.board.fen())

    # basically what stockfish does. 
    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        # if our piece was just captured, sense where it was captured
        if self.my_piece_captured_square:
            # instead of directly returning the square to scan, save as a local variable for edge correction in all algos
            poten_square = self.my_piece_captured_square
            poten_square = self.edge_correct(poten_square)
            return poten_square

        # if we might capture a piece when we move, sense where the capture will occur
        future_move = self.choose_move(move_actions, seconds_left)
        if future_move is not None and self.board.piece_at(future_move.to_square) is not None:
            poten_square = future_move.to_square
            poten_square = self.edge_correct(poten_square)
            return poten_square

        # otherwise, just randomly choose a sense action, but don't sense on a square where our pieces are located
        for square, piece in self.board.piece_map().items():
            if piece.color == self.color:
                sense_actions.remove(square)
    
        poten_square = random.choice(sense_actions)
        poten_square = self.edge_correct(poten_square)
        return poten_square

    # move scan away from edge to prevent it from being partially wasted
    def edge_correct(self, Square):
        n_square = Square
        
        # if on outer rows, move one row away from the edge
        if (chess.square_rank(n_square) == 0):
            n_square += 8
        elif (chess.square_rank(n_square) == 7):
            n_square -= 8
        
        # if on outer columns, move one column away from the edge
        if (chess.square_file(n_square) == 0):
            n_square += 1
        elif (chess.square_file(n_square) == 7):
            n_square -= 1
            
        return n_square

    # register where we see other pieces
    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)
        # self.stockfish.set_fen_position(self.board.fen())

    def stockfish_move_conversion(self, move):
        source = move[:2]
        dest = move[2:]

        return chess.Move( self.space_conversions[source], self.space_conversions[dest] )

    def evaluateBoard(self, board : chess.Board):
        pieceScores = {chess.PAWN : 10, chess.ROOK: 50, chess.KNIGHT: 70, chess.BISHOP: 30, chess.QUEEN: 100, chess.KING: 100000 }
        pawnEvals = [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,  5.0,
        1.0,  1.0,  2.0,  3.0,  3.0,  2.0,  1.0,  1.0,
        0.5,  0.5,  1.0,  2.5,  2.5,  1.0,  0.5,  0.5,
        0.0,  0.0,  0.0,  2.0,  2.0,  0.0,  0.0,  0.0,
        0.5, -0.5, -1.0,  0.0,  0.0, -1.0, -0.5,  0.5,
        0.5,  1.0, 1.0,  -2.0, -2.0,  1.0,  1.0,  0.5,
        0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0]

        knightEvals =[-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0,
        -4.0, -2.0,  0.0,  0.0,  0.0,  0.0, -2.0, -4.0,
        -3.0,  0.0,  1.0,  1.5,  1.5,  1.0,  0.0, -3.0,
        -3.0,  0.5,  1.5,  2.0,  2.0,  1.5,  0.5, -3.0,
        -3.0,  0.0,  1.5,  2.0,  2.0,  1.5,  0.0, -3.0,
        -3.0,  0.5,  1.0,  1.5,  1.5,  1.0,  0.5, -3.0,
        -4.0, -2.0,  0.0,  0.5,  0.5,  0.0, -2.0, -4.0,
        -5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]

        bishopEvals = [ -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0,
        -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
        -1.0,  0.0,  0.5,  1.0,  1.0,  0.5,  0.0, -1.0,
        -1.0,  0.5,  0.5,  1.0,  1.0,  0.5,  0.5, -1.0,
        -1.0,  0.0,  1.0,  1.0,  1.0,  1.0,  0.0, -1.0,
        -1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0, -1.0,
        -1.0,  0.5,  0.0,  0.0,  0.0,  0.0,  0.5, -1.0,
        -2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]

        rookEvals = [  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,
        0.5,  1.0,  1.0,  1.0,  1.0,  1.0,  1.0,  0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        -0.5,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -0.5,
        0.0,   0.0, 0.0,  0.5,  0.5,  0.0,  0.0,  0.0]

        queenEvals = [  -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0,
        -1.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0, -1.0,
        -1.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
        -0.5,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
        0.0,  0.0,  0.5,  0.5,  0.5,  0.5,  0.0, -0.5,
        -1.0,  0.5,  0.5,  0.5,  0.5,  0.5,  0.0, -1.0,
        -1.0,  0.0,  0.5,  0.0,  0.0,  0.0,  0.0, -1.0,
        -2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]

        kingEvals = [ -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0,
        -2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0,
        -1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0,
        2.0,  2.0,  0.0,  0.0,  0.0,  0.0,  2.0,  2.0 ,
        2.0,  3.0,  1.0,  0.0,  0.0,  1.0,  3.0,  2.0 ]

        if self.color == chess.BLACK:
            pawnEvals = pawnEvals[::-1]
            knightEvals = knightEvals[::-1]
            bishopEvals = bishopEvals[::-1]
            rookEvals = rookEvals[::-1]
            queenEvals = queenEvals[::-1]
            kingEvals = kingEvals[::-1]
        score = 0

        #pawns
        for piece in board.pieces(chess.PAWN, self.color):
            score += pawnEvals[piece]
        #rooks
        for piece in board.pieces(chess.ROOK, self.color):
            score += rookEvals[piece]
        #knights
        for piece in board.pieces(chess.KNIGHT, self.color):
            score += knightEvals[piece]
        #bishops
        for piece in board.pieces(chess.BISHOP, self.color):
            score += bishopEvals[piece]
        #queen
        for piece in board.pieces(chess.QUEEN, self.color):
            score += queenEvals[piece]
        #king
        for piece in board.pieces(chess.KING, self.color):
            score += kingEvals[piece]
        # print(score)
        return score

    def calculateBestMove(self, board: chess.Board, move_actions: List[chess.Move]):
        best_move = None
        cur_score = 0
        best_score = -1000000
        test_board = board
        # print("move actions:" + str(move_actions))
        for move in move_actions:
            test_board = board
            test_board.push(move)
            cur_score = self.evaluateBoard(test_board)
            if best_score < cur_score:
                    best_score = cur_score
                    best_move = move
        return best_move



    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        # if we might be able to take the king, try to
        enemy_king_square = self.board.king(not self.color)
        if enemy_king_square:
            # if there are any ally pieces that can take king, execute one of those moves
            # print("Try to cap king")
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                print("attack king " + str(attacker_square) + str(enemy_king_square))
                
                king_cap_move = chess.SQUARE_NAMES[attacker_square] + chess.SQUARE_NAMES[enemy_king_square]
                print("attack king name " + king_cap_move)
                
                if king_cap_move in move_actions:
                    return chess.Move(attacker_square, enemy_king_square)
                else:
                    print("Failed attack, move blocked by unseen piece")

        # best_move = self.stockfish.get_best_move()
        # print("Try best move")
        best_move = self.calculateBestMove(self.board, move_actions)
        # stock_move = self.stockfish_move_conversion(best_move)
        # ucimove = chess.Move.from_uci(self.stockfish.get_best_move())
        ucimove = best_move
        self.lastMove = ucimove
        # if ucimove not in move_actions and ucimove is not self.lastMove:
        if ucimove not in move_actions:
            print("failed move check, do random")
            choice = random.choice(move_actions)
            self.board.push(choice)
            # self.stockfish.set_fen_position(self.board.fen())
            return choice
        # print("Best: " + str(best_move))
        self.board.push(ucimove)
        # self.stockfish.set_fen_position(self.board.fen())
        return ucimove 


    def update_beliefs(self, sense_results):
        pass


    # don't change
    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # if a move was executed, apply it to our board
        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        pass

