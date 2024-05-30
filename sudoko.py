from typing import TypeAlias, Generator

Grid: TypeAlias = list[list[int]]
SetGrid: TypeAlias = list[list[set[int]]]

# Examples from https://sudoku.com/
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

EXAMPLE_EXPECTED = """
+---+---+---+---+---+---+---+---+---+
| 2 │ 9 │ 4 | 8 │ 3 │ 7 | 6 │ 1 │ 5 |
+---+---+---+---+---+---+---+---+---+
| 1 │ 7 │ 6 | 4 │ 9 │ 5 | 2 │ 3 │ 8 |
+---+---+---+---+---+---+---+---+---+
| 5 │ 8 │ 3 | 1 │ 6 │ 2 | 4 │ 9 │ 7 |
+---+---+---+---+---+---+---+---+---+
| 7 │ 6 │ 9 | 2 │ 5 │ 8 | 3 │ 4 │ 1 |
+---+---+---+---+---+---+---+---+---+
| 3 │ 5 │ 8 | 9 │ 1 │ 4 | 7 │ 2 │ 6 |
+---+---+---+---+---+---+---+---+---+
| 4 │ 1 │ 2 | 6 │ 7 │ 3 | 5 │ 8 │ 9 |
+---+---+---+---+---+---+---+---+---+
| 9 │ 4 │ 1 | 5 │ 2 │ 6 | 8 │ 7 │ 3 |
+---+---+---+---+---+---+---+---+---+
| 8 │ 3 │ 5 | 7 │ 4 │ 9 | 1 │ 6 │ 2 |
+---+---+---+---+---+---+---+---+---+
| 6 │ 2 │ 7 | 3 │ 8 │ 1 | 9 │ 5 │ 4 |
+---+---+---+---+---+---+---+---+---+"""

HARD = """
_____2___
___6_3___
_9_7____2
__2_14__8
37_82___1
185_6____
53____9__
__9___257
82_94____
"""

EXPERT = """
46_98_3__
__97_6_2_
_____19__
5_61_4___
_42___6__
____6547_
9________
657329___
2______93
"""

EXTREME = """
_5_____2_
__64__13_
4___9____
___1____2
__8_____9
_3__7_81_
__39__64_
________8
_7___5___
"""

def convert_to_grid(s: str) -> list[list[int]]:
    return [
        [int(c) if c != '_' else 0 for c in line]
        for line in s.splitlines()
        if line
    ]

SUDOKU = convert_to_grid(EXTREME)

def new_sudoku(grid: Grid) -> SetGrid:
    return [
        [
            {n} if n else set(range(1,10))
            for n in row
        ]
        for row in grid
    ]

def pretty(grid: SetGrid):
    # print(grid)
    # return

    def cellstr(x):
        if len(x) > 5:
            return x[0:4]+"+"
        else:
            n2 = ( 5 - len(x) ) // 2
            n1 = 5 - len(x) - n2
            return " " * n1 + x + " " * n2

    print("+-----+-----+-----+-----+-----+-----+-----+-----+-----+")
    sep = None
    for row in grid:
        if sep is not None:
            print(sep)
        print("|", end="")
        for cell in row:
            txt = "".join(map(str, cell))
            print(f"{cellstr(txt)}", end="|")
        print()
        sep = "+-----+-----+-----+-----+-----+-----+-----+-----+-----+"
    print("+-----+-----+-----+-----+-----+-----+-----+-----+-----+")


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

def find_box_values(grid: SetGrid, irow: int, icol: int) -> Generator[set[int], None, None]:
    """Find the values in the 3x3 containing box"""
    box_row = irow // 3 * 3
    box_col = icol // 3 * 3
    for row in range(box_row, box_row + 3):
        for col in range(box_col, box_col + 3):
            if row != irow or col != icol:
                    yield grid[row][col]

def find_singleton_box_set_values(grid: SetGrid, irow: int, icol: int) -> Generator[set[int], None, None]:
    """Find the values in the 3x3 containing box"""
    for values in find_box_values(grid, irow, icol):
        if len(values) == 1:
            yield next(iter(values))

def other_row_coords(row: int, col: int) -> Generator[tuple[int, int], None, None]:
    """Find the coordinates in the row, excluding the current cell"""
    for c in range(9):
        if c != col:
            yield row, c

def other_col_coords(row: int, col: int) -> Generator[tuple[int, int], None, None]:
    """Find the coordinates in the row, excluding the current cell"""
    for r in range(9):
        if r != row:
            yield r, col

def other_row_values(grid: SetGrid, row: int, col: int) -> Generator[set[int], None, None]:
    """Find the values in the row that are already taken, excluding the current cell"""
    for r, c in other_row_coords(row, col):
        yield grid[r][c]

