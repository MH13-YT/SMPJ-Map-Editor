import tkinter as tk
from tkinter import ttk

#Fonctionnalité en développement planifié

class MapLayoutEditor(tk.Frame):
    def __init__(self, parent, map_name):
        super().__init__(parent)
        self.map_name = map_name
        
        # Exemple de message pour indiquer que cette classe est en développement
        label = ttk.Label(self, text=f"MapLayoutEditor - En développement")
        label.pack(pady=20)