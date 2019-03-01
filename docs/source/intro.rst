Introduction to Reconnaissance Chess
====================================

The overall idea of Reconnaissance Chess is that you play chess without sight of the opponent's pieces, and you gain
information about the opponent's position
by sensing.  On your turn, you first pick a part of the board to sense.  Your sensor has a 3 square x 3 square field of
view, and once you pick where to sense you are shown what the ground truth board position looks like in that 3x3 window.
Then you select a move, similar to classical chess.

Most of the rules follow classical chess, including piece movements, initial board configuration, en passant capture,
pawn promotion, castling, etc. However, there are some modifications, many of which are required because
of the uncertainty in the game.  One major change from classical chess is that in Recon Chess the goal is to simply
capture the opponent king, there are no notions of checkmate or check.  Also, because the true board position is
uncertain, you may try to make a move that is actually illegal; this results in either a loss of turn or a modification
to your requested move.  See the full rules below.

In addition to sensing, there are other sources of information about the true position.  You are always notified about
where your pieces move (or don't) and when one of your pieces was captured by the opponent (but you are not told the
piece that did the
capturing); this information allows you to keep track of the true position of your own pieces.  You are notified if you make
a capture (but not which piece is captured). And there is also information to be gained about the opponent from moves
you attempted but where not legal (e.g., attempted pawn captures). It is up to the player to fuse this information
during the game to form their best representation of the true board state (i.e., a "world model").  It is the job
of the "game arbiter" (implemented as part of this python package) to maintain the ground truth board position, control
the game flow, and notify each player about
any information they have gained through sensing, moving, or captures.