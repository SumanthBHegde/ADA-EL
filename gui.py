#!/usr/bin/env python3
"""
=============================================================
  SUDOKU SOLVER — GUI Application
  Using Backtracking and Branch & Bound Algorithms
=============================================================
Framework : Python 3 + Tkinter (built-in, no install needed)
Pattern   : Object-Oriented (class SudokuApp)

LAYOUT:
  ┌──────────────────────────────────────────────────┐
  │               TITLE BAR                          │
  ├────────────────────────┬─────────────────────────┤
  │                        │  STATISTICS PANEL        │
  │    9×9 SUDOKU GRID     │  ─────────────────────   │
  │                        │  BT: time / nodes / BT   │
  │                        │  BB: time / nodes / pruned│
  ├────────────────────────┴─────────────────────────┤
  │  [BT Solve] [BB Solve] [Viz BT] [Viz BB]         │
  │  [Easy] [Medium] [Hard] [Expert] [Clear] [Stop]  │
  │  Animation Speed: [●───────────]                 │
  ├──────────────────────────────────────────────────┤
  │  STATUS BAR                                      │
  └──────────────────────────────────────────────────┘
=============================================================
"""

import tkinter as tk
from tkinter import messagebox, font as tkfont
import copy
import random

from backtracking   import BacktrackingSolver
from branch_and_bound import BranchBoundSolver
from puzzles        import PUZZLES, PUZZLE_NAMES, DIFFICULTY_GROUPS, \
                           get_random_puzzle, count_empty, count_givens

# ==============================================================
#  COLOR PALETTE  (change values here to re-theme the whole app)
# ==============================================================
C = {
    # Window / Frame backgrounds
    "bg_main"      : "#f0f4f8",
    "bg_card"      : "#ffffff",
    "bg_title"     : "#1e3a5f",
    "bg_status"    : "#1e3a5f",
    "bg_stats"     : "#f0f4f8",

    # Grid cells
    "cell_normal"  : "#ffffff",
    "cell_given"   : "#dbeafe",   # light blue  — pre-filled cells
    "cell_place"   : "#fef9c3",   # light yellow — currently placing
    "cell_back"    : "#fee2e2",   # light red    — backtracking
    "cell_bt_done" : "#e0f2fe",   # sky blue     — BT final answer
    "cell_bb_done" : "#dcfce7",   # light green  — BB final answer

    # Cell text
    "num_given"    : "#1e3a8a",   # dark blue, bold
    "num_bt"       : "#1d4ed8",   # blue
    "num_bb"       : "#15803d",   # green
    "num_place"    : "#92400e",   # amber
    "num_back"     : "#b91c1c",   # red

    # Borders
    "border_box"   : "#374151",   # thick — 3×3 box
    "border_cell"  : "#cbd5e1",   # thin  — individual cell

    # Buttons
    "btn_bt"       : "#1d4ed8",
    "btn_bb"       : "#15803d",
    "btn_viz_bt"   : "#0369a1",
    "btn_viz_bb"   : "#166534",
    "btn_easy"     : "#7c3aed",
    "btn_medium"   : "#a855f7",
    "btn_hard"     : "#db2777",
    "btn_expert"   : "#dc2626",
    "btn_broken"   : "#7f1d1d",
    "btn_clear"    : "#6b7280",
    "btn_stop"     : "#ea580c",
    "btn_fg"       : "#ffffff",
    "btn_hover"    : "#000000",   # placeholder — see _add_hover

    # Text
    "fg_title"     : "#ffffff",
    "fg_status"    : "#93c5fd",
    "fg_label"     : "#1e293b",
    "fg_stats_hdr" : "#1e3a5f",
    "fg_stats_val" : "#374151",
}

