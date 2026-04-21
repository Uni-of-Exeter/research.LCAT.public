import numpy as np

# 7x7 grid:
# - outer ring = ocean (False)
# - 5x5 island of land (True)
# - ONE small 1-cell lake at (3, 3)
SMALL_LAKE_MASK = np.array(
    [
        [False, False, False, False, False, False, False],
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True, False,  True,  True, False],  # lake at (3,3)
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True,  True, False],
        [False, False, False, False, False, False, False],
    ],
    dtype=bool,
)

# Same layout but with a 2x2 lake at (3,3), (3,4), (4,3), (4,4)
BIG_LAKE_MASK = np.array(
    [
        [False, False, False, False, False, False, False],
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True, False, False,  True, False],
        [False,  True,  True, False, False,  True, False],
        [False,  True,  True,  True,  True,  True, False],
        [False, False, False, False, False, False, False],
    ],
    dtype=bool,
)

# Expected outputs for different thresholds

# Case 1: small lake, threshold big enough → lake filled
EXPECTED_SMALL_LAKE_FILLED = np.array(
    [
        [False, False, False, False, False, False, False],
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True,  True, False],  # lake now filled
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True,  True, False],
        [False, False, False, False, False, False, False],
    ],
    dtype=bool,
)

# Case 2: big lake, threshold too small → unchanged
EXPECTED_BIG_LAKE_UNCHANGED = BIG_LAKE_MASK.copy()

# Case 3: big lake, threshold big enough → lake filled
EXPECTED_BIG_LAKE_FILLED = np.array(
    [
        [False, False, False, False, False, False, False],
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True,  True, False],
        [False,  True,  True,  True,  True,  True, False],  # lake now land
        [False,  True,  True,  True,  True,  True, False],  # lake now land
        [False,  True,  True,  True,  True,  True, False],
        [False, False, False, False, False, False, False],
    ],
    dtype=bool,
)
