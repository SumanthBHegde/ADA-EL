# Viva Questions & Answers
### Sudoku Solver — Backtracking & Branch and Bound
#### Design and Analysis of Algorithms Lab

---

## Section A — Basic Concepts (Q1–Q10)

**Q1. What is Sudoku, and what are its rules?**

Sudoku is a 9×9 logic puzzle. A valid solution must place digits 1–9 in every row, every column, and every 3×3 sub-grid, such that no digit repeats within any of these three constraint regions. Given cells are pre-filled; the solver must fill the remaining empty cells.

---

**Q2. What is the Backtracking algorithm?**

Backtracking is a recursive depth-first search algorithm. It builds the solution incrementally, one cell at a time. At each step it places a candidate digit, verifies the three Sudoku constraints, and recurses. If a conflict is found at any depth, it "backtracks" — undoes the last placement — and tries the next candidate digit. If no candidate works, it returns failure to the parent call.

---

**Q3. What is the time complexity of the Backtracking approach for Sudoku?**

O(9^m), where m is the number of empty cells.

- At each empty cell, up to 9 digits can be tried.
- There are m such cells to fill.
- In the worst case every combination is explored.

Recurrence: T(m) = 9·T(m-1), which solves to T(m) = O(9^m).

---

**Q4. Derive the recurrence T(m) = 9·T(m-1) and prove T(m) = O(9^m).**

At each recursive call we pick one empty cell and try up to 9 digits. Each successful placement reduces the count of empty cells by 1, giving:

```
T(m) = 9 × T(m-1) + O(1)
```

Expanding k times:
```
T(m) = 9^1 · T(m-1)
     = 9^2 · T(m-2)
     ...
     = 9^k · T(m-k)
```

Setting k = m:
```
T(m) = 9^m · T(0) = 9^m · O(1) = O(9^m)
```

---

**Q5. What is Branch and Bound?**

