Rules of Reconnaissance Chess
=============================

Reconnaissance Chess can be thought of as a family of chess variants that incorporate sensing and incomplete information.
This python package implements a version of the game with the following rules.

1. The Rules of Standard Chess apply, with the exceptions and modifications that follow.

2. The objective of the game is to capture the king, not deliver checkmate. When one player captures the other player's king, the game is ended, and the capturing player wins.

3. The rules associated with check are all eliminated.  This includes: a player is not told if their king is in check, a player may make a move that leaves their king in check, and can castle into or through check.

4. All rules associated with stalemates or automatic draw conditions are eliminated.

5. Each player's turn has three phases, played in this order: turn start phase, sense phase, and move phase.

    a. Turn Start phase: the player's turn begins, and if the opponent captured a piece on their turn, the current player is given the capture square (thus the current player also knows which piece was captured).

    b. Sense phase: the player chooses any square on the chessboard to target their sensor.  Then, the true state of the game board in a three square by three square window centered at the chosen square is revealed to the sensing player.  This includes showing all pieces and empty squares in the 3x3 window.

    c. Move phase: the player chooses any chess move, or chooses to "pass."  If the move is a pawn promotion and the player does not specify a piece to promote to, then a queen promotion is assumed. Then, given that move, one of three conditions holds:

        i. The move is legal on the game board.

        ii. The moving piece is a queen, bishop, or rook and the move is illegal on the game board because one or more opponent pieces block the path of the moving piece.  Then, the move is modified so that the destination square is the location of the first obstructing opponent piece, and that opponent piece is captured.  (Note: this rule does not apply to a castling king).

        iii. The moving piece is a pawn, moving two squares forward on that pawn's first move, and the move is illegal because an opponent's piece blocks the path of the pawn.  Then, the move is modified so that the pawn moves only one square if that modified move is legal, otherwise the player's move is illegal.

        iv. If any of (i)-(iii) do not hold, the move is considered illegal (or the player chose to pass which has the same result).

       The results of the move are then determined: if condition (iv) holds, then no changes are made to the board, the player is notified that their move choice was illegal (or the pass is acknowledged), and the player's turn is over.  Otherwise the move is made on the game board.  If the move was modified because of (ii) or (iii), then the modified move is made, and the current player is notified of the modified move in the move results.  If the move results in a capture, the current player is notified that they captured a piece and which square the capture occurred, but not the type of opponent piece captured (the opponent will be notified of the capture square on their turn start phase).  If the move captures the opponent's king, the game ends and both players are notified.  The current player's turn is now over and play proceeds to the opponent.

6. The only information revealed to either player about the game or opponent actions is that explicitly stated in (5).

7. The game can also be played with a chess clock, in which case the player is notified of their remaining clock time, but not their opponent's remaining clock time.  Both players are notified if either player loses on time.