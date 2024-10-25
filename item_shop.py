# Fonction principale pour charger et traiter les fichiers ItemShop pour les 7 maps
import json
import os
from tkinter import Tk, ttk
import tkinter as tk


class ShopEditor:
    def __init__(
        self, parent, shop_name, data_store, map_name, general_items, map_items
    ):
        self.data_store = data_store  # Remplace global_data par data_store
        self.map_name = map_name.replace(" ", "_")
        self.shop_name = shop_name

        map_specific_items = map_items[self.map_name]["items"]
        combined_items = ["Empty"] + map_specific_items + general_items

        self.widgets = {"P0": {}, "P1": {}, "P2": {}}

        self.create_phase(parent, "Standard", "P0", combined_items)
        self.create_phase(parent, "Standard (5 Last Turns)", "P1", combined_items)
        self.create_phase(parent, "Pro Mode", "P2", combined_items)

    def create_phase(self, parent, phase_label, phase_name, combined_items):
        # Créer un frame pour chaque phase
        phase_frame = ttk.LabelFrame(parent, text=phase_label)
        phase_frame.pack(fill="x", padx=5, pady=5)

        # Création des 5 slots pour la phase
        for i in range(1, 6):
            # Encadrer chaque slot et définir la largeur du slot à 28
            slot_frame = ttk.LabelFrame(phase_frame, text=f"Slot {i}", width=28)
            slot_frame.grid(row=0, column=i - 1, padx=5, pady=5, sticky="nsew")

            # Configurer une grille dans le slot_frame pour centrer les widgets
            slot_frame.grid_columnconfigure(0, weight=1)

            # Configurer les widgets avec une taille de 10
            self.widgets[phase_name][f"slot{i}"] = {
                "item": ttk.Combobox(
                    slot_frame, values=combined_items, width=20, justify="center"
                ),
                "count": ttk.Combobox(
                    slot_frame, values=[1, 2], width=20, justify="center"
                ),
                "price": tk.Spinbox(
                    slot_frame, from_=0, to=999, width=20, justify="center"
                ),
            }

            # Ajouter les widgets à la grille et les centrer
            self.widgets[phase_name][f"slot{i}"]["item"].grid(
                row=0, column=0, padx=29, pady=5, sticky="ew"
            )
            self.widgets[phase_name][f"slot{i}"]["count"].grid(
                row=1, column=0, padx=29, pady=5, sticky="ew"
            )
            self.widgets[phase_name][f"slot{i}"]["price"].grid(
                row=2, column=0, padx=29, pady=5, sticky="ew"
            )

    def load_shop_data(self, phase_name, data_store):
        self.data_store = data_store
        for slot_num in range(1, 6):
            # Récupérer les données du slot avec vérification à chaque étape
            shop_data = self.data_store.get(self.shop_name)
            phase_data = shop_data.get(phase_name)
            slot_data = phase_data.get(f"slot{slot_num}")

            # Vérifier si les données de slot sont trouvées
            if slot_data:
                # Mettre à jour les widgets avec les données trouvées
                self.widgets[phase_name][f"slot{slot_num}"]["item"].set(
                    slot_data.get("item", "")
                )
                self.widgets[phase_name][f"slot{slot_num}"]["count"].set(
                    slot_data.get("count", "")
                )
                self.widgets[phase_name][f"slot{slot_num}"]["price"].delete(0, "end")
                self.widgets[phase_name][f"slot{slot_num}"]["price"].insert(
                    0, slot_data.get("price", 0)
                )

    def save_shop_data(self, phase_name):
        for slot_num in range(1, 6):
            self.data_store[self.shop_name][phase_name][f"slot{slot_num}"] = {
                "item": self.widgets[phase_name][f"slot{slot_num}"]["item"].get(),
                "count": self.widgets[phase_name][f"slot{slot_num}"]["count"].get(),
                "price": self.widgets[phase_name][f"slot{slot_num}"]["price"].get(),
            }
        return self.data_store


def save_itemshop_mapdata(BASE_PATH, map_name, data):
    def save_itemshop_map_json(data):
        data_file = []
        for shop_name in ["Koopa", "Kamek"]:
            if shop_name == "Koopa":
                type_value = 0
            else:
                type_value = 1
            for p in range(0, 3):
                if (
                    data[f"{shop_name}Shop"][f"P{p}"][f"slot1"]["item"] == "Empty" and 
                    data[f"{shop_name}Shop"][f"P{p}"][f"slot2"]["item"] == "Empty" and 
                    data[f"{shop_name}Shop"][f"P{p}"][f"slot3"]["item"] == "Empty" and 
                    data[f"{shop_name}Shop"][f"P{p}"][f"slot4"]["item"] == "Empty" and 
                    data[f"{shop_name}Shop"][f"P{p}"][f"slot5"]["item"] == "Empty"
                ):
                    print(f"No Item in {map_name} {shop_name}Shop in Phase {p}, Replacing 1st empty slot with 'Stone'")
                    data_file.append(
                        {"Phase": p, "Type": type_value, "Item": "Stone", "Count": 1, "Price": 0},
                    )
                for s in range(1, 6):
                    if data[f"{shop_name}Shop"][f"P{p}"][f"slot{s}"]["item"] != "Empty":
                        data_file.append(
                            {
                                "Phase": p,
                                "Type": type_value,
                                "Item": data[f"{shop_name}Shop"][f"P{p}"][f"slot{s}"]["item"],
                                "Count": int(
                                    data[f"{shop_name}Shop"][f"P{p}"][f"slot{s}"]["count"]
                                ),
                                "Price": int(
                                    data[f"{shop_name}Shop"][f"P{p}"][f"slot{s}"]["price"]
                                ),
                            },
                        )
        return data_file

    file_name = f"bd00_ItemShop_{map_name}.json"
    file_path = os.path.join(BASE_PATH, file_name)
    file_data = {}
    file_data[f"{map_name}"] = []
    file_data[f"{map_name}"] = save_itemshop_map_json(data)
    with open(file_path, "w") as f:
        json.dump(file_data, f)


