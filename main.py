import json
import os
import subprocess
import sys
import time
import hashlib
import shutil
import re
import tkinter as tk
import traceback
from tkinter import ttk, messagebox, simpledialog

from editor import JamboreeMapEditor


def manage_dependencies():
    import importlib.util
    import importlib.metadata

    if getattr(sys, "frozen", False):
        return True
    project_path = os.getcwd()
    requirements_file = os.path.join(project_path, "requirements.txt")

    try:
        if importlib.util.find_spec("pipreqs") is None:
            print("pipreqs is not installed. Starting installation...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pipreqs"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        print("Generating requirements.txt with pipreqs...")
        subprocess.check_call(
            [sys.executable, "-m", "pipreqs.pipreqs", project_path, "--force"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if os.path.exists(requirements_file):
            with open(requirements_file, "r") as file:
                requirements_content = file.read().strip().splitlines()

            print("\nContent of requirements.txt:")
            print("\n".join(requirements_content))

            installed_packages = {
                pkg.metadata["Name"].lower()
                for pkg in importlib.metadata.distributions()
            }

            packages_to_install = [
                pkg
                for pkg in requirements_content
                if pkg.split("==")[0].lower() not in installed_packages
            ]

            if not packages_to_install:
                print(
                    "\nAll dependencies are already installed. Skipping installation."
                )
                return True

            print(
                f"\nThe following dependencies are missing and will be installed: {', '.join(packages_to_install)}"
            )
            print("\nThe installation of dependencies will start in 5 seconds.")

            for i in range(5, 0, -1):
                print(f"{i}...", end="", flush=True)
                time.sleep(1)

            print("\nInstalling missing dependencies...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install"] + packages_to_install
            )
            print("All missing dependencies are installed.")
            return True
        else:
            print("Error: requirements.txt not found (pipreqs generation error).")
            input("Press any key to exit...")
            return False

    except subprocess.CalledProcessError as e:
        print(f"Error in process: {e}")
        input("Press any key to exit...")
        return False


if getattr(sys, "frozen", False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))


WORKSPACE_DIR = os.path.join(BASE_PATH, "workspace")
CORE_DIR = os.path.join(BASE_PATH, "CORE")


EXPECTED_CORE_CHECKSUM = (
    "c7486a455de3573ec3eb5b8450840940866e06395ef67bea41d3aebaab1221db"
)


def calculate_checksum_for_directory(directory):
    sha256 = hashlib.sha256()
    for root, _, files in sorted(os.walk(directory)):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
    return sha256.hexdigest()


def correct_and_verify_core_integrity():
    if not os.path.exists(CORE_DIR):
        os.mkdir(CORE_DIR)
        os.mkdir(os.path.join(CORE_DIR, "bd~bd00.nx"))
        os.mkdir(os.path.join(CORE_DIR, "bd~bd01.nx"))
        os.mkdir(os.path.join(CORE_DIR, "bd~bd02.nx"))
        os.mkdir(os.path.join(CORE_DIR, "bd~bd03.nx"))
        os.mkdir(os.path.join(CORE_DIR, "bd~bd04.nx"))
        os.mkdir(os.path.join(CORE_DIR, "bd~bd05.nx"))
        os.mkdir(os.path.join(CORE_DIR, "bd~bd06.nx"))
        os.mkdir(os.path.join(CORE_DIR, "bd~bd07.nx"))
        raise FileNotFoundError(
            "The CORE directory is missing.\n"
            "SMPJ Map Item Editor created this folder for you.\n"
        )

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

    if calculated_checksum != EXPECTED_CORE_CHECKSUM:
        messagebox.showerror(
            "Original file integrity check failed",
            f"SMPJ Map Editor needs files available in the game romfs in an uncompressed state to work\n"
            f"The automatic game files integrity check failed (Files are missing or damaged)\n"
            "\n"
            f"To correctly integrate the game files into this folder.\n"
            f"- Use Switch Toolbox to extract bd~bd00.nx.bea to bd~bd07.nx.bea to his related folders on the CORE folder\n"
            "\n"
            f"Expected checksum: {EXPECTED_CORE_CHECKSUM}\n"
            f"Actual checksum: {calculated_checksum}",
        )
        raise ValueError(
            f"Original file integrity check failed.\n"
            f"- Use Switch Toolbox to extract bd~bd00.nx.bea to bd~bd07.nx.bea to his related folders on the CORE folder\n"
            "\n"
            f"Expected checksum: {EXPECTED_CORE_CHECKSUM}\n"
            f"Actual checksum: {calculated_checksum}"
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
    root.geometry("280x220")
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

    root.mainloop()

    return (
        os.path.join(WORKSPACE_DIR, selected_workspace.get())
        if selected_workspace.get()
        else None
    )


if __name__ == "__main__":
    try:
        if manage_dependencies():
            ensure_directories()
            workspace_path = main_interface()
            if workspace_path:
                app = JamboreeMapEditor(workspace_path)
                app.mainloop()
        else:
            print("Unable to install dependencies")
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
