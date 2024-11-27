import tkinter as tk
from tkinter import ttk
import json
import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Dictionnaire de couleurs associées à chaque type de MassAttr
mass_attr_colors = {
    "Item": "forestgreen",
    "Happening": "green",
    "Chance": "gold",
    "Plus": "blue",
    "Minus": "red",
    "Lucky": "cyan",
    "Unlucky": "crimson",
    "VS": "midnightblue",
    "Koopa": "black",
    "SpotTeresa": "silver",
    "SpotItemShopNokonoko": "darkred",
    "SpotItemShopKameck": "darkred",
    "SpotBranch": "gray",
    "SpotEvent": "indigo",
    "SpotBranchKey": "yellow"
}

mass_attr_list = [
    "Item", "Chance", "Plus", "Minus", "Lucky", "Unlucky", "VS", "Koopa"
    # "SpotItemShopNokonoko", "SpotItemShopKameck", "SpotBranch", "SpotEvent", "SpotBranchKey", "SpotTeresa"
]

class MapLayoutEditor:
    def __init__(self, parent, map_name, workspace_path, reverse_x=False, reverse_y=False, initial_zoom=None, initial_position=None):
        self.frame = ttk.Frame(parent)
        self.frame.pack(side="left", padx=5, pady=5, fill="both", expand=True)
        self.info_label = ttk.Label(self.frame, text="Zoom: (xlim, ylim) | Center: (x, y)")
        self.info_label.pack(side="bottom", fill="x", padx=5, pady=5)

        # Initialiser les variables
        self.map_name = map_name
        self.map_index = int(map_name.replace("Map", ""))
        self.workspace_path = workspace_path
        self.reverse_x = reverse_x
        self.reverse_y = reverse_y
        self.map_layout_data = {}  # Stocker les données brutes

        # Variables pour stocker l'état avant modification
        self.prev_zoom = None
        self.prev_center = None
        
        legend_frame = ttk.Frame(self.frame)
        legend_frame.pack(side="right", padx=5, pady=5, fill="y")
        
        ttk.Label(legend_frame, text="Map Key").pack()

        for mass_attr, color in mass_attr_colors.items():
            # Créer un label pour chaque type de MassAttr
            color_box = tk.Canvas(legend_frame, width=20, height=20, bg=color)
            color_box.pack(side="top", padx=2, pady=2)
            label = ttk.Label(legend_frame, text=mass_attr)
            label.pack(side="top", padx=2, pady=2)

        # Initialiser Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(100, 200))
        self.fig.set_size_inches(self.frame.winfo_width(), self.frame.winfo_height())
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

        # Ajouter un contour autour de la zone de la carte
        self.canvas_widget.config(bd=3, relief="solid", highlightbackground="black")

        # Activer le mode interactif (pour zoom et pan sans la barre d'outils)
        self.canvas.draw_idle()

        # Associer la fermeture de l'application à une méthode propre
        self.root = self.get_root(parent)  # Récupérer l'objet Tk
        self.root.protocol("WM_DELETE_WINDOW", self.quit_application)
        
        self.prev_zoom = self.get_zoom()  # Zoom initial basé sur les limites actuelles
        self.prev_center = self.get_center()

        # Appliquer le zoom et la position initiale
        if initial_zoom:
            self.set_zoom(*initial_zoom)
        if initial_position:
            self.set_position(*initial_position)

        # Activer le zoom par molette
        self.cid_zoom = self.fig.canvas.mpl_connect("scroll_event", self.on_zoom)

        # Ajouter des événements pour les clics sur les nœuds et les flèches
        self.cid_click = self.fig.canvas.mpl_connect("button_press_event", self.on_click)

        # Capturer les événements de clavier pour déplacer la carte
        self.canvas_widget.bind("<Left>", lambda event: self.move_map(dx=-0.5))
        self.canvas_widget.bind("<Right>", lambda event: self.move_map(dx=0.5))
        self.canvas_widget.bind("<Up>", lambda event: self.move_map(dy=0.5))
        self.canvas_widget.bind("<Down>", lambda event: self.move_map(dy=-0.5))
        

    def move_map(self, dx=0, dy=0):
        """Déplacer la carte (modifie les limites de la vue)."""
        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        new_xlim = (xlim[0] + dx, xlim[1] + dx)
        new_ylim = (ylim[0] + dy, ylim[1] + dy)
        self.set_zoom(new_xlim, new_ylim)

        # Mettre à jour l'info
        self.update_info_label()

    def update_info_label(self):
        """Mettre à jour l'affichage de l'état du zoom et du centre."""
        zoom = self.get_zoom()
        center = self.get_center()
        self.info_label.config(
            text=f"Zoom: ({zoom[0][0]:.2f}, {zoom[1][0]:.2f}) | Center: ({center[0]:.2f}, {center[1]:.2f})\t\t Use Arrow Keys to Move Map (Up Left Down Right), and Scroll for Zoom/Dezoom"
        )

    def on_zoom(self, event):
        """Gestion du zoom."""
        scale_factor = 1.1 if event.button == "down" else 0.9
        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        new_xlim = (xlim[0] * scale_factor, xlim[1] * scale_factor)
        new_ylim = (ylim[0] * scale_factor, ylim[1] * scale_factor)
        self.set_zoom(new_xlim, new_ylim)

        # Mettre à jour l'info
        self.update_info_label()

    def set_zoom(self, xlim, ylim):
        """Définir le niveau de zoom."""
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.fig.canvas.draw()

        # Mettre à jour l'info
        self.update_info_label()
        
    def create_legend(self):
        legend_frame = ttk.Frame(self.frame)
        legend_frame.pack(side="right", padx=5, pady=5, fill="y")
        
        ttk.Label(legend_frame, text="Map Key").pack()

        for mass_attr, color in mass_attr_colors.items():
            # Créer un label pour chaque type de MassAttr
            color_box = tk.Canvas(legend_frame, width=20, height=20, bg=color)
            color_box.pack(side="top", padx=2, pady=2)
            label = ttk.Label(legend_frame, text=mass_attr)
            label.pack(side="top", padx=2, pady=2)

    def draw_map(self):
        """Dessine la carte en utilisant les données de nœuds et de chemins."""
        self.ax.clear()

        # Couleur par défaut pour les nœuds inconnus ou ayant un MassAttr vide
        default_color = "gray"

        # Dictionnaires pour stocker les informations des nœuds et flèches
        node_positions = {}
        self.node_patches = {}
        self.arrow_patches = []

        # Calculer les positions des nœuds à partir des chemins
        for path in self.map_layout_data["MapPath"]:
            node_no = path["NodeNo"]
            for segment in path["Path"]:
                target_node = segment["NodeNo"]
                # Vérifier la présence des données "Bezier"
                if "Bezier" not in segment or not segment["Bezier"]:
                    continue

                bezier = segment["Bezier"][0]
                start_pos = (bezier["Position0X"] * 0.5, bezier["Position0Z"] * 0.5)
                end_pos = (bezier["Position1X"] * 0.5, bezier["Position1Z"] * 0.5)

                if node_no not in node_positions:
                    x, y = start_pos
                    node_positions[node_no] = (
                        -x if self.reverse_x else x,  # Inverser X si reverse_x est True
                        -y if self.reverse_y else y   # Inverser Y si reverse_y est True
                    )

                if target_node not in node_positions:
                    x, y = end_pos
                    node_positions[target_node] = (
                        -x if self.reverse_x else x,  # Inverser X si reverse_x est True
                        -y if self.reverse_y else y   # Inverser Y si reverse_y est True
                    )

        # Dessiner les chemins (flèches)
        for path in self.map_layout_data["MapPath"]:
            node_no = path["NodeNo"]
            for segment in path["Path"]:
                target_node = segment["NodeNo"]
                # Ignorer si les positions ne sont pas disponibles
                if node_no not in node_positions or target_node not in node_positions:
                    continue

                x1, y1 = node_positions[node_no]
                x2, y2 = node_positions[target_node]

                # Ajouter une flèche reliant les deux nœuds
                arrow_patch = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="->",mutation_scale=15,color="black",
            )
                self.arrow_patches.append(arrow_patch)
                self.ax.add_patch(arrow_patch)

        # Dessiner les nœuds
        for node_data in self.map_layout_data["MapNode"]:
            node_no = node_data["NodeNo"]
            mass_attr = node_data["MassAttr"]
            node_color = mass_attr_colors.get(mass_attr, default_color)

            # Vérifier si la position du nœud est connue
            if node_no not in node_positions:
                continue
            x, y = node_positions[node_no]

            # Dessiner le nœud
            node_patch = self.ax.add_patch(Circle((x, y), 0.3 if mass_attr else 0.1, color=node_color, alpha=0.7))
            self.node_patches[node_no] = node_patch
        
        x_positions = [x for x, y in node_positions.values()]
        y_positions = [y for x, y in node_positions.values()]      

        # Marge supplémentaire autour des nœuds
        x_margin = 0.5  # Augmenter cette valeur pour plus de marge
        y_margin = 0.5  # Augmenter cette valeur pour plus de marge

        # Trouver les coordonnées minimales et maximales des nœuds
        x_min, x_max = min(x_positions), max(x_positions)
        y_min, y_max = min(y_positions), max(y_positions)

        # Définir les nouvelles limites pour que la carte occupe plus d'espace
        new_xlim = (x_min - x_margin, x_max + x_margin)
        new_ylim = (y_min - y_margin, y_max + y_margin)

        # Redimensionner la figure (changez ici les dimensions souhaitées)
        self.fig.set_size_inches(13, 16)  # Définir la taille de la figure (en pouces)
        self.fig.tight_layout()  # Ajuste l'espacement des éléments

        # Mettre à jour les limites de la vue
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        # Mettre à jour l'info
        self.update_info_label()

        # Autres ajustements pour les objets de la carte
        self.ax.autoscale_view()
        self.ax.axis('off')

        # Redessiner la carte
        self.canvas.draw()
        
    def get_center(self):
        """Retourne le centre de la vue actuelle (coordonnées moyennes)."""
        x_center = (self.ax.get_xlim()[0] + self.ax.get_xlim()[1]) / 2
        y_center = (self.ax.get_ylim()[0] + self.ax.get_ylim()[1]) / 2
        return (x_center, y_center)

    def get_zoom(self):
        """Retourne le niveau de zoom actuel (limites de l'axe)."""
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        return (xlim, ylim)

    def quit_application(self):
        """Gestionnaire pour fermer proprement l'application."""
        plt.close(self.fig)  # Fermer la figure Matplotlib
        self.frame.master.quit()  # Fermer la fenêtre principale Tkinter
        
    def set_position(self, x, y):
        """Définir la position du centre de la vue."""
        xlim, ylim = self.ax.get_xlim(), self.ax.get_ylim()
        x_range = (xlim[1] - xlim[0]) / 2
        y_range = (ylim[1] - ylim[0]) / 2
        new_xlim = (x - x_range, x + x_range)
        new_ylim = (y - y_range, y + y_range)
        self.set_zoom(new_xlim, new_ylim)

    def on_click(self, event):
        """Gestion des clics sur les nœuds et les flèches."""
        if event.inaxes != self.ax:
            return

        # Enregistrer l'état actuel avant modification
        self.prev_zoom = self.get_zoom()
        self.prev_center = self.get_center()
        # Vérification du clic sur un nœud
        for node_no, node_patch in self.node_patches.items():
            if node_patch.contains(event)[0]:
                for node_data in self.map_layout_data["MapNode"]:
                    if int(node_data["NodeNo"]) == int(node_no):
                        mass_attr = node_data["MassAttr"]
                        # Vérifier si le MassAttr du nœud est dans la liste des MassAttr modifiables
                        if mass_attr in mass_attr_list:
                            new_mass_attr = self.get_next_mass_attr(mass_attr)  # Obtenez la valeur suivante pour MassAttr
                            node_data["MassAttr"] = new_mass_attr  # Modifier la valeur dans les données
                            self.draw_map() # Redessiner la carte après modification
                            break

        # Restaurer l'état du zoom et de la position
        if self.prev_zoom and self.prev_center:
            self.set_zoom(self.prev_zoom[0], self.prev_zoom[1])
            self.set_position(self.prev_center[0], self.prev_center[1])
        return
        
    def get_next_mass_attr(self, current_mass_attr):
        """Retourner la prochaine valeur MassAttr à appliquer."""
        mass_attr_types = mass_attr_list  # Liste de tous les types possibles
        current_index = mass_attr_types.index(current_mass_attr)
        next_index = (current_index + 1) % len(mass_attr_types)  # Obtenir l'index suivant (avec boucle)
        return mass_attr_types[next_index]

    def get_root(self, parent):
        """Obtenir la racine Tkinter."""
        while parent:
            if isinstance(parent, tk.Tk):  # Rechercher la fenêtre principale Tk
                return parent

            # Vérification de la racine via winfo_toplevel
            top_level = parent.winfo_toplevel()
            if isinstance(top_level, tk.Tk):
                return top_level

            # Vérifier ce que retourne winfo_parent()
            parent_winfo = parent.winfo_parent()
            if isinstance(parent_winfo, tk.Widget):
                parent = parent_winfo  # Aller au parent supérieur
            elif isinstance(parent_winfo, str) and parent_winfo == "":  # Fin du parcours
                break
            else:
                break

        raise ValueError("Aucun parent de type Tk trouvé.")
    
    def load_data(self,map_layout_data):
        self.map_layout_data = map_layout_data
        self.draw_map()
        
    def save_data(self):
        return self.map_layout_data
        