def load_itemshop_mapdata(BASE_PATH, map_name):
    def load_itemshop_map_json(map_name, BASE_PATH):
        file_name = f"bd00_ItemShop_{map_name}.json"
        file_path = os.path.join(BASE_PATH, file_name)
        try:
            with open(file_path, "r") as f:
                return json.load(f)[f"{map_name}"]
        except FileNotFoundError:
            print(f"File not found : {file_name}")
            return []
        except json.JSONDecodeError:
            print(f"Error occurred while reading file : {file_name}")
            return []

    def init_itemshop_slots():
        return {
            "slot1": {"item": "Empty", "count": "0", "price": "0"},
            "slot2": {"item": "Empty", "count": "0", "price": "0"},
            "slot3": {"item": "Empty", "count": "0", "price": "0"},
            "slot4": {"item": "Empty", "count": "0", "price": "0"},
            "slot5": {"item": "Empty", "count": "0", "price": "0"},
        }

    def read_itemshops(item_shop_data):
        # Vérifie que item_shop_data est une liste
        if not isinstance(item_shop_data, list):
            raise TypeError("item_shop_data doit être un tableau d'objets.")

        # Initialisation des variables de phase et type
        koopa_P0 = init_itemshop_slots()
        koopa_P1 = init_itemshop_slots()
        koopa_P2 = init_itemshop_slots()
        kamek_P0 = init_itemshop_slots()
        kamek_P1 = init_itemshop_slots()
        kamek_P2 = init_itemshop_slots()

        slot_tracker = {
            "Koopa_P0": 1,
            "Koopa_P1": 1,
            "Koopa_P2": 1,
            "Kamek_P0": 1,
            "Kamek_P1": 1,
            "Kamek_P2": 1,
        }

        # Parcourir chaque entrée du tableau d'objets JSON
        for entry in item_shop_data:
            # Vérifie que les clés nécessaires existent dans chaque entry
            if not all(
                key in entry for key in ["Phase", "Type", "Item", "Count", "Price"]
            ):
                continue  # Sauter cette entrée si elle est invalide

            phase = entry["Phase"]
            shop_type = entry["Type"]

            # Traite les types Koopa et Kamek
            if shop_type == 0:  # Koopa
                if phase == 0:
                    slot_num = f"slot{slot_tracker['Koopa_P0']}"
                    koopa_P0[slot_num] = {
                        "item": entry["Item"],
                        "count": str(entry["Count"]),
                        "price": str(entry["Price"]),
                    }
                    slot_tracker["Koopa_P0"] += 1
                elif phase == 1:
                    slot_num = f"slot{slot_tracker['Koopa_P1']}"
                    koopa_P1[slot_num] = {
                        "item": entry["Item"],
                        "count": str(entry["Count"]),
                        "price": str(entry["Price"]),
                    }
                    slot_tracker["Koopa_P1"] += 1
                elif phase == 2:
                    slot_num = f"slot{slot_tracker['Koopa_P2']}"
                    koopa_P2[slot_num] = {
                        "item": entry["Item"],
                        "count": str(entry["Count"]),
                        "price": str(entry["Price"]),
                    }
                    slot_tracker["Koopa_P2"] += 1
            elif shop_type == 1:  # Kamek
                if phase == 0:
                    slot_num = f"slot{slot_tracker['Kamek_P0']}"
                    kamek_P0[slot_num] = {
                        "item": entry["Item"],
                        "count": str(entry["Count"]),
                        "price": str(entry["Price"]),
                    }
                    slot_tracker["Kamek_P0"] += 1
                elif phase == 1:
                    slot_num = f"slot{slot_tracker['Kamek_P1']}"
                    kamek_P1[slot_num] = {
                        "item": entry["Item"],
                        "count": str(entry["Count"]),
                        "price": str(entry["Price"]),
                    }
                    slot_tracker["Kamek_P1"] += 1
                elif phase == 2:
                    slot_num = f"slot{slot_tracker['Kamek_P2']}"
                    kamek_P2[slot_num] = {
                        "item": entry["Item"],
                        "count": str(entry["Count"]),
                        "price": str(entry["Price"]),
                    }
                    slot_tracker["Kamek_P2"] += 1

        # Regrouper les résultats dans une structure
        regroupement_map = {
            "KoopaShop": {
                "P0": koopa_P0,
                "P1": koopa_P1,
                "P2": koopa_P2,
            },
            "KamekShop": {
                "P0": kamek_P0,
                "P1": kamek_P1,
                "P2": kamek_P2,
            },
        }
        return regroupement_map

    # Charger le fichier JSON pour de la carte
    item_shop_data = load_itemshop_map_json(map_name, BASE_PATH)

    # Trier les données pour cette carte
    map_data = read_itemshops(item_shop_data)
    return map_data
