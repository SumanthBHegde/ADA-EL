# Pseudocode — Sudoku Solver
### Design and Analysis of Algorithms — Lab Project

---

## Algorithm 1: Backtracking

### High-Level Description
```
SUDOKU-BACKTRACK(grid):
  cell ← FIND-EMPTY(grid)          // scan left-to-right, top-to-bottom
  IF cell = NIL THEN
    RETURN True                    // base case: grid complete
  (row, col) ← cell
  FOR num = 1 TO 9 DO
    IF IS-VALID(grid, row, col, num) THEN
      grid[row][col] ← num         // try placing num
      IF SUDOKU-BACKTRACK(grid) THEN
        RETURN True                // solution found ✔
      grid[row][col] ← 0           // backtrack: undo placement
  RETURN False                     // no digit works → trigger backtrack
```

### IS-VALID Procedure
```
IS-VALID(grid, row, col, num):
  // Check Row
  FOR c = 0 TO 8 DO
    IF grid[row][c] = num THEN RETURN False

  // Check Column
  FOR r = 0 TO 8 DO
    IF grid[r][col] = num THEN RETURN False

  // Check 3×3 Box
  box_r ← 3 * (row DIV 3)
  box_c ← 3 * (col DIV 3)
  FOR r = box_r TO box_r+2 DO
    FOR c = box_c TO box_c+2 DO
      IF grid[r][c] = num THEN RETURN False

  RETURN True                      // all constraints satisfied
```

### FIND-EMPTY Procedure
```
FIND-EMPTY(grid):
  FOR row = 0 TO 8 DO
    FOR col = 0 TO 8 DO
      IF grid[row][col] = 0 THEN
        RETURN (row, col)
  RETURN NIL                       // no empty cell found
```

---

## Algorithm 2: Branch and Bound (MRV + Forward Checking)

### High-Level Description
```
SUDOKU-BRANCH-BOUND(grid):
  (cell, domain) ← MRV-CELL(grid)  // BRANCH: pick most constrained cell
  IF cell = NIL THEN
    RETURN True                     // base case: grid complete
  IF |domain| = 0 THEN
    RETURN False                    // BOUND: dead-end, prune immediately
  (row, col) ← cell
  FOR num ∈ domain (sorted) DO
    grid[row][col] ← num
    IF FORWARD-CHECK(grid) THEN    // BOUND: check all empty cells
      IF SUDOKU-BRANCH-BOUND(grid) THEN
        RETURN True                // solution found ✔
    ELSE
      pruned_branches ← pruned_branches + 1  // branch eliminated
    grid[row][col] ← 0            // backtrack
  RETURN False
```

### MRV-CELL Procedure (Minimum Remaining Values)
```
MRV-CELL(grid):
  min_size ← ∞
  best_cell ← NIL
  best_domain ← ∅
  FOR row = 0 TO 8 DO
    FOR col = 0 TO 8 DO
      IF grid[row][col] = 0 THEN
        domain ← GET-DOMAIN(grid, row, col)
        IF |domain| = 0 THEN
          RETURN (row, col), ∅     // instant dead-end signal
        IF |domain| < min_size THEN
          min_size ← |domain|
          best_cell ← (row, col)
          best_domain ← domain
          IF min_size = 1 THEN
            RETURN best_cell, best_domain   // can't do better
  RETURN best_cell, best_domain
```

### GET-DOMAIN Procedure
```
GET-DOMAIN(grid, row, col):
  domain ← {1, 2, 3, 4, 5, 6, 7, 8, 9}
  // Remove row conflicts
  FOR each val IN grid[row] DO
    domain ← domain \ {val}
  // Remove column conflicts
  FOR r = 0 TO 8 DO
    domain ← domain \ {grid[r][col]}
  // Remove box conflicts
  box_r ← 3 * (row DIV 3)
  box_c ← 3 * (col DIV 3)
  FOR r = box_r TO box_r+2 DO
    FOR c = box_c TO box_c+2 DO
      domain ← domain \ {grid[r][c]}
  RETURN domain
```

### FORWARD-CHECK Procedure
```
FORWARD-CHECK(grid):
  FOR row = 0 TO 8 DO
    FOR col = 0 TO 8 DO
      IF grid[row][col] = 0 THEN
        IF |GET-DOMAIN(grid, row, col)| = 0 THEN
          RETURN False             // dead-end detected → prune
  RETURN True                     // all empty cells still viable
```

---

## Complexity Analysis

### Backtracking
```
Recurrence:    T(m) = 9 · T(m-1) + O(1)

Expansion:     T(m) = 9^1 · T(m-1)
                    = 9^2 · T(m-2)
                    = 9^k · T(m-k)
               At k = m:
                    = 9^m · T(0)
                    = 9^m · O(1)
               ∴  T(m) = O(9^m)
```

### Branch and Bound
```
Worst case:    T(m) = O(9^m)   (same as backtracking)

In practice:   Effective branching factor b < 9 due to:
                 1. MRV selects cells with smaller domains
                 2. Forward checking prunes entire sub-trees early
               Observed speedup: 10x – 100x on typical Sudoku puzzles
```

---

## Flowchart — Backtracking

```
        [START]
           │
           ▼
   [Find Empty Cell]
           │
    ┌──── NIL? ────┐
    │ Yes          │ No
    ▼              ▼
 [RETURN        [Set num = 1]
  True]              │
                     ▼
            [Is num valid?] ──No──► [num = num + 1]
                     │                    │
                    Yes                   │
                     ▼                    ▼
             [Place num]        [num > 9?] ──Yes──► [RETURN False]
                     │
                     ▼
               [Recurse]
                     │
             ┌──── True? ─────┐
             │ Yes             │ No
             ▼                 ▼
        [RETURN True]    [Remove num]
                         [Try num+1]
```

---

*Pseudocode document for academic submission.*
