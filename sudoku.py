from typing import TypeAlias, Generator
import math

TinyIntSet: TypeAlias = set[int]
SudokuGrid: TypeAlias = list[list[TinyIntSet]]

class Configuration:
    """A configuration for a Sudoku grid, with methods that only depend on the size of the grid."""

    def __init__(self, *, size, do_print=False):
        self._print = do_print
        self._size = size
        self._cell_count = size * size
        print( 'SIZE', self._size, 'CELL_COUNT', self._cell_count)

    def cell_count(self) -> int:
        return self._cell_count
    
    def cell_range(self) -> range:
        return range(self._cell_count)
    
    def other_row_coords(self, row: int, col: int) -> Generator[tuple[int, int], None, None]:
        """Find the coordinates in the row, excluding the current cell"""
        for c in self.cell_range():
            if c != col:
                yield row, c

    def other_col_coords(self, row: int, col: int) -> Generator[tuple[int, int], None, None]:
        """Find the coordinates in the row, excluding the current cell"""
        for r in self.cell_range():
            if r != row:
                yield r, col

    def other_box_coords(self, row: int, col: int) -> Generator[tuple[int, int], None, None]:
        """Find the coordinates in the 3x3 containing box, excluding the current cell"""
        box_row = row // self._size * self._size
        box_col = col // self._size * self._size
        for r in range(box_row, box_row + self._size):
            for c in range(box_col, box_col + self._size):
                if r != row or c != col:
                    yield r, c


def as_1_char(x):
    """Convert an integer to a single character string, from 0 to 35"""
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return alphabet[x]


class Sudoku:
    """A Sudoku grid, with methods to simplify and solve it."""

    def __init__(self, *, grid: SudokuGrid, configuration=None, do_print:bool = False):
        self._configuration = configuration or Configuration(do_print=do_print, size=math.isqrt(len(grid)))
        self._grid = grid

    def print(self, *args, **kwargs):
        self._configuration._print(*args, **kwargs)

    def is_printing(self) -> bool:
        return self._configuration._print

    def get(self, row: int, col: int) -> set[int]:
        return self._grid[row][col]
    
    def set_choice(self, row: int, col: int, value: int):
        """Must be used with care, as it surgically updates the Sudoku grid."""
        self._grid[row][col] = {value}

    def pretty(self):
        """Print the Sudoku grid in a human-friendly format."""

        def cellstr(x):
            if len(x) > 5:
                return x[0:4]+"+"
            else:
                n2 = ( 5 - len(x) ) // 2
                n1 = 5 - len(x) - n2
                return " " * n1 + x + " " * n2

        N = self._configuration.cell_count()
        print(N*"+-----", end='')
        print("+")
        sep = False
        for row in self._grid:
            if sep:
                print(N*"+-----", end='')
                print("+")
            print("|", end="")
            for cell in row:
                txt = "".join(map(as_1_char, cell))
                print(f"{cellstr(txt)}", end="|")
            print()
            sep = True
        print(N*"+-----", end='')
        print("+")

    def find_minimum_set(self) -> tuple[int, int] | None:
        """Find a cell with the smallest set of possible values."""
        sofar = self._configuration.cell_count()
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
        """Repeatedly apply the constraints until no more changes are made."""
        R = self._configuration.cell_range()
        return Sudoku(
            grid=[[Focus(self, row, col).calculate_options() for col in R] for row in R], 
            configuration=self._configuration
        )
    
    def is_valid(self) -> bool:
        """Check if the Sudoku grid is valid i.e. no cells have an empty set."""
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
        """Return the Sudoku grid as a puzzle string."""
        return "\n".join(
            "".join(as_1_char(next(iter(cell))) if len(cell) == 1 else "_"
            for cell in row)
            for row in self._grid
        )

    def solve(self, guesses) -> Generator['Sudoku', None, None]:
        if self.is_printing():
            self.pretty()
            print()
        for sg in self.simplify():
            if minimum := sg.find_minimum_set():
                row, col = minimum
                L = list(sg.get(row, col))
                for choice in L:
                    new_guesses = [ f"Guessing {row=}, {col=}, {choice=}", *guesses ]       
                    if self.is_printing():
                        print(f"Guesses: {new_guesses}")
                    # IMPORTANT: This mutates the Sudoku object, so this is only 
                    # safe because SudokuGrids are generated completely fresh by 
                    # propagate_constraints() and hence simplify().
                    sg.set_choice(row, col, choice)
                    yield from sg.solve(new_guesses)
            elif sg.is_valid():
                yield sg


