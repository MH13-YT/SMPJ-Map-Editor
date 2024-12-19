# SMPJ Map Editor

SMPJ Map Editor is a data editor for the game Super Mario Party Jamboree

**THIS TOOL ISN'T A MAP MAKER or a variant of Party Studio**
it will **never** allow you to modify the position of the squares on the board, or the textures of the maps, this will require a 3D editor and will be much more complex to develop it should be considered as a **rudimentary map editor** allowing you to wait until a complete editor was developed or [Party Studio](https://github.com/MapStudioProject/Party-Studio) was updated

## Features
### WARNING
Although this tool integrates certain security it is and remains in the **EXPERIMENTAL** state
therefore it is intended for users with a minimum of knowledge of switch modding as well as Super Mario Party Jamboree modding

Since **version 0.0.3** this software use pip dependancy, you can use `pip install -r requirements.txt` for installing it
This change comes following the addition of *map editing functionality* which requires the python [matplotlib](https://pypi.org/project/matplotlib/) module

### Current Features
- Edit items obtainable in the shops (**Only Koopa and Kamek**, it cannot edit Rainbow Galleria specific shop)
- Edit items obtainable by the item bag
- Edit items obtainable by the item case (can also remove object minigames option)
- Edit events (Lucky, Unlucky and Bowser)
- Edit hidden blocks
- Edit map (Change types (Blue/Red/Lucky/Unlucky/Bowser/Chance Time...)

### Planned Features
No Features planned actually

### Features in mind
- Change paths
- Add support for Boo spots
- Add support for event boxes

## How to Install
### Prerequisites
- A complete dump of the Super Mario Party Jamboree romfs file, google is your friend for obtain it
- Switch Toolbox (for extract files from "bd\~bd00.nx.bea to bd\~bd07.nx.bea" Archive and place the files on a folder named "bd\~bd00.nx" to "bd\~bd07.nx" in the CORE folder on the same place than `main.py`)
- Python with Tinkerer/Tk installed (The software is developed and tested with python 3.12)
