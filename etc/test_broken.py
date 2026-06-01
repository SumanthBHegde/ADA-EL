#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from puzzles import PUZZLES
from backtracking import BacktrackingSolver
from branch_and_bound import BranchBoundSolver

broken = ["Contradictory Row", "Contradictory Box", "All Ones"]

for name in broken:
    print('\n==', name, '==')
    grid = PUZZLES[name]
    for solver_cls in (BacktrackingSolver, BranchBoundSolver):
        solver = solver_cls()
        solved_grid, ok = solver.solve_puzzle([row[:] for row in grid])
        print(f"{solver_cls.__name__}: solved={ok}, stats={solver.get_stats()}")
