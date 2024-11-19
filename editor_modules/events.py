import json
import os
import tkinter as tk
from tkinter import ttk

result_options = {
    "LuckyMass": [
        "7Coin",
        "10Coin",
        "12Coin",
        "15Coin",
        "20Coin",
        "10CoinTakeMass",
        "DoubleDice",
        "WarpBox",
        "JustDice",
        "NormalDokan",
        "ItemBag",
        "WanwanWhistle",
        "Kinoko",
        "Key",
        "ManyKinoko",
        "SlowKinoko",
        "ChangeBox",
        "Roulette",
        "TripleDice",
    ],
    "UnluckyMass": [
        "Rob3Coin",
        "Rob5Coin",
        "Rob7Coin",
        "Give3Coin",
        "Give5Coin",
        "Give7Coin",
        "GetStone",
        "GiveItem",
    ],
    "KoopaMass": [
        "Rob10Coin",
        "Rob15Coin",
        "Rob20Coin",
        "Rob30Coin",
        "RobHalfCoin",
        "Rob10CoinAll",
        "Revolution",
        "Shuffle",
        "Rob1Star",
        "Get100Star",
        "Get1000Coin",
    ],
}


class EventDataManager:
    def __init__(self):
        self.event_status = {}
        self.event_data = {}
        self.listeners = []

    def register_listener(self, listener):
        """Enregistre une interface (listener) pour une carte donnée."""
        self.listeners.append(listener)

    def get_event_data(self, map_name, data_type):
        """Récupère les données des événements pour une carte et un type spécifique."""
        if map_name in self.event_data and data_type in self.event_data[map_name]:
            return self.event_data[map_name][data_type]
        else:
            return []

    def get_events_status(self):
        """Récupère les données des événements pour une carte et un type spécifique."""
        status = True
        for map_name, map_data in self.event_status.items():
            if (
                map_data["LuckyMass"] == False
                or map_data["UnluckyMass"] == False
                or map_data["KoopaMass"] == False
            ):
                status = False
        return status

    def update_event_data(self, map_name, data_type, event_data):
        """Met à jour les données des événements pour une carte et un type spécifique."""
        if map_name not in self.event_data:
            self.event_data[map_name] = {}
        self.event_data[map_name][data_type] = event_data

    def update_event_status(self, map_name, data_type, status):
        """Met à jour les données des événements pour une carte et un type spécifique."""
        if map_name not in self.event_status:
            self.event_status[map_name] = {}
        self.event_status[map_name][data_type] = status

    def sync_with_linked_maps(self, map_name, data_type):
        """Synchronise les événements entre les cartes liées pour KoopaMass uniquement."""
        if data_type == "KoopaMass" and map_name != "Map06":
            linked_maps = self.get_linked_maps(map_name)
            current_data = self.event_data.get(map_name, {}).get(data_type, [])

            # Synchroniser les données sur les cartes liées
            for linked_map in linked_maps:
                if linked_map not in self.event_data:
                    self.event_data[linked_map] = {}
                self.event_data[linked_map][
                    data_type
                ] = current_data  # Synchroniser les données
            self.notify_listeners()

    def get_linked_maps(self, map_name):
        """Retourne les cartes liées pour un type spécifique de carte KoopaMass."""
        linked_maps = []
        if map_name.startswith("Map"):
            map_number = int(map_name[3:])
            if map_number != 6:
                linked_maps = [
                    f"Map{n:02d}" for n in range(1, 8) if n != 6 and n != map_number
                ]
        return linked_maps

    def notify_listeners(self):
        """Avertit toutes les interfaces liées que des données ont été mises à jour."""
        for listener in self.listeners:
            listener.update_event_listbox()


