from typing import TypeAlias, Generator

Grid: TypeAlias = list[list[int]]
SudokuGrid: TypeAlias = list[list[set[int]]]

def convert_to_grid(puzzle: str) -> list[list[int]]:
    """Convert a puzzle string to a 2D grid of integers."""
    return [
        [int(c) if c != '_' else 0 for c in line]
        for line in puzzle.splitlines()
        if line
    ]

def new_sudoku(grid: Grid) -> SudokuGrid:
    """Convert a grid of integers to the a grid of possible-values."""
    return [
        [
            {n} if n else set(range(1,10))
            for n in row
        ]
        for row in grid
    ]


class Sudoku:

    def __init__(self, *, puzzle: str | None = None, grid: SudokuGrid | None = None, print=False):
        """Create a Sudoku object from a puzzle string or a grid of sets."""
        self._print = print
        if puzzle is not None:
            # print(f'{puzzle=}')
            self._grid = new_sudoku(convert_to_grid(puzzle))
        elif grid is not None:
            self._grid = grid

    def get(self, row: int, col: int) -> set[int]:
        return self._grid[row][col]
    
    def set(self, row: int, col: int, value: int):
        """Must be used with care, as it surgically updates the Sudoku grid."""
        self._grid[row][col] = {value}

    def pretty(self):

        def cellstr(x):
            if len(x) > 5:
                return x[0:4]+"+"
            else:
                n2 = ( 5 - len(x) ) // 2
                n1 = 5 - len(x) - n2
                return " " * n1 + x + " " * n2

        print("+-----+-----+-----+-----+-----+-----+-----+-----+-----+")
        sep = None
        for row in self._grid:
            if sep is not None:
                print(sep)
            print("|", end="")
            for cell in row:
                txt = "".join(map(str, cell))
                print(f"{cellstr(txt)}", end="|")
            print()
            sep = "+-----+-----+-----+-----+-----+-----+-----+-----+-----+"
        print("+-----+-----+-----+-----+-----+-----+-----+-----+-----+")

    def find_minimum_set(self) -> tuple[int, int] | None:
        sofar = 9
        (i, j) = (-1, -1)
        for r, row in enumerate(self._grid):
            for c, col in enumerate(row):
                L = len(col)  # Size of set.
                if 2 <= L < sofar:
                    sofar = L
                    i, j = r, c
        if i == -1:
            return None
        else:
            return (i, j)

    def propagate_constraints(self) -> 'Sudoku':
        return Sudoku(grid=[[Focus(self, row, col).calculate_options() for col in range(9)] for row in range(9)], print=self._print)
    
    def is_valid(self) -> bool:
        for row in self._grid:
            for cell in row:
                if not cell:
                    return False
        return True

    def simplify(self) -> Generator['Sudoku', None, None]:
        """Returns either 0 or 1 results"""
        sudoku = self
        while sudoku.is_valid():
            g = sudoku.propagate_constraints()
            if g._grid == sudoku._grid:
                yield sudoku
                break
            sudoku = g

    def as_puzzle_string(self) -> str:
        return "\n".join(
            "".join(str(next(iter(cell))) if len(cell) == 1 else "_"
            for cell in row)
            for row in self._grid
        )

    def solve(self, guesses) -> Generator['Sudoku', None, None]:
        if self._print:
            self.pretty()
            print()
        for sg in self.simplify():
            if minimum := sg.find_minimum_set():
                row, col = minimum
                L = list(sg.get(row, col))
                for choice in L:
                    new_guesses = [ f"Guessing {row=}, {col=}, {choice=}", *guesses ]       
                    if self._print:
                        print(f"Guesses: {new_guesses}")
                    # IMPORTANT: This mutates the Sudoku object, so this is only 
                    # safe because objects are generated fresh by simplify().
                    sg.set(row, col, choice)
                    yield from sg.solve(new_guesses)
            else:
                yield sg


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

