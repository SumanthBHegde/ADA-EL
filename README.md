# Sudoku Solver — Backtracking & Branch and Bound

> **Course:** Design and Analysis of Algorithms — Lab/Mini Project  
> **Language:** Python 3 | **GUI:** Tkinter | **Paradigm:** Object-Oriented Programming

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)  
2. [Algorithms Used](#2-algorithms-used)  
3. [Project Structure](#3-project-structure)  
4. [How to Run](#4-how-to-run)  
5. [GUI Features](#5-gui-features)  
6. [Time Complexity](#6-time-complexity)  
7. [Sample Puzzles](#7-sample-puzzles)  
8. [Algorithm Comparison](#8-algorithm-comparison)  

---

## 1. Problem Statement

Sudoku is a logic-based combinatorial number-placement puzzle. The objective is to fill a 9×9 grid with digits so that:
- Each **row** contains the digits 1–9 with no repetition.
- Each **column** contains the digits 1–9 with no repetition.
- Each of the nine **3×3 sub-grids** contains the digits 1–9 with no repetition.

This project solves the Sudoku puzzle using two algorithms and visually demonstrates and compares their performance.

---

## 2. Algorithms Used

### 2.1 Backtracking
- **Strategy:** Recursive DFS — scans cells left-to-right, top-to-bottom.
- **Validity check:** Row + Column + 3×3 Box.
- **On failure:** Undo last placement and try next digit.
- **Worst case:** O(9^m) where m = number of empty cells.

### 2.2 Branch and Bound (MRV + Forward Checking)
- **Branching:** Minimum Remaining Values (MRV) heuristic — always selects the most constrained cell.
- **Bounding:** Forward Checking — after each assignment, prune branches where any empty cell has no valid options.
- **Why faster in practice:** MRV detects dead-ends earlier; forward checking prunes entire subtrees.
- **Worst case:** Still O(9^m), but significantly faster on typical inputs.

---

## 3. Project Structure

```
sudoku_solver/
│
├── main.py              ← Entry point — run this file
├── gui.py               ← Full Tkinter GUI (SudokuApp class)
├── backtracking.py      ← Backtracking algorithm (BacktrackingSolver)
├── branch_and_bound.py  ← Branch & Bound algorithm (BranchBoundSolver)
├── puzzles.py           ← 7 sample puzzles (Easy / Medium / Hard / Expert)
│
├── README.md            ← This file
├── requirements.txt     ← No external dependencies
├── report.md            ← Full academic project report
├── pseudocode.md        ← Pseudocode for both algorithms
└── viva_qa.md           ← 30 Viva questions with detailed answers
```

---

## 4. How to Run

### Prerequisites
- Python 3.7 or higher
- Tkinter (bundled with Python on Windows and macOS)

```bash
# Linux (if tkinter is missing):
sudo apt-get install python3-tk   # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
```

### Run the application

```bash
# Navigate to the project directory
cd sudoku_solver

# Launch the GUI
python main.py
```

That's it — no `pip install` required.

---

## 5. GUI Features

| Button | Description |
|--------|-------------|
| ⚡ Backtracking | Instantly solve using backtracking |
| 🌿 Branch & Bound | Instantly solve using B&B |
| ▶ Visualize BT | Animated step-by-step backtracking |
| ▶ Visualize BB | Animated step-by-step branch & bound |
| Easy / Medium / Hard / Expert | Load a random puzzle of that difficulty |
| 🗑 Clear | Reset the grid |
| ⏹ Stop | Halt the running animation |
| Speed Slider | Control animation speed (Slow ↔ Fast) |

### Cell Colour Guide

| Colour | Meaning |
|--------|---------|
| Light blue | Given (pre-filled) cell |
| Yellow | Cell currently being tried (during animation) |
| Red-tinted | Cell being cleared (backtrack) |
| Sky blue | Final answer — Backtracking |
| Light green | Final answer — Branch & Bound |

### Statistics Panel
After solving, the right panel shows:
- **Time (s):** Wall-clock solve time in seconds
- **Nodes Explored:** Total cell-assignment attempts
- **Backtracks:** Number of undo operations
- **Branches Pruned:** (B&B only) Subtrees eliminated

---

## 6. Time Complexity

### Recurrence Relation

For a Sudoku puzzle with **m** empty cells:

```
T(m) = 9 × T(m-1) + O(1)
```

### Expansion

```
T(m) = 9 × T(m-1)
     = 9 × [9 × T(m-2)]       = 9² × T(m-2)
     = 9 × [9² × T(m-3)]      = 9³ × T(m-3)
     ⋮
     = 9^m × T(0)
     = 9^m × O(1)
     = O(9^m)
```

### Why exponential?
- At each empty cell, we have up to **9 choices**.
- There are **m** empty cells to fill.
- In the absolute worst case every branch must be explored.
- A standard 9×9 Sudoku has 50–65 empty cells, giving up to 9^64 ≈ 10^61 possibilities.

### Why Branch & Bound is faster in practice?
- **MRV** reduces the effective branching factor — cells with fewer options are explored first, failing fast.
- **Forward Checking** eliminates branches as soon as a dead-end is detected, before recursing deeper.
- Typical Sudoku: B&B explores 10–100× fewer nodes than pure backtracking.
- Worst case is still O(9^m) — no polynomial algorithm for Sudoku is known (NP-complete family).

---

## 7. Sample Puzzles

| Name | Difficulty | Givens | Empty |
|------|-----------|--------|-------|
| Easy 1 | Easy | 30 | 51 |
| Easy 2 | Easy | 28 | 53 |
| Medium 1 | Medium | 28 | 53 |
| Medium 2 | Medium | 25 | 56 |
| Hard 1 | Hard | 22 | 59 |
| Hard 2 | Hard | 22 | 59 |
| Expert | Expert | 17 | 64 |

---

## 8. Algorithm Comparison

| Criterion | Backtracking | Branch & Bound |
|-----------|-------------|----------------|
| Cell selection | Fixed (left→right, top→bottom) | MRV (most constrained first) |
| Dead-end detection | After placing — when recursion fails | Before placing — forward checking |
| Pruning | Implicit (trying all options) | Explicit (domain becomes empty) |
| Nodes explored | More | Fewer (often 10–100× fewer) |
| Time (practical) | Slower | Faster |
| Worst-case | O(9^m) | O(9^m) |
| Space | O(m) | O(m) |
| Implementation complexity | Simple | Moderate |

---

*Generated for academic submission — Design and Analysis of Algorithms Lab*
