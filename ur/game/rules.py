# Board geometry for the standard Royal Game of Ur layout.
#
# Progress 0   = off-board (waiting area)
# Progress 1-14 = squares on the board
# Progress 15  = scored (finished)

P1_PATH = {
    0: None,
    1: (2, 3),
    2: (2, 2),
    3: (2, 1),
    4: (2, 0),
    5: (1, 0),
    6: (1, 1),
    7: (1, 2),
    8: (1, 3),
    9: (1, 4),
    10: (1, 5),
    11: (1, 6),
    12: (1, 7),
    13: (2, 7),
    14: (2, 6),
    15: None,
}

P2_PATH = {
    0: None,
    1: (0, 3),
    2: (0, 2),
    3: (0, 1),
    4: (0, 0),
    5: (1, 0),
    6: (1, 1),
    7: (1, 2),
    8: (1, 3),
    9: (1, 4),
    10: (1, 5),
    11: (1, 6),
    12: (1, 7),
    13: (0, 7),
    14: (0, 6),
    15: None,
}

# Squares that grant an extra turn and protect from capture (central rosetta only)
ROSETTAS = {(0, 0), (2, 0), (1, 3), (0, 6), (2, 6)}

FINAL_SQUARE = 14  # Last square before scoring
FINISH = 15  # Progress value meaning the piece has scored
