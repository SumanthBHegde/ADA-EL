#!/usr/bin/env python3
"""
=============================================================
  BRANCH AND BOUND ALGORITHM — Sudoku Solver
=============================================================
Algorithm Type  : Branch and Bound with MRV Heuristic
Time Complexity : O(9^m) worst-case; far better in practice
Space Complexity: O(m) for the recursion call stack

KEY IMPROVEMENTS OVER PURE BACKTRACKING:
---------------------------------------------------------------------------
  BRANCHING STRATEGY — Minimum Remaining Values (MRV) Heuristic
      Instead of picking cells in fixed order (left-to-right, top-to-bottom),
      we always choose the empty cell that has the FEWEST legal values left.

      Why does this help?
        • Cells with 1 valid value *must* take that value — no choice to make.
        • Detecting dead-ends earlier (cells with 0 values) avoids exploring
          thousands of useless sub-trees.
        • This is also called the "fail-first" principle.

  BOUNDING FUNCTION — Forward Checking
      After placing a digit in a cell, we immediately scan every other
      empty cell and compute its domain (set of still-valid digits).
      If ANY empty cell ends up with an empty domain, we know this
      branch can NEVER lead to a solution, so we PRUNE it instantly.

      Without forward checking:
          We might place numbers in 10 cells before discovering that
          cell #11 has no valid options.
      With forward checking:
          We detect the dead-end after placing the very first
          inconsistent digit, saving enormous computation.
---------------------------------------------------------------------------

COMPLEXITY NOTE:
  The worst-case is still O(9^m) because in adversarial cases the MRV
  heuristic offers no advantage and forward checking finds no conflicts.
  However, for typical Sudoku puzzles the practical speedup is 10–100×.
=============================================================
"""

import time
import copy


class BranchBoundSolver:
    """
    Solves a 9×9 Sudoku puzzle using Branch and Bound.

    Techniques used:
        • MRV (Minimum Remaining Values) variable-ordering heuristic
        • Forward Checking (bounding / constraint propagation)

    Attributes:
        steps           (list)  : (row, col, val, type) for visualization.
        nodes_explored  (int)   : Number of cell-assignment attempts.
        pruned_branches (int)   : Branches eliminated by forward checking.
        backtracks      (int)   : Number of backtracks performed.
        solving_time    (float) : Wall-clock time in seconds.
    """

    def __init__(self):
        self.steps: list            = []
        self.nodes_explored: int    = 0
        self.pruned_branches: int   = 0
        self.backtracks: int        = 0
        self.solving_time: float    = 0.0

    # ----------------------------------------------------------
    #  Public Interface
    # ----------------------------------------------------------

    def solve_puzzle(self, grid: list, record_steps: bool = False):
        """
        Solve a Sudoku puzzle and return the result.

        Args:
            grid         : 9×9 list-of-lists; 0 = empty cell.
            record_steps : If True, fill self.steps for animation.

        Returns:
            (solved_grid, success) — success is True/False.
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
        Recursive Branch-and-Bound solve function.

        Step 1: BRANCH — Use MRV to select the most constrained cell.
        Step 2: BOUND  — After each assignment, run forward checking.
                         If any cell loses all valid values, prune.
        Step 3: RECURSE or BACKTRACK.
        """
        # --- SELECT variable (BRANCH) ---
        cell, domain = self._find_mrv_cell(grid)

        # BASE CASE A: No empty cells → puzzle is solved
        if cell is None:
            return True

        # BASE CASE B: A cell has zero valid options → dead end (BOUND)
        if len(domain) == 0:
            self.pruned_branches += 1
            return False

        row, col = cell
        self.nodes_explored += 1

        # Try each value in the domain (sorted for deterministic output)
        for num in sorted(domain):
            # --- PLACE ---
            grid[row][col] = num
            if record_steps:
                self.steps.append((row, col, num, 'place'))

            # --- FORWARD CHECK (BOUND) ---
            # After this assignment, does every other empty cell
            # still have at least one valid value?
            if self._forward_check(grid):
                # Branch looks viable → recurse deeper
                if self._solve(grid, record_steps):
                    return True   # ✔ Solution propagated up
            else:
                # Branch is provably dead → prune immediately
                self.pruned_branches += 1

            # --- BACKTRACK ---
            grid[row][col] = 0
            self.backtracks += 1
            if record_steps:
                self.steps.append((row, col, 0, 'backtrack'))

        return False   # All values exhausted for this cell

    # ----------------------------------------------------------
    #  MRV Heuristic
    # ----------------------------------------------------------

    def _find_mrv_cell(self, grid: list):
        min_size = 10        # More than the maximum possible (9)
        best_cell = None
        best_domain = None

        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    domain = self._get_domain(grid, row, col)

                    # Instant dead-end: return immediately
                    if len(domain) == 0:
                        return (row, col), set()

                    if len(domain) < min_size:
                        min_size   = len(domain)
                        best_cell  = (row, col)
                        best_domain = domain

                        # Early exit: a cell with exactly 1 valid value
                        # is already the most constrained possible
                        if min_size == 1:
                            return best_cell, best_domain

        return best_cell, best_domain   # May be (None, None) if grid full

    # ----------------------------------------------------------
    #  Domain Computation
    # ----------------------------------------------------------

    def _get_domain(self, grid: list, row: int, col: int) -> set:
        """
        Return the set of digits {1..9} that are legal for (row, col).

        A digit is illegal if it already appears in:
            • The same row
            • The same column
            • The same 3×3 box
        """
        domain = set(range(1, 10))

        # Eliminate row conflicts
        domain -= set(grid[row])

        # Eliminate column conflicts
        domain -= {grid[r][col] for r in range(9)}

        # Eliminate 3×3-box conflicts
        box_r = 3 * (row // 3)
        box_c = 3 * (col // 3)
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                domain.discard(grid[r][c])

        return domain

    # ----------------------------------------------------------
    #  Forward Checking (Bounding Function)
    # ----------------------------------------------------------

    def _forward_check(self, grid: list) -> bool:
        """
        After a recent assignment, verify that EVERY remaining empty
        cell still has at least one legal digit.

        Returns:
            True  — All empty cells still have ≥ 1 valid option.
            False — At least one empty cell has NO valid options
                    (this branch is guaranteed to fail → prune it).
        """
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    if len(self._get_domain(grid, row, col)) == 0:
                        return False   # Dead-end detected
        return True   # Branch still viable

    # ----------------------------------------------------------
    #  Helpers
    # ----------------------------------------------------------

    def _reset_stats(self):
        """Clear counters before a fresh solve."""
        self.steps           = []
        self.nodes_explored  = 0
        self.pruned_branches = 0
        self.backtracks      = 0
        self.solving_time    = 0.0

    def get_stats(self) -> dict:
        """Return a summary dictionary for the GUI stats panel."""
        return {
            "Algorithm"       : "Branch & Bound",
            "Time (s)"        : f"{self.solving_time:.6f}",
            "Nodes Explored"  : self.nodes_explored,
            "Backtracks"      : self.backtracks,
            "Branches Pruned" : self.pruned_branches,
            "Steps Recorded"  : len(self.steps),
        }
