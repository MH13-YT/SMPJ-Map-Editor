import tkinter as tk
from tkinter import ttk

#Fonctionnalité en développement planifié

class EventEditor(tk.Frame):
    def __init__(self, parent, event_type, map_name):
        super().__init__(parent)
        self.event_type = event_type
        self.map_name = map_name
        
        # Exemple de message pour indiquer que cette classe est en développement
        label = ttk.Label(self, text=f"EventEditor - En développement")
        label.pack(pady=20)