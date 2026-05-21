#!/usr/bin/env python3
"""
=============================================================
  BACKTRACKING ALGORITHM — Sudoku Solver
=============================================================
Algorithm Type  : Recursive Depth-First Search (DFS)
Time Complexity : O(9^m)  where m = number of empty cells
Space Complexity: O(m)    for the recursion call stack

HOW IT WORKS:
  1. Scan the grid left-to-right, top-to-bottom.
  2. Find the first empty cell (value = 0).
  3. Try placing digits 1 through 9 in that cell.
  4. For each digit, check validity against:
       - All cells in the same row
       - All cells in the same column
       - All cells in the same 3×3 box
  5. If valid, place the digit and recurse.
  6. If the recursion eventually fails (no valid digit
     for a later cell), BACKTRACK: remove the digit and
     try the next one.
  7. Repeat until the grid is completely filled.
=============================================================
"""

import time
import copy


class BacktrackingSolver:

    def __init__(self):
        self.steps: list       = []
        self.nodes_explored: int = 0
        self.backtracks: int   = 0
        self.solving_time: float = 0.0

    # ----------------------------------------------------------
    #  Public Interface
    # ----------------------------------------------------------

    def solve_puzzle(self, grid: list, record_steps: bool = False):
        """
        Solve a Sudoku puzzle and return the result.

        Args:
            grid         : 9×9 list-of-lists; 0 represents empty cells.
            record_steps : If True, fill self.steps for animation.

        Returns:
            (solved_grid, success) where success is True/False.
        """
        self._reset_stats()
        grid_copy = copy.deepcopy(grid)

        start = time.perf_counter()
        success = self._solve(grid_copy, record_steps)
        self.solving_time = time.perf_counter() - start

        return grid_copy, success

    # ----------------------------------------------------------
    #  Core Algorithm
    # ----------------------------------------------------------

    def _solve(self, grid: list, record_steps: bool) -> bool:
        """
        Recursive backtracking function.

        Returns True when a complete, valid solution is found.
        Returns False when no digit 1–9 fits in the current empty
        cell, signalling the parent call to backtrack.
        """
        # BASE CASE: no empty cell means puzzle is completely solved
        empty_cell = self._find_empty_cell(grid)
        if empty_cell is None:
            return True                          # ✔ Solution found

        row, col = empty_cell

        # RECURSIVE CASE: try every digit from 1 to 9
        for num in range(1, 10):
            self.nodes_explored += 1

            if self._is_valid(grid, row, col, num):
                # ------ PLACE ------
                grid[row][col] = num
                if record_steps:
                    self.steps.append((row, col, num, 'place'))

                # ------ RECURSE ------
                if self._solve(grid, record_steps):
                    return True                  # ✔ Propagated success

                # ------ BACKTRACK ------
                grid[row][col] = 0
                self.backtracks += 1
                if record_steps:
                    self.steps.append((row, col, 0, 'backtrack'))

        return False   # No digit worked → trigger backtrack in parent

    # ----------------------------------------------------------
    #  Helper Methods
    # ----------------------------------------------------------

    def _find_empty_cell(self, grid: list):
        """
        Scan the grid left-to-right, top-to-bottom.
        Returns (row, col) of the first empty cell, or None.
        """
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    return (row, col)
        return None   # Grid is full

    def _is_valid(self, grid: list, row: int, col: int, num: int) -> bool:

        # --- Row check ---
        if num in grid[row]:
            return False

        # --- Column check ---
        for r in range(9):
            if grid[r][col] == num:
                return False

        # --- 3×3 Box check ---
        box_r = 3 * (row // 3)   # Top row of this box
        box_c = 3 * (col // 3)   # Left col of this box
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if grid[r][c] == num:
                    return False

        return True   # All three constraints satisfied

    def _reset_stats(self):
        """Clear counters before a fresh solve."""
        self.steps          = []
        self.nodes_explored = 0
        self.backtracks     = 0
        self.solving_time   = 0.0

    def get_stats(self) -> dict:
        """Return a summary dictionary for display in the GUI."""
        return {
            "Algorithm"       : "Backtracking",
            "Time (s)"        : f"{self.solving_time:.6f}",
            "Nodes Explored"  : self.nodes_explored,
            "Backtracks"      : self.backtracks,
            "Steps Recorded"  : len(self.steps),
        }
