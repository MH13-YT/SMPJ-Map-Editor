import json
import os
import tkinter as tk
from tkinter import ttk

class ItemMassEditor:
    def __init__(self, parent, data_store, map_name, app_width, general_items, map_items):
        self.data_store = data_store
        self.map_name = map_name.replace(" ", "_")
        # Combiner les items spécifiques à la carte avec les items généraux
        self.combined_items = map_items[self.map_name]["items"] + general_items
        self.lots = {}  # Conteneur pour chaque lot

        # Création du conteneur principal
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Nombre de colonnes et de lignes dans la grille
        columns = 5
        rows = 2

        # Calcul de la largeur des colonnes
        column_width = app_width // columns

        # Configurer les colonnes et lignes du conteneur principal pour centrer la grille
        for col in range(columns):
            self.frame.grid_columnconfigure(col, weight=1, uniform="group")  # Pour une largeur égale
        for row in range(rows):
            self.frame.grid_rowconfigure(row, weight=1, uniform="group")  # Pour une hauteur égale

        # Liste des lots, excluant les numéros 4 et 6
        available_lots = [0, 1, 2, 3, 5, 7, 8]

        # Créer une grille de 4 colonnes et 2 lignes (réorganiser les lots disponibles)
        num_columns = 7  # Nombre de colonnes
        for index, lot_no in enumerate(available_lots):
            self.create_lot_column(lot_no, app_width, index, num_columns)

    def create_lot_column(self, lot_no, app_width, index, num_columns):
        """Créer une colonne pour un lot spécifique."""
        column_width = app_width // num_columns

        # Calculer la ligne et la colonne dans la grille
        row = index // num_columns  # Détermine la ligne
        column = index % num_columns  # Détermine la colonne

        # Création d'un LabelFrame pour le lot
        lot_frame = ttk.LabelFrame(self.frame, text=f"{lot_no}", width=column_width)
        lot_frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")

        # Widgets pour ajouter des éléments
        entry = ttk.Combobox(lot_frame, values=self.combined_items, width=18)
        entry.pack(pady=5)

        add_button = ttk.Button(lot_frame, text="Add Item", command=lambda: self.add_item(lot_no, entry))
        add_button.pack(pady=5)

        # Scrollable Listbox
        scroll_frame = tk.Frame(lot_frame)
        scroll_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(scroll_frame)
        listbox = tk.Listbox(scroll_frame, yscrollcommand=scrollbar.set, height=10)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)

        # Remove button
        remove_button = ttk.Button(lot_frame, text="Remove Item", command=lambda: self.remove_item(lot_no))
        remove_button.pack(pady=5)

        # Sauvegarde des widgets pour ce lot
        self.lots[lot_no] = {
            "entry": entry,
            "listbox": listbox
        }

    def add_item(self, lot_no, entry):
        """Ajoute un élément au lot spécifié."""
        item = entry.get()
        if item:
            listbox = self.lots[lot_no]["listbox"]
            listbox.insert(tk.END, item)

    def remove_item(self, lot_no):
        """Supprime l'élément sélectionné du lot spécifié."""
        listbox = self.lots[lot_no]["listbox"]
        selected_item = listbox.curselection()
        if selected_item:
            listbox.delete(selected_item)

    def load_items(self, data):
        # Récupérer tous les items pour la carte spécifiée
        items = data.get(self.map_name, [])

        # Parcourir chaque item
        for item in items:
            # Récupérer le nom de l'item et le numéro du lot
            item_name = item.get("Item", "")
            lot_number = item.get("No", None)

            # Si le lot_number existe, insérer l'item dans la listbox correspondante
            if item_name and lot_number is not None:
                # Vérifier si le lot_number existe dans self.lots
                lot_data = self.lots.get(lot_number)
            
                if lot_data:  # Si le lot existe
                    listbox = lot_data.get("listbox")  # Récupérer la Listbox dans le dictionnaire
                    if listbox:  # Si la Listbox est bien présente
                        # Formater l'affichage de l'item avec son numéro de lot
                        display_text = f"{item_name}"
                        # Insérer l'item dans la Listbox associée au numéro du lot
                        listbox.insert(tk.END, display_text)
                    else:
                        print(f"Listbox for Lot {lot_number} is not available.")
                else:
                    print(f"Lot number {lot_number} does not exist in self.lots.")


    def save_items(self):
        """Sauvegarde les données des lots."""
        items = []
    
        # Parcours de chaque lot dans les self.lots
        for lot_no, widgets in self.lots.items():
            listbox = widgets.get("listbox")
        
            if listbox:  # Si la listbox existe
                # On parcourt les éléments de la listbox
                for i in range(listbox.size()):
                    item_text = listbox.get(i)
                    item_data = item_text.split(" - ")
                    item_name = item_data[0]  # Nom de l'item

                    # Ajouter l'item avec son lot_number dans la sauvegarde
                    items.append({
                        "Item": item_name,
                        "No": lot_no  # Enregistrer le numéro du lot
                    })
        
            else:
                print(f"Listbox for Lot {lot_no} is not available.")
    
        # Sauvegarder les données pour la carte spécifique (self.map_name)
        self.data_store[self.map_name] = items
        return items

def process_itemmass_data(item_data):
    """
    Traite les données de ItemMass ou ItemMass.
    """
    results = []
    for entry in item_data:
        if all(key in entry for key in ["Item", "No"]):
            results.append(entry)
        else:
            continue
    return results

def load_itemmass_mapdata(base_path,map_name):
    """
    Charge les fichiers JSON pour ItemMass et ItemMass pour la carte associé.
    """
    item_mass_data = {}
    item_mass_raw_data = []
    file_name = os.path.join("bd~bd00.nx", "bd", "bd00", "data",f"bd00_ItemMass_{map_name}.json")
    file_path = os.path.join(base_path, file_name)
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            item_mass_raw_data = data.get(map_name)
    except FileNotFoundError:
        print(f"File not found : {file_name}")
    except json.JSONDecodeError:
        print(f"Error occurred while reading file : {file_name}")
        
    # Charger les données pour ItemMass
    item_mass_data[map_name] = process_itemmass_data(item_mass_raw_data)
    return item_mass_data

def save_itemmass_mapdata(base_path,item_mass_data,map_name):
    file_name = os.path.join("bd~bd00.nx", "bd", "bd00", "data",f"bd00_ItemMass_{map_name}.json")
    file_path = os.path.join(base_path, file_name)
    with open(file_path, 'w', encoding='utf-8-sig') as f:
        file_data = {}
        file_data[f"{map_name}"] = []
        file_data[f"{map_name}"] = item_mass_data
        json.dump(file_data, f, indent=4)

