import os
import shutil
import time
from tqdm import tqdm
from pywinauto import Application
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

def bea_archives_extractor(BASE_PATH, bea_archives):
    CORE_DIR = os.path.join(BASE_PATH, "CORE")
    ROMFS_DIR = os.path.join(BASE_PATH, "ROMFS", "Archive")

    print("Lancement de Switch Toolbox...")
    app = Application(backend="uia").start(os.path.join(BASE_PATH, "Switch Toolbox", "Toolbox.exe"))
    window = app.window(title_re="Toolbox.*")
    window.wait("ready", timeout=10)
    while not window.exists():
        time.sleep(1)
    window.set_focus()

    for file in tqdm(bea_archives, desc="Extraction des archives BEA", unit="fichier"):
        os.makedirs(os.path.join(CORE_DIR, file), exist_ok=True)
        dialog_exist = False
        while not dialog_exist:
            window.type_keys("^o")
            file_path = os.path.join(ROMFS_DIR, file) + ".bea"
            dialog = window.child_window(control_type="Window", found_index=0)
            if dialog.exists():
                combo_box = dialog.child_window(auto_id="1148", control_type="ComboBox")
                edit_control = combo_box.child_window(control_type="Edit")
                edit_control.set_text(file_path)
                time.sleep(1)
                open_button = dialog.child_window(auto_id="1", control_type="Button")
                open_button.click()
                dialog_exist = True
        time.sleep(2)
        window.type_keys("^b")
        time.sleep(2)

        folder_dialog = None
        for w in app.windows():
            try:
                if w.child_window(control_type="ComboBox").exists() or w.child_window(control_type="Edit").exists():
                    folder_dialog = w
                    break
            except:
                continue

        if folder_dialog:
            combo_box = folder_dialog.child_window(control_type="ComboBox")
            edit_control = combo_box.child_window(control_type="Edit")
            edit_control.set_text(os.path.join(CORE_DIR, file))
            ok_button = folder_dialog.child_window(control_type="Button", title="OK")
            ok_button.click()

        time.sleep(2)
        file_dialog = window.child_window(control_type="Window", found_index=0)
        while not file_dialog.exists():
            time.sleep(1)
        combo_box = file_dialog.child_window(auto_id="1148", control_type="ComboBox")
        file_edit_control = combo_box.child_window(control_type="Edit")
        file_edit_control.set_text(os.path.join(CORE_DIR, file))
        time.sleep(1)
        file_open_button = file_dialog.child_window(auto_id="1", control_type="Button")
        file_open_button.click()

import os
import shutil
import time
from tqdm import tqdm
from pywinauto.application import Application
from tkinter import messagebox

def bea_archives_repacker(instructions, BASE_PATH, OUTPUT_DIR):
    ROMFS_DIR = os.path.join(BASE_PATH, "ROMFS")
    os.makedirs(os.path.join(OUTPUT_DIR, "romfs", "Archive"), exist_ok=True)

    # Confirmation message before starting the process
    proceed = messagebox.askyesno(
        "BEA Repacker (Confirmation)",
        "The BEA Repacker will launch Switch Toolbox and allow SMPJ Map Editor to control the window.\nPlease do not touch the screen during the process.\nSMPJ Map Editor's terminal output will show you the progress.\n\nDo you want to continue?"
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
        time.sleep(1)
    window.set_focus()

    print("Opening and modifying BEA files...")
    for file in tqdm(instructions.keys(), desc="Modifying BEA files", unit="file"):
        window.type_keys("^o")
        file_path = os.path.join(OUTPUT_DIR, "romfs", "Archive", file) + ".bea"
        dialog = window.child_window(control_type="Window", found_index=0)
        while not dialog.exists():
            time.sleep(1)
        combo_box = dialog.child_window(auto_id="1148", control_type="ComboBox")
        edit_control = combo_box.child_window(control_type="Edit")
        edit_control.set_text(file_path)
        open_button = dialog.child_window(auto_id="1", control_type="Button")
        open_button.click()

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
                        time.sleep(1)
                    combo_box = file_dialog.child_window(auto_id="1148", control_type="ComboBox")
                    edit_control = combo_box.child_window(control_type="Edit")
                    edit_control.set_text(files_instruction["source"])
                    open_button = file_dialog.child_window(auto_id="1", control_type="Button")
                    open_button.click()
            except Exception as e:
                messagebox.showerror("Error", f"Error during replacement: {str(e)}")
                print(f"Error during replacement: {e}")
                return 2  # Code 2: Replacement error

    print("Saving modifications...")
    window.type_keys("^s")
    for file in tqdm(instructions.keys(), desc="Saving files", unit="file"):
        save_dialog = window.child_window(control_type="Window", found_index=0)
        while not save_dialog.exists():
            time.sleep(1)
        buttons = save_dialog.children(control_type="Button")
        for btn in buttons:
            button_text = btn.texts()
            if button_text and button_text[0] == "OK":
                btn.click()
                break
    window.close()
    return 0  # Code 0: Success
