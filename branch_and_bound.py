#!/usr/bin/env python3

import time
import copy


class BranchBoundSolver:
  

    def __init__(self):
        self.steps: list            = []
        self.nodes_explored: int    = 0
        self.pruned_branches: int   = 0
        self.backtracks: int        = 0
        self.solving_time: float    = 0.0

    
    

    def solve_puzzle(self, grid: list, record_steps: bool = False):
        
        self._reset_stats()
        grid_copy = copy.deepcopy(grid)

        start = time.perf_counter()
        success = self._solve(grid_copy, record_steps)
        self.solving_time = time.perf_counter() - start

        return grid_copy, success


    def _solve(self, grid: list, record_steps: bool) -> bool:
       
        # --- SELECT variable (BRANCH) ---
        cell, domain = self._find_mrv_cell(grid)

        # BASE CASE A: No empty cells → puzzle is solved
        if cell is None:
            return True

        # BASE CASE B: A cell has zero valid options → dead end 
        if len(domain) == 0:
            self.pruned_branches += 1
            return False

        row, col = cell
        self.nodes_explored += 1

        for num in sorted(domain):
            # --- PLACE ---
            grid[row][col] = num
            if record_steps:
                self.steps.append((row, col, num, 'place'))

            if self._forward_check(grid):
                if self._solve(grid, record_steps):
                    return True   
            else:
                self.pruned_branches += 1

            # --- BACKTRACK ---
            grid[row][col] = 0
            self.backtracks += 1
            if record_steps:
                self.steps.append((row, col, 0, 'backtrack'))

        return False   # All values exhausted for this cell

    
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

                        if min_size == 1:
                            return best_cell, best_domain

        return best_cell, best_domain   # May be (None, None) if grid full

        

    def _get_domain(self, grid: list, row: int, col: int) -> set:
        
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

    

    def _forward_check(self, grid: list) -> bool:
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    if len(self._get_domain(grid, row, col)) == 0:
                        return False   # Dead-end detected
        return True   # Branch still viable

    

    def _reset_stats(self):
        """Clear counters before a fresh solve."""
        self.steps           = []
        self.nodes_explored  = 0
        self.pruned_branches = 0
        self.backtracks      = 0
        self.solving_time    = 0.0

    def get_stats(self) -> dict:
        return {
            "Algorithm"       : "Branch & Bound",
            "Time (s)"        : f"{self.solving_time:.6f}",
            "Nodes Explored"  : self.nodes_explored,
            "Backtracks"      : self.backtracks,
            "Branches Pruned" : self.pruned_branches,
            "Steps Recorded"  : len(self.steps),
        }
