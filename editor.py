import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from editor_modules.hidden_block import HiddenBlockEditor
from editor_modules.item_bag import ItemBagEditor, load_itembag_mapdata, save_itembag_mapdata
from editor_modules.item_mass import ItemMassEditor, load_itemmass_mapdata, save_itemmass_mapdata
from editor_modules.item_shop import ItemShopEditor, load_itemshop_mapdata, save_itemshop_mapdata
from editor_modules.events import EventEditor
from editor_modules.map_layout import MapLayoutEditor

# Dimensions de l'application
APP_WIDTH = 1100
APP_HEIGHT = 850

# Lot d'items général
general_items = [
    "Stone", #Lodestone
    "ItemBag", #Sac A Objet
    "Kinoko", #Champignon
    "ManyKinoko", #Coupon Champignon
    "SlowKinoko", #Dé Tronqué
    "ManySlowKinoko", #Coupon Dé Tronqué
    "SuperSlowKinoko", #Lot Dé Tronqué
    "JustDice", #Dé Pipé
    "DoubleDice", #Double Dé
    "TripleDice", #Triple Dé
    "GoldDoubleDice", #Double Dé Doré
    "GoldTripleDice", #Triple Dé Doré
    "NormalPipe", #Tuyau
    "GoldPipe", #Tuyau Doré
    "WarpBox", #Boite de Teleportation
    "ShoppingPipe", #Boite de Teleportation Shop
    "ChangeBox", #Miroir Echange
    "SuperChangeBox", #Super Miroir Echange
    "KoopaPhone", #Telephone Bowser
    "ShoppingPhone", #Telephone KoopaShop
    "StealBox", #Coffre Pillage
    "DuelGrove", #Gant de Duel
    "SuperDuelGrove", #Super Gant de Duel
    "10CoinTakeMass", #Piege 10 Pieces
    "HalfCoinTakeMass", #Piege mi pieces
    "StarTakeMass", #Piege 1 Etoile
    "TereBell", #Cloche Boo
    "WanwanWhistle", #Sifflet Chomp
    "HiddenBlockCard", #Carte Bloc Caché
    ]

# Noms et lots d'items spécifiques par map
map_items = {
    "Map01": {
        "name": "Goomba Lagoon", 
        "items": [
            "Shell" #Conque des Marais
            ]
        },
    "Map02": {
        "name": "Western Land", 
        "items": [
            "Key" #Clé Squelette
            ]},
    "Map03": {
        "name": "Mario's Rainbow Castle",
        "items": [
                "Roulette" #Tour
                ]
            },
    "Map04": {
        "name": "Roll 'em Raceway",
        "items": [
            "MachDice" #Dé 4
            ]
        },
    "Map05": {
        "name": "Rainbow Galleria", 
        "items": [
            "PriceHikeSticker" #Coupon Inflation
            ]
        },
    "Map06": {
        "name": "King Bowser's Keep",
        "items": [
            "ConveyorSwitch", #Switch
            "Key",  #Clé Squelette
        ],
    },
    "Map07": {
        "name": "Mega Wiggler's Tree Party", 
        "items": [
            "AlarmClock"  #Cloche Wiggler
            ]
        },
}


class MapTab(tk.Frame):
    def __init__(self, parent, map_name, item_shop_data, item_bag_data, item_mass_data, WORKSPACE_PATH):
        super().__init__(parent)
        self.WORKSPACE_PATH = WORKSPACE_PATH
        self.item_shop_data = item_shop_data
        self.item_bag_data = item_bag_data
        self.item_mass_data = item_mass_data
        self.map_name = map_name.replace(" ", "_")

        # Nouveau Notebook principal pour organiser les onglets
        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.pack(fill="both", expand=True)

        # Onglet "Shops" pour inclure le shop_notebook (Koopa et Kamek)
        self.shops_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.shops_tab, text="Shops")
        self.shop_notebook = ttk.Notebook(self.shops_tab)
        self.shop_notebook.pack(fill="both", expand=True)

        # Onglets Koopa Shop et Kamek Shop
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

        # Onglet "Items Packs" pour inclure l'ItemListManager
        self.items_packs_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.items_packs_tab, text="Item Packs")
        self.items_packs_notebook = ttk.Notebook(self.items_packs_tab)
        self.items_packs_notebook.pack(fill="both", expand=True)

        # Onglets Item Bag et Item Mass
        item_bag_tab = ttk.Frame(self.items_packs_notebook)
        self.items_packs_notebook.add(item_bag_tab, text="Item Bag")
        self.item_bag = ItemBagEditor(
            item_bag_tab,
            self.item_bag_data,
            self.map_name,
            APP_WIDTH,
            general_items,
            map_items
        )

        item_mass_tab = ttk.Frame(self.items_packs_notebook)
        self.items_packs_notebook.add(item_mass_tab, text="Item Mass")
        self.item_mass = ItemMassEditor(
            item_mass_tab,
            self.item_mass_data,
            self.map_name,
            APP_WIDTH,
            general_items,
            map_items
        )
        
        self.events_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.events_tab, text="Events")
        self.events_notebook = ttk.Notebook(self.events_tab)
        self.events_notebook.pack(fill="both", expand=True)

        lucky_tab = ttk.Frame(self.events_notebook)
        self.events_notebook.add(lucky_tab, text="Lucky")
        self.lucky_events = EventEditor(lucky_tab, "Lucky", self.map_name)

        unlucky_tab = ttk.Frame(self.events_notebook)
        self.events_notebook.add(unlucky_tab, text="Unlucky")
        self.unlucky_events = EventEditor(unlucky_tab, "Unlucky", self.map_name)

        koopa_mass_tab = ttk.Frame(self.events_notebook)
        self.events_notebook.add(koopa_mass_tab, text="KoopaMass")
        self.koopa_mass_events = EventEditor(koopa_mass_tab, "KoopaMass", self.map_name)

        self.hidden_block_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.hidden_block_tab, text="Hidden Block")
        self.hidden_block = HiddenBlockEditor(self.hidden_block_tab, self.map_name)
        
        self.map_layout_tab = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.map_layout_tab, text="Map Layout")
        self.map_layout = MapLayoutEditor(self.map_layout_tab, self.map_name)
        
        # Onglet en Développement
        self.main_notebook.tab(2, state="disabled")
        self.main_notebook.tab(3, state="disabled")
        self.main_notebook.tab(4, state="disabled")

    def load_data(self):
        self.item_shop_data = load_itemshop_mapdata(self.WORKSPACE_PATH, self.map_name)
        self.koopa_shop.load_shop_data("P0", self.item_shop_data)
        self.koopa_shop.load_shop_data("P1", self.item_shop_data)
        self.koopa_shop.load_shop_data("P2", self.item_shop_data)
        self.kamek_shop.load_shop_data("P0", self.item_shop_data)
        self.kamek_shop.load_shop_data("P1", self.item_shop_data)
        self.kamek_shop.load_shop_data("P2", self.item_shop_data)
        # Charger les données pour ItemBag et ItemMass
        self.item_bag_data = load_itembag_mapdata(
            self.WORKSPACE_PATH, self.map_name
        )
        self.item_mass_data = load_itemmass_mapdata(
            self.WORKSPACE_PATH, self.map_name
        )
        # Charger les items pour les sections ItemBag et ItemMass
        self.item_bag.load_items(self.item_bag_data)
        self.item_mass.load_items(self.item_mass_data)

    def save_data(self):
        self.item_shop_data = self.koopa_shop.save_shop_data("P0")
        self.item_shop_data = self.koopa_shop.save_shop_data("P1")
        self.item_shop_data = self.koopa_shop.save_shop_data("P2")
        self.item_shop_data = self.kamek_shop.save_shop_data("P0")
        self.item_shop_data = self.kamek_shop.save_shop_data("P1")
        self.item_shop_data = self.kamek_shop.save_shop_data("P2")
        self.item_bag_data = self.item_bag.save_items()
        self.item_mass_data = self.item_mass.save_items()
        save_itembag_mapdata(
            self.WORKSPACE_PATH, self.item_bag_data, self.map_name
        )
        save_itemmass_mapdata(
            self.WORKSPACE_PATH, self.item_mass_data, self.map_name
        )
        save_itemshop_mapdata(self.WORKSPACE_PATH, self.map_name, self.item_shop_data)


class JamboreeMapEditor(tk.Tk):
    def __init__(self,WORKSPACE_PATH):
        super().__init__()
        self.WORKSPACE_PATH = WORKSPACE_PATH
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)
        self.title(f"Super Mario Party Jamboree : Map Editor | {os.path.basename(WORKSPACE_PATH)}")

        # Séparation des variables globales en trois variables
        self.item_shop_data = {}
        self.item_bag_data = {}
        self.item_mass_data = {}

        style = ttk.Style(self)
        style.configure("TNotebook", tabposition="n")
        style.configure(
            "TNotebook.Tab", width=APP_WIDTH // 7, padding=[5, 5], anchor="center"
        )

        self.notebook = ttk.Notebook(self, style="TNotebook")
        self.notebook.pack(expand=1, fill="both")

        for i in range(1, 8):
            map_name = f"Map0{i}"
            tab = MapTab(
                self.notebook,
                map_name,
                self.item_shop_data,
                self.item_bag_data,
                self.item_mass_data,
                self.WORKSPACE_PATH
            )
            self.notebook.add(tab, text=map_items[map_name]["name"])

            self.item_shop_data[map_name] = {
                "KoopaShop": {"P0": {}, "P1": {}, "P2": {}},
                "KamekShop": {"P0": {}, "P1": {}, "P2": {}},
            }
            self.item_bag_data[map_name] = []
            self.item_mass_data[map_name] = []

        # Frame for the load and save buttons (stacked vertically)
        self.button_frame = tk.Frame(self, width=APP_WIDTH)
        self.button_frame.pack(side="left", padx=10, pady=10)

        self.save_button = tk.Button(
            self.button_frame,
            text="Save Map Data",
            command=self.save_data,
            width=APP_WIDTH,
            state="disabled"
        )
        self.save_button.pack(pady=5)
        self.after(100, self.load_data)

    def load_data(self):
        if not os.path.exists(os.path.join(self.WORKSPACE_PATH,"bd~bd00.nx", "bd", "bd00", "data")):
            # Afficher un message d'alerte si le dossier n'existe pas
            messagebox.showerror("Error", f"The workspace data cannot be read correctly")
        else:
            errors = []
            for i in range(1, 8):
                for file in [
                    os.path.join("bd~bd00.nx", "bd", "bd00", "data",f"bd00_ItemBag_Map{str(i).zfill(2)}.json"),
                    os.path.join("bd~bd00.nx", "bd", "bd00", "data",f"bd00_ItemMass_Map{str(i).zfill(2)}.json"),
                    os.path.join("bd~bd00.nx", "bd", "bd00", "data",f"bd00_ItemShop_Map{str(i).zfill(2)}.json")
                    ]:
                    file_path = os.path.join(self.WORKSPACE_PATH, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8-sig') as json_file:
                            json.load(json_file)
                    except Exception as error:
                        # Ajouter le message d'erreur à la liste
                        errors.append(f"Cannot Read File {file_path}:\n {error}\n")

                # Vérifier s'il y a des erreurs et les afficher dans une boîte de message
            if errors:
                error_message = "\n".join(errors)
                messagebox.showerror("Error", f"The following errors occurred:\n{error_message}")
                return
                   
            for tab in self.notebook.tabs():
                tab_widget = self.notebook.nametowidget(tab)
                tab_widget.load_data()
            self.save_button.config(state='normal')

    def save_data(self):
        if not os.path.exists(self.WORKSPACE_PATH):
            # Afficher un message d'alerte si le dossier n'existe pas
            messagebox.showerror("Error", f"The workspace data cannot be read correctly")
        else:
            for tab in self.notebook.tabs():
                tab_widget = self.notebook.nametowidget(tab)
                tab_widget.save_data()
            messagebox.showinfo("Data Saved", "The bd~bd00.nx folder has been modified successfuly")
