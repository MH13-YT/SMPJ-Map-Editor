import os
import json
import tkinter as tk
from tkinter import ttk

# Exemple de structure des lots (peut être chargée dynamiquement)
LOTS = [
    {"data": -1, "name": "1 Star"},
    {"data": 5, "name": "5 Coins"},
    {"data": 6, "name": "6 Coins"},
    {"data": 7, "name": "7 Coins"},
    {"data": 10, "name": "10 Coins"},
    {"data": 12, "name": "12 Coins"},
    {"data": 15, "name": "15 Coins"},
    {"data": 20, "name": "20 Coins"},
    {"data": 30, "name": "30 Coins"},
]

# Fonction utilitaire pour convertir entre ID de lot et nom
def get_lot_name_by_data(data):
    """Retourne le nom lisible pour un ID de lot donné."""
    for lot in LOTS:
        if lot["data"] == data:
            return lot["name"]
    return f"Unknown ({data})"

def get_lot_data_by_name(name):
    """Retourne l'ID de lot associé à un nom donné."""
    for lot in LOTS:
        if lot["name"] == name:
            return lot["data"]
    return None

class HiddenBlockDataManager:
    def __init__(self):
        self.hiddenblock_data = {}  # Dictionnaire des données de blocs cachés
        self.listeners = []  # Liste des listeners pour les notifications

    def register_listener(self, listener):
        """Enregistre un éditeur pour être notifié des changements."""
        self.listeners.append(listener)

    def get_hiddenblock_data(self, map_name):
        """Récupère les données des blocs cachés pour une carte donnée."""
        return self.hiddenblock_data.get(map_name, [])

    def update_hiddenblock_data(self, map_name, data_type, hiddenblock_data):
        """Met à jour les données des événements (ici des blocs cachés)."""
        if map_name not in self.hiddenblock_data:
            self.hiddenblock_data[map_name] = {}
        self.hiddenblock_data[map_name][data_type] = hiddenblock_data
        self.notify_listeners()

    def sync_with_linked_maps(self, map_name):
        """Synchronise les données entre les cartes liées pour le fichier HiddenBlock."""
        linked_maps = self.get_linked_maps(map_name)
        current_data = self.get_hiddenblock_data(map_name)
        
        # Synchroniser les données sur les cartes liées
        for linked_map in linked_maps:
            self.hiddenblock_data[linked_map] = current_data
        self.notify_listeners()

    def get_linked_maps(self, map_name):
        """Retourne les cartes liées."""
        linked_maps = []
        if map_name.startswith("Map"):
            map_number = int(map_name[3:])
            linked_maps = [f"Map{n:02d}" for n in range(1, 8) if n != 6 and n != map_number]
        return linked_maps

    def notify_listeners(self):
        """Avertit tous les éditeurs enregistrés que des données ont été mises à jour."""
        for listener in self.listeners:
            listener.refresh_data()

