[private]
default:
    just --list

# Run unit tests.
test:
    poetry run mypy --check-untyped-defs sudoku.py
    poetry run pytest