# Font definitions
FONT_TITLE    = ("Helvetica", 18, "bold")
FONT_SUBTITLE = ("Helvetica", 10)
FONT_CELL     = ("Helvetica", 18, "bold")
FONT_CELL_GV  = ("Helvetica", 18, "bold")
FONT_BTN      = ("Helvetica", 10, "bold")
FONT_LABEL    = ("Helvetica", 10)
FONT_LABEL_B  = ("Helvetica", 10, "bold")
FONT_STAT_HDR = ("Helvetica", 11, "bold")
FONT_STAT_VAL = ("Helvetica", 10)
FONT_STATUS   = ("Helvetica", 10)

# Animation speed options  (label → milliseconds per step)
SPEED_OPTIONS = [
    ("Slow (200ms)",   200),
    ("Normal (60ms)",   60),
    ("Fast (15ms)",     15),
    ("Turbo (3ms)",      3),
]

CELL_W = 52     # pixel width  of each cell
CELL_H = 52     # pixel height of each cell


# ==============================================================
#  MAIN APPLICATION CLASS
# ==============================================================

class SudokuApp:
    """
    Full Tkinter Sudoku solver application.

    Responsibilities:
        • Build and manage the UI (grid, buttons, stats, status bar)
        • Accept user input into the 9×9 grid
        • Delegate solving to BacktrackingSolver / BranchBoundSolver
        • Animate step-by-step solving using Tkinter's .after() scheduler
        • Display performance statistics after each solve
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sudoku Solver — Backtracking & Branch-and-Bound")
        self.root.configure(bg=C["bg_main"])
        self.root.resizable(False, False)

        # ---- Solver instances ----
        self.bt_solver = BacktrackingSolver()
        self.bb_solver = BranchBoundSolver()

        # ---- Grid state ----
        # cells[r][c] → tk.Entry widget
        self.cells      = [[None] * 9 for _ in range(9)]
        # cell_vars[r][c] → tk.StringVar bound to entry
        self.cell_vars  = [[tk.StringVar() for _ in range(9)] for _ in range(9)]
        # original puzzle snapshot (9×9 int grid, 0 = empty)
        self.original   = [[0] * 9 for _ in range(9)]
        # tracks which cells were given (cannot be edited by solver display)
        self.is_given   = [[False] * 9 for _ in range(9)]

        # ---- Animation state ----
        self.anim_steps : list = []   # collected (r,c,val,type) tuples
        self.anim_index : int  = 0
        self.animating  : bool = False
        self.anim_job          = None  # Tkinter after() job handle
        self.anim_delay : int  = 60   # ms between animation steps
        self.anim_mode  : str  = ""   # "BT" or "BB"

        # ---- Build UI ----
        self._build_title()
        self._build_body()    # grid + stats side-by-side
        self._build_controls()
        self._build_status()

        # ---- Load default puzzle ----
        self.load_puzzle_by_difficulty("Medium")

    # ==========================================================
    #  UI CONSTRUCTION
    # ==========================================================

    def _build_title(self):
        """Top title bar."""
        title_frame = tk.Frame(self.root, bg=C["bg_title"], pady=12)
        title_frame.pack(fill="x")

        tk.Label(title_frame,
                 text="🔢  SUDOKU SOLVER",
                 font=FONT_TITLE,
                 bg=C["bg_title"], fg=C["fg_title"]
                 ).pack()
        tk.Label(title_frame,
                 text="Backtracking  ·  Branch and Bound  |  Algorithm Design & Analysis",
                 font=FONT_SUBTITLE,
                 bg=C["bg_title"], fg="#93c5fd"
                 ).pack()

    def _build_body(self):
        """Middle section: grid on the left, stats on the right."""
        body = tk.Frame(self.root, bg=C["bg_main"], padx=16, pady=12)
        body.pack(fill="both", expand=True)

        self._build_grid(body)
        self._build_stats_panel(body)

    def _build_grid(self, parent):
        """Construct the 9×9 Sudoku entry grid."""
        # Outer wrapper
        outer = tk.Frame(parent, bg=C["border_box"], bd=3, relief="solid")
        outer.pack(side="left", padx=(0, 16), fill="both")

        # Create 3×3 arrangement of 3×3 "box frames"
        for box_r in range(3):
            for box_c in range(3):
                # Each box has a solid border to show the 3×3 regions
                box = tk.Frame(outer,
                               bg=C["border_cell"],
                               bd=2,
                               relief="solid",
                               highlightthickness=0)
                box.grid(row=box_r, column=box_c,
                         padx=1, pady=1,
                         sticky="nsew")

                # 9 cells inside each box
                for cell_r in range(3):
                    for cell_c in range(3):
                        r = box_r * 3 + cell_r
                        c = box_c * 3 + cell_c

                        var = self.cell_vars[r][c]

                        entry = tk.Entry(
                            box,
                            textvariable=var,
                            width=2,
                            font=FONT_CELL,
                            justify="center",
                            bg=C["cell_normal"],
                            fg=C["num_given"],
                            relief="flat",
                            bd=0,
                            highlightthickness=1,
                            highlightbackground=C["border_cell"],
                            highlightcolor=C["btn_bt"],
                            insertwidth=1,
                        )
                        entry.grid(row=cell_r, column=cell_c,
                                   padx=1, pady=1,
                                   ipadx=10, ipady=8)

                        # Validate: only single digit 1-9 allowed
                        entry.bind("<KeyRelease>",
                                   lambda e, rv=r, cv=c: self._on_key(rv, cv))
                        # Visual focus ring
                        entry.bind("<FocusIn>",
                                   lambda e, en=entry: en.configure(
                                       highlightbackground=C["btn_bt"]))
                        entry.bind("<FocusOut>",
                                   lambda e, en=entry: en.configure(
                                       highlightbackground=C["border_cell"]))

                        self.cells[r][c] = entry

    def _build_stats_panel(self, parent):
        """Right-side statistics panel."""
        stats_outer = tk.Frame(parent, bg=C["bg_stats"],
                               bd=1, relief="solid")
        stats_outer.pack(side="left", fill="both", expand=True)

        # Header
        tk.Label(stats_outer,
                 text="⏱  Performance Statistics",
                 font=FONT_STAT_HDR,
                 bg=C["bg_stats"], fg=C["fg_stats_hdr"],
                 pady=8
                 ).pack(fill="x")

        tk.Frame(stats_outer, height=1, bg="#cbd5e1").pack(fill="x")

        # ---- Backtracking stats ----
        self._build_stat_section(stats_outer,
                                 "BACKTRACKING",
                                 C["btn_bt"],
                                 "bt")

        tk.Frame(stats_outer, height=1, bg="#cbd5e1").pack(fill="x", pady=4)

        # ---- Branch & Bound stats ----
        self._build_stat_section(stats_outer,
                                 "BRANCH & BOUND",
                                 C["btn_bb"],
                                 "bb")

        tk.Frame(stats_outer, height=1, bg="#cbd5e1").pack(fill="x", pady=4)

        # ---- Puzzle info ----
        info_frame = tk.Frame(stats_outer, bg=C["bg_stats"], padx=10)
        info_frame.pack(fill="x", pady=4)

        tk.Label(info_frame, text="PUZZLE INFO",
                 font=FONT_LABEL_B, bg=C["bg_stats"],
                 fg=C["fg_stats_hdr"]).pack(anchor="w")

        self.lbl_puzzle_name = tk.Label(info_frame, text="Name: —",
                                        font=FONT_STAT_VAL,
                                        bg=C["bg_stats"], fg=C["fg_stats_val"])
        self.lbl_puzzle_name.pack(anchor="w")

        self.lbl_givens = tk.Label(info_frame, text="Givens: —",
                                   font=FONT_STAT_VAL,
                                   bg=C["bg_stats"], fg=C["fg_stats_val"])
        self.lbl_givens.pack(anchor="w")

        self.lbl_empty = tk.Label(info_frame, text="Empty cells: —",
                                  font=FONT_STAT_VAL,
                                  bg=C["bg_stats"], fg=C["fg_stats_val"])
        self.lbl_empty.pack(anchor="w")

        # ---- Complexity note ----
        tk.Frame(stats_outer, height=1, bg="#cbd5e1").pack(fill="x", pady=4)
        note = tk.Label(stats_outer,
                        text="Complexity: O(9^m)\nm = empty cells",
                        font=("Helvetica", 9, "italic"),
                        bg=C["bg_stats"], fg="#64748b",
                        justify="center", pady=6)
        note.pack()

    def _build_stat_section(self, parent, title, color, prefix):
        """Create a labelled block of stat labels for one algorithm."""
        frame = tk.Frame(parent, bg=C["bg_stats"], padx=10)
        frame.pack(fill="x", pady=4)

        tk.Label(frame, text=title, font=FONT_LABEL_B,
                 bg=color, fg="white",
                 padx=6, pady=2, relief="flat"
                 ).pack(anchor="w", fill="x")

        # We'll store label references as instance attributes
        rows = [
            ("Time (s):",       f"{prefix}_lbl_time"),
            ("Nodes Explored:", f"{prefix}_lbl_nodes"),
            ("Backtracks:",     f"{prefix}_lbl_bt"),
        ]
        if prefix == "bb":
            rows.append(("Branches Pruned:", "bb_lbl_pruned"))

        for text, attr in rows:
            row_f = tk.Frame(frame, bg=C["bg_stats"])
            row_f.pack(fill="x", pady=1)
            tk.Label(row_f, text=text, font=FONT_STAT_VAL,
                     bg=C["bg_stats"], fg=C["fg_stats_val"],
                     width=16, anchor="w"
                     ).pack(side="left")
            lbl = tk.Label(row_f, text="—", font=FONT_LABEL_B,
                           bg=C["bg_stats"], fg=color)
            lbl.pack(side="left")
            setattr(self, attr, lbl)

    def _build_controls(self):
        """Bottom button panel and speed slider."""
        ctrl = tk.Frame(self.root, bg=C["bg_card"],
                        bd=1, relief="flat", pady=10, padx=16)
        ctrl.pack(fill="x")

        # ---- Row 1: Solve buttons ----
        row1 = tk.Frame(ctrl, bg=C["bg_card"])
        row1.pack(fill="x", pady=4)

        tk.Label(row1, text="Solve:", font=FONT_LABEL_B,
                 bg=C["bg_card"], fg=C["fg_label"], width=6).pack(side="left")

        self._btn(row1, "⚡ Backtracking",  C["btn_bt"],   self.solve_bt)
        self._btn(row1, "🌿 Branch & Bound", C["btn_bb"],  self.solve_bb)
        tk.Frame(row1, width=20, bg=C["bg_card"]).pack(side="left")
        self._btn(row1, "▶ Visualize BT",  C["btn_viz_bt"], self.visualize_bt)
        self._btn(row1, "▶ Visualize BB",  C["btn_viz_bb"], self.visualize_bb)
        tk.Frame(row1, width=20, bg=C["bg_card"]).pack(side="left")
        self.btn_stop = self._btn(row1, "⏹ Stop",
                                  C["btn_stop"],  self.stop_animation,
                                  state="disabled")

        # ---- Row 2: Load / Clear buttons ----
        row2 = tk.Frame(ctrl, bg=C["bg_card"])
        row2.pack(fill="x", pady=4)

        tk.Label(row2, text="Load:", font=FONT_LABEL_B,
                 bg=C["bg_card"], fg=C["fg_label"], width=6).pack(side="left")

        for diff, color in [("Easy",   C["btn_easy"]),
                             ("Medium", C["btn_medium"]),
                             ("Hard",   C["btn_hard"]),
                             ("Expert", C["btn_expert"]),
                             ("Broken", C["btn_broken"])]:
            self._btn(row2, diff, color,
                      lambda d=diff: self.load_puzzle_by_difficulty(d))

        tk.Frame(row2, width=20, bg=C["bg_card"]).pack(side="left")
        self._btn(row2, "🗑 Clear", C["btn_clear"], self.clear_grid)

        # ---- Row 3: Speed slider ----
        row3 = tk.Frame(ctrl, bg=C["bg_card"])
        row3.pack(fill="x", pady=4)

        tk.Label(row3, text="Viz Speed:", font=FONT_LABEL_B,
                 bg=C["bg_card"], fg=C["fg_label"], width=10).pack(side="left")

        self.speed_var = tk.IntVar(value=60)
        speed_scale = tk.Scale(row3,
                               from_=200, to=1,
                               orient="horizontal",
                               variable=self.speed_var,
                               bg=C["bg_card"],
                               fg=C["fg_label"],
                               highlightthickness=0,
                               length=220,
                               showvalue=False,
                               troughcolor="#dbeafe",
                               command=lambda v: setattr(self,
                                   "anim_delay", int(v)))
        speed_scale.pack(side="left")
        tk.Label(row3, text="◀ Slow  |  Fast ▶",
                 font=("Helvetica", 8), bg=C["bg_card"],
                 fg=C["fg_label"]).pack(side="left", padx=6)

    def _btn(self, parent, text, color, command, state="normal"):
        """Helper: create a styled button and return the widget."""
        b = tk.Button(parent,
                      text=text,
                      font=FONT_BTN,
                      bg=color,
                      fg=C["btn_fg"],
                      activebackground=color,
                      activeforeground="white",
                      relief="flat",
                      bd=0,
                      padx=12, pady=5,
                      cursor="hand2",
                      command=command,
                      state=state)
        b.pack(side="left", padx=4)

        # Simple hover effect
        def on_enter(e, btn=b, bg=color):
            if btn["state"] != "disabled":
                btn.configure(bg=self._darken(bg))

        def on_leave(e, btn=b, bg=color):
            if btn["state"] != "disabled":
                btn.configure(bg=bg)

        b.bind("<Enter>", on_enter)
        b.bind("<Leave>", on_leave)
        return b

    def _build_status(self):
        """Bottom status bar."""
        bar = tk.Frame(self.root, bg=C["bg_status"], pady=5)
        bar.pack(fill="x", side="bottom")

        self.status_var = tk.StringVar(value="✅  Ready  —  Load a puzzle and press Solve.")
        tk.Label(bar,
                 textvariable=self.status_var,
                 font=FONT_STATUS,
                 bg=C["bg_status"], fg=C["fg_status"],
                 padx=12
                 ).pack(side="left")

        # Animation progress label (right side)
        self.anim_progress_var = tk.StringVar(value="")
        tk.Label(bar,
                 textvariable=self.anim_progress_var,
                 font=FONT_STATUS,
                 bg=C["bg_status"], fg="#fbbf24",
                 padx=12
                 ).pack(side="right")

    # ==========================================================
    #  GRID INTERACTION
    # ==========================================================

    def _on_key(self, r: int, c: int):
        """
        Called on every key-release inside a cell.
        Validates that the entry contains a single digit 1-9 (or is empty).
        """
        val = self.cell_vars[r][c].get()

        # Allow only last character if user types fast
        if len(val) > 1:
            val = val[-1]
            self.cell_vars[r][c].set(val)

        # Accept only 1-9; clear anything else
        if val and (not val.isdigit() or val == "0"):
            self.cell_vars[r][c].set("")
        elif val.isdigit() and val != "0":
            self.cell_vars[r][c].set(val)

    def get_grid(self) -> list:
        """
        Read current Entry widget values and return a 9×9 int grid.
        Empty cells become 0.
        """
        grid = []
        for r in range(9):
            row = []
            for c in range(9):
                val = self.cell_vars[r][c].get().strip()
                row.append(int(val) if val.isdigit() and val != "0" else 0)
            grid.append(row)
        return grid

    def set_grid(self, grid: list, puzzle_name: str = ""):
        """
        Write a 9×9 int grid into the Entry widgets.
        Marks cells with pre-given values in blue.
        """
        for r in range(9):
            for c in range(9):
                val = grid[r][c]
                self.original[r][c] = val
                self.is_given[r][c] = (val != 0)

                if val != 0:
                    self.cell_vars[r][c].set(str(val))
                    self.cells[r][c].configure(
                        bg=C["cell_given"],
                        fg=C["num_given"],
                        font=FONT_CELL_GV,
                        state="normal",
                        disabledbackground=C["cell_given"],
                        disabledforeground=C["num_given"],
                    )
                    self.cells[r][c].configure(state="disabled")
                else:
                    self.cell_vars[r][c].set("")
                    self.cells[r][c].configure(
                        bg=C["cell_normal"],
                        fg=C["num_bt"],
                        font=FONT_CELL,
                        state="normal")

        # Update puzzle info labels
        givens = count_givens(grid)
        empty  = count_empty(grid)
        self.lbl_puzzle_name.configure(text=f"Name: {puzzle_name or '—'}")
        self.lbl_givens.configure(text=f"Givens:  {givens}")
        self.lbl_empty.configure(text=f"Empty:   {empty}")

    def _set_cell_color(self, r: int, c: int,
                        bg: str, fg: str, val=None):
        """
        Update the visual appearance of a single cell.
        Enables the cell temporarily, updates it, re-disables if given.
        """
        cell = self.cells[r][c]
        cell.configure(state="normal")
        cell.configure(bg=bg, fg=fg)
        if val is not None:
            if val == 0:
                self.cell_vars[r][c].set("")
            else:
                self.cell_vars[r][c].set(str(val))
        if self.is_given[r][c]:
            cell.configure(state="disabled",
                           disabledbackground=bg,
                           disabledforeground=fg)

    # ==========================================================
    #  LOAD / CLEAR
    # ==========================================================

    def load_puzzle_by_difficulty(self, difficulty: str):
        """Load a random puzzle of the specified difficulty."""
        if self.animating:
            self.stop_animation()
        name, grid = get_random_puzzle(difficulty)
        self.set_grid(grid, name)
        self._reset_stats_display()
        self.set_status(f"✅  Loaded '{name}'  ({difficulty})  —  Press Solve or Visualize.")

    def clear_grid(self):
        """Clear all cells and reset to a blank grid."""
        if self.animating:
            self.stop_animation()
        blank = [[0] * 9 for _ in range(9)]
        self.set_grid(blank, "Blank")
        self._reset_stats_display()
        self.set_status("🗑  Grid cleared.  Enter your own puzzle or load a sample.")

    # ==========================================================
    #  SOLVE (instant, no animation)
    # ==========================================================

    def solve_bt(self):
        """Solve the current puzzle with Backtracking (instant)."""
        if self.animating:
            messagebox.showwarning("Animation Running",
                                   "Please stop the animation first.")
            return

        grid = self.get_grid()
        if not self._has_puzzle(grid):
            return

        self.set_status("⚡  Solving with Backtracking...")
        self.root.update()

        solved, success = self.bt_solver.solve_puzzle(grid, record_steps=False)

        if success:
            self._display_solution(solved, mode="BT")
            self._update_stats_display("BT")
            self.set_status(
                f"✅  Backtracking solved!  "
                f"Time: {self.bt_solver.solving_time:.4f}s  |  "
                f"Nodes: {self.bt_solver.nodes_explored}  |  "
                f"Backtracks: {self.bt_solver.backtracks}"
            )
        else:
            self.set_status("❌  No solution found by Backtracking.")
            messagebox.showerror("No Solution",
                                 "This puzzle has no valid solution.")

    def solve_bb(self):
        """Solve the current puzzle with Branch & Bound (instant)."""
        if self.animating:
            messagebox.showwarning("Animation Running",
                                   "Please stop the animation first.")
            return

        grid = self.get_grid()
        if not self._has_puzzle(grid):
            return

        self.set_status("🌿  Solving with Branch & Bound...")
        self.root.update()

        solved, success = self.bb_solver.solve_puzzle(grid, record_steps=False)

        if success:
            self._display_solution(solved, mode="BB")
            self._update_stats_display("BB")
            self.set_status(
                f"✅  Branch & Bound solved!  "
                f"Time: {self.bb_solver.solving_time:.4f}s  |  "
                f"Nodes: {self.bb_solver.nodes_explored}  |  "
                f"Pruned: {self.bb_solver.pruned_branches}"
            )
        else:
            self.set_status("❌  No solution found by Branch & Bound.")
            messagebox.showerror("No Solution",
                                 "This puzzle has no valid solution.")

    def _display_solution(self, solved: list, mode: str):
        """Fill solved (non-given) cells with appropriate colour."""
        bg  = C["cell_bt_done"] if mode == "BT" else C["cell_bb_done"]
        fg  = C["num_bt"]       if mode == "BT" else C["num_bb"]

        for r in range(9):
            for c in range(9):
                if not self.is_given[r][c]:
                    self._set_cell_color(r, c, bg, fg, solved[r][c])

    # ==========================================================
    #  VISUALIZE (step-by-step animation)
    # ==========================================================

    def visualize_bt(self):
        """Collect BT steps then animate them."""
        self._start_visualization("BT")

    def visualize_bb(self):
        """Collect BB steps then animate them."""
        self._start_visualization("BB")

    def _start_visualization(self, mode: str):
        """
        1. Read current grid.
        2. Run solver in step-recording mode (fast, no GUI update).
        3. If solvable, reset grid to original and start animation.
        """
        if self.animating:
            self.stop_animation()
            return

        grid = self.get_grid()
        if not self._has_puzzle(grid):
            return

        self.set_status(f"{'⚡' if mode == 'BT' else '🌿'}  "
                        f"Collecting {'BT' if mode == 'BT' else 'BB'} steps...")
        self.root.update()

        # Run solver with step recording
        if mode == "BT":
            solver   = self.bt_solver
        else:
            solver   = self.bb_solver

        solved, success = solver.solve_puzzle(grid, record_steps=True)

        if not success:
            self.set_status("❌  Puzzle has no solution.")
            messagebox.showerror("No Solution",
                                 "This puzzle has no valid solution.")
            return

        # --- Update stats immediately ---
        self._update_stats_display(mode)

        # --- Reset grid to original, then animate ---
        self.set_grid(copy.deepcopy(self.original))  # restore originals
        # Re-update puzzle info (set_grid wipes the name label; fine here)

        self.anim_steps  = solver.steps[:]
        self.anim_index  = 0
        self.anim_mode   = mode
        self.animating   = True
        self.anim_delay  = self.speed_var.get()

        # Enable / disable stop button
        self.btn_stop.configure(state="normal")

        total = len(self.anim_steps)
        self.set_status(f"▶  Animating {mode} — {total} steps.  "
                        f"Use Stop to halt.")
        self._animate_next()

    def _animate_next(self):
        """
        Called repeatedly via root.after() to advance the animation
        by one step.  Stops automatically when all steps are consumed.
        """
        if not self.animating:
            return

        if self.anim_index >= len(self.anim_steps):
            # Animation complete
            self._finish_animation()
            return

        r, c, val, step_type = self.anim_steps[self.anim_index]
        self.anim_index += 1

        # Choose colours based on step type and algorithm
        if step_type == 'place':
            bg = C["cell_place"]
            fg = C["num_place"]
        else:   # 'backtrack'
            bg = C["cell_back"]
            fg = C["num_back"]

        # Update the cell
        if not self.is_given[r][c]:
            self._set_cell_color(r, c, bg, fg, val)

        # Update progress
        total = len(self.anim_steps)
        self.anim_progress_var.set(
            f"Step {self.anim_index}/{total}  "
            f"({'Placing' if step_type == 'place' else 'Backtracking'})"
        )

        # Schedule next step
        delay = max(1, self.speed_var.get())
        self.anim_job = self.root.after(delay, self._animate_next)

    def _finish_animation(self):
        """Called when animation reaches the last step."""
        self.animating = False
        self.anim_job  = None
        self.btn_stop.configure(state="disabled")
        self.anim_progress_var.set("")

        # Colour all solved cells in the final "done" colour
        mode = self.anim_mode
        bg   = C["cell_bt_done"] if mode == "BT" else C["cell_bb_done"]
        fg   = C["num_bt"]       if mode == "BT" else C["num_bb"]

        for r in range(9):
            for c in range(9):
                val = self.cell_vars[r][c].get()
                if val and not self.is_given[r][c]:
                    self._set_cell_color(r, c, bg, fg, int(val))

        solver = self.bt_solver if mode == "BT" else self.bb_solver
        self.set_status(
            f"✅  {mode} animation complete!  "
            f"Time: {solver.solving_time:.4f}s  |  "
            f"Steps shown: {len(self.anim_steps)}"
        )

    def stop_animation(self):
        """Halt an in-progress animation."""
        if self.anim_job:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None
        self.animating = False
        self.btn_stop.configure(state="disabled")
        self.anim_progress_var.set("")
        self.set_status("⏹  Animation stopped.")

    # ==========================================================
    #  STATISTICS DISPLAY
    # ==========================================================

    def _update_stats_display(self, mode: str):
        """Push latest solver stats into the stats-panel labels."""
        if mode in ("BT", "both"):
            s = self.bt_solver
            self.bt_lbl_time.configure(
                text=f"{s.solving_time:.6f} s")
            self.bt_lbl_nodes.configure(text=str(s.nodes_explored))
            self.bt_lbl_bt.configure(text=str(s.backtracks))

        if mode in ("BB", "both"):
            s = self.bb_solver
            self.bb_lbl_time.configure(
                text=f"{s.solving_time:.6f} s")
            self.bb_lbl_nodes.configure(text=str(s.nodes_explored))
            self.bb_lbl_bt.configure(text=str(s.backtracks))
            self.bb_lbl_pruned.configure(text=str(s.pruned_branches))

    def _reset_stats_display(self):
        """Reset all stat labels to '—'."""
        for attr in ("bt_lbl_time", "bt_lbl_nodes", "bt_lbl_bt",
                     "bb_lbl_time", "bb_lbl_nodes", "bb_lbl_bt",
                     "bb_lbl_pruned"):
            lbl = getattr(self, attr, None)
            if lbl:
                lbl.configure(text="—")



    def set_status(self, msg: str):
        """Update the bottom status bar text."""
        self.status_var.set(msg)
        self.root.update_idletasks()

    def _has_puzzle(self, grid: list) -> bool:
        """Return False (with a warning) if the grid is completely empty."""
        if all(grid[r][c] == 0 for r in range(9) for c in range(9)):
            messagebox.showwarning("Empty Grid",
                                   "Please load a puzzle first.")
            return False
        return True

    @staticmethod
    def _darken(hex_color: str, amount: int = 30) -> str:
        """
        Return a slightly darker version of a hex colour string.
        Used for button hover effects.
        """
        try:
            hex_color = hex_color.lstrip("#")
            r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r = max(0, r - amount)
            g = max(0, g - amount)
            b = max(0, b - amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color
