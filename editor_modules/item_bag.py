import json
import os
import tkinter as tk
from tkinter import ttk


class ItemBagEditor:
    def __init__(
        self, parent, data_store, map_name, app_width, general_items, map_items
    ):
        self.data_store = data_store
        self.map_name = map_name.replace(" ", "_")

        map_specific_items = map_items[self.map_name]["items"]
        combined_items = map_specific_items + general_items

        self.frame = ttk.Frame(parent)
        self.frame.pack(
            side="left",
            padx=(app_width * 0.05, app_width * 0.05 // 2),
            pady=10,
            fill="both",
            expand=True,
        )

        self.add_form_frame = tk.Frame(self.frame)
        self.add_form_frame.pack(pady=5)

        self.add_button_frame = tk.Frame(self.frame)
        self.add_button_frame.pack(pady=5)

        self.phase_names = ["Standard", "Standard (5 Last Turns)"]
        self.phase_map = {name: idx for idx, name in enumerate(self.phase_names)}

        self.phase_label = ttk.Label(self.add_form_frame, text="Phase:")
        self.phase_label.grid(row=0, column=1, padx=5, pady=5)
        self.phase_combobox = ttk.Combobox(
            self.add_form_frame, values=self.phase_names, width=25
        )
        self.phase_combobox.grid(row=0, column=2, padx=5, pady=5)

        self.unique_var = tk.IntVar()
        self.unique_checkbutton = tk.Checkbutton(
            self.add_form_frame, text="Unique", variable=self.unique_var
        )
        self.unique_checkbutton.grid(row=0, column=3, padx=5, pady=5)

        self.entry = ttk.Combobox(self.add_form_frame, values=combined_items, width=20)
        self.entry.grid(row=0, column=0, padx=5, pady=5)
        self.add_button = ttk.Button(
            self.add_button_frame, text="Add Item", command=self.add_item, width=160
        )
        self.add_button.grid(row=0, column=4, padx=5, pady=5)

        self.phase_frames = {}
        for phase in range(2):
            phase_frame = ttk.LabelFrame(
                self.frame, text=f"{self.phase_names[phase]}", padding=(10, 5)
            )
            phase_frame.pack(fill="both", expand=True, padx=5, pady=5)
            self.phase_frames[phase] = phase_frame

            scroll_frame = tk.Frame(phase_frame)
            scroll_frame.pack(fill="both", expand=True)

            scrollbar = tk.Scrollbar(scroll_frame)
            listbox = tk.Listbox(scroll_frame, yscrollcommand=scrollbar.set, height=5)
            scrollbar.config(command=listbox.yview)
            scrollbar.pack(side="right", fill="y")
            listbox.pack(side="left", fill="both", expand=True)
            self.phase_frames[phase].listbox = listbox

        self.remove_button_frame = tk.Frame(self.frame)
        self.remove_button_frame.pack(pady=5)

        self.remove_button = ttk.Button(
            self.remove_button_frame,
            text="Remove Item",
            command=self.remove_item,
            width=160,
        )
        self.remove_button.pack(pady=5)

    def add_item(self):
        item = self.entry.get()
        if item:
            phase_name = self.phase_combobox.get()
            phase_idx = self.phase_map.get(phase_name)

            unique = "Unique" if self.unique_var.get() else "Not Unique"
            display_text = f"{item} - {unique}"
            self.phase_frames[phase_idx].listbox.insert(tk.END, display_text)

    def remove_item(self):
        for phase in range(3):
            selected_item = self.phase_frames[phase].listbox.curselection()
            if selected_item:
                self.phase_frames[phase].listbox.delete(selected_item)
                break

    def load_items(self, data):
        self.data_store = data
        items = self.data_store.get(self.map_name)
        for item in items:
            phase = item.get("Phase")
            unique = "Unique" if item.get("Unique") else "Not Unique"
            display_text = f"{item['Item']} - {unique}"
            self.phase_frames[phase].listbox.insert(tk.END, display_text)

    def save_items(self):
        items = []
        for phase in range(2):
            for i in range(self.phase_frames[phase].listbox.size()):
                item_text = self.phase_frames[phase].listbox.get(i)
                item_data = item_text.split(" - ")
                item_name = item_data[0]
                unique = not "Not Unique" in item_data[1]
                items.append({"Item": item_name, "Phase": phase, "Unique": int(unique)})
        self.data_store[self.map_name] = items
        return items


def process_itembag_data(item_data, data_key):
    results = []
    for entry in item_data:
        if all(key in entry for key in ["Item", "Phase", "Unique"]):
            results.append(entry)
        else:
            continue
    return results


def load_itembag_mapdata(base_path, map_name):
    item_bag_data = {}
    item_bag_raw_data = []
    file_name = os.path.join(
        "bd~bd00.nx", "bd", "bd00", "data", f"bd00_ItemBag_{map_name}.json"
    )
    file_path = os.path.join(base_path, file_name)
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            item_bag_raw_data = data.get(map_name)
    except FileNotFoundError:
        print(f"File not found : {file_name}")
    except json.JSONDecodeError:
        print(f"Error occurred while reading file : {file_name}")

    item_bag_data[map_name] = process_itembag_data(item_bag_raw_data, "ItemBag")
    return item_bag_data


def save_itembag_mapdata(base_path, item_bag_data, map_name):
    file_name = os.path.join(
        "bd~bd00.nx", "bd", "bd00", "data", f"bd00_ItemBag_{map_name}.json"
    )
    file_path = os.path.join(base_path, file_name)
    with open(file_path, "w", encoding="utf-8-sig") as f:
        file_data = {}
        file_data[f"{map_name}"] = []
        file_data[f"{map_name}"] = item_bag_data
        json.dump(file_data, f, indent=4)
