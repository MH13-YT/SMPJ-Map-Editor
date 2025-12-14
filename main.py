import filecmp
import json
import os
import os
import sys
import hashlib
import shutil
import re
import tkinter as tk
import traceback
from tkinter import ttk, messagebox, simpledialog

from bea_archive_manager import (
    bea_archives_extractor,
    bea_archives_repacker,
    is_bea_lib_available,
    download_bea_lib_latest_via_curl,
)
from editor import JamboreeMapEditor

if getattr(sys, "frozen", False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CORE_DIR = os.path.join(BASE_PATH, "CORE")
ROMFS_DIR = os.path.join(BASE_PATH, "ROMFS")
WORKSPACE_DIR = os.path.join(BASE_PATH, "workspace")
OUTPUT_DIR = os.path.join(BASE_PATH, "output")

REQUIRED_BEA_FILES = [
    "bd~bd00.nx",
    "bd~bd01.nx",
    "bd~bd02.nx",
    "bd~bd03.nx",
    "bd~bd04.nx",
    "bd~bd05.nx",
    "bd~bd06.nx",
    "bd~bd07.nx",
]

EXPECTED_CORE_CHECKSUMS = {
    "a2cdc050aa73b3c0d29e790a8a0fd1df500cf524eab365d427df56c2303c1756": "1.0.0 <=> 2.2.0"
}

# Global variable to track main menu window
main_window = None

def calculate_checksum_for_directory(directory):
    sha256 = hashlib.sha256()
    for root, _, files in sorted(os.walk(directory)):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
    return sha256.hexdigest()

def correct_and_verify_core_integrity(STE=False):
    if not os.path.exists(CORE_DIR):
        os.mkdir(CORE_DIR)
        for bea_folder in REQUIRED_BEA_FILES:
            os.makedirs(os.path.join(CORE_DIR, bea_folder), exist_ok=True)

    # Correction JSON
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

    # Checksum CORE
    calculated_checksum = calculate_checksum_for_directory(CORE_DIR)

    valid_checksum = False
    valid_checksums_text = "Checksum valides :\n"
    for CHECKSUM in EXPECTED_CORE_CHECKSUMS.keys():
        valid_checksums_text += (
            EXPECTED_CORE_CHECKSUMS[CHECKSUM] + " : " + CHECKSUM + "\n"
        )
        if CHECKSUM == calculated_checksum:
            valid_checksum = True

    if not valid_checksum:
        lib_ok = is_bea_lib_available()

        # Tentative de download auto si la lib manque
        if not lib_ok:
            if messagebox.askyesno(
                "BEA Library missing",
                "BezelEngineArchive_Lib.dll is missing.\n"
                "Do you want to automatically download the latest release from GitHub (via curl)?",
            ):
                if download_bea_lib_latest_via_curl():
                    lib_ok = is_bea_lib_available()
                else:
                    messagebox.showerror(
                        "Download failed",
                        "Automatic download failed. Please download manually from GitHub.\n"
                        "https://github.com/KillzXGaming/BEA-Library-Editor/releases",
                    )

        if (
            STE is False
            and lib_ok
            and os.path.isdir(ROMFS_DIR)
            and bool(os.listdir(ROMFS_DIR))
        ):
            user_choice = messagebox.askyesno(
                "Original file integrity check failed",
                "SMPJ Map Editor a besoin des fichiers du jeu en état non compressé pour fonctionner.\n"
                "The automatic game files integrity check failed (Files are missing or damaged).\n"
                "\n"
                "Do you want to try an automated extraction from BEA archives?\n"
                "(ROMFS must contain the game romfs content)\n"
                "\n"
                f"Checksum actuel : {calculated_checksum}\n"
                f"{valid_checksums_text}\n"
            )
            if user_choice:
                extractor = bea_archives_extractor(BASE_PATH, REQUIRED_BEA_FILES)
                match extractor:
                    case 0:
                        messagebox.showinfo(
                            "Finished",
                            "BEA Extraction is complete, please restart SMPJ Map Editor",
                        )
                        sys.exit(
                            "BEA Extraction is complete, please restart SMPJ Map Editor"
                        )
                    case 1:
                        messagebox.showwarning(
                            "Extraction Error",
                            "An error occured into the extraction, a required BEA File is missing",
                        )
                        raise RuntimeError(
                            "BEA Extraction Error : "
                            "An error occured into the extraction, a required BEA File is missing"
                        )
                    case 2:
                        messagebox.showerror(
                            "Extraction Error",
                            "An error occured into the extraction, an error occured in one BEA File extraction",
                        )
                        raise RuntimeError(
                            "BEA Extraction Error : "
                            "An error occured into the extraction, an error occured in one BEA File extraction"
                        )
        else:
            msg = (
                "SMPJ Map Editor needs files available in the game romfs in an uncompressed state to work\n"
                "The automatic game files integrity check failed (Files are missing or damaged)\n"
                "\n"
                "To correctly integrate the game files into this folder:\n"
                "- Ensure BezelEngineArchive_Lib.dll is present in the BezelEngineArchive_Lib folder\n"
                "- Copy the content of the romfs of Super Mario Party Jamboree into the ROMFS Folder (Not ROMFS/romfs)\n"
                "- Launch SMPJ Map Editor again to let it extract bd~bd00.nx.bea to bd~bd07.nx.bea\n"
                "  into the related folders in CORE using the BEA-Library-Editor backend.\n"
                "\n"
                f"Actual checksum: {calculated_checksum}\n"
                f"{valid_checksums_text}\n"
            )
            messagebox.showerror(
                "Original file integrity check failed",
                msg,
            )
            raise ValueError("Original file integrity check failed.")

def ensure_directories():
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    os.makedirs(ROMFS_DIR, exist_ok=True)
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

def show_main_menu(current_root=None):
    """Show main menu - uses existing root or creates new one"""
    global main_window
    
    # Destroy previous main window if exists
    if main_window:
        main_window.destroy()
    
    # Use existing root or create new
    if current_root:
        root = current_root
        root.deiconify()  # Bring to front if hidden
    else:
        root = tk.Tk()
    
    root.title("SMPJ Map Editor - Main Menu")
    root.geometry("420x340")
    root.resizable(False, False)
    main_window = root
    
    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    
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
        workspaces = update_workspace_list()
        if workspace in workspaces:
            workspace_path = os.path.join(WORKSPACE_DIR, workspace)
            root.withdraw()  # Hide main menu
            # Launch editor
            app = JamboreeMapEditor(workspace_path)
            app.protocol("WM_DELETE_WINDOW", lambda: return_to_main_menu(app))
            app.mainloop()
            # Editor closed, show main menu again
            show_main_menu(root)
        else:
            messagebox.showerror("Error", "Please select a valid workspace.")

    def export_workspace():
        workspace = combobox.get()
        workspaces = update_workspace_list()
        if workspace in workspaces:
            workspace_path = os.path.join(WORKSPACE_DIR, workspace)
            output_path = os.path.join(OUTPUT_DIR, workspace)
            packages_path_list = [
                os.path.join(
                    output_path,
                    "Simple Mod Manager (SMM)",
                    "mods",
                    "Super Mario Party Jamboree",
                    workspace,
                    "contents",
                    "0100965017338000",
                    "romfs",
                ),
                os.path.join(
                    output_path,
                    "RYUJINX",
                    "mods",
                    "contents",
                    "0100965017338000",
                    workspace,
                    "romfs",
                ),
                os.path.join(
                    output_path,
                    "YUZU",
                    "load",
                    "0100965017338000",
                    workspace,
                    "romfs",
                ),
            ]
            if os.path.exists(output_path):
                shutil.rmtree(output_path)
            os.makedirs(output_path, exist_ok=True)

            instructions = {}
            for current_root, _, file_list in os.walk(workspace_path):
                for file_name in file_list:
                    modified_file_path = os.path.join(current_root, file_name)
                    relative_file_path = os.path.relpath(
                        modified_file_path, workspace_path
                    )
                    original_file_path = os.path.join(CORE_DIR, relative_file_path)

                    if not os.path.exists(original_file_path) or not filecmp.cmp(
                        original_file_path, modified_file_path, shallow=False
                    ):
                        parts = relative_file_path.split(os.sep)
                        bea_name = parts[0]
                        inner_rel = os.path.join(*parts[1:])

                        if bea_name not in instructions:
                            instructions[bea_name] = []

                        instructions[bea_name].append(
                            {
                                "source": modified_file_path,
                                "destination": inner_rel,
                            }
                        )

            repack = bea_archives_repacker(instructions, BASE_PATH, output_path)

            match repack:
                case 0:
                    for root, dirs, files in os.walk(os.path.join(output_path, "romfs")):
                        for name in files:
                            if name.endswith(".work"):
                                file_path = os.path.join(root, name)
                                os.remove(file_path)
                    for folder in packages_path_list:
                        shutil.copytree(os.path.join(output_path, "romfs"), folder)
                    messagebox.showinfo("Finished", "Exportation finished")
                case 1:
                    messagebox.showwarning(
                        "Aborted",
                        "BEA Repack Aborted by User : Aborting Exportation",
                    )
                case 2:
                    messagebox.showerror(
                        "Error",
                        "An error occured in BEA Repack : Aborting Exportation",
                    )

    def return_to_main_menu(editor_window):
        """Helper to return to main menu from editor"""
        editor_window.destroy()
        root.deiconify()  # Show main menu again

    def on_main_closing():
        sys.exit(0)

    # Bind closing event - EXIT PROGRAM
    root.protocol("WM_DELETE_WINDOW", on_main_closing)

    # Create UI elements
    ttk.Label(root, text="SMPJ Map Editor", font=("Arial", 14)).pack(pady=5)
    ttk.Label(root, text="(This is not a map maker)", font=("Arial", 10)).pack(pady=0)
    ttk.Label(
        root,
        text="(WARNING : This tool is in experimental state)",
        font=("Arial", 10),
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

    tk.Button(root, text="Load Workspace", command=load_workspace, width=100).pack(
        pady=5
    )

    lib_ok = is_bea_lib_available()
    romfs_ok = os.path.isdir(ROMFS_DIR) and bool(os.listdir(ROMFS_DIR))

    if lib_ok and romfs_ok:
        tk.Button(
            root, text="Export Workspace", command=export_workspace, width=100
        ).pack(pady=5)
    else:
        def missing_dep_warning():
            if not lib_ok:
                if messagebox.askyesno(
                    "BEA Library missing",
                    "BezelEngineArchive_Lib.dll is missing.\n"
                    "Do you want to automatically download the latest release from GitHub (via curl)?",
                ):
                    if download_bea_lib_latest_via_curl():
                        messagebox.showinfo(
                            "Download complete",
                            "Download finished. Please restart SMPJ Map Editor.",
                        )
                    else:
                        messagebox.showerror(
                            "Download failed",
                            "Automatic download failed. Please download manually:\n"
                            "https://github.com/KillzXGaming/BEA-Library-Editor/releases",
                        )
            elif not romfs_ok:
                messagebox.showerror(
                    "ROMFS missing",
                    "ROMFS folder is missing or empty.\n"
                    "Please copy the game romfs content into the ROMFS folder.",
                )

        tk.Button(
            root,
            text="Export Workspace",
            command=missing_dep_warning,
            width=100,
        ).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    try:
        ensure_directories()
        show_main_menu()  # Single call, handles loop internally
    except Exception as e:
        traceback.print_exc()
        print("===================================")
        print("An error was occured")
        print(f"Source of error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
