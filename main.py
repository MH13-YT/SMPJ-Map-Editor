import filecmp
import json
import os
import sys
import hashlib
import shutil
import re
import tkinter as tk
import traceback
from tkinter import ttk, messagebox, simpledialog

from bea_archive_manager import bea_archives_extractor, bea_archives_repacker
from editor import JamboreeMapEditor

if getattr(sys, "frozen", False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))


TOOLBOX_DIR = os.path.join(BASE_PATH, "Switch Toolbox")

CORE_DIR = os.path.join(BASE_PATH, "CORE")
ROMFS_DIR = os.path.join(BASE_PATH, "ROMFS")
WORKSPACE_DIR = os.path.join(BASE_PATH, "workspace")
OUTPUT_DIR = os.path.join(BASE_PATH, "output")


REQUIRED_BEA_FILES = [
    "bd~bd00.nx","bd~bd01.nx","bd~bd02.nx","bd~bd03.nx","bd~bd04.nx","bd~bd05.nx","bd~bd06.nx","bd~bd07.nx"
]

EXPECTED_CORE_CHECKSUMS = {
    "a2cdc050aa73b3c0d29e790a8a0fd1df500cf524eab365d427df56c2303c1756" : "1.0.0 - 1.0.1 - 1.1.1"
}


def calculate_checksum_for_directory(directory):
    sha256 = hashlib.sha256()
    for root, _, files in sorted(os.walk(directory)):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
    return sha256.hexdigest()


def correct_and_verify_core_integrity(STE = False):
    if not os.path.exists(CORE_DIR):
        os.mkdir(CORE_DIR)
        for bea_folder in REQUIRED_BEA_FILES:
            os.makedirs(os.path.join(CORE_DIR, bea_folder), exist_ok=True)

    for root, _, files in os.walk(CORE_DIR):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8-sig") as json_file:
                        content = json_file.read()

                    content_fixed = re.sub(r",\s*(\]|\})", r"\1", content)

                    content_fixed = re.sub(r"(?<=\})(?=\s*,)", r"", content_fixed)
                    content_fixed = re.sub(r"\}[^}]*$", r"}", content_fixed)

                    try:
                        json_data = json.loads(content_fixed)
                    except json.JSONDecodeError as error:
                        raise ValueError(
                            f"Failed to load JSON file after correction: {file_path}\n"
                            f"Error: {error}"
                        )

                    with open(file_path, "w", encoding="utf-8-sig") as json_file:
                        json.dump(json_data, json_file, indent=4, ensure_ascii=False)

                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"Failed to correct or load JSON file: {file_path}\n"
                        f"Error: {error}"
                    )

    sha256 = hashlib.sha256()
    for root, _, files in sorted(os.walk(CORE_DIR)):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
    calculated_checksum = sha256.hexdigest()
    valid_checksum = False
    supported_versions = ""
    valid_checksums_text = "Checksum valides :\n"
    for CHECKSUM in EXPECTED_CORE_CHECKSUMS.keys():
        valid_checksums_text = valid_checksums_text + EXPECTED_CORE_CHECKSUMS[CHECKSUM] + " : " + CHECKSUM + "\n"
        if (CHECKSUM == calculated_checksum):
            valid_checksum = True
            supported_versions = EXPECTED_CORE_CHECKSUMS[CHECKSUM]
    if (valid_checksum == False):
        if (STE == False and os.path.exists(os.path.join(BASE_PATH,"Switch Toolbox","Toolbox.exe")) and os.path.isdir(ROMFS_DIR) and bool(os.listdir(ROMFS_DIR))):
            user_choice = messagebox.askyesno(
            "Original file integrity check failed",
            f"SMPJ Map Editor a besoin des fichiers du jeu en état non compressé pour fonctionner.\n"
            f"The automatic game files integrity check failed (Files are missing or damaged).\n"
            "\n"
            "Do you want to try an automated extraction with Switch Toolbox ?\n"
            "\n"
            f"Checksum actuel : {calculated_checksum}\n"
            f"{valid_checksums_text}\n"
            )
            if (user_choice == True):
                bea_archives_extractor(BASE_PATH,REQUIRED_BEA_FILES)
                correct_and_verify_core_integrity(True)
        else:
            messagebox.showerror(
                "Original file integrity check failed",
                f"SMPJ Map Editor needs files available in the game romfs in an uncompressed state to work\n"
                f"The automatic game files integrity check failed (Files are missing or damaged)\n"
                "\n"
                f"To correctly integrate the game files into this folder.\n"
                f"- (Windows Only) Copy Switch Toolbox binaries files into 'Switch Toolbox' Folder and the content of the romfs of Super Mario Party Jamboree into the ROMFS Folder (Not ROMFS/romfs)\n"
                f"- Use Switch Toolbox to extract bd~bd00.nx.bea to bd~bd07.nx.bea to his related folders on the CORE folder\n"
                "\n"
                f"Actual checksum: {calculated_checksum}",
                f"{valid_checksums_text}\n"
            )

            raise ValueError(
                f"Original file integrity check failed.\n"
                f"- (Windows Only) Copy Switch Toolbox binaries files into 'Switch Toolbox' Folder and the content of the romfs of Super Mario Party Jamboree into the ROMFS Folder (Not ROMFS/romfs)\n"
                f"- Use Switch Toolbox to extract bd~bd00.nx.bea to bd~bd07.nx.bea to his related folders on the CORE folder\n"
                "\n"
                f"Actual checksum: {calculated_checksum}"
                f"{valid_checksums_text}\n"
            )


