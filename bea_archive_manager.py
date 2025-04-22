import os
import shutil
import time
from tqdm import tqdm
from pywinauto import Application, findwindows
from pywinauto.keyboard import send_keys
from tkinter import messagebox
def search_in_treeview(treeview, item_name):
    # Liste les enfants du contrôle
    children = treeview.children()

    for child in children:
        # Vérifie si l'élément est un TreeItem et si son nom correspond
        if child.element_info.control_type == "TreeItem" and child.element_info.name == item_name:
            return child  # Retourne l'objet TreeItem trouvé

        # Si l'élément est un CheckBox contenant d'autres éléments, exploration récursive
        if child.element_info.control_type == "CheckBox":
            found_item = search_in_treeview(child, item_name)
            if found_item:
                return found_item

    return None  # Retourne None si l'élément n'est pas trouvé

def bea_archives_extractor(base_path, bea_files):
    switch_toolbox_path = os.path.join(base_path, "Switch Toolbox", "Toolbox.exe")

    # Ouvrir Switch Toolbox une seule fois
    app = Application(backend="uia").start(switch_toolbox_path)
    main_win = app.window(title_re=".*Toolbox.*")
    main_win.wait("visible", timeout=10)
    main_win.set_focus()

    # Utiliser tqdm pour la progression
    for bea_file in tqdm(bea_files, desc="Traitement des fichiers BEA", unit="fichier"):
        full_bea_path = os.path.join(base_path, "ROMFS", "Archive", f"{bea_file}.bea")

        if not os.path.exists(full_bea_path):
            return 1

        # Attente de la boîte de dialogue "Open"
        open_dialog = None
        timeout = 10
        start_time = time.time()

        while time.time() - start_time < timeout and open_dialog is None:
            # Ouvrir le fichier via Ctrl+O
            send_keys("^o")
            try:
                handles = findwindows.find_windows(class_name="#32770")
                if handles:
                    for handle_select in handles:
                        try:
                            # Initialiser l'application avant d'utiliser le handle
                            app = Application(backend="uia").connect(handle=handle_select)
                            open_dialog = app.window(handle=handle_select)
                            
                            # Attendre que la fenêtre soit visible et prête
                            open_dialog.wait("visible", timeout=5)
                            
                            # Si la fenêtre 'Open' est trouvée, on arrête la boucle
                            if "Open" in open_dialog.window_text():
                                break
                        except Exception as e:
                            continue
            except Exception:
                pass

        if not open_dialog:
            return 2

        # Remplir le champ fichier et cliquer sur Ouvrir
        open_dialog.set_focus()
        file_input = open_dialog.child_window(auto_id="1148", control_type="ComboBox").child_window(control_type="Edit")
        file_input.set_text(full_bea_path)

        open_button = open_dialog.child_window(auto_id="1", control_type="Button")
        open_button.click()

        time.sleep(2)  # attendre que le BEA s'ouvre
        send_keys("^b")  # Extraction via Ctrl+B

        # Attente de la boîte de dialogue "Select Folder"
        select_folder_dialog = None
        timeout = 30
        start_time = time.time()

        while time.time() - start_time < timeout and select_folder_dialog is None:
            try:
                # Chercher toutes les fenêtres de type "#32770"
                handles = findwindows.find_windows(class_name="#32770")
                if handles:
                    for handle_select in handles:
                        try:
                            app = Application(backend="uia").connect(handle=handle_select)
                            select_folder_dialog = app.window(handle=handle_select)
                            select_folder_dialog.wait("visible", timeout=5)
                            if "Select Folder" in select_folder_dialog.window_text():
                                break
                        except Exception:
                            continue
            except Exception:
                pass

        if not select_folder_dialog:
            return 2

        # Choisir le dossier de sortie
        output_dir = os.path.join(base_path, "CORE", bea_file)
        select_folder_dialog.set_focus()

        folder_input = select_folder_dialog.child_window(control_type="Edit", found_index=0)  # Utilisation de 'found_index' pour spécifier le bon champ
        ok_button = select_folder_dialog.child_window(auto_id="1", control_type="Button")
        if folder_input and ok_button:
            folder_input.set_text(output_dir)
            ok_button.click()
    # Optionnel : fermer Switch Toolbox après le traitement de tous les fichiers BEA
    try:
        main_win.kill()
    except Exception:
        pass  # Si impossible de fermer, on continue sans afficher de message
    return 0