class EventEditor:
    def __init__(self, parent, data_type, map_name, app_width, event_data_manager):
        self.event_data_manager = event_data_manager
        self.rates_totals = {"Rate0": 0.0, "Rate1": 0.0, "Rate2": 0.0, "Rate3": 0.0}
        self.map_name = map_name.replace(" ", "_")
        self.data_type = data_type  # Type: LuckyMass, KoopaMass, UnluckyMass
        self.result_options = result_options.get(self.data_type, [])

        self.frame = ttk.Frame(parent)
        self.frame.pack(
            side="left",
            padx=(app_width * 0.05, app_width * 0.05 // 2),
            pady=10,
            fill="both",
            expand=True,
        )

        self.entries = {}
        self.create_ui(app_width)

        # Enregistrer ce gestionnaire d'interface (listener) pour la carte actuelle
        if data_type == "KoopaMass" and map_name != "Map06":
            event_data_manager.register_listener(self)

    def create_ui(self, app_width):
        """Crée l'interface utilisateur pour les événements."""
        # Configuration du cadre principal pour utiliser toute la largeur disponible
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(
            5, weight=1
        )  # La listbox doit s'étendre verticalement

        # Cadre pour les cumuls
        self.cumul_frame = ttk.LabelFrame(
            self.frame, text="Cumul Rates", width=app_width
        )
        self.cumul_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Labels pour afficher les cumuls de rates
        self.rate_labels = {}
        for i, rate in enumerate(["Rate0", "Rate1", "Rate2", "Rate3"]):
            label = ttk.Label(
                self.cumul_frame, text=f"{rate}: {self.rates_totals[rate]}"
            )
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            self.rate_labels[rate] = label

        entry_frame = ttk.LabelFrame(
            self.frame, text="Add Event Entry", width=app_width
        )
        entry_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        entry_frame.grid_columnconfigure(
            1, weight=1
        )  # Les entrées peuvent s'étendre horizontalement

        labels = ["Rate0", "Rate1", "Rate2", "Rate3"]
        self.entries = {}
        for i, label in enumerate(labels):
            ttk.Label(entry_frame, text=label).grid(
                row=i, column=0, padx=5, pady=5, sticky="w"
            )
            entry = tk.Spinbox(entry_frame, from_=0, to=999)
            entry.grid(
                row=i, column=1, padx=5, pady=5, sticky="ew"
            )  # Étendre horizontalement
            self.entries[label] = entry

        ttk.Label(entry_frame, text="Result").grid(
            row=4, column=0, padx=5, pady=5, sticky="w"
        )

        # Ajouter un contrôle pour vérifier si result_options contient des données valides pour le combobox
        if self.result_options:
            self.result_combobox = ttk.Combobox(
                entry_frame, values=self.result_options, width=15
            )
        else:
            self.result_combobox = ttk.Combobox(
                entry_frame, values=["No options available"], width=15
            )

        self.result_combobox.grid(
            row=4, column=1, padx=5, pady=5, sticky="ew"
        )  # Étendre horizontalement

        add_button = ttk.Button(
            self.frame, text="Add Entry", command=self.add_event_entry
        )
        add_button.grid(
            row=2, column=0, padx=10, pady=10, sticky="ew"
        )  # Étendre horizontalement

        # Listbox pour occuper l'espace restant et s'étendre
        self.listbox = tk.Listbox(self.frame, height=10, width=50)
        self.listbox.grid(
            row=3, column=0, padx=10, pady=10, sticky="nsew"
        )  # Étendre dans toutes les directions

        # Bouton "Remove Selected" également extensible horizontalement
        self.remove_button = ttk.Button(
            self.frame, text="Remove Selected", command=self.remove_event_entry
        )
        self.remove_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

    def load_event_data(self, data):
        """Charge les données d'événements depuis le gestionnaire."""
        self.event_data_manager.update_event_data(self.map_name, self.data_type, data)
        self.update_event_listbox()

    def update_event_listbox(self):
        """Met à jour la liste des événements dans le Listbox."""
        self.current_data = self.event_data_manager.get_event_data(
            self.map_name, self.data_type
        )
        self.listbox.delete(0, tk.END)

        # Recalculer les totaux des rates
        self.recalculate_totals()

        for entry in self.current_data:
            display_text = f"{entry['Result']:<25}\t | Rate0: {entry['Rate0']} Rate1: {entry['Rate1']} Rate2: {entry['Rate2']} Rate3: {entry['Rate3']}"
            self.listbox.insert(tk.END, display_text)

        # Mettre à jour les labels d'affichage des cumuls avec les couleurs
        for rate, total in self.rates_totals.items():
            color = "green" if total != 0 else "red"
            self.rate_labels[rate].config(text=f"{rate}: {total}", foreground=color)

        if (
            self.rates_totals["Rate0"] == 0
            or self.rates_totals["Rate1"] == 0
            or self.rates_totals["Rate2"] == 0
            or self.rates_totals["Rate3"] == 0
        ):
            self.event_data_manager.update_event_status(
                self.map_name, self.data_type, False
            )
        else:
            self.event_data_manager.update_event_status(
                self.map_name, self.data_type, True
            )

    def recalculate_totals(self):
        """Recalculer les totaux des rates à partir des entrées."""
        # Réinitialiser les totaux des rates
        self.rates_totals = {"Rate0": 0.0, "Rate1": 0.0, "Rate2": 0.0, "Rate3": 0.0}

        # Calculer les totaux des rates en fonction des entrées
        for entry in self.current_data:
            for rate in self.rates_totals:
                self.rates_totals[rate] += entry[rate]

    def add_event_entry(self):
        """Ajoute un événement aux données et synchronise les cartes liées si nécessaire."""
        try:
            rate0 = float(self.entries["Rate0"].get())
            rate1 = float(self.entries["Rate1"].get())
            rate2 = float(self.entries["Rate2"].get())
            rate3 = float(self.entries["Rate3"].get())
            result = self.result_combobox.get()
            new_entry = {
                "Rate0": rate0,
                "Rate1": rate1,
                "Rate2": rate2,
                "Rate3": rate3,
                "Result": result,
            }
            self.current_data.append(new_entry)

            # Mise à jour des événements pour la carte
            self.event_data_manager.update_event_data(
                self.map_name, self.data_type, self.current_data
            )

            # Synchronisation avec les cartes liées, uniquement si data_type est KoopaMass et carte modifiée est 1, 2, 3, 4, 5 ou 7
            self.event_data_manager.sync_with_linked_maps(self.map_name, self.data_type)

            # Recalculer les totaux et mettre à jour l'affichage
            self.recalculate_totals()
            self.update_event_listbox()

        except ValueError as e:
            print(f"Error: {e}")

    def remove_event_entry(self):
        """Supprime l'événement sélectionné dans la liste."""
        try:
            selected_index = self.listbox.curselection()[0]
            self.current_data.pop(selected_index)
            # Mise à jour des événements après suppression et synchronisation avec les cartes liées
            self.event_data_manager.update_event_data(
                self.map_name, self.data_type, self.current_data
            )
            self.event_data_manager.sync_with_linked_maps(self.map_name, self.data_type)

            # Recalculer les totaux et mettre à jour l'affichage
            self.recalculate_totals()
            self.update_event_listbox()

        except IndexError:
            print("No item selected for removal.")


# Fonctions pour traiter les données, charger et sauvegarder


def process_event_data(event_data):
    """
    Traite les données des événements pour s'assurer que chaque entrée a les clés nécessaires
    et les valeurs dans le bon format.
    """
    results = []
    for entry in event_data:
        if all(key in entry for key in ["Rate0", "Rate1", "Rate2", "Rate3", "Result"]):
            results.append(entry)
        else:
            continue
    return results


def load_event_mapdata(base_path, map_name, data_type):
    """
    Charge les fichiers JSON pour les événements associés à une carte et un type spécifique.
    """
    event_data = {}
    raw_event_data = []
    if data_type == "KoopaMass" and map_name != "Map06":
        map_name = "Map00"
    file_name = os.path.join(
        "bd~bd00.nx", "bd", "bd00", "data", f"bd00_{data_type}_{map_name}.json"
    )
    file_path = os.path.join(base_path, file_name)

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            raw_event_data = data.get(map_name, [])
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error occurred while reading file: {file_name}")

    # Charger les données pour les événements
    event_data = process_event_data(raw_event_data)
    return event_data


def save_event_mapdata(base_path, event_data, map_name, data_type):
    """
    Sauvegarde les données des événements dans le fichier JSON.
    """
    if data_type == "KoopaMass" and map_name != "Map06":
        map_name = "Map00"
    file_name = os.path.join(
        "bd~bd00.nx", "bd", "bd00", "data", f"bd00_{data_type}_{map_name}.json"
    )
    file_path = os.path.join(base_path, file_name)
    with open(file_path, "w", encoding="utf-8-sig") as f:
        file_data = {map_name: event_data}
        json.dump(file_data, f, indent=4)