def ensure_directories():
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    correct_and_verify_core_integrity()


def create_workspace():
    workspace_name = simpledialog.askstring(
        "Create Workspace", "Enter the name of the new workspace:"
    )
    if workspace_name:
        workspace_path = os.path.join(WORKSPACE_DIR, workspace_name)
        try:
            if os.path.exists(workspace_path):
                raise FileExistsError(
                    f"A workspace with this name already exists: {workspace_name}"
                )
            shutil.copytree(CORE_DIR, workspace_path)
            messagebox.showinfo("Success", f"Workspace created: {workspace_path}")
            return workspace_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create the workspace: {e}")
    return None


def main_interface():
    root = tk.Tk()
    root.title("SMPJ Map Editor")
    root.geometry("350x250")
    root.resizable(False, False)

    selected_workspace = tk.StringVar()

    def update_workspace_list():
        workspaces = [
            d
            for d in os.listdir(WORKSPACE_DIR)
            if os.path.isdir(os.path.join(WORKSPACE_DIR, d))
        ]
        combobox["values"] = workspaces
        if workspaces:
            combobox.set("Select a workspace")
        else:
            combobox.set("No workspace available")
        return workspaces

    def create_workspace_wrapper():
        if create_workspace():
            update_workspace_list()

    def load_workspace():
        workspace = combobox.get()
        if workspace in update_workspace_list():
            selected_workspace.set(workspace)
            root.destroy()
        else:
            messagebox.showerror("Error", "Please select a valid workspace.")

    def export_workspace():
        workspace = combobox.get()
        if workspace in update_workspace_list():
            selected_workspace.set(workspace)
            workspace_path = os.path.join(WORKSPACE_DIR, selected_workspace.get())
            output_path = os.path.join(OUTPUT_DIR, selected_workspace.get())
            # Supprimer le dossier de destination s'il existe déjà, puis le recréer
            if os.path.exists(output_path):
                shutil.rmtree(output_path)
            os.makedirs(output_path, exist_ok=True)
            instructions = {}
            # Parcourir les fichiers du dossier modifié
            for current_root, _, file_list in os.walk(workspace_path):
                for file_name in file_list:
                    modified_file_path = os.path.join(current_root, file_name)
                    relative_file_path = os.path.relpath(modified_file_path, workspace_path)
                    original_file_path = os.path.join(CORE_DIR, relative_file_path)
                    
                    # Vérifier si le fichier existe dans l'original et s'il est identique
                    if not os.path.exists(original_file_path) or not filecmp.cmp(original_file_path, modified_file_path, shallow=False):
                        entry = relative_file_path.split(os.sep)
                        if entry[0] not in instructions:
                            instructions[entry[0]] = []
                        instructions[entry[0]].append({"source": modified_file_path, "destination": entry[-1]})
            bea_archives_repacker(instructions, BASE_PATH, workspace_path, OUTPUT_DIR)
                        
        else:
            messagebox.showerror("Error", "Please select a valid workspace.")

    ttk.Label(root, text="SMPJ Map Editor", font=("Arial", 14)).pack(pady=5)
    ttk.Label(root, text="(This is not a map maker)", font=("Arial", 10)).pack(pady=0)
    ttk.Label(
        root, text="(WARNING : This tool is in experimental state)", font=("Arial", 10)
    ).pack(pady=5)
    ttk.Button(
        root, text="Create a New Workspace", command=create_workspace_wrapper, width=100
    ).pack(pady=5)
    ttk.Label(root, text="Select an existing Workspace:", font=("Arial", 12)).pack(
        pady=5
    )

    combobox = ttk.Combobox(root, state="readonly", width=100)
    combobox.pack(pady=5, fill=tk.X, padx=20)
    update_workspace_list()

    ttk.Button(root, text="Load Workspace", command=load_workspace, width=100).pack(
        pady=5
    )

    ttk.Button(root, text="Export Workspace", command=export_workspace, width=100).pack(
        pady=5
    )

    root.mainloop()

    return (
        os.path.join(WORKSPACE_DIR, selected_workspace.get())
        if selected_workspace.get()
        else None
    )

if __name__ == "__main__":
    try:
        ensure_directories()
        workspace_path = main_interface()
        if workspace_path:
            app = JamboreeMapEditor(workspace_path)
            app.mainloop()
    except Exception as e:
        traceback.print_exc()
        print("===================================")
        print("An error was occured")
        print(f"Source of error: {e}")