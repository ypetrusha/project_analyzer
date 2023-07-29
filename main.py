import tkinter as tk

import openai

from project_analyzer import ProjectAnalyzer
from ui import ProjectAnalyzerUI
import dotenv
import os


def main():
    dotenv.load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    if api_base:
        openai.api_base = api_base
    root = tk.Tk()
    analyzer = ProjectAnalyzer()
    ui = ProjectAnalyzerUI(root, analyzer)
    root.mainloop()


if __name__ == "__main__":
    main()