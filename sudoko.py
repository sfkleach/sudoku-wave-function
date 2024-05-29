EXAMPLE = """
___83_6__
1____5___
5_3__2497
__9__83__
3___1_7_6
_126_____
9___2_87_
___749__2
62_3__954
"""

# Example equates to this
SUDOKU = [
    [0, 0, 0, 8, 3, 0, 6, 0, 0],
    [1, 0, 0, 0, 0, 5, 0, 0, 0],
    [5, 0, 3, 0, 0, 2, 4, 9, 7],
    [0, 0, 9, 0, 0, 8, 3, 0, 0],
    [3, 0, 0, 0, 1, 0, 7, 0, 6],
    [0, 1, 2, 6, 0, 0, 0, 0, 0],
    [9, 0, 0, 0, 2, 0, 8, 7, 0],
    [0, 0, 0, 7, 4, 9, 0, 0, 2],
    [6, 2, 0, 3, 0, 0, 9, 5, 4],
]

# SUDOKU2 = [[{n} if n else set(range(1, 10)) for n in row] for row in SUDOKU]

EXPECTED = """
┏━━━┯━━━┯━━━┳━━━┯━━━┯━━━┳━━━┯━━━┯━━━┓
┃ 2 │ 9 │ 4 ┃ 8 │ 3 │ 7 ┃ 6 │ 1 │ 5 ┃
┠───┼───┼───╂───┼───┼───╂───┼───┼───┨
┃ 1 │ 7 │ 6 ┃ 4 │ 9 │ 5 ┃ 2 │ 3 │ 8 ┃
┠───┼───┼───╂───┼───┼───╂───┼───┼───┨
┃ 5 │ 8 │ 3 ┃ 1 │ 6 │ 2 ┃ 4 │ 9 │ 7 ┃
┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫
┃ 7 │ 6 │ 9 ┃ 2 │ 5 │ 8 ┃ 3 │ 4 │ 1 ┃
┠───┼───┼───╂───┼───┼───╂───┼───┼───┨
┃ 3 │ 5 │ 8 ┃ 9 │ 1 │ 4 ┃ 7 │ 2 │ 6 ┃
┠───┼───┼───╂───┼───┼───╂───┼───┼───┨
┃ 4 │ 1 │ 2 ┃ 6 │ 7 │ 3 ┃ 5 │ 8 │ 9 ┃
┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫
┃ 9 │ 4 │ 1 ┃ 5 │ 2 │ 6 ┃ 8 │ 7 │ 3 ┃
┠───┼───┼───╂───┼───┼───╂───┼───┼───┨
┃ 8 │ 3 │ 5 ┃ 7 │ 4 │ 9 ┃ 1 │ 6 │ 2 ┃
┠───┼───┼───╂───┼───┼───╂───┼───┼───┨
┃ 6 │ 2 │ 7 ┃ 3 │ 8 │ 1 ┃ 9 │ 5 │ 4 ┃
┗━━━┷━━━┷━━━┻━━━┷━━━┷━━━┻━━━┷━━━┷━━━┛"""

from typing import TypeAlias, Generator

Grid: TypeAlias = list[list[int]]
SetGrid: TypeAlias = list[list[set[int]]]


def pretty(grid: SetGrid):
    print("┏━━━━━┯━━━━━┯━━━━━┳━━━━━┯━━━━━┯━━━━━┳━━━━━┯━━━━━┯━━━━━┓")
    for row in grid:
        print("┃", end="")
        for cell in row:
            txt = "".join(map(str, cell))
            print(f"{txt:<5}", end="┃")
        print()
        print("┠─────┼─────┼─────╂─────┼─────┼─────╂─────┼─────┼─────┨")
    print("┗━━━━━┷━━━━━┷━━━━━┻━━━━━┷━━━━━┷━━━━━┻━━━━━┷━━━━━┷━━━━━┛")


def get_set_sudoku(grid: Grid) -> SetGrid:
    return [
        [calculate_initial_options(grid, row, col) for col in range(9)]
        for row in range(9)
    ]


def find_minimum_set(grid: SetGrid) -> tuple[int, int] | None:
    sofar = 9
    (i, j) = (-1, -1)
    for r, row in enumerate(grid):
        for c, col in enumerate(row):
            L = len(col)  # Size of set.
            if 2 <= L < sofar:
                sofar = L
                i, j = r, c
    if i == -1:
        return None
    else:
        return (i, j)


def find_box_values(grid: Grid, row: int, col: int) -> set[int]:
    """Find the values in the 3x3 containing box"""
    box_row = row // 3 * 3
    box_col = col // 3 * 3
    elements = {
        grid[row][col]
        for row in range(box_row, box_row + 3)
        for col in range(box_col, box_col + 3)
    }
    return elements


def find_singleton_box_set_values(grid: SetGrid, irow: int, icol: int) -> set[int]:
    """Find the values in the 3x3 containing box"""
    box_row = irow // 3 * 3
    box_col = icol // 3 * 3
    values = set()
    for row in range(box_row, box_row + 3):
        for col in range(box_col, box_col + 3):
            if not (row == irow and col == icol):
                if len(grid[row][col]) == 1:
                    values |= grid[row][col]
    return values


def calculate_initial_options(grid: Grid, row: int, col: int) -> set[int]:
    if grid[row][col] != 0:
        return {grid[row][col]}
    row_values = set(grid[row]) - {grid[row][col]}
    col_values = {grid[r][col] for r in range(9)} - {grid[row][col]}
    box_values = find_box_values(grid, row, col) - {grid[row][col]}
    options = set(range(1, 10)) - row_values - col_values - box_values
    return options


def calculate_options(grid: SetGrid, row: int, col: int) -> set[int]:
    singleton_row_values = {
        next(iter(value_set))
        for c, value_set in enumerate(grid[row])
        if len(value_set) == 1 and c != col
    }
    singleton_col_values = {
        next(iter(grid[row][c]))
        for r, c in enumerate(range(9))
        if len(grid[row][c]) == 1 and r != row
    }
    box_values = find_singleton_box_set_values(grid, row, col)
    print(f"{grid[row][col]},srv={singleton_row_values}, src={singleton_col_values}, bv={box_values}")
    options = grid[row][col] - singleton_row_values - singleton_col_values - box_values
    return options


def get_set_sudoku_from_set_sudoku(grid: SetGrid) -> SetGrid:
    return [[calculate_options(grid, row, col) for col in range(9)] for row in range(9)]


set_sudoku = get_set_sudoku(SUDOKU)
print(calculate_options(set_sudoku, 0, 2))
print(find_minimum_set(set_sudoku))
pretty(set_sudoku)
"""
THE PLAN:
1. First convert the sudoku to a set sudoku of all possible options
2. Collapse all singletons
3. Find the smallest non singleton-set
4. Pick one of its values and just set it (w backtracking)
5. Calculate new setgrid 
6. go again
"""


def iteration_1(grid: SetGrid) -> Generator[SetGrid, None, None]:
    if minimum := find_minimum_set(grid):
        row, col = minimum
        print(f"{row=}, {col=}, {grid[row][col]}")
        for choice in list(grid[row][col]):
            grid[row][col] = {choice}
            pretty(get_set_sudoku_from_set_sudoku(grid))
            yield get_set_sudoku_from_set_sudoku(grid)
    else:
        print("Oh no, no minimum set")


list(iteration_1(set_sudoku))