Branch and Bound is a general algorithmic framework for combinatorial optimisation and constraint satisfaction. It divides the problem into sub-problems (branching) and evaluates a bounding function to eliminate branches that cannot lead to a valid or optimal solution. In Sudoku, we branch on which cell to assign next (MRV) and bound by forward checking (prune when any cell's domain becomes empty).

---

**Q6. What is the MRV (Minimum Remaining Values) heuristic?**

MRV is a variable-ordering heuristic that always selects the unassigned variable (empty cell) with the fewest legal values remaining. This is the "fail-first" principle — cells with fewer options are more likely to cause failures, so exploring them first detects dead-ends earlier and prunes larger portions of the search tree.

---

**Q7. What is Forward Checking?**

After assigning a value to a cell, Forward Checking immediately looks ahead at every other unassigned cell and recomputes their domains (valid options). If any empty cell's domain becomes empty after the assignment, the current branch is provably infeasible and is pruned before recursing further.

---

**Q8. What data structures are used in this project?**

| Structure | Usage |
|-----------|-------|
| 9×9 list-of-lists | Represent the Sudoku grid |
| Set | Store the domain of valid values for a cell |
| List (stack via recursion) | Call stack for backtracking |
| Tuple | Store (row, col) cell references |
| List of tuples | Record animation steps (row, col, val, type) |

---

**Q9. What is the space complexity of the backtracking algorithm?**

O(m) where m is the number of empty cells — the maximum depth of the recursion stack. Each recursive call uses O(1) local variables, giving O(m) total stack space. The grid itself is modified in-place (O(1) extra space per call).

---

**Q10. What are the three constraints verified in Sudoku?**

1. **Row constraint** — each digit 1–9 appears exactly once in every row.
2. **Column constraint** — each digit 1–9 appears exactly once in every column.
3. **Box constraint** — each digit 1–9 appears exactly once in every 3×3 sub-grid.

---

## Section B — Algorithm Design (Q11–Q20)

**Q11. Why is Sudoku considered NP-complete (or NP-hard for generalised n×n Sudoku)?**

For an n×n generalised Sudoku, the problem of determining whether a solution exists is NP-complete. This means:
- No known polynomial-time algorithm exists.
- Solutions can be verified in polynomial time.
- The problem is at least as hard as any problem in NP.

For the fixed 9×9 case it is solvable in O(1) technically (finite fixed size), but the complexity as a function of empty cells is O(9^m), which is exponential in the number of unknowns.

---

**Q12. Why does the worst-case complexity of Branch & Bound remain O(9^m)?**

In an adversarial puzzle specifically constructed to defeat MRV:
- Every empty cell always has exactly 9 valid candidates.
- Forward checking never finds an empty domain.

In this case, MRV gives no selection advantage and forward checking prunes nothing. The algorithm degenerates to pure backtracking → O(9^m).

---

**Q13. How does MRV reduce the effective branching factor?**

If MRV selects cells that frequently have only 1 or 2 valid options:
- A cell with 1 option requires no choice — forced assignment.
- A cell with 2 options creates only 2 branches instead of 9.

The effective branching factor b < 9, making the practical complexity closer to O(b^m) with b << 9, even though the theoretical worst case is unchanged.

---

**Q14. Explain the difference between Backtracking and Dynamic Programming.**

| Aspect | Backtracking | Dynamic Programming |
|--------|-------------|---------------------|
| Problem type | Constraint satisfaction | Optimisation |
| Sub-problems | Overlapping (but revisited differently) | Overlapping, shared |
| Memoisation | Not used | Core technique |
| Pruning | Yes (on constraint violation) | Yes (via subproblem results) |
| Example | Sudoku, N-Queens | Fibonacci, Knapsack |

---

**Q15. Why is the `find_empty_cell()` function important in Backtracking?**

It determines the order in which cells are filled. Backtracking uses a fixed left-to-right, top-to-bottom scan, which is simple but not optimal. Branch & Bound replaces this with MRV, which dynamically selects the most constrained cell — a key source of its practical speedup.

---

**Q16. What is the "fail-first" principle?**

A search heuristic that advocates exploring the most constrained choices first. In Sudoku, cells with fewer valid options are more likely to lead to a contradiction. By trying these cells first (MRV), we detect dead-ends earlier and avoid wasting time in sub-trees that are guaranteed to fail.

---

**Q17. How is the 3×3 box identified for a cell at (row, col)?**

The top-left corner of the containing 3×3 box is at:
```
box_row = 3 × (row // 3)
box_col = 3 × (col // 3)
```
The box spans rows `[box_row, box_row+2]` and columns `[box_col, box_col+2]`.

---

**Q18. What is constraint propagation and how does Forward Checking relate to it?**

Constraint propagation is the process of applying constraints to reduce variable domains before or during search. Forward Checking is a simple form of constraint propagation: it propagates only after each assignment and only for directly constrained neighbours. Arc Consistency (AC-3) is a stronger form that propagates through chains of constraints, reducing domains further.

---

**Q19. Can the Sudoku solver run into infinite loops? Why or why not?**

No. The grid has exactly 81 cells, each filled at most once. Every recursive call either:
- Fills one more cell (reducing empty cells from m to m-1), or
- Returns immediately (base case or failure).

Since m is finite and strictly decreases with each placement, the recursion must terminate in finite time.

---

**Q20. What is the advantage of recording steps for animation separately from the actual solving?**

Recording and replaying keeps the algorithm pure and fast:
- The solver runs at full speed without GUI updates.
- All steps are stored; only then does the GUI animate them.
- Separating concerns makes code cleaner and the algorithm timing accurate.
- The solver's measured time reflects algorithm performance, not rendering speed.

---

## Section C — Implementation & Analysis (Q21–30)

**Q21. Why is `copy.deepcopy()` used when solving?**

The solver modifies the grid in-place during solving. Without a deep copy, solving would permanently alter the original user-entered puzzle. A deep copy creates a completely independent grid so the original is preserved for reset/comparison.

---

**Q22. What is the role of `time.perf_counter()` over `time.time()`?**

`time.perf_counter()` provides the highest-resolution timer available on the platform, suitable for short-duration benchmarks (microseconds). `time.time()` measures wall-clock time but with lower resolution and is affected by system clock adjustments. For algorithm timing, `perf_counter()` is the preferred choice.

---

**Q23. How does the GUI handle the animation without freezing?**

By using Tkinter's `root.after(delay_ms, callback)` method instead of `time.sleep()`. The `after()` method schedules the next animation step to execute after `delay_ms` milliseconds, returning control to the Tkinter event loop immediately. This keeps the GUI responsive (buttons remain clickable, the Stop button works) throughout the animation.

---

**Q24. What happens if a Sudoku puzzle has no solution?**

Both solvers return `False`. The GUI shows an error message box: "This puzzle has no valid solution." This can happen if the initial given digits already contain a conflict (duplicate in a row/column/box).

---

**Q25. What is the significance of the 17-given "Expert" puzzle?**

17 is the theoretically proven minimum number of given cells for a 9×9 Sudoku to have a unique solution. Puzzles with 16 or fewer givens cannot guarantee a unique solution. Expert puzzles with exactly 17 givens are the hardest class and require the deepest search trees.

---

**Q26. How could this solver be extended with Arc Consistency (AC-3)?**

After each assignment, instead of only checking direct row/col/box neighbours (Forward Checking), AC-3 would:
1. Add all arcs (pairs of constrained cells) to a queue.
2. For each arc (Xi, Xj), remove values from Xi's domain that have no support in Xj's domain.
3. If Xi's domain shrinks, re-add all arcs involving Xi.

This propagates constraints further, reducing domains more aggressively and pruning even more branches.

---

**Q27. What OOP principles are demonstrated in this project?**

| Principle | How Demonstrated |
|-----------|-----------------|
| Encapsulation | Each solver class encapsulates its algorithm and statistics; GUI class encapsulates all UI logic |
| Abstraction | `solve_puzzle()` is a clean public interface hiding recursion details |
| Single Responsibility | `backtracking.py`, `branch_and_bound.py`, `gui.py`, `puzzles.py` each have one clear responsibility |
| Separation of Concerns | Algorithm modules know nothing about Tkinter; GUI knows nothing about algorithm internals |

---

**Q28. Compare the number of "nodes explored" between BT and B&B on a Hard puzzle.**

Typical results on a Hard puzzle (~22 givens, ~59 empty cells):

| Metric | Backtracking | Branch & Bound |
|--------|-------------|----------------|
| Nodes explored | 50,000–200,000 | 500–5,000 |
| Backtracks | 5,000–25,000 | 50–500 |
| Time | 0.1–2.0 s | 0.001–0.05 s |

Branch & Bound explores approximately 10–100× fewer nodes.

---

**Q29. What real-world applications use backtracking or branch & bound?**

| Application | Algorithm |
|------------|-----------|
| Sudoku, N-Queens, Crosswords | Backtracking |
| Travelling Salesman Problem | Branch & Bound |
| Knapsack Problem | Branch & Bound |
| Scheduling / Resource allocation | Branch & Bound |
| Compiler register allocation | Graph colouring via backtracking |
| Cryptarithmetic | Constraint propagation / backtracking |
| SAT solvers (DPLL) | Backtracking + unit propagation |

---

**Q30. What future enhancements could be made to this project?**

1. **AC-3 constraint propagation** — stronger pruning than forward checking.
2. **Naked Singles / Hidden Singles** — human-like deduction before backtracking.
3. **Puzzle generator** — generate valid Sudoku puzzles with a unique solution.
4. **Difficulty auto-detection** — classify puzzles by solving techniques required.
5. **Heatmap visualization** — show which cells were explored most frequently.
6. **Multi-threading** — run BT and BB simultaneously, show real-time race.
7. **Web version** — port to HTML/CSS/JavaScript for browser-based demo.
8. **Hint system** — guide the user toward the next logical step.

---

*Viva preparation document — Design and Analysis of Algorithms Lab*
