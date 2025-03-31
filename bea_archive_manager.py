import os
import shutil
import time
from pywinauto import Application

def search_in_treeview(treeview, item_name):
    # Liste les enfants du contrôle
    children = treeview.children()

    for child in children:
        # Vérifie si l'élément est un TreeItem et si son nom correspond
        if child.element_info.control_type == "TreeItem" and child.element_info.name == item_name:
            print(f"Trouvé l'élément : {item_name}")
            return child  # Retourne l'objet TreeItem trouvé

        # Si l'élément est un CheckBox contenant d'autres éléments, exploration récursive
        if child.element_info.control_type == "CheckBox":
            found_item = search_in_treeview(child, item_name)
            if found_item:
                return found_item

    return None  # Retourne None si l'élément n'est pas trouvé

def bea_archives_extractor(BASE_PATH, bea_archives):
    CORE_DIR = os.path.join(BASE_PATH, "CORE")
    ROMFS_DIR = os.path.join(BASE_PATH, "ROMFS", "Archive")
    
    # Connexion à Switch Toolbox (si son chemin est connu)
    app = Application(backend="uia").start(os.path.join(BASE_PATH,"Switch Toolbox","Toolbox.exe"))
    # Attendre que la fenêtre principale s'ouvre
    app.window(title_re="Toolbox.*").wait("ready", timeout=10)

    # Récupérer la fenêtre principale (le titre changeant, on utilise une regex)
    window = app.window(title_re="Toolbox.*")
    window_exist = False
    while (window_exist == False):
        if window.exists():
            window_exist = True
            window.set_focus()

    # Boucle pour ouvrir les fichiers un par un
    for file in bea_archives:
        # Saisir le chemin du fichier dans la zone de texte (Edit)
        os.makedirs(os.path.join(CORE_DIR, file), exist_ok=True)
        dialog_exist = False
        while (dialog_exist == False):
            # Ouvrir la boîte de dialogue d'ouverture de fichier (Ctrl + O)
            window.type_keys("^o")
            # Générer le chemin complet du fichier
            file_path = os.path.join(ROMFS_DIR, file) + ".bea"
            # Trouver la fenêtre de dialogue d'ouverture de fichier via la fenêtre enfant de 'window'
            dialog = window.child_window(control_type="Window", found_index=0)  # On prend le premier contrôle de type "Window" de la fenêtre enfant
            if dialog.exists():
                combo_box = dialog.child_window(auto_id="1148", control_type="ComboBox")
                # Cibler l'Edit à l'intérieur du ComboBox
                edit_control = combo_box.child_window(control_type="Edit")
            
                # Saisir le chemin du fichier dans la zone de texte (Edit)
                edit_control.set_text(file_path)

                # Trouver et cliquer sur le bouton "Open"
                open_button = dialog.child_window(auto_id="1", control_type="Button")
                open_button.click()
                dialog_exist = True
        time.sleep(2)
        window.type_keys("^b")  # Ouvrir la boîte de dialogue de sélection de dossier
        time.sleep(2)

        # Liste toutes les fenêtres ouvertes de l'application
        windows = app.windows()

        # Cherche une fenêtre contenant un ComboBox ou un Edit (zone de texte)
        folder_dialog = None
        for w in windows:
            try:
                if w.child_window(control_type="ComboBox").exists() or w.child_window(control_type="Edit").exists():
                    folder_dialog = w
                    print(f"✅ Boîte de dialogue détectée : {w.window_text()}")
                    break  # On prend la première fenêtre trouvée
            except Exception as e:
                print(f"Erreur en accédant à l'élément : {e}")
                continue  # Si l'élément n'existe pas ou une erreur se produit, on continue à chercher

        if folder_dialog:
            folder_dialog.print_control_identifiers()  # Liste les éléments cliquables pour vérifier
            # Cibler l'Edit à l'intérieur du ComboBox
            combo_box = folder_dialog.child_window(control_type="ComboBox")
            edit_control = combo_box.child_window(control_type="Edit")
            # Saisir le chemin du dossier
            edit_control.set_text(os.path.join(CORE_DIR, file))

            # Trouver et cliquer sur le bouton "OK" ou "Select Folder"
            ok_button = folder_dialog.child_window(control_type="Button", title="OK")  # Ajuste si nécessaire
            ok_button.click()
            print(f"✅ Dossier sélectionné : {os.path.join(CORE_DIR, file)}")
        else:
            print("❌ Boîte de dialogue non trouvée !")

        time.sleep(2)
        file_dialog = window.child_window(control_type="Window", found_index=0)  # On prend le premier contrôle de type "Window" de la fenêtre enfant
        file_dialog_exist = False
        while (file_dialog_exist == False):
            if file_dialog.exists():
                input(file_dialog.print_control_identifiers())
                combo_box = file_dialog.child_window(auto_id="1148", control_type="ComboBox")
                # Cibler l'Edit à l'intérieur du ComboBox
                file_edit_control = combo_box.child_window(control_type="Edit")
                file_edit_control.set_text(os.path.join(CORE_DIR, file))

                # Trouver et cliquer sur le bouton "Open"
                file_open_button = file_dialog.child_window(auto_id="1", control_type="Button")
                file_open_button.click()
                file_dialog_exist = True

