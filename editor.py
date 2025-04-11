import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from editor_modules.hidden_block import (
    HiddenBlockDataManager,
    HiddenBlockEditor,
    load_hiddenblock_mapdata,
    save_hiddenblock_mapdata,
)
from editor_modules.item_bag import (
    ItemBagEditor,
    load_itembag_mapdata,
    save_itembag_mapdata,
)
from editor_modules.item_mass import (
    ItemMassEditor,
    load_itemmass_mapdata,
    save_itemmass_mapdata,
)
from editor_modules.item_shop import (
    ItemShopEditor,
    load_itemshop_mapdata,
    save_itemshop_mapdata,
)
from editor_modules.events import (
    EventEditor,
    EventDataManager,
    load_event_mapdata,
    save_event_mapdata,
)
from editor_modules.map_layout import (
    MapLayoutEditor,
    load_map_layout_mapdata,
    save_map_layout_mapdata,
)

APP_WIDTH = 1600
APP_HEIGHT = 900

general_items = [
    "Stone",
    "ItemBag",
    "Kinoko",
    "ManyKinoko",
    "SlowKinoko",
    "ManySlowKinoko",
    "SuperSlowKinoko",
    "JustDice",
    "DoubleDice",
    "TripleDice",
    "GoldDoubleDice",
    "GoldTripleDice",
    "NormalPipe",
    "GoldPipe",
    "WarpBox",
    "ShoppingPipe",
    "ChangeBox",
    "SuperChangeBox",
    "KoopaPhone",
    "ShoppingPhone",
    "StealBox",
    "DuelGrove",
    "SuperDuelGrove",
    "10CoinTakeMass",
    "HalfCoinTakeMass",
    "StarTakeMass",
    "TereBell",
    "WanwanWhistle",
    "HiddenBlockCard",
]

map_items = {
    "Map01": {"name": "Goomba Lagoon", "items": ["Shell"]},
    "Map02": {"name": "Western Land", "items": ["Key"]},
    "Map03": {"name": "Mario's Rainbow Castle", "items": ["Roulette"]},
    "Map04": {"name": "Roll 'em Raceway", "items": ["MachDice"]},
    "Map05": {
        "name": "Rainbow Galleria",
        "items": ["PriceHikeSticker"],
    },
    "Map06": {
        "name": "King Bowser's Keep",
        "items": [
            "ConveyorSwitch",
            "Key",
        ],
    },
    "Map07": {
        "name": "Mega Wiggler's Tree Party",
        "items": ["AlarmClock"],
    },
}

map_layout_settings = {
    "Map01": {"reverse_x": False, "reverse_y": True},
    "Map02": {"reverse_x": False, "reverse_y": True},
    "Map03": {"reverse_x": False, "reverse_y": True},
    "Map04": {"reverse_x": False, "reverse_y": True},
    "Map05": {"reverse_x": False, "reverse_y": True},
    "Map06": {"reverse_x": False, "reverse_y": True},
    "Map07": {"reverse_x": False, "reverse_y": True},
}


