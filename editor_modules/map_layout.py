import tkinter as tk
from tkinter import ttk


# Planified Development
class MapLayoutEditor(tk.Frame):
    def __init__(self, parent, map_name):
        super().__init__(parent)
        self.map_name = map_name

        label = ttk.Label(self, text="MapLayoutEditor - En développement")
        label.pack(pady=20)
