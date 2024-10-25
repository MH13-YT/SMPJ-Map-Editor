import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from item_shop import ShopEditor, load_itemshop_mapdata, save_itemshop_mapdata
from item_list_manager import ItemListManager, load_item_mapdata, save_item_mapdata

# Dimensions de l'application
APP_WIDTH = 1100
APP_HEIGHT = 850

# Obtenir le chemin du répertoire où l'exécutable est situé
if getattr(sys, 'frozen', False):
    # Si le script est exécuté sous forme d'exécutable (.exe)
    application_path = os.path.dirname(sys.executable)
    app_extension = "the executable"
else:
    # Si le script est exécuté en tant que script Python
    application_path = os.path.dirname(os.path.abspath(__file__))
    app_extension = "main.py"
# Chemin du dossier contenant les fichiers JSON
BASE_PATH = os.path.join(application_path,"bd~bd00.nx", "bd", "bd00", "data")

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
    def __init__(self, parent, map_name, item_shop_data, item_bag_data, item_mass_data):
        super().__init__(parent)
        self.item_shop_data = item_shop_data
        self.item_bag_data = item_bag_data
        self.item_mass_data = item_mass_data
        self.map_name = map_name.replace(" ", "_")

        # Notebook pour Koopa et Kamek Shops
        self.shop_notebook = ttk.Notebook(self)
        self.shop_notebook.pack(fill="both", expand=True)

        koopa_tab = ttk.Frame(self.shop_notebook)
        self.shop_notebook.add(koopa_tab, text="Koopa Shop")
        self.koopa_shop = ShopEditor(
            koopa_tab,
            "KoopaShop",
            self.item_shop_data,
            self.map_name,
            general_items,
            map_items,
        )

        kamek_tab = ttk.Frame(self.shop_notebook)
        self.shop_notebook.add(kamek_tab, text="Kamek Shop")
        self.kamek_shop = ShopEditor(
            kamek_tab,
            "KamekShop",
            self.item_shop_data,
            self.map_name,
            general_items,
            map_items,
        )

        # Ajout des sections ItemBag et ItemMass
        self.item_bag = ItemListManager(
            self,
            "Item Bag",
            "ItemBag",
            self.item_bag_data,
            self.map_name,
            APP_WIDTH,
            general_items,
            map_items,
            True,
            False,
        )
        self.item_mass = ItemListManager(
            self,
            "Item Mass",
            "ItemMass",
            self.item_mass_data,
            self.map_name,
            APP_WIDTH,
            general_items,
            map_items,
            False,
            True,
        )

    def load_data(self):
        self.item_shop_data = load_itemshop_mapdata(BASE_PATH, self.map_name)
        self.koopa_shop.load_shop_data("P0", self.item_shop_data)
        self.koopa_shop.load_shop_data("P1", self.item_shop_data)
        self.koopa_shop.load_shop_data("P2", self.item_shop_data)
        self.kamek_shop.load_shop_data("P0", self.item_shop_data)
        self.kamek_shop.load_shop_data("P1", self.item_shop_data)
        self.kamek_shop.load_shop_data("P2", self.item_shop_data)
        # Charger les données pour ItemBag et ItemMass
        self.item_bag_data, self.item_mass_data = load_item_mapdata(
            BASE_PATH, self.map_name
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
        save_item_mapdata(
            BASE_PATH, self.item_bag_data, self.item_mass_data, self.map_name
        )
        save_itemshop_mapdata(BASE_PATH, self.map_name, self.item_shop_data)


class JamboreeMapEditor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.resizable(False, False)
        self.title("Jamboree Map Item Editor")

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

        self.load_button = tk.Button(
            self.button_frame,
            text="Load Maps Data",
            command=self.load_data,
            width=APP_WIDTH,
        )
        self.load_button.pack(pady=5)

        self.save_button = tk.Button(
            self.button_frame,
            text="Save Map Data",
            command=self.save_data,
            width=APP_WIDTH,
            state="disabled"
        )
        self.save_button.pack(pady=5)

    def load_data(self):
        if not os.path.exists(BASE_PATH):
            # Afficher un message d'alerte si le dossier n'existe pas
            messagebox.showerror("Error", f"The folder bd~bd00.nx cannot be found, please extract the contents of bd~bd00.nx.bea from Switch Toolbox into a folder named bd~bd00.nx and place it on the same folder than {app_extension}")
        else:
            errors = []
            for i in range(1, 8):
                for file in [f"bd00_ItemBag_Map{str(i).zfill(2)}.json", f"bd00_ItemMass_Map{str(i).zfill(2)}.json", f"bd00_ItemShop_Map{str(i).zfill(2)}.json"]:
                    file_path = os.path.join(BASE_PATH, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8-sig') as json_file:
                            json.load(json_file)
                    except json.JSONDecodeError as error:
                        # Ajouter le message d'erreur à la liste
                        errors.append(f"Cannot Read File {file}:\n {error}\n")

                # Vérifier s'il y a des erreurs et les afficher dans une boîte de message
            if errors:
                error_message = "\n".join(errors)
                messagebox.showerror("Error", f"The following errors occurred:\n{error_message}")
                return
                   
            for tab in self.notebook.tabs():
                tab_widget = self.notebook.nametowidget(tab)
                tab_widget.load_data()
            self.save_button.config(state='normal')
            self.load_button.config(state='disabled')
            messagebox.showinfo("Data Loaded", "The bd~bd00.nx folder has been loaded, good editing")

    def save_data(self):
        if not os.path.exists(BASE_PATH):
            # Afficher un message d'alerte si le dossier n'existe pas
            messagebox.showerror("Error", f"The folder bd~bd00.nx cannot be found, please extract the contents of bd~bd00.nx.bea from Switch Toolbox into a folder named bd~bd00.nx and place it on the same folder than {app_extension}")
        else:
            for tab in self.notebook.tabs():
                tab_widget = self.notebook.nametowidget(tab)
                tab_widget.save_data()
            messagebox.showinfo("Data Saved", "The bd~bd00.nx folder has been modified successfuly")


if __name__ == "__main__":
    app = JamboreeMapEditor()
    app.mainloop()