def get_file_path(file_type, workspace_path, map_name):
    """Retourne le chemin du fichier en fonction du type (MapNode ou MapPath)."""
    map_index = int(map_name.replace("Map", ""))
    file_name = f"bd{map_index:02d}_{file_type}.json"
    base_path = os.path.join(
        workspace_path,
        f"bd~bd{map_index:02d}.nx",
        "bd",
        f"bd{map_index:02d}",
        "data",
    )
    return os.path.join(base_path, file_name)

def load_map_layout_mapdata(workspace_path,map_name):
    """Charge les données des nœuds et chemins depuis les fichiers JSON."""
    file_path_nodes = get_file_path("MapNode",workspace_path,map_name)
    file_path_path = get_file_path("MapPath",workspace_path,map_name)

    try:
        with open(file_path_nodes, "r", encoding="utf-8-sig") as file:
            data_nodes = json.load(file)
        with open(file_path_path, "r", encoding="utf-8-sig") as file:
            data_path = json.load(file)

        map_layout_data = {
            "MapNode":data_nodes["MapNode"],
            "MapPath":data_path["MapPath"]
        }
        return map_layout_data
    except FileNotFoundError as e:
        print(f"Error occurred while reading file : {e}")
    return {"MapNode":[],"MapPath":[]}
    
            
def save_map_layout_mapdata(workspace_path,map_name,map_layout_data):
    """Sauvegarde les données des nœuds et chemins dans des fichiers JSON."""
    file_path_nodes = get_file_path("MapNode",workspace_path,map_name)
    file_path_path = get_file_path("MapPath",workspace_path,map_name)

    # Créer un dictionnaire avec les données de la carte
    data_nodes = {"MapNode": map_layout_data["MapNode"]}
    data_path = {"MapPath": map_layout_data["MapPath"]}

    try:
        # Sauvegarder les données des nœuds dans le fichier JSON
        with open(file_path_nodes, "w", encoding="utf-8-sig") as file:
            json.dump(data_nodes, file, ensure_ascii=False, indent=4)

        # Sauvegarder les données des chemins dans le fichier JSON
        with open(file_path_path, "w", encoding="utf-8-sig") as file:
            json.dump(data_path, file, ensure_ascii=False, indent=4)
            
    except FileNotFoundError as e:
        print(f"Error occurred while writing file : {e}")