def other_col_values(grid: SetGrid, row: int, col: int) -> Generator[set[int], None, None]:
    """Find the values in the column that are already taken, excluding the current cell"""
    for r, c in other_col_coords(row, col):
        yield grid[r][c]

def taken_row_values(grid: SetGrid, row: int, col: int):
    """Find the values in the row that are already taken, excluding the current cell"""
    for value_set in other_row_values(grid, row, col):
        if len(value_set) == 1:
            yield next(iter(value_set))

def taken_col_values(grid: SetGrid, row: int, col: int):
    """Find the values in the column that are already taken, excluding the current cell"""
    for value_set in other_col_values(grid, row, col):
        if len(value_set) == 1:
            yield next(iter(value_set))

def forced_row_value(grid: SetGrid, row: int, col: int):
    """Find the value that is forced by the other values in the row"""
    other_values = set().union(*other_row_values(grid, row, col))
    return grid[row][col] - other_values

def forced_col_value(grid: SetGrid, row: int, col: int):
    """Find the value that is forced by the other values in the column"""
    other_values = set().union(*other_col_values(grid, row, col))
    return grid[row][col] - other_values

def forced_box_value(grid: SetGrid, row: int, col: int):
    """Find the value that is forced by the other values in the box"""
    other_values = set().union(*find_box_values(grid, row, col))
    return grid[row][col] - other_values


def calculate_options(grid: SetGrid, row: int, col: int) -> set[int]:

    forced = None
    
    frv = forced_row_value(grid, row, col)
    if len(frv) == 1:
        if forced is None:
            forced = frv
        elif forced != frv:
            forced = set()
    elif len(frv) > 1:
        forced = set()
    
    fcv = forced_col_value(grid, row, col)
    if len(fcv) == 1:
        if forced is None:
            forced = fcv
        elif forced != fcv:
            forced = set()
    elif len(fcv) > 1:
        forced = set()
    
    fbv = forced_box_value(grid, row, col)
    if len(fbv) == 1:
        if forced is None:
            forced = fbv
        elif forced != fbv:
            forced = set()
    elif len(fbv) > 1:
        forced = set()

    if forced is not None:
        return forced

    singleton_row_values = set(taken_row_values(grid, row, col))
    singleton_col_values = set(taken_col_values(grid, row, col))
    box_values = set(find_singleton_box_set_values(grid, row, col))
    options = grid[row][col] - singleton_row_values - singleton_col_values - box_values
    # print(f"{grid[row][col]}, srv={singleton_row_values}, src={singleton_col_values}, bv={box_values}")
    # print(f"{options=}")
    # if forced is not None and not(forced) and options:
    #     print(f"{row=}, {col=}, value={grid[row][col]}")
    #     print(f"{options=}, {forced=}")
    #     print(f"{frv=}, {list(other_row_values())}")
    #     print(f"{fcv=}, {list(other_col_values())}")
    #     print(f"{fbv=}")
    return options

def propagate_constraints(grid: SetGrid) -> SetGrid:
    return [[calculate_options(grid, row, col) for col in range(9)] for row in range(9)]

"""
THE PLAN:
1. First convert the sudoku to a set sudoku of all possible options
2. Collapse all singletons
3. Find the smallest non singleton-set
4. Pick one of its values and just set it (w backtracking)
5. Calculate new setgrid 
6. go again
"""

def is_valid(grid: SetGrid) -> bool:
    for row in grid:
        for cell in row:
            if not cell:
                return False
    return True

def simplify(grid: SetGrid) -> Generator[SetGrid, None, None]:
    while is_valid(grid):
        g = propagate_constraints(grid)
        if g == grid:
            yield grid
            break
        grid = g

def solve(grid: SetGrid, guesses) -> Generator[SetGrid, None, None]:
    pretty(grid)
    print()
    for sg in simplify(grid):
        if minimum := find_minimum_set(sg):
            row, col = minimum
            L = list(sg[row][col])
            for choice in L:
                new_guesses = [ f"Guessing {row=}, {col=}, {choice=}", *guesses ]       
                print(f"Guesses: {new_guesses}")
                sg[row][col] = {choice}
                yield from solve(sg, new_guesses)
        else:
            yield sg

def main(puzzle: str):
    S = new_sudoku(convert_to_grid(puzzle))
    
    simplified = list(simplify(S))
    if not simplified:
        print("No solution")
        return
    
    for n, G in enumerate(solve(simplified[0], [])):
        print(f'SOLUTION #{n+1}')
        pretty(G)
        break

if __name__ == "__main__":
    main(EXTREME)
