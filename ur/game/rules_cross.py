# Board geometry for the cross-shaped Royal Game of Ur board.
#
# The board is a + / cross shape:
#
#   North arm  (col 4, rows 0-3)   — future P3 entry path
#   Horizontal (row  4, cols 0-8)  — P1 enters West (col 0), P2 enters East (col 8)
#   Center col (col 4, rows 5-10)  — shared combat corridor (sq 6-11)
#   Lower Y    (row 11, cols 2-6)  — P1 exits left, P2 exits right
#   South exit (col 4, rows 12-13) — future P3 exit path
#
# Progress 0  = off-board (waiting)
# Progress 1-14 = squares on the board
# Progress 15 = scored

# P1 — enters from the West arm, exits left branch of lower Y
P1_PATH_CROSS = {
    0: None,
    1: (4, 0),   # sq1  entry a — far left
    2: (4, 1),   # sq2  b
    3: (4, 2),   # sq3  c
    4: (4, 3),   # sq4  d  ✿ rosette
    5: (4, 4),   # sq5  e  shared entry
    6: (5, 4),   # sq6  f
    7: (6, 4),   # sq7  g
    8: (7, 4),   # sq8  h  ✿ rosette (shared)
    9: (8, 4),   # sq9  i
    10: (9, 4),  # sq10 j
    11: (10, 4), # sq11 k
    12: (11, 4), # sq12 l  shared junction
    13: (11, 3), # sq13 m  exit
    14: (11, 2), # sq14 n  ✿ rosette
    15: None,
}

# P2 — enters from the East arm, exits right branch of lower Y
P2_PATH_CROSS = {
    0: None,
    1: (4, 8),   # sq1  entry a — far right
    2: (4, 7),   # sq2  b
    3: (4, 6),   # sq3  c
    4: (4, 5),   # sq4  d  ✿ rosette
    5: (4, 4),   # sq5  e  shared entry (same as P1)
    6: (5, 4),   # sq6  f
    7: (6, 4),   # sq7  g
    8: (7, 4),   # sq8  h  ✿ rosette (shared)
    9: (8, 4),   # sq9  i
    10: (9, 4),  # sq10 j
    11: (10, 4), # sq11 k
    12: (11, 4), # sq12 l  shared junction (same as P1)
    13: (11, 5), # sq13 m  exit
    14: (11, 6), # sq14 n  ✿ rosette
    15: None,
}

# Future P3 path — North arm entry, South exit
P3_PATH_CROSS = {
    0: None,
    1: (0, 4),   # sq1  North arm top
    2: (1, 4),
    3: (2, 4),
    4: (3, 4),   # sq4  ✿ rosette
    5: (4, 4),   # sq5  shared entry
    6: (5, 4),
    7: (6, 4),
    8: (7, 4),   # sq8  ✿ rosette (shared)
    9: (8, 4),
    10: (9, 4),
    11: (10, 4),
    12: (11, 4), # sq12 junction
    13: (12, 4), # sq13 South exit
    14: (13, 4), # sq14 ✿ rosette
    15: None,
}

# Rosettes in the 2-player game (P1 sq4, P2 sq4, shared sq8, P1 sq14, P2 sq14)
CROSS_ROSETTAS = {(4, 3), (4, 5), (7, 4), (11, 2), (11, 6)}

# Extended set including P3 rosettes (for 3-player cross)
CROSS_ROSETTAS_3P = CROSS_ROSETTAS | {(3, 4), (13, 4)}

# Standard piece count matching the existing 2-player game
PIECES_PER_PLAYER = 3
FINISH = 15

# Maps each board template key (a-z) to its (board_row, board_col)
CROSS_TEMPLATE_COORD: dict[str, tuple] = {
    # North arm
    "a": (0, 4), "b": (1, 4), "c": (2, 4), "d": (3, 4),
    # Horizontal row: P1 entry (e-h), centre (i), P2 entry (j-m)
    "e": (4, 0), "f": (4, 1), "g": (4, 2), "h": (4, 3),
    "i": (4, 4),
    "j": (4, 5), "k": (4, 6), "l": (4, 7), "m": (4, 8),
    # Shared centre column
    "n": (5, 4), "o": (6, 4), "p": (7, 4),
    "q": (8, 4), "r": (9, 4), "s": (10, 4),
    # Lower Y junction row
    "t": (11, 2), "u": (11, 3), "v": (11, 4), "w": (11, 5), "x": (11, 6),
    # South exit
    "y": (12, 4), "z": (13, 4),
}
