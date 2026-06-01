#!/usr/bin/env python3
"""Demo script for the Sudoku solver project.

Run this file to see a sample puzzle solved by both
Backtracking and Branch & Bound, with timing and stats.
"""

import sys
import os
import copy

# Ensure imports work when running from the project directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from puzzles import PUZZLES, get_random_puzzle
from backtracking import BacktrackingSolver
from branch_and_bound import BranchBoundSolver


def pretty_print_grid(grid):
    """Print a 9x9 Sudoku grid in a readable format."""
    horizontal = "+-------+-------+-------+"
    for r, row in enumerate(grid):
        if r % 3 == 0:
            print(horizontal)
        row_str = ""
        for c, value in enumerate(row):
            if c % 3 == 0:
                row_str += "| "
            row_str += f"{value if value != 0 else '.'} "
        row_str += "|"
        print(row_str)
    print(horizontal)


def solve_and_print(solver, grid, name):
    """Solve the grid with the given solver and print stats."""
    solved_grid, success = solver.solve_puzzle(grid, record_steps=False)
    print(f"\n{name} result:")
    print("Solved:" if success else "No solution found.")
    print(pretty_stats(solver.get_stats()))
    pretty_print_grid(solved_grid)


def pretty_stats(stats):
    """Format stats dictionary into a readable multiline string."""
    return "\n".join(f"{key}: {value}" for key, value in stats.items())


def main():
    if len(sys.argv) > 1:
        difficulty = sys.argv[1].capitalize()
        if difficulty in ("Easy", "Medium", "Hard", "Expert"):
            puzzle_name, puzzle = get_random_puzzle(difficulty)
        else:
            print("Usage: python demo.py [easy|medium|hard|expert]")
            return
    else:
        puzzle_name, puzzle = "Easy 1", copy.deepcopy(PUZZLES["Easy 1"])

    print("Sudoku Solver Demo")
    print("====================")
    print(f"Puzzle: {puzzle_name}")
    pretty_print_grid(puzzle)

    bt_solver = BacktrackingSolver()
    bb_solver = BranchBoundSolver()

    solve_and_print(bt_solver, copy.deepcopy(puzzle), "Backtracking")
    solve_and_print(bb_solver, copy.deepcopy(puzzle), "Branch & Bound")

    print("\nDemo complete.")
    print("Run with a difficulty argument to solve a different sample puzzle:")
    print("  python demo.py hard")


if __name__ == "__main__":
    main()
