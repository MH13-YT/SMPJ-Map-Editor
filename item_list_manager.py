import json
import os
import tkinter as tk
from tkinter import ttk

class ItemListManager:
    def __init__(self, parent, title, data_key, data_store, map_name, app_width, general_items, map_items, include_phase_unique=False, include_lot=False):
        self.data_store = data_store
        self.map_name = map_name.replace(" ", "_")
        self.data_key = data_key
        
        map_specific_items = map_items[self.map_name]["items"]
        combined_items = map_specific_items + general_items
        
        if include_lot:
            combined_items = ["Max"] + combined_items # Max = Object Mini Games

        self.frame = ttk.LabelFrame(parent, text=title)
        self.frame.pack(side="left", padx=(app_width * 0.05, app_width * 0.05 // 2), pady=10, fill="both", expand=True)

        # Frame for the Add button and entry (on the same line)
        self.add_button_frame = tk.Frame(self.frame)
        self.add_button_frame.pack(pady=5)

        # Add combobox for phases and checkbox for unique (for ItemBag)
        if include_phase_unique:
            self.phase_label = ttk.Label(self.add_button_frame, text="Phase:")
            self.phase_label.grid(row=0, column=1, padx=5, pady=5)
            self.phase_combobox = ttk.Combobox(self.add_button_frame, values=[0, 1], width=10)
            self.phase_combobox.grid(row=0, column=2, padx=5, pady=5)

            self.unique_var = tk.IntVar()
            self.unique_checkbutton = tk.Checkbutton(self.add_button_frame, text="Unique", variable=self.unique_var)
            self.unique_checkbutton.grid(row=0, column=3, padx=5, pady=5)

        # Add spinbox for lot number (for ItemMass)
        if include_lot:
            self.lot_label = ttk.Label(self.add_button_frame, text="Lot No:")
            self.lot_label.grid(row=0, column=1, padx=5, pady=5)
            self.lot_spinbox = tk.Spinbox(self.add_button_frame, from_=0, to=8, width=5)
            self.lot_spinbox.grid(row=0, column=2, padx=5, pady=5)

        # Add button and entry for item list (item at the left-most)
        self.entry = ttk.Combobox(self.add_button_frame, values=combined_items, width=20)
        self.entry.grid(row=0, column=0, padx=5, pady=5)
        self.add_button = ttk.Button(self.add_button_frame, text="Add Item", command=self.add_item)
        self.add_button.grid(row=0, column=4, padx=5, pady=5)

        # Scrollable frame for the Listbox
        self.scroll_frame = tk.Frame(self.frame)
        self.scroll_frame.pack(fill="both", expand=True)

        # Scrollable Listbox (smaller size to gain space)
        self.scrollbar = tk.Scrollbar(self.scroll_frame)
        self.listbox = tk.Listbox(self.scroll_frame, yscrollcommand=self.scrollbar.set, height=5)
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.pack(side="left", fill="both", expand=True)

        # Frame for the Remove button (below the scroll area)
        self.remove_button_frame = tk.Frame(self.frame)
        self.remove_button_frame.pack(pady=5)

        # Remove button (below the scroll area)
        self.remove_button = ttk.Button(self.remove_button_frame, text="Remove Item", command=self.remove_item)
        self.remove_button.pack(pady=5)

    def add_item(self):
        item = self.entry.get()
        if item:
            if hasattr(self, 'phase_combobox'):  # ItemBag
                phase = self.phase_combobox.get()
                unique = "Unique" if self.unique_var.get() else "Not Unique"
                display_text = f"{item} - Phase: {phase}, {unique}"
            elif hasattr(self, 'lot_spinbox'):  # ItemMass
                lot_number = self.lot_spinbox.get()
                display_text = f"{item} - Lot No: {lot_number}"
            self.listbox.insert(tk.END, display_text)

    def remove_item(self):
        selected_item = self.listbox.curselection()
        if selected_item:
            self.listbox.delete(selected_item)

    def load_items(self,data):
        self.data_store = data
        items = self.data_store.get(self.map_name)
        for item in items:
            if self.data_key == "ItemBag":
                phase = item.get("Phase")
                unique = "Unique" if item.get("Unique") else "Not Unique"
                display_text = f"{item['Item']} - Phase: {phase}, {unique}"
            elif self.data_key == "ItemMass":
                lot_number = item.get("No")
                display_text = f"{item['Item']} - Lot No: {lot_number}"
            self.listbox.insert(tk.END, display_text)

    def save_items(self):
        items = []
        for i in range(self.listbox.size()):
            item_text = self.listbox.get(i)
            item_data = item_text.split(" - ")
            item_name = item_data[0]

            if self.data_key == "ItemBag":
                phase = int(item_data[1].split(": ")[1].split(",")[0])  # Extract phase number
                unique = "Unique" in item_data[1]  # Check if "Unique" is present
                items.append({
                    "Item": item_name,
                    "Phase": phase,
                    "Unique": int(unique)
                })
            elif self.data_key == "ItemMass":
                lot_number = int(item_data[1].split(": ")[1])  # Extract lot number
                items.append({
                    "Item": item_name,
                    "No": lot_number
                })
        self.data_store[self.map_name] = items
        return items

def load_item_data(map_number, data_type, base_path):
    """
    Charge les données JSON pour ItemBag ou ItemMass.
    """
    file_name = f"bd00_{data_type}_{map_number}.json"
    file_path = os.path.join(base_path, file_name)
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get(map_number)
    except FileNotFoundError:
        print(f"File not found : {file_name}")
        return []
    except json.JSONDecodeError:
        print(f"Error occurred while reading file : {file_name}")
        return []

def process_item_data(item_data, data_key):
    """
    Traite les données de ItemBag ou ItemMass.
    """
    results = []
    for entry in item_data:
        if data_key == "ItemBag" and all(key in entry for key in ["Item", "Phase", "Unique"]):
            results.append(entry)
        elif data_key == "ItemMass" and all(key in entry for key in ["Item", "No"]):
            results.append(entry)
        else:
            continue
    return results

def load_item_mapdata(base_path,map_name):
    """
    Charge les fichiers JSON pour ItemBag et ItemMass pour la carte associé.
    """
    item_bag_data = {}
    item_mass_data = {}
        
    # Charger les données pour ItemBag
    item_bag_raw_data = load_item_data(map_name, "ItemBag", base_path)
    item_bag_data[map_name] = process_item_data(item_bag_raw_data, "ItemBag")
        
    # Charger les données pour ItemMass
    item_mass_raw_data = load_item_data(map_name, "ItemMass", base_path)
    item_mass_data[map_name] = process_item_data(item_mass_raw_data, "ItemMass")

    return item_bag_data, item_mass_data

def save_item_mapdata(base_path,item_bag_data,item_mass_data,map_name):
    file_name = f"bd00_ItemBag_{map_name}.json"
    file_path = os.path.join(base_path, file_name)
    with open(file_path, 'w') as f:
        file_data = {}
        file_data[f"{map_name}"] = []
        file_data[f"{map_name}"] = item_bag_data
        json.dump(file_data, f, indent=4)
    
    # Sauvegarde des données ItemMass
    file_name = f"bd00_ItemMass_{map_name}.json"
    file_path = os.path.join(base_path, file_name)
    with open(file_path, 'w') as f:
        file_data = {}
        file_data[f"{map_name}"] = []
        file_data[f"{map_name}"] = item_mass_data
        json.dump(file_data, f, indent=4)