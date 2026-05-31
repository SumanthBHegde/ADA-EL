#!/usr/bin/env python3


import tkinter as tk
import sys
import os

# Make sure imports work when run from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import SudokuApp


def main():
    
    root = tk.Tk()

    # Allow the window to grow if the display requires it
    root.resizable(True, True)
    root.minsize(980, 720)

    # Centre the window on screen
    root.update_idletasks()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - 1000) // 2
    y = (screen_h - 740) // 2
    root.geometry(f"1000x740+{x}+{y}")

    app = SudokuApp(root) 

    root.mainloop()


if __name__ == "__main__":
    main()