def other_box_coords(row: int, col: int) -> Generator[tuple[int, int], None, None]:
    """Find the coordinates in the 3x3 containing box, excluding the current cell"""
    box_row = row // 3 * 3
    box_col = col // 3 * 3
    for r in range(box_row, box_row + 3):
        for c in range(box_col, box_col + 3):
            if r != row or c != col:
                yield r, c


class Focus:

    def __init__(self, sudoku: Sudoku, row: int, col: int):
        self._sudoku = sudoku
        self._row = row
        self._col = col

    def find_box_values(self) -> Generator[set[int], None, None]:
        """Find the values in the 3x3 containing box"""
        for r, c in other_box_coords(self._row, self._col):
            yield self._sudoku.get(r, c)

    def find_singleton_box_set_values(self) -> Generator[int, None, None]:
        """Find the values in the 3x3 containing box"""
        for values in self.find_box_values():
            if len(values) == 1:
                yield next(iter(values))

    def other_row_values(self) -> Generator[set[int], None, None]:
        """Find the values in the row that are already taken, excluding the current cell"""
        for r, c in other_row_coords(self._row, self._col):
            yield self._sudoku.get(r, c)

    def other_col_values(self) -> Generator[set[int], None, None]:
        """Find the values in the column that are already taken, excluding the current cell"""
        for r, c in other_col_coords(self._row, self._col):
            yield self._sudoku.get(r, c)

    def taken_row_values(self) -> Generator[int, None, None]:
        """Find the values in the row that are already taken, excluding the current cell"""
        for value_set in self.other_row_values():
            if len(value_set) == 1:
                yield next(iter(value_set))

    def taken_col_values(self):
        """Find the values in the column that are already taken, excluding the current cell"""
        for value_set in self.other_col_values():
            if len(value_set) == 1:
                yield next(iter(value_set))

    def value(self):
        return self._sudoku.get(self._row, self._col)

    def forced_row_value(self):
        """Find the value that is forced by the other values in the row"""
        other_values = set().union(*self.other_row_values())
        return self.value() - other_values

    def forced_col_value(self):
        """Find the value that is forced by the other values in the column"""
        other_values = set().union(*self.other_col_values())
        return self.value() - other_values

    def forced_box_value(self):
        """Find the value that is forced by the other values in the box"""
        other_values = set().union(*self.find_box_values())
        return self.value() - other_values

    def calculate_options(self) -> set[int]:

        forced = None
        
        frv = self.forced_row_value()
        if len(frv) == 1:
            if forced is None:
                forced = frv
            elif forced != frv:
                forced = set()
        elif len(frv) > 1:
            forced = set()
        
        fcv = self.forced_col_value()
        if len(fcv) == 1:
            if forced is None:
                forced = fcv
            elif forced != fcv:
                forced = set()
        elif len(fcv) > 1:
            forced = set()
        
        fbv = self.forced_box_value()
        if len(fbv) == 1:
            if forced is None:
                forced = fbv
            elif forced != fbv:
                forced = set()
        elif len(fbv) > 1:
            forced = set()

        if forced is not None:
            return forced

        singleton_row_values = set(self.taken_row_values())
        singleton_col_values = set(self.taken_col_values())
        box_values = set(self.find_singleton_box_set_values())
        options = self.value() - singleton_row_values - singleton_col_values - box_values
        return options

def solve(puzzle: str) -> str:
    """Solve a Sudoku puzzle and return the solution as a puzzle string."""
    S = Sudoku(puzzle=puzzle)
    simplified = list(S.simplify())
    if simplified:
        for n, G in enumerate(simplified[0].solve([])):
            return G.as_puzzle_string()

def main(puzzle: str):
    """Solve a Sudoku puzzle and print the progress and solution."""
    S = Sudoku(puzzle=puzzle, print=True)
    simplified = list(S.simplify())
    if not simplified:
        print("No solution")
        return
    
    for n, G in enumerate(simplified[0].solve([])):
        print(f'SOLUTION #{n+1}')
        G.pretty()
        break