class Forcing:
    """A class to track forced values in a Sudoku grid."""
            
    def __init__(self):
        self._forced: set[int] | None = None

    def restrict_by_value_group(self, current, values):
        forced_choices = current - set().union(*values)
        if len(forced_choices) == 1:
            if self._forced is None:
                self._forced = forced_choices
            elif self._forced != forced_choices:
                self._forced = set()                
        elif len(forced_choices) > 1:
            self._forced = set()

    def has_forced_value(self):
        return self._forced is not None

    def forced_value(self):
        return self._forced

class Focus:
    """A cell in a Sudoku grid, with methods to calculate the possible values."""

    def __init__(self, sudoku: Sudoku, row: int, col: int):
        self._sudoku = sudoku
        self._row = row
        self._col = col

    def value(self):
        return self._sudoku.get(self._row, self._col)
    
    def other_row_coords(self):
        return self._sudoku._configuration.other_row_coords(self._row, self._col)
    
    def other_col_coords(self):
        return self._sudoku._configuration.other_col_coords(self._row, self._col)
    
    def other_box_coords(self):
        return self._sudoku._configuration.other_box_coords(self._row, self._col)
    
    def as_values(self, coords):
        for r, c in coords:
            yield self._sudoku.get(r, c)

    def value_groups(self):
        yield self.as_values( self.other_row_coords() )
        yield self.as_values( self.other_col_coords() )
        yield self.as_values( self.other_box_coords() )

    def calculate_options(self) -> set[int]:
        """Calculate the possible values for this cell given the 
        values in the row, column and box.
        """
         
        current = self.value()
        
        forcing = Forcing()
        for values in self.value_groups():
            forcing.restrict_by_value_group(current, values)
        
        if forcing.has_forced_value():
            current = current & forcing.forced_value()

        if not current:
            return current
        
        for values in self.value_groups():
            if not current:
                return current
            current = current - { next(iter(v)) for v in values if len(v) == 1 }
        
        return current


class Puzzle:
    """A Sudoku puzzle. The grid is represented as a list of lists of sets."""

    def __init__(self, puzzle: str):
        self._grid: SudokuGrid = [
            [ {int(c)} if c != '_' else set(range(1,len(line)+1)) for c in line ]
            for line in puzzle.splitlines()
            if line
        ]  

    def new_sudoku(self, *, do_print=False) -> 'Sudoku':
        return Sudoku(grid=self._grid, do_print=do_print)


def solve(puzzle: str) -> str:
    """Solve a Sudoku puzzle and return the solution as a puzzle string."""
    P = Puzzle(puzzle=puzzle)
    S = P.new_sudoku()
    simplified = list(S.simplify())
    if simplified:
        for n, G in enumerate(simplified[0].solve([])):
            return G.as_puzzle_string()
    return "No solution"

def main(puzzle: str):
    """Solve a Sudoku puzzle and print the progress and solution."""
    P = Puzzle(puzzle=puzzle)
    S = P.new_sudoku(do_print=True)
    simplified = list(S.simplify())
    if not simplified:
        print("No solution")
        return
    
    for n, G in enumerate(simplified[0].solve([])):
        print(f'SOLUTION #{n+1}')
        G.pretty()
        return
    
    print("No solution")

