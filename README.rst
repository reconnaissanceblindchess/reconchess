reconchess: python package for Reconnaissance Chess
====================================================

Introduction
------------

Reconnaissance Chess is a chess variant (more precisely, a family of chess variants) invented as an R&D project at Johns Hopkins Applied Physics Laboratory (JHU/APL). Reconnaissance Chess adds the following elements to standard (classical) chess: sensing; incomplete information; decision making under uncertainty; coupled management of ‘battle forces’ and ‘sensor resources’; and adjudication of multiple, simultaneous, and competing objectives. Reconnaissance chess is a paradigm and test bed for understanding and experimenting with autonomous decision making under uncertainty and in particular managing a network of sensors to maintain situational awareness informing tactical and strategic decision making.

The game implemented in this python package is a relatively basic version using only one kind of sensor that provides perfect information in a small region of the chess board. In the future, extended versions may include noisy sensors of different types; multiple sensing actions per turn; the need to divide attention and resources among multiple, concurrent games; and other complicating factors.

This package includes a "game arbiter" which controls the game flow, maintains the ground truth game board, and notifies players of information collected by sense and move actions.  The package also contains a client API for interacting with the arbiter, which can be used by bot players or other game interfaces.

Installation
------------

::

    pip install reconchess

License
-------

Distributed under BSD 3-Clause License, for details see LICENSE file.


