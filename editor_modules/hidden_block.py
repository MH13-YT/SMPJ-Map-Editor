import os
import json
import random
import tkinter as tk
from tkinter import ttk


LOTS = [
    {"data": -1, "name": "\u20071 Star"},
    {"data": 5, "name": "\u20075 Coins"},
    {"data": 6, "name": "\u20076 Coins"},
    {"data": 7, "name": "\u20077 Coins"},
    {"data": 8, "name": "\u20078 Coins"},
    {"data": 9, "name": "\u20079 Coins"},
    {"data": 10, "name": "10 Coins"},
    {"data": 12, "name": "12 Coins"},
    {"data": 13, "name": "13 Coins"},
    {"data": 15, "name": "15 Coins"},
    {"data": 20, "name": "20 Coins"},
    {"data": 30, "name": "30 Coins"},
]


def get_lot_name_by_data(data):
    for lot in LOTS:
        if lot["data"] == data:
            return lot["name"]
    return f"Unknown ({data})"


def get_lot_data_by_name(name):
    for lot in LOTS:
        if lot["name"] == name:
            return lot["data"]
    return None


class HiddenBlockDataManager:
    def __init__(self):
        self.hiddenblock_data = {}
        self.listeners = []

    def register_listener(self, listener):
        self.listeners.append(listener)

    def get_hiddenblock_data(self, map_name):
        return self.hiddenblock_data.get(map_name, [])

    def update_hiddenblock_data(self, map_name, hiddenblock_data):
        if map_name not in self.hiddenblock_data:
            self.hiddenblock_data[map_name] = {}
        self.hiddenblock_data[map_name] = hiddenblock_data
        self.notify_listeners()

    def sync_with_linked_maps(self, map_name):
        linked_maps = self.get_linked_maps(map_name)
        current_data = self.get_hiddenblock_data(map_name)

        for linked_map in linked_maps:
            self.hiddenblock_data[linked_map] = current_data
        self.notify_listeners()

    def get_linked_maps(self, map_name):
        linked_maps = []
        if map_name.startswith("Map"):
            map_number = int(map_name[3:])
            linked_maps = [f"Map{n:02d}" for n in range(1, 8) if n != map_number]
        return linked_maps

    def notify_listeners(self):
        for listener in self.listeners:
            listener.refresh_data()