class MapTab(tk.Frame):
    def __init__(
        self,
        parent,
        map_name,
        item_shop_data,
        item_bag_data,
        item_mass_data,
        event_data_manager,
        hiddenblock_data_manager,
        luckymass_data,
        unluckymass_data,
        masskoopa_data,
        hidden_block_data,
        WORKSPACE_PATH,
    ):
        super().__init__(parent)
        self.WORKSPACE_PATH = WORKSPACE_PATH
        self.item_shop_data = item_shop_data
        self.item_bag_data = item_bag_data
        self.item_mass_data = item_mass_data
        self.event_data_manager = event_data_manager
        self.hiddenblock_data_manager = hiddenblock_data_manager
        self.luckymass_data = luckymass_data
        self.unluckymass_data = unluckymass_data
        self.masskoopa_data = masskoopa_data
        self.hidden_block_data = hidden_block_data

        self.map_name = map_name.replace(" ", "_")

        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.pack(fill="both", expand=True)

        self.shops_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.shops_tab, text="Shops")
        self.shop_notebook = ttk.Notebook(self.shops_tab)
        self.shop_notebook.pack(fill="both", expand=True)

        koopa_tab = ttk.Frame(self.shop_notebook)
        self.shop_notebook.add(koopa_tab, text="Koopa Shop")
        self.koopa_shop = ItemShopEditor(
            koopa_tab,
            "KoopaShop",
            self.item_shop_data,
            self.map_name,
            general_items,
            map_items,
        )

        kamek_tab = ttk.Frame(self.shop_notebook)
        self.shop_notebook.add(kamek_tab, text="Kamek Shop")
        self.kamek_shop = ItemShopEditor(
            kamek_tab,
            "KamekShop",
            self.item_shop_data,
            self.map_name,
            general_items,
            map_items,
        )

        self.items_packs_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.items_packs_tab, text="Item Packs")
        self.items_packs_notebook = ttk.Notebook(self.items_packs_tab)
        self.items_packs_notebook.pack(fill="both", expand=True)

        item_bag_tab = ttk.Frame(self.items_packs_notebook)
        self.items_packs_notebook.add(item_bag_tab, text="Item Bag")
        self.item_bag = ItemBagEditor(
            item_bag_tab,
            self.item_bag_data,
            self.map_name,
            APP_WIDTH,
            general_items,
            map_items,
        )

        item_mass_tab = ttk.Frame(self.items_packs_notebook)
        self.items_packs_notebook.add(item_mass_tab, text="Item Mass")
        self.item_mass = ItemMassEditor(
            item_mass_tab,
            self.item_mass_data,
            self.map_name,
            APP_WIDTH,
            general_items,
            map_items,
        )

        self.events_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.events_tab, text="Events")
        self.events_notebook = ttk.Notebook(self.events_tab)
        self.events_notebook.pack(fill="both", expand=True)

        lucky_tab = ttk.Frame(self.events_notebook)
        self.events_notebook.add(lucky_tab, text="Lucky")
        self.lucky_events = EventEditor(
            lucky_tab, "LuckyMass", self.map_name, APP_WIDTH, self.event_data_manager
        )

        unlucky_tab = ttk.Frame(self.events_notebook)
        self.events_notebook.add(unlucky_tab, text="Unlucky")
        self.unlucky_events = EventEditor(
            unlucky_tab,
            "UnluckyMass",
            self.map_name,
            APP_WIDTH,
            self.event_data_manager,
        )

        koopa_mass_tab = ttk.Frame(self.events_notebook)
        self.events_notebook.add(koopa_mass_tab, text="KoopaMass")
        self.koopa_mass_events = EventEditor(
            koopa_mass_tab,
            "KoopaMass",
            self.map_name,
            APP_WIDTH,
            self.event_data_manager,
        )

        self.hidden_block_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.hidden_block_tab, text="Hidden Block")
        self.hidden_block = HiddenBlockEditor(
            self.hidden_block_tab,
            self.map_name,
            APP_WIDTH,
            self.hiddenblock_data_manager,
        )

        self.map_layout_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.map_layout_tab, text="Map Layout")
        self.map_layout = MapLayoutEditor(
            self.map_layout_tab,
            self.map_name,
            self.WORKSPACE_PATH,
            map_layout_settings[map_name]["reverse_x"],
            map_layout_settings[map_name]["reverse_y"],
        )

    def load_data(self):
        self.item_shop_data = load_itemshop_mapdata(self.WORKSPACE_PATH, self.map_name)
        self.koopa_shop.load_shop_data("P0", self.item_shop_data)
        self.koopa_shop.load_shop_data("P1", self.item_shop_data)
        self.koopa_shop.load_shop_data("P2", self.item_shop_data)
        self.kamek_shop.load_shop_data("P0", self.item_shop_data)
        self.kamek_shop.load_shop_data("P1", self.item_shop_data)
        self.kamek_shop.load_shop_data("P2", self.item_shop_data)

        self.item_bag_data = load_itembag_mapdata(self.WORKSPACE_PATH, self.map_name)
        self.item_bag.load_items(self.item_bag_data)

        self.item_mass_data = load_itemmass_mapdata(self.WORKSPACE_PATH, self.map_name)
        self.item_mass.load_items(self.item_mass_data)

        self.luckymass_data = load_event_mapdata(
            self.WORKSPACE_PATH, self.map_name, "LuckyMass"
        )
        self.lucky_events.load_event_data(self.luckymass_data)

        self.unluckymass_data = load_event_mapdata(
            self.WORKSPACE_PATH, self.map_name, "UnluckyMass"
        )
        self.unlucky_events.load_event_data(self.unluckymass_data)

        self.koopamass_data = load_event_mapdata(
            self.WORKSPACE_PATH, self.map_name, "KoopaMass"
        )
        self.koopa_mass_events.load_event_data(self.koopamass_data)

        self.hidden_block_data = load_hiddenblock_mapdata(
            self.WORKSPACE_PATH, self.map_name
        )
        self.hidden_block.load_hiddenblock_data(self.hidden_block_data)

        self.map_layout_data = load_map_layout_mapdata(
            self.WORKSPACE_PATH, self.map_name
        )
        self.map_layout.load_data(self.map_layout_data)

    def randomize_data(self):
        self.koopa_shop.randomize_shop_data("P0")
        self.koopa_shop.randomize_shop_data("P1")
        self.koopa_shop.randomize_shop_data("P2")
        self.kamek_shop.randomize_shop_data("P0")
        self.kamek_shop.randomize_shop_data("P1")
        self.kamek_shop.randomize_shop_data("P2")
        self.item_bag.randomize_items()
        self.item_mass.randomize_items()
        self.lucky_events.randomize_event_data()
        self.unlucky_events.randomize_event_data()
        self.koopa_mass_events.randomize_event_data()
        self.hidden_block.randomize_hiddenblock_data()
        self.map_layout.randomize_data()

    def save_data(self):
        self.item_shop_data = self.koopa_shop.save_shop_data("P0")
        self.item_shop_data = self.koopa_shop.save_shop_data("P1")
        self.item_shop_data = self.koopa_shop.save_shop_data("P2")
        self.item_shop_data = self.kamek_shop.save_shop_data("P0")
        self.item_shop_data = self.kamek_shop.save_shop_data("P1")
        self.item_shop_data = self.kamek_shop.save_shop_data("P2")
        save_itemshop_mapdata(self.WORKSPACE_PATH, self.map_name, self.item_shop_data)

        self.item_bag_data = self.item_bag.save_items()
        save_itembag_mapdata(self.WORKSPACE_PATH, self.item_bag_data, self.map_name)

        self.item_mass_data = self.item_mass.save_items()
        save_itemmass_mapdata(self.WORKSPACE_PATH, self.item_mass_data, self.map_name)

        self.luckymass_data = self.event_data_manager.get_event_data(
            self.map_name, "LuckyMass"
        )
        save_event_mapdata(
            self.WORKSPACE_PATH, self.luckymass_data, self.map_name, "LuckyMass"
        )

        self.unluckymass_data = self.event_data_manager.get_event_data(
            self.map_name, "UnluckyMass"
        )
        save_event_mapdata(
            self.WORKSPACE_PATH, self.unluckymass_data, self.map_name, "UnluckyMass"
        )

        self.koopamass_data = self.event_data_manager.get_event_data(
            self.map_name, "KoopaMass"
        )
        save_event_mapdata(
            self.WORKSPACE_PATH, self.koopamass_data, self.map_name, "KoopaMass"
        )

        self.hidden_block_data = self.hiddenblock_data_manager.get_hiddenblock_data(
            self.map_name
        )
        save_hiddenblock_mapdata(
            self.WORKSPACE_PATH, self.hidden_block_data, self.map_name
        )

        self.map_layout_data = self.map_layout.save_data()
        save_map_layout_mapdata(
            self.WORKSPACE_PATH, self.map_name, self.map_layout_data
        )


