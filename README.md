# SMPJ Map Editor

**SMPJ Map Editor** is a data editor for the game **Super Mario Party Jamboree**.
## Disclaimer

This software is a **fan-made tool** developed for educational and modding purposes.  
It is **not affiliated with Nintendo** or the developers of *Super Mario Party Jamboree*.  
Use at your own risk.

**⚠️ THIS TOOL IS NOT A MAP MAKER**  
> It is **not** a variant or fork of [Party Studio](https://github.com/MapStudioProject/Party-Studio).  
> It will **never** allow you to modify the position of the board spaces or the map textures.  
> These features would require a full 3D editor and are far more complex to implement.  
> This software should be considered a **rudimentary map editor**, meant to help users wait until a full-fledged editor or *Party Studio* update becomes available.

---

## Usage in Mods

You are free to use SMPJ Map Editor to create board modifications **without any restrictions**.  
The tool outputs are fully yours to distribute in your mods.

**Project credit is greatly appreciated** (though not legally required):  
`Board data edited with SMPJ Map Editor`  
**[GitHub](https://github.com/MH13-YT/SMPJ-Map-Editor)** | **[GameBanana](https://gamebanana.com/wips/88664)**

---

## Features

### ⚠️ WARNING

Since **version 1.1.0**, the software uses **pythonnet** (.NET/Mono) along with **BezelEngineArchive_Lib** to extract and repack Bezel Engine Archive files.
> **Note:**  
> This tool relies on an **external C# library**:  
> [KillzXGaming/BEA-Library-Editor – BezelEngineArchive_Lib](https://github.com/KillzXGaming/BEA-Library-Editor/tree/master/BezelEngineArchive_Lib)  
> This library is **automatically downloaded on the first launch** of the application.
> **Implemented for Windows with .NET 8** (tested and working). **Mono support implemented but untested.**

---

### Current Features

- Edit items obtainable in shops (**Koopa and Kamek shops only**, Rainbow Galleria shops is not supported).  
- Edit items obtainable from **Item Bags**.  
- Edit items obtainable from **Item Cases** (can also remove item minigames).  
- Edit **events** (Lucky, Unlucky, Bowser).  
- Edit **hidden blocks**.  
- Edit **board spaces** (change types such as Blue, Red, Lucky, Unlucky, Bowser, Chance Time, etc.).

---

### Planned Features

No new features are planned at the moment.

---

### Features In Mind

- Change paths.  
- Add support for **Boo spaces**.
- Add support for **Star spaces**.

---

## How to Install

### Prerequistes
- A **complete dump** of the *Super Mario Party Jamboree* romfs folder *(you must obtain this by yourself)*.  
- Internet connection enabled during the first start so the tool can **automatically download the C# library**.

### Option 1 — Using Releases (Recommended)

1. Download the latest version from the project’s **[Releases](https://github.com/.../releases)** page.  
2. Extract the downloaded archive.  
3. Run the included `.exe` file.

> ⚠️ **Note:** builds created with **PyInstaller** can be flagged as **false positives** by some antivirus software.  
> The project is fully open-source — feel free to inspect the code before running it.

---

### Option 2 — Run from Source Code

#### Additional Prerequisites
- **Python** installed with **Tkinter** (required to launch the GUI if running from source).  
  Check the `.python-version` file for the latest supported Python version.  

#### Install dependencies

Use: pip install -r requirements.txt

---

## Credits

- **KillzXGaming** - for [BezelEngineArchive_Lib](https://github.com/KillzXGaming/BEA-Library-Editor/tree/master/BezelEngineArchive_Lib) (GPLv3)

---

### License

This project is licensed under the terms of the **GNU General Public License v3 (GPLv3)**.  
You are free to use, modify, and distribute this software under the same license terms.  
See the file [LICENSE](./LICENSE) for the complete text of the GPLv3.

Because this project interfaces directly with the **BezelEngineArchive_Lib** library (licensed under GPLv3),  
SMPJ Map Editor adopts the same license to maintain compatibility.

---