class HiddenBlockEditor:
    def __init__(self, parent, map_name, app_width, data_manager):
        self.data_manager = data_manager
        self.map_name = map_name.replace(" ", "_")
        self.lots = {}

        self.parent = parent
        self.app_width = app_width

        self.frame = ttk.Frame(parent)
        self.frame.pack(
            side="left",
            padx=(app_width * 0.05, app_width * 0.05 // 2),
            pady=10,
            fill="both",
            expand=True,
        )

        self.create_ui()
        self.data_manager.register_listener(self)

    def create_ui(self):
        columns = 6
        rows = 1

        for col in range(columns):
            self.frame.grid_columnconfigure(col, weight=1, uniform="group")
        for row in range(rows):
            self.frame.grid_rowconfigure(row, weight=1, uniform="group")

        num_columns = 6
        for index, lot_no in enumerate(range(num_columns)):
            self.create_lot_column(lot_no, self.app_width, index, num_columns)

    def create_lot_column(self, lot_no, app_width, index, num_columns):
        column_width = app_width // num_columns
        row = index // num_columns
        column = index % num_columns

        lot_frame = ttk.LabelFrame(self.frame, text=f"Lot {lot_no}", width=column_width)
        lot_frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")

        entry = ttk.Combobox(
            lot_frame, values=[lot["name"] for lot in LOTS], width=column_width
        )
        entry.pack(pady=5)

        rate_entry = ttk.Spinbox(lot_frame, from_=1, to=999, width=column_width)
        rate_entry.pack(pady=5)

        add_button = ttk.Button(
            lot_frame,
            text="Add Block",
            command=lambda: self.add_block(lot_no, entry, rate_entry),
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
            text="Remove Block",
            command=lambda: self.remove_block(lot_no),
            width=column_width,
        )
        remove_button.pack(pady=5)

        self.lots[lot_no] = {
            "entry": entry,
            "rate_entry": rate_entry,
            "listbox": listbox,
        }

    def add_block(self, lot_no, entry, rate_entry):
        block_name = entry.get()
        block_data = get_lot_data_by_name(block_name)
        rate = rate_entry.get()

        if block_data is not None and rate.isdigit() and 0 <= int(rate) <= 999:
            listbox = self.lots[lot_no]["listbox"]
            listbox.insert(tk.END, f"{block_name} (ID: {block_data}, Rate: {rate})")

            current_data = self.data_manager.get_hiddenblock_data(self.map_name)

            if not isinstance(current_data, list):
                current_data = []

            new_entry = {
                "No": lot_no,
                "Result": block_data,
                "Rate": int(rate),
            }
            current_data.append(new_entry)

            self.data_manager.update_hiddenblock_data(
                self.map_name, current_data
            )
            self.data_manager.sync_with_linked_maps(self.map_name)
            
    def randomize_hiddenblock_data(self):
        num_columns = 6
        hidden_block_data = []
        for lot_no in range(num_columns):
            for lot in LOTS:
                new_entry = {
                    "No": lot_no,
                    "Result": lot["data"],
                    "Rate": random.randint(0, 255),
                }
                hidden_block_data.append(new_entry)

        self.data_manager.update_hiddenblock_data(
            self.map_name, hidden_block_data
        )
        self.data_manager.sync_with_linked_maps(self.map_name)

    def remove_block(self, lot_no):
        listbox = self.lots[lot_no]["listbox"]

        selected_index = listbox.curselection()

        if selected_index:
            selected_index = selected_index[0]
            selected_text = listbox.get(selected_index)

            current_data = self.data_manager.get_hiddenblock_data(self.map_name)
            block_to_remove = None
            for block in current_data:
                lot_name = get_lot_name_by_data(block["Result"])
                display_text = f"    {lot_name.ljust(12 if "Star" in lot_name else 0,"\u200a")}   {f'(Rate: {str(block['Rate']).ljust(3, '\u2007')[:3]})'}    "
                if display_text in selected_text and block["No"] == lot_no:
                    block_to_remove = block
                    break

            if block_to_remove:
                current_data.remove(block_to_remove)

            self.data_manager.update_hiddenblock_data(
                self.map_name, current_data
            )
            self.data_manager.sync_with_linked_maps(self.map_name)

    def load_hiddenblock_data(self, data):
        self.data_manager.update_hiddenblock_data(self.map_name, data)
        self.refresh_data()

    def refresh_data(self):
        for lot_no, lot_data in self.lots.items():
            lot_data["listbox"].delete(0, tk.END)

        blocks = self.data_manager.get_hiddenblock_data(self.map_name)

        for block in blocks:
            if (
                isinstance(block, dict)
                and "No" in block
                and "Result" in block
                and "Rate" in block
            ):
                lot_no = block["No"]
                result_data = block["Result"]
                rate = block["Rate"]

                lot_name = get_lot_name_by_data(result_data)
                display_text = f"    {lot_name.ljust(12 if "Star" in lot_name else 0,"\u200a")}   {f'(Rate: {str(rate).ljust(3, '\u2007')[:3]})'}    "
                lot_data = self.lots.get(lot_no)
                if lot_data:
                    listbox = lot_data["listbox"]
                    listbox.insert(tk.END, display_text)

    def save_blocks(self):
        blocks = []
        for lot_no, widgets in self.lots.items():
            listbox = widgets["listbox"]
            if listbox:
                for i in range(listbox.size()):
                    item_text = listbox.get(i)
                    lot_name, rate_info = item_text.split(" (Rate: ")
                    result_data = get_lot_data_by_name(lot_name.strip())
                    rate = int(rate_info.strip(")"))

                    if result_data is not None:
                        blocks.append(
                            {"No": lot_no, "Result": result_data, "Rate": rate}
                        )
        return blocks


def process_hiddenblock_data(hiddenblock_data):
    results = []
    for entry in hiddenblock_data:
        if all(key in entry for key in ["Result", "No", "Rate"]):
            results.append(entry)
        else:
            continue
    return results


def load_hiddenblock_mapdata(base_path, map_name):
    hiddenblock_data = []
    file_name = os.path.join(
        "bd~bd00.nx", "bd", "bd00", "data", "bd00_HiddenBlock.json"
    )
    file_path = os.path.join(base_path, file_name)

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            hiddenblock_data = data.get("HiddenBlock", [])
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error occurred while reading file: {file_name}")

    hiddenblock_data = process_hiddenblock_data(hiddenblock_data)
    return hiddenblock_data


def save_hiddenblock_mapdata(base_path, hiddenblock_data, map_name):
    file_name = os.path.join(
        "bd~bd00.nx", "bd", "bd00", "data", "bd00_HiddenBlock.json"
    )
    file_path = os.path.join(base_path, file_name)
    try:
        with open(file_path, "w", encoding="utf-8-sig") as f:
            file_data = {"HiddenBlock": hiddenblock_data}
            json.dump(file_data, f, indent=4)
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error occurred while writing to file: {file_name}")