class JamboreeMapEditor(tk.Tk):
    def __init__(self, WORKSPACE_PATH):
        super().__init__()
        self.WORKSPACE_PATH = WORKSPACE_PATH
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)
        self.title(
            f"Super Mario Party Jamboree : Map Editor | {os.path.basename(WORKSPACE_PATH)}"
        )

        self.item_shop_data = {}
        self.item_bag_data = {}
        self.item_mass_data = {}
        self.luckymass_data = {}
        self.unluckymass_data = {}
        self.koopamass_data = {}
        self.hiddenblock_data = {}
        self.event_data_manager = EventDataManager()
        self.hiddenblock_data_manager = HiddenBlockDataManager()

        style = ttk.Style(self)
        style.configure("TNotebook", tabposition="n")
        style.configure(
            "TNotebook.Tab", width=APP_WIDTH // 7, padding=[5, 5], anchor="center"
        )

        self.notebook = ttk.Notebook(self, style="TNotebook", height=600)
        self.notebook.pack(expand=1, fill="both")

        for i in range(1, 8):
            map_name = f"Map0{i}"
            tab = MapTab(
                self.notebook,
                map_name,
                self.item_shop_data,
                self.item_bag_data,
                self.item_mass_data,
                self.event_data_manager,
                self.hiddenblock_data_manager,
                self.luckymass_data,
                self.unluckymass_data,
                self.koopamass_data,
                self.hiddenblock_data,
                self.WORKSPACE_PATH,
            )
            self.notebook.add(tab, text=map_items[map_name]["name"])

            self.item_shop_data[map_name] = {
                "KoopaShop": {"P0": {}, "P1": {}, "P2": {}},
                "KamekShop": {"P0": {}, "P1": {}, "P2": {}},
            }
            self.item_bag_data[map_name] = []
            self.item_mass_data[map_name] = []
            
        self.general_frame = tk.Frame(self)
        self.general_frame.pack(side="right", padx=10, pady=10)

        self.speed_frame = tk.Frame(self, width=APP_WIDTH)
        self.speed_frame.pack(side="top", padx=10, pady=10)

        self.speed_label = tk.Label(self.speed_frame, text="Player Move Parameters")
        self.speed_label.pack(anchor="center")

        self.speed_entries_frame = tk.Frame(self.speed_frame)
        self.speed_entries_frame.pack()

        standard_speed_column_frame = tk.Frame(self.speed_entries_frame)
        standard_speed_column_frame.pack(side="left", padx=5)
        standard_speed_label = tk.Label(
            standard_speed_column_frame, text="Standard Speed"
        )
        standard_speed_label.pack(anchor="center")
        self.standard_speed_entry = ttk.Spinbox(
            standard_speed_column_frame, from_=1, to=150, increment=1, width=15
        )
        self.standard_speed_entry.pack(anchor="center", pady=5)

        circuit_speed_column_frame = tk.Frame(self.speed_entries_frame)
        circuit_speed_column_frame.pack(side="left", padx=5)
        circuit_speed_label = tk.Label(circuit_speed_column_frame, text="Circuit Speed")
        circuit_speed_label.pack(anchor="center")
        self.circuit_speed_entry = ttk.Spinbox(
            circuit_speed_column_frame, from_=1, to=150, increment=1, width=15
        )
        self.circuit_speed_entry.pack(anchor="center", pady=5)

        machdice_speed_column_frame = tk.Frame(self.speed_entries_frame)
        machdice_speed_column_frame.pack(side="left", padx=5)
        machdice_speed_label = tk.Label(
            machdice_speed_column_frame, text="Machdice Speed"
        )
        machdice_speed_label.pack(anchor="center")
        self.machdice_speed_entry = ttk.Spinbox(
            machdice_speed_column_frame, from_=1, to=150, increment=1, width=15
        )
        self.machdice_speed_entry.pack(anchor="center", pady=5)


        self.button_frame = tk.Frame(self.general_frame,width=100,)
        self.button_frame.pack(side="left", padx=5, pady=10)
        self.randomize_button = tk.Button(
            self.button_frame,
            text="Randomize Map Data",
            command=self.randomize_data,
            state="disabled",
            width=100,
        )
        self.randomize_button.pack(pady=5)
        self.save_button = tk.Button(
            self.button_frame,
            text="Save Map Data",
            command=self.save_data,
            state="disabled",
            width=100,
        )
        self.save_button.pack(pady=5)
        self.after(150, self.load_data)

    def load_player_move_parameters(self):
        file_path = os.path.join(
            self.WORKSPACE_PATH,
            "bd~bd00.nx",
            "bd",
            "bd00",
            "data",
            "bd00_PlayerMove.json",
        )
        try:
            with open(file_path, "r", encoding="utf-8-sig") as json_file:
                player_move_parameters_data = json.load(json_file)
                self.standard_speed_entry.set(
                    player_move_parameters_data["PlayerMove"][0]["MaxSpeed"]
                )
                self.circuit_speed_entry.set(
                    player_move_parameters_data["PlayerMove"][0]["CircuitSpeed"]
                )
                self.machdice_speed_entry.set(
                    player_move_parameters_data["PlayerMove"][0]["MachSpeed"]
                )
        except Exception as error:
            print(f"Cannot Read File {file_path}:\n {error}\n")
        return player_move_parameters_data
    
    def save_player_move_parameters(self):
        file_path = os.path.join(
            self.WORKSPACE_PATH,
            "bd~bd00.nx",
            "bd",
            "bd00",
            "data",
            "bd00_PlayerMove.json",
        )
        try:
            player_move_parameters_data = {}
            with open(file_path, "r", encoding="utf-8-sig") as json_file:
                player_move_parameters_data = json.load(json_file)
                for player_move in player_move_parameters_data["PlayerMove"]:
                    player_move["MaxSpeed"] = int(self.standard_speed_entry.get())
                    player_move["CircuitSpeed"] = int(self.circuit_speed_entry.get())
                    player_move["MachSpeed"] = int(self.machdice_speed_entry.get())
            with open(file_path, "w", encoding="utf-8-sig") as json_file:
                json.dump(player_move_parameters_data, json_file, indent=4)
        except Exception as error:
            print(f"Cannot Read File {file_path}:\n {error}\n")

    def load_data(self):
        if not os.path.exists(
            os.path.join(self.WORKSPACE_PATH, "bd~bd00.nx", "bd", "bd00", "data")
        ):
            messagebox.showerror("Error", "The workspace data cannot be read correctly")
        else:
            errors = []
            for i in range(1, 8):
                for file in [
                    os.path.join(
                        "bd~bd00.nx",
                        "bd",
                        "bd00",
                        "data",
                        f"bd00_ItemBag_Map{str(i).zfill(2)}.json",
                    ),
                    os.path.join(
                        "bd~bd00.nx",
                        "bd",
                        "bd00",
                        "data",
                        f"bd00_ItemMass_Map{str(i).zfill(2)}.json",
                    ),
                    os.path.join(
                        "bd~bd00.nx",
                        "bd",
                        "bd00",
                        "data",
                        f"bd00_ItemShop_Map{str(i).zfill(2)}.json",
                    ),
                    os.path.join(
                        "bd~bd00.nx",
                        "bd",
                        "bd00",
                        "data",
                        f"bd00_LuckyMass_Map{str(i).zfill(2)}.json",
                    ),
                    os.path.join(
                        "bd~bd00.nx",
                        "bd",
                        "bd00",
                        "data",
                        f"bd00_UnluckyMass_Map{str(i).zfill(2)}.json",
                    ),
                    os.path.join(
                        f"bd~bd{str(i).zfill(2)}.nx",
                        "bd",
                        f"bd{str(i).zfill(2)}",
                        "data",
                        f"bd{str(i).zfill(2)}_MapNode.json",
                    ),
                    os.path.join(
                        f"bd~bd{str(i).zfill(2)}.nx",
                        "bd",
                        f"bd{str(i).zfill(2)}",
                        "data",
                        f"bd{str(i).zfill(2)}_MapPath.json",
                    ),
                    os.path.join(
                        "bd~bd00.nx",
                        "bd",
                        "bd00",
                        "data",
                        "bd00_HiddenBlock.json",
                    ),
                    os.path.join(
                        "bd~bd00.nx",
                        "bd",
                        "bd00",
                        "data",
                        "bd00_PlayerMove.json",
                    ),
                ]:
                    file_path = os.path.join(self.WORKSPACE_PATH, file)
                    try:
                        with open(file_path, "r", encoding="utf-8-sig") as json_file:
                            json.load(json_file)
                    except Exception as error:
                        errors.append(f"Cannot Read File {file_path}:\n {error}\n")

            if errors:
                error_message = "\n".join(errors)
                messagebox.showerror(
                    "Error", f"The following errors occurred:\n{error_message}"
                )
                return
            self.load_player_move_parameters()
            for tab in self.notebook.tabs():
                tab_widget = self.notebook.nametowidget(tab)
                tab_widget.load_data()
            self.save_button.config(state="normal")
            self.randomize_button.config(state="normal")

    def save_data(self):
        if not os.path.exists(self.WORKSPACE_PATH):
            messagebox.showerror("Error", "The workspace data cannot be read correctly")
        else:
            if not self.event_data_manager.get_events_status():
                messagebox.showinfo(
                    "Events Errors",
                    "The Event tab compliance check failed, please check if every rate settings are valid",
                )
                return
            self.save_player_move_parameters()
            for tab in self.notebook.tabs():
                tab_widget = self.notebook.nametowidget(tab)
                tab_widget.save_data()
            messagebox.showinfo(
                "Data Saved", "The workspace files has been modified successfuly"
            )

    def randomize_data(self):
        for tab in self.notebook.tabs():
            tab_widget = self.notebook.nametowidget(tab)
            tab_widget.randomize_data()
        messagebox.showinfo(
            "Data Randomized", "The data has been randomized successfuly"
        )
