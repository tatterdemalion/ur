# Board geometry for the 3-player Royal Game of Ur.
#
# Progress 0   = off-board (waiting area)
# Progress 1-14 = squares on the board
# Progress 15  = scored (finished)
#
# P1 (row 2) and P2 (row 0) are identical to ur/game/rules.py.
# P3 (row 3) mirrors the same structure.

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

P3_PATH = {
    0: None,
    1: (3, 3),
    2: (3, 2),
    3: (3, 1),
    4: (3, 0),
    5: (1, 0),
    6: (1, 1),
    7: (1, 2),
    8: (1, 3),
    9: (1, 4),
    10: (1, 5),
    11: (1, 6),
    12: (1, 7),
    13: (3, 7),
    14: (3, 6),
    15: None,
}

PATHS = [P1_PATH, P2_PATH, P3_PATH]

# Original 5 rosettes plus (3,0) and (3,6) for P3's private rosettes
ROSETTAS = {(0, 0), (2, 0), (3, 0), (1, 3), (0, 6), (2, 6), (3, 6)}

PIECES_PER_PLAYER = 4
FINISH = 15