def bea_archives_repacker(instructions, BASE_PATH, OUTPUT_DIR):
    ROMFS_DIR = os.path.join(BASE_PATH, "ROMFS")
    os.makedirs(os.path.join(OUTPUT_DIR, "romfs", "Archive"), exist_ok=True)

    # Confirmation message before starting the process
    proceed = messagebox.askyesno(
        "BEA Repacker (Confirmation)",
        "The BEA Repacker will launch Switch Toolbox and allow SMPJ Map Editor to control the window.\nPlease do not touch anything during the process.\nSMPJ Map Editor's terminal output will show you the progress.\n\nDo you want to continue?"
    )
    if not proceed:
        print("Operation cancelled by the user.")
        return 1  # Code 1: User cancelled the operation

    print("Copying BEA files to the output directory...")
    for file in tqdm(instructions.keys(), desc="Copying files", unit="file"):
        shutil.copy(f"{os.path.join(ROMFS_DIR, 'Archive', file)}.bea", f"{os.path.join(OUTPUT_DIR, 'romfs', 'Archive', file)}.bea")

    print("Launching Switch Toolbox...")
    app = Application(backend="uia").start(os.path.join(BASE_PATH, "Switch Toolbox", "Toolbox.exe"))
    window = app.window(title_re="Toolbox.*")
    window.wait("ready", timeout=10)
    while not window.exists():
        continue
    window.set_focus()

    print("Opening and modifying BEA files...")
    for file in tqdm(instructions.keys(), desc="Modifying BEA files", unit="file"):
        window.type_keys("^o")
        dialog = window.child_window(control_type="Window", found_index=0)
        while not dialog.exists():
            continue
        combo_box = dialog.child_window(auto_id="1148", control_type="ComboBox")
        edit_control = combo_box.child_window(control_type="Edit")
        open_button = dialog.child_window(auto_id="1", control_type="Button")
        if edit_control and open_button:
            edit_control.set_text(os.path.join(OUTPUT_DIR, "romfs", "Archive", file) + ".bea")
            open_button.click()
        else:
            raise RuntimeError("Edit control or Open button not found in file dialog (UI Not Found)")

        window.type_keys("^p")
        tree_view = window.child_window(control_type="Tree", found_index=0)
        for files_instruction in tqdm(instructions[file], desc=f"Replacing files in {file}.bea", unit="file"):
            try:
                fichier = search_in_treeview(tree_view, files_instruction["destination"])
                if fichier:
                    fichier.select()
                    window.type_keys("^b")
                    file_dialog = window.child_window(control_type="Window", found_index=0)
                    while not file_dialog.exists():
                        continue
                    combo_box = file_dialog.child_window(auto_id="1148", control_type="ComboBox")
                    edit_file_control = combo_box.child_window(control_type="Edit")
                    open_file_button = file_dialog.child_window(auto_id="1", control_type="Button")
                    if edit_file_control and open_file_button:
                        edit_file_control.set_text(files_instruction["source"])
                        open_file_button.click()
                    else:
                        raise RuntimeError("Edit control or Open button not found in file dialog (UI Not Found)")
                        
            except Exception as e:
                messagebox.showerror("Error", f"Error during replacement: {str(e)}")
                print(f"Error during replacement: {e}")
                return 2  # Code 2: Replacement error

    print("Saving modifications...")
    window.type_keys("^s")
    for file in tqdm(instructions.keys(), desc="Saving files", unit="file"):
        save_dialog = window.child_window(control_type="Window", found_index=0)
        while not save_dialog.exists():
            continue
        buttons = save_dialog.children(control_type="Button")
        for btn in buttons:
            button_text = btn.texts()
            if button_text and button_text[0] == "OK":
                btn.click()
                break
    app.kill()
    return 0  # Code 0: Success
