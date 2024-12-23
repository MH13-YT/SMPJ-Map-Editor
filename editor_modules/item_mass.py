import json
import os
import random
import tkinter as tk
from tkinter import ttk


class ItemMassEditor:
    def __init__(
        self, parent, data_store, map_name, app_width, general_items, map_items
    ):
        self.data_store = data_store
        self.map_name = map_name.replace(" ", "_")
        self.combined_items = map_items[self.map_name]["items"] + general_items
        self.lots = {}

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = 7
        rows = 1

        for col in range(columns):
            self.frame.grid_columnconfigure(col, weight=1, uniform="group")
        for row in range(rows):
            self.frame.grid_rowconfigure(row, weight=1, uniform="group")

        num_columns = 7
        for index, lot_no in enumerate([0, 1, 2, 3, 5, 7, 8]):
            self.create_lot_column(lot_no, app_width, index, num_columns)

    def create_lot_column(self, lot_no, app_width, index, num_columns):
        column_width = app_width // num_columns

        row = index // num_columns
        column = index % num_columns

        lot_frame = ttk.LabelFrame(self.frame, text=f"{lot_no}", width=column_width)
        lot_frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")

        entry = ttk.Combobox(lot_frame, values=self.combined_items, width=column_width)
        entry.pack(pady=5)

        add_button = ttk.Button(
            lot_frame,
            text="Add Item",
            command=lambda: self.add_item(lot_no, entry),
            width=column_width,
        )
        add_button.pack(pady=5)

        scroll_frame = tk.Frame(lot_frame)
        scroll_frame.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(scroll_frame)
        listbox = tk.Listbox(
            scroll_frame, yscrollcommand=scrollbar.set, height=10, width=column_width
        )
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)

        remove_button = ttk.Button(
            lot_frame,
            text="Remove Item",
            command=lambda: self.remove_item(lot_no),
            width=column_width,
        )
        remove_button.pack(pady=5)

        self.lots[lot_no] = {"entry": entry, "listbox": listbox}

    def add_item(self, lot_no, entry):
        item = entry.get()
        if item:
            listbox = self.lots[lot_no]["listbox"]
            listbox.insert(tk.END, item)

    def remove_item(self, lot_no):
        listbox = self.lots[lot_no]["listbox"]
        selected_item = listbox.curselection()
        if selected_item:
            listbox.delete(selected_item)

    def load_items(self, data):
        items = data.get(self.map_name, [])

        for item in items:
            item_name = item.get("Item", "")
            lot_number = item.get("No", None)

            if item_name and lot_number is not None:
                lot_data = self.lots.get(lot_number)

                if lot_data:
                    listbox = lot_data.get("listbox")
                    if listbox:
                        display_text = f"{item_name}"
                        listbox.insert(tk.END, display_text)
                    else:
                        print(f"Listbox for Lot {lot_number} is not available.")
                else:
                    print(f"Lot number {lot_number} does not exist in self.lots.")
                    
    def randomize_items(self, probability=0.2):
        for lot_no, widgets in self.lots.items():
            listbox = widgets.get("listbox")
            if listbox:
                listbox.delete(0, tk.END)
                for item in self.combined_items:
                    if random.random() < probability:
                        listbox.insert(tk.END, item)
            else:
                print(f"Listbox for Lot {lot_no} is not available")
            

    def save_items(self):
        items = []

        for lot_no, widgets in self.lots.items():
            listbox = widgets.get("listbox")

            if listbox:
                for i in range(listbox.size()):
                    item_text = listbox.get(i)
                    item_data = item_text.split(" - ")
                    item_name = item_data[0]
                    items.append({"Item": item_name, "No": lot_no})

            else:
                print(f"Listbox for Lot {lot_no} is not available.")

        self.data_store[self.map_name] = items
        return items


def process_itemmass_data(item_data):
    results = []
    for entry in item_data:
        if all(key in entry for key in ["Item", "No"]):
            results.append(entry)
        else:
            continue
    return results


def load_itemmass_mapdata(base_path, map_name):
    item_mass_data = {}
    item_mass_raw_data = []
    file_name = os.path.join(
        "bd~bd00.nx", "bd", "bd00", "data", f"bd00_ItemMass_{map_name}.json"
    )
    file_path = os.path.join(base_path, file_name)
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            item_mass_raw_data = data.get(map_name)
    except FileNotFoundError:
        print(f"File not found : {file_name}")
    except json.JSONDecodeError:
        print(f"Error occurred while reading file : {file_name}")

    item_mass_data[map_name] = process_itemmass_data(item_mass_raw_data)
    return item_mass_data


def save_itemmass_mapdata(base_path, item_mass_data, map_name):
    file_name = os.path.join(
        "bd~bd00.nx", "bd", "bd00", "data", f"bd00_ItemMass_{map_name}.json"
    )
    file_path = os.path.join(base_path, file_name)
    with open(file_path, "w", encoding="utf-8-sig") as f:
        file_data = {}
        file_data[f"{map_name}"] = []
        file_data[f"{map_name}"] = item_mass_data
        json.dump(file_data, f, indent=4)
