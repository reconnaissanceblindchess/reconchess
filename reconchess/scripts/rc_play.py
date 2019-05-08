import pkg_resources
import traceback
import argparse
import random
import contextlib
from reconchess import *
import datetime

# block output from pygame
with contextlib.redirect_stdout(None):
    import pygame


class Window:
    LIGHT_COLOR = (240, 217, 181)
    DARK_COLOR = (181, 136, 99)

    HIGHLIGHT_COLOR = (255, 255, 0)
    CAPTURE_COLOR = (255, 0, 0)

    LIGHT_SQUARES = list(chess.SquareSet(chess.BB_LIGHT_SQUARES))
    DARK_SQUARES = list(chess.SquareSet(chess.BB_DARK_SQUARES))

    def __init__(self):
        self.fps = 30
        self.width = 640
        self.height = 640
        self.square_size = self.width // 8

        self.image_by_piece = {}
        for color in chess.COLORS:
            for piece_type in chess.PIECE_TYPES:
                piece = chess.Piece(piece_type, color)

                img_path = 'res/{}/{}.png'.format(chess.COLOR_NAMES[color], piece.symbol())
                full_path = pkg_resources.resource_filename('reconchess', img_path)

                img = pygame.image.load(full_path)
                img = pygame.transform.scale(img, (self.square_size, self.square_size))
                self.image_by_piece[piece] = img

        pygame.init()
        pygame.display.set_caption('Recon Chess')
        pygame.display.set_icon(
            pygame.transform.scale(self.image_by_piece[chess.Piece(chess.KING, chess.WHITE)], (32, 32)))

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = pygame.Surface((self.screen.get_size()))

        self.perspective = chess.WHITE

        self.callback_by_event = {}

    def register_callback(self, event, callback):
        self.callback_by_event[event] = callback

    def coords_to_square(self, x, y):
        file = (x // self.square_size)
        if self.perspective == chess.WHITE:
            rank = ((self.height - y) // self.square_size)
        else:
            rank = (y // self.square_size)
        return chess.square(file, rank)

    def square_to_coords(self, square):
        rank = chess.square_rank(square)
        file = chess.square_file(square)
        x = file * self.square_size
        if self.perspective == chess.WHITE:
            y = (7 - rank) * self.square_size
        else:
            y = rank * self.square_size
        return x, y

    def square_rect(self, square):
        x, y = self.square_to_coords(square)
        return x, y, self.square_size, self.square_size

    def mouse_on_board(self):
        return pygame.mouse.get_focused()

    def right_pressed(self):
        return pygame.mouse.get_pressed()[2]

    def left_pressed(self):
        return pygame.mouse.get_pressed()[0]

    def draw(self, board, highlighted_squares=None, capture_squares=None, ignored_square=None, floating_piece=None):
        self.background.fill((0, 0, 0))

        self.draw_board()
        self.draw_pieces_on(board, ignored_square)

        if highlighted_squares is not None:
            for square in highlighted_squares:
                self.draw_highlight(square)

        if capture_squares is not None:
            for square in capture_squares:
                if square is not None:
                    self.draw_capture(square)

        if floating_piece:
            self.draw_piece_at(floating_piece, *pygame.mouse.get_pos())

        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        self.clock.tick(self.fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type in self.callback_by_event:
                self.callback_by_event[event.type](event)

    def draw_board(self):
        for square in chess.SQUARES:
            color = self.LIGHT_COLOR if square in self.LIGHT_SQUARES else self.DARK_COLOR
            pygame.draw.rect(self.background, color, self.square_rect(square))

    def draw_pieces_on(self, board, ignored_square=None):
        for square in chess.SQUARES:
            if square == ignored_square:
                continue

            piece = board.piece_at(square)
            if piece is not None:
                image = self.image_by_piece[piece]
                self.background.blit(image, self.square_rect(square))

    def draw_piece_at(self, piece, x, y):
        x -= self.square_size / 2
        y -= self.square_size / 2
        if piece is not None:
            image = self.image_by_piece[piece]
            self.background.blit(image, (x, y, self.square_size, self.square_size))

    def draw_highlight(self, square):
        pygame.draw.rect(self.background, self.HIGHLIGHT_COLOR, self.square_rect(square), 3)

    def draw_capture(self, square):
        pygame.draw.rect(self.background, self.CAPTURE_COLOR, self.square_rect(square), 3)


class UIPlayer(Player):
    def __init__(self):
        self.window = Window()
        self.window.register_callback(pygame.MOUSEBUTTONUP, self._handle_mouse_up)

        self.board = None
        self.color = None
        self.ally_capture_square = None
        self.enemy_capture_square = None

    def handle_game_start(self, color: Color, board: chess.Board):
        self.board = board
        self.color = color
        self.window.perspective = color

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        self.ally_capture_square = capture_square
        self.board.turn = self.color

        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

        self.window.draw(self.board, capture_squares=[self.enemy_capture_square, self.ally_capture_square])

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        while True:
            if self.window.mouse_on_board():
                square = self.window.coords_to_square(*pygame.mouse.get_pos())
                if square in sense_actions:
                    sense_area = self._squares_in_sense_around(square)
                else:
                    sense_area = []
            else:
                sense_area = []

            self.window.draw(self.board, highlighted_squares=sense_area,
                             capture_squares=[self.enemy_capture_square, self.ally_capture_square])

            if self.window.left_pressed() and self.window.mouse_on_board():
                square = self.window.coords_to_square(*pygame.mouse.get_pos())
                if square in sense_actions:
                    return square

    def _squares_in_sense_around(self, center):
        rank, file = chess.square_rank(center), chess.square_file(center)
        squares = []
        for dr in [-1, 0, 1]:
            for df in [-1, 0, 1]:
                r, f = rank + dr, file + df
                if 0 <= r < 8 and 0 <= f < 8:
                    squares.append(chess.square(f, r))
        return squares

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

        self.window.draw(self.board, capture_squares=[self.enemy_capture_square, self.ally_capture_square])

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        selected_square = None
        floating_piece = None

        while True:
            if selected_square is not None:
                to_squares = [move.to_square for move in move_actions if move.from_square == selected_square]
            elif self.window.mouse_on_board():
                square = self.window.coords_to_square(*pygame.mouse.get_pos())
                to_squares = [move.to_square for move in move_actions if move.from_square == square]
            else:
                to_squares = []

            self.window.draw(self.board, highlighted_squares=to_squares, ignored_square=selected_square,
                             floating_piece=floating_piece,
                             capture_squares=[self.enemy_capture_square, self.ally_capture_square])

            # picking up piece
            if self.window.left_pressed() and self.window.mouse_on_board():
                mouse_square = self.window.coords_to_square(*pygame.mouse.get_pos())
                piece = self.board.piece_at(mouse_square)
                if selected_square is None and piece is not None and piece.color == self.color:
                    selected_square = mouse_square
                    floating_piece = self.board.piece_at(mouse_square)

            # dropping/playing piece
            if selected_square is not None and not self.window.left_pressed():
                if not self.window.mouse_on_board():
                    selected_square = None
                    floating_piece = None
                else:
                    to_square = self.window.coords_to_square(*pygame.mouse.get_pos())
                    move = chess.Move(selected_square, to_square)
                    promotion_move = chess.Move(selected_square, to_square, promotion=chess.QUEEN)
                    if move in move_actions:
                        return move
                    elif promotion_move in move_actions:
                        return promotion_move
                    else:
                        selected_square = None
                        floating_piece = None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        if taken_move is not None:
            self.board.push(taken_move)

        self.enemy_capture_square = capture_square

        self.window.draw(self.board, capture_squares=[self.enemy_capture_square, self.ally_capture_square])

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        pass

    def _handle_mouse_up(self, event):
        if event.button == 3 and self.window.mouse_on_board():
            square = self.window.coords_to_square(*pygame.mouse.get_pos())
            self._rotate_piece_at(square)

    def _rotate_piece_at(self, square):
        piece = self.board.piece_at(square)
        if piece is not None and piece.color == self.color:
            return

        if piece is None:
            self.board.set_piece_at(square, chess.Piece(chess.PAWN, not self.color))
        else:
            if piece.piece_type == chess.KING:
                self.board.set_piece_at(square, None)
            else:
                self.board.set_piece_at(square, chess.Piece(piece.piece_type + 1, not self.color))


def main():
    parser = argparse.ArgumentParser(description='Allows you to play against a bot. Useful for testing and debugging.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('bot_path', help='Path to bot source file.')
    parser.add_argument('--color', default='random', choices=['white', 'black', 'random'],
                        help='The color you want to play as.')
    parser.add_argument('--seconds_per_player', default=900, type=float,
                        help='number of seconds each player has to play the entire game.')
    args = parser.parse_args()

    bot_name, bot_constructor = load_player(args.bot_path)
    bot = bot_constructor()
    player = UIPlayer()

    players = [player, bot]
    player_names = ['Human', bot_name]
    if args.color == 'black' or (args.color == 'random' and random.uniform(0, 1) < 0.5):
        players.reverse()
        player_names.reverse()

    game = LocalGame(args.seconds_per_player)

    try:
        winner_color, win_reason, history = play_local_game(players[0], players[1], game)
        winner = 'Draw' if winner_color is None else chess.COLOR_NAMES[winner_color]
    except:
        traceback.print_exc()
        game.end()

        winner = 'ERROR'
        history = game.get_game_history()

    print('Game Over!')
    print('Winner: {}!'.format(winner))

    timestamp = datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

    replay_path = '{}-{}-{}-{}.json'.format(player_names[0], player_names[1], winner, timestamp)
    print('Saving replay to {}...'.format(replay_path))
    history.save(replay_path)


if __name__ == '__main__':
    main()