class HiddenBlockEditor:
    def __init__(self, parent, map_name, app_width, data_manager):
        self.data_manager = data_manager  # Gestionnaire de données central
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
        columns = 5
        rows = 2

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

        entry = ttk.Combobox(lot_frame, values=[lot["name"] for lot in LOTS], width=18)
        entry.pack(pady=5)

        rate_entry = ttk.Spinbox(lot_frame, width=18, from_=1, to=999)  # Entrée pour le rate
        rate_entry.pack(pady=5)

        add_button = ttk.Button(lot_frame, text="Add Block", command=lambda: self.add_block(lot_no, entry, rate_entry))
        add_button.pack(pady=5)

        scroll_frame = tk.Frame(lot_frame)
        scroll_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(scroll_frame)
        listbox = tk.Listbox(scroll_frame, yscrollcommand=scrollbar.set, height=10)
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)

        remove_button = ttk.Button(lot_frame, text="Remove Block", command=lambda: self.remove_block(lot_no))
        remove_button.pack(pady=5)

        self.lots[lot_no] = {
            "entry": entry,
            "rate_entry": rate_entry,
            "listbox": listbox
        }

    def add_block(self, lot_no, entry, rate_entry):
        """Ajoute un bloc au lot spécifié avec un Rate."""
        block_name = entry.get()
        block_data = get_lot_data_by_name(block_name)
        rate = rate_entry.get()

        # Vérifier que le rate est un nombre à 3 chiffres
        if block_data is not None and rate.isdigit() and 0 <= int(rate) <= 999:
            listbox = self.lots[lot_no]["listbox"]
            listbox.insert(tk.END, f"{block_name} (ID: {block_data}, Rate: {rate})")

            current_data = self.data_manager.get_hiddenblock_data(self.map_name)
        
            # Débogage : vérifier la structure de current_data
            print(f"current_data avant ajout: {current_data}")
        
            # Assurez-vous que current_data est une liste de dictionnaires
            if not isinstance(current_data, list):
                current_data = []

            new_entry = {
                "No": lot_no,
                "Result": block_data,
                "Rate": int(rate),  # Convertir le rate en entier
            }
            current_data.append(new_entry)

            self.data_manager.update_hiddenblock_data(self.map_name, "HiddenBlock", current_data)
            self.data_manager.sync_with_linked_maps(self.map_name)

    def load_hiddenblock_data(self, data):
        """Charge les données d'événements depuis le gestionnaire."""
        self.data_manager.update_hiddenblock_data(self.map_name,"HiddenBlock", data)
        self.refresh_data()

    def refresh_data(self):
        """Actualise les blocs affichés dans l'interface graphique."""
        # Vider les anciennes données dans les Listboxes
        for lot_no, lot_data in self.lots.items():
            lot_data["listbox"].delete(0, tk.END)

        # Extraire les blocs depuis 'HiddenBlock' si disponibles
        blocks = self.data_manager.get_hiddenblock_data(self.map_name).get("HiddenBlock", [])

        # Débogage : vérifier la structure de blocks

        for block in blocks:
            if isinstance(block, dict) and "No" in block and "Result" in block and "Rate" in block:
                lot_no = block["No"]
                result_data = block["Result"]
                rate = block["Rate"]

                lot_name = get_lot_name_by_data(result_data)
                display_text = f"{lot_name} (Rate: {rate})"
                print(display_text)

                lot_data = self.lots.get(lot_no)
                if lot_data:
                    listbox = lot_data["listbox"]
                    listbox.insert(tk.END, display_text)

    def save_blocks(self):
        """Sauvegarde les données des blocs dans un format JSON."""
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
                        blocks.append({
                            "No": lot_no,
                            "Result": result_data,
                            "Rate": rate
                        })
        return blocks

def process_hiddenblock_data(hiddenblock_data):
    """
    Traite les données des blocs cachés pour s'assurer que chaque entrée a les clés nécessaires
    et les valeurs dans le bon format.
    """
    results = []
    for entry in hiddenblock_data:
        # Vérifie que chaque entrée a les clés nécessaires : "Result", "No", "Rate"
        if all(key in entry for key in ["Result", "No", "Rate"]):
            results.append(entry)
        else:
            continue
    return results


def load_hiddenblock_mapdata(base_path, map_name):
    """
    Charge les fichiers JSON pour les blocs cachés associés à une carte spécifique.
    """
    hiddenblock_data = []
    file_name = os.path.join("bd~bd00.nx", "bd", "bd00", "data", "bd00_HiddenBlock.json")
    file_path = os.path.join(base_path, file_name)

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            hiddenblock_data = data.get("HiddenBlock", [])
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error occurred while reading file: {file_name}")

    # Traite les données
    hiddenblock_data = process_hiddenblock_data(hiddenblock_data)
    return hiddenblock_data

def save_hiddenblock_mapdata(base_path, hiddenblock_data, map_name):
    """
    Sauvegarde les données des blocs cachés dans le fichier JSON.
    """
    file_name = os.path.join("bd~bd00.nx", "bd", "bd00", "data", "bd00_HiddenBlock.json")
    file_path = os.path.join(base_path, file_name)
    
    try:
        with open(file_path, "w", encoding="utf-8-sig") as f:
            # Enregistrer les données des blocs cachés sous le nom de la carte
            file_data = {map_name: hiddenblock_data}
            json.dump(file_data, f, indent=4)
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error occurred while writing to file: {file_name}")