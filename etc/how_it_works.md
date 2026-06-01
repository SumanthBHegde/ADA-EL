# How the Sudoku Solver Project Works

This document explains the structure and execution flow of the Sudoku solver project.
It describes the main files, how the GUI interacts with the solver classes, and how the two algorithms operate.

## 1. Project Overview

The project solves 9×9 Sudoku puzzles using two algorithms:
- `BacktrackingSolver` in `backtracking.py`
- `BranchBoundSolver` in `branch_and_bound.py`

A graphical user interface in `gui.py` lets you load sample puzzles, run both algorithms, and visualize solving progress.
`main.py` starts the app.

## 2. File Responsibilities

- `main.py`
  - Entry point for the application.
  - Creates the Tkinter root window and instantiates `SudokuApp`.
  - Starts the Tkinter event loop.

- `gui.py`
  - Contains `SudokuApp`, the full Tkinter GUI.
  - Builds the 9×9 grid, controls, buttons, stats panel, and status bar.
  - Loads puzzles from `puzzles.py`.
  - Validates user input and prevents invalid entries.
  - Delegates solving tasks to the solver classes.
  - Runs animations using Tkinter `.after()`.

- `backtracking.py`
  - Defines `BacktrackingSolver`.
  - Implements standard recursive backtracking.
  - Checks row, column, and 3×3 box constraints.
  - Records performance statistics.

- `branch_and_bound.py`
  - Defines `BranchBoundSolver`.
  - Uses Minimum Remaining Values (MRV) to choose the most constrained cell.
  - Uses forward checking to prune branches early.
  - Records statistics including pruned branches.

- `puzzles.py`
  - Stores sample puzzles in `PUZZLES`.
  - Provides `get_random_puzzle()` and utility functions.
  - Defines difficulty categories for the GUI buttons.

- `demo.py`
  - Demonstrates the solver outside the GUI.
  - Loads a sample puzzle and solves it with both algorithms.
  - Prints the initial puzzle, solved puzzle, and stats.

## 3. Data Representation

The project represents Sudoku puzzles as a 9×9 list of lists:
- `0` means an empty cell.
- `1–9` are filled values.

Example:
```python
puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    ...
]
```

The GUI stores this grid internally as `self.original` and updates the display with `tk.StringVar` values.

## 4. Execution Flow

### GUI mode (`python main.py`)

1. `main.py` calls `SudokuApp(root)`.
2. `SudokuApp.__init__()` builds the UI and loads a default puzzle.
3. The user clicks a button such as `Backtracking` or `Branch & Bound`.
4. `SudokuApp` reads the current grid from the entry widgets.
5. The selected solver is called via `solve_puzzle(grid, record_steps=False)`.
6. The solver returns the solved grid and `True`/`False`.
7. The GUI updates the grid display and the stats panel.
8. If animation is selected, the GUI uses the recorded steps to animate placement and backtracking.

### Demo mode (`python demo.py`)

1. `demo.py` imports the solver classes and sample puzzles.
2. It selects a puzzle by difficulty or uses `Easy 1` by default.
3. It creates solver instances and solves the same puzzle with both algorithms.
4. It prints the original and solved grids plus solver statistics.

## 5. Backtracking Algorithm

`BacktrackingSolver.solve_puzzle()` calls `_solve()` with a deep copy of the grid.

The algorithm:
- Finds the first empty cell with `_find_empty_cell()`.
- Tries digits `1` through `9`.
- Uses `_is_valid()` to ensure the value is legal in the row, column, and 3×3 box.
- Places the digit and recurses.
- If deeper recursion fails, it resets the cell to `0` and tries the next digit.
- If no digit works, it backtracks to the previous cell.

Statistics collected:
- `nodes_explored`
- `backtracks`
- `solving_time`

## 6. Branch and Bound Algorithm

`BranchBoundSolver` improves on backtracking by choosing the best next cell and pruning dead branches.

The algorithm:
- Finds the most constrained empty cell using `_find_mrv_cell()`.
- Computes the legal domain of values for that cell with `_get_domain()`.
- If a cell has zero legal values, it prunes immediately.
- Tries each value from the domain.
- After each assignment, runs `_forward_check()` to ensure all other empty cells still have at least one legal option.
- If forward checking fails, it prunes that branch instead of recursing.
- Otherwise it recurses deeper.

Additional statistics:
- `pruned_branches`
- `nodes_explored`
- `backtracks`
- `solving_time`

## 7. GUI Features and Controls

- `Backtracking` — Solve immediately using pure backtracking.
- `Branch & Bound` — Solve immediately using the MRV-based solver.
- `Visualize BT` — Animate backtracking steps.
- `Visualize BB` — Animate branch-and-bound steps.
- `Easy`, `Medium`, `Hard`, `Expert` — Load a random puzzle from that difficulty.
- `Clear` — Reset the grid to empty.
- `Stop` — Halt any running animation.
- `Animation Speed` — Control the delay between visualization steps.

## 8. How Components Connect

- `main.py` → starts `SudokuApp`
- `SudokuApp` → loads puzzles from `puzzles.py`
- `SudokuApp` → calls `BacktrackingSolver` or `BranchBoundSolver`
- Solver classes → return a solved grid and stats
- `SudokuApp` → updates the GUI using the solver result

## 9. Running the Project

From the project folder:

```bash
python main.py
```

To run the demo script:

```bash
python demo.py
```

To solve a specific difficulty in demo mode:

```bash
python demo.py hard
```