def bea_archives_repacker(instructions, BASE_PATH, OUTPUT_DIR):
    ROMFS_DIR = os.path.join(BASE_PATH, "ROMFS")
    # Connexion à Switch Toolbox (si son chemin est connu)
    app = Application(backend="uia").start(os.path.join(BASE_PATH,"Switch Toolbox","Toolbox.exe"))
    # Attendre que la fenêtre principale s'ouvre
    app.window(title_re="Toolbox.*").wait("ready", timeout=10)

    # Récupérer la fenêtre principale (le titre changeant, on utilise une regex)
    window = app.window(title_re="Toolbox.*")
    window_exist = False
    while (window_exist == False):
        if window.exists():
            window_exist = True
            window.set_focus()


    for file in instructions.keys():
        # Créer les dossiers nécessaires dans le chemin de destination
        os.makedirs(os.path.join(OUTPUT_DIR,"romfs","Archive"), exist_ok=True)
        # Copier le fichier
        shutil.copy(f"{os.path.join(ROMFS_DIR,'Archive',file)}.bea", f"{os.path.join(OUTPUT_DIR,'romfs','Archive',file)}.bea")

    # Boucle pour ouvrir les fichiers un par un
    for file in instructions.keys():
        # Ouvrir la boîte de dialogue d'ouverture de fichier (Ctrl + O)
        window.type_keys("^o")
        # Générer le chemin complet du fichier
        file_path = os.path.join(OUTPUT_DIR, "romfs", "Archive", file) + ".bea"
        # Trouver la fenêtre de dialogue d'ouverture de fichier via la fenêtre enfant de 'window'
        dialog = window.child_window(control_type="Window", found_index=0)  # On prend le premier contrôle de type "Window" de la fenêtre enfant
        dialog_exist = False
        while (dialog_exist == False):
            if dialog.exists():
                combo_box = dialog.child_window(auto_id="1148", control_type="ComboBox")
                # Cibler l'Edit à l'intérieur du ComboBox
                edit_control = combo_box.child_window(control_type="Edit")
            
                # Saisir le chemin du fichier dans la zone de texte (Edit)
                edit_control.set_text(file_path)

                # Trouver et cliquer sur le bouton "Open"
                open_button = dialog.child_window(auto_id="1", control_type="Button")
                open_button.click()
                dialog_exist = True
        window.type_keys("^p")
        tree_view = window.child_window(control_type="Tree", found_index=0)
        for files_instruction in instructions[file]:
            try:
                fichier = search_in_treeview(tree_view, files_instruction["destination"])
                if fichier != None:
                    fichier.select()
                    window.type_keys("^b")
                    file_dialog = window.child_window(control_type="Window", found_index=0)  # On prend le premier contrôle de type "Window" de la fenêtre enfant
                    file_dialog_exist = False
                    while (file_dialog_exist == False):
                        if dialog.exists():
                            combo_box = file_dialog.child_window(auto_id="1148", control_type="ComboBox")
                            # Cibler l'Edit à l'intérieur du ComboBox
                            edit_control = combo_box.child_window(control_type="Edit")
                        
                            # Saisir le chemin du fichier dans la zone de texte (Edit)
                            edit_control.set_text(files_instruction["source"])

                            # Trouver et cliquer sur le bouton "Open"
                            open_button = file_dialog.child_window(auto_id="1", control_type="Button")
                            open_button.click()
                            file_dialog_exist = True
            except Exception as e:
                continue
        window.type_keys("^q")
