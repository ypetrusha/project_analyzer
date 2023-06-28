import tkinter as tk
from project_analyzer import ProjectAnalyzer
from ui import ProjectAnalyzerUI


def main():
    root = tk.Tk()
    analyzer = ProjectAnalyzer()
    ui = ProjectAnalyzerUI(root, analyzer)
    root.mainloop()


if __name__ == "__main__":
    main()