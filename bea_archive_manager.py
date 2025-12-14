import os
import appdirs
import sys
import json
import subprocess
import tempfile
import zipfile
import platform
from pathlib import Path
from contextlib import suppress

from pythonnet import load  # pythonnet >= 3.x

from typing import Dict, List
import shutil
from tqdm import tqdm

import zstandard as zstd  # pip install zstandard
import gc
import io

# FIX PyInstaller --windowed
if not sys.stdin:
    sys.stdin = io.StringIO()
if not sys.stdout:
    sys.stdout = io.StringIO()
if not sys.stderr:
    sys.stderr = io.StringIO()

# Reusable Zstd decompressor
_zstd_decompressor = zstd.ZstdDecompressor()
_zstd_compression_level = 3  # reasonable level, adjust if needed

# ----------------------------------------------------------------------
# .NET runtime initialization - FIXED
# ----------------------------------------------------------------------

def init_dotnet_runtime():
    """Initialize .NET with complete system log suppression"""
    system = platform.system()
    
    try:
        if system == "Windows":
            load("coreclr")
        else:
            load("mono")
    except Exception as e:
        raise RuntimeError(f".NET Runtime Initialization Failed: {e}")

init_dotnet_runtime()
import clr
from System import Array, Byte, Activator, GC, Console
from System.IO import FileStream, FileMode, FileAccess, FileShare, StringWriter

# GLOBAL Console silencing - CORRECTED
null_writer = StringWriter()
Console.SetOut(null_writer)
Console.SetError(null_writer)

# ----------------------------------------------------------------------
# Silent wrapper for BEA operations - FIXED (no msvcrt/os.dup2)
# ----------------------------------------------------------------------

def silent_bea_operation(func, *args, **kwargs):
    """Execute BEA operation with total log suppression - SIMPLIFIED"""
    # Save/restore Console output only (no file descriptors)
    old_out = Console.Out
    old_err = Console.Error
    null_writer = StringWriter()
    Console.SetOut(null_writer)
    Console.SetError(null_writer)
    
    try:
        return func(*args, **kwargs)
    finally:
        # Restore Console output
        Console.SetOut(old_out)
        Console.SetError(old_err)

# ----------------------------------------------------------------------
# Paths and constants (PyInstaller-aware)
# ----------------------------------------------------------------------


# Cache directory (persistant)
CACHE_DIR = Path(appdirs.user_cache_dir("SMPJ_Map_Editor", "SMPJ_Map_Editor"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)  # ✅ CRÉE le dossier

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # PyInstaller : utilise _MEIPASS + fallback cache pour libs
    BASE_PATH = Path(sys._MEIPASS)
    BASE_LIB_DIR = BASE_PATH / "libs"
    
    # Si libs absent dans bundle → cache persistant
    if not BASE_LIB_DIR.exists():
        BASE_LIB_DIR = CACHE_DIR / "libs"
        BASE_LIB_DIR.mkdir(parents=True, exist_ok=True)
else:
    # Dev : dossier projet
    BASE_PATH = Path(__file__).resolve().parent
    BASE_LIB_DIR = BASE_PATH / "libs"
    
    # Si libs/ absent → cache persistant
    if not BASE_LIB_DIR.exists():
        BASE_LIB_DIR = CACHE_DIR / "libs"
        BASE_LIB_DIR.mkdir(parents=True, exist_ok=True)

LIB_FOLDER_NAME = "BezelEngineArchive_Lib"
BEA_LIB_ROOT = BASE_LIB_DIR / LIB_FOLDER_NAME
BEA_DLL = BEA_LIB_ROOT / "BezelEngineArchive_Lib.dll"

GITHUB_LATEST_API = "https://api.github.com/repos/KillzXGaming/BEA-Library-Editor/releases/latest"

# ----------------------------------------------------------------------
# Library presence check
# ----------------------------------------------------------------------

def is_bea_lib_available() -> bool:
    return BEA_LIB_ROOT.is_dir() and BEA_DLL.is_file()

# ----------------------------------------------------------------------
# Download latest release via GitHub API + curl
# ----------------------------------------------------------------------

def download_bea_lib_latest_via_curl() -> bool:
    """Download latest BEA-Library-Editor release and extract DLLs"""
    BEA_LIB_ROOT.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            ["curl", "-sL", GITHUB_LATEST_API],
            check=True,
            capture_output=True,
            text=True,
        )
        release = json.loads(result.stdout)
    except Exception as e:
        print(f"[ERR] Failed to query GitHub release: {e}")
        return False

    assets = release.get("assets", [])
    zip_asset = None
    for asset in assets:
        name = asset.get("name", "")
        if name.lower().endswith(".zip"):
            zip_asset = asset
            break

    if zip_asset is None:
        print("[ERR] No .zip asset found in latest release.")
        return False

    download_url = zip_asset.get("browser_download_url")
    if not download_url:
        print("[ERR] browser_download_url missing for asset.")
        return False

    print(f"[INFO] Selected asset: {zip_asset['name']} -> {download_url}")

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / zip_asset["name"]
        cmd = ["curl", "-L", "-o", str(zip_path), download_url]
        try:
            print("[INFO] Downloading asset via curl...")
            res = subprocess.run(cmd, check=False)
            if res.returncode != 0:
                print(f"[ERR] curl failed with code {res.returncode}")
                return False
        except FileNotFoundError:
            print("[ERR] curl not found on this system.")
            return False

        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                dll_found = False

                for member in zf.namelist():
                    if not member.lower().endswith(".dll"):
                        continue

                    target_name = Path(member).name
                    target_path = BEA_LIB_ROOT / target_name

                    print(f"[INFO] Extracting {member} -> {target_path}")

                    tmp_extract = Path(tmpdir) / target_name
                    with zf.open(member) as src, open(tmp_extract, "wb") as dst:
                        dst.write(src.read())

                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    if target_path.exists():
                        target_path.unlink()
                    tmp_extract.replace(target_path)

                    if target_name.lower() == "bezelenginearchive_lib.dll":
                        dll_found = True

                if not dll_found:
                    print("[ERR] BezelEngineArchive_Lib.dll not found in archive.")
                    return False

            return True
        except Exception as e:
            print(f"[ERR] Error during extraction: {e}")
            return False

# ----------------------------------------------------------------------
# BEA library (.NET) initialization - SILENT
# ----------------------------------------------------------------------

def _init_bea_lib():
    if not is_bea_lib_available():
        print(
            "BezelEngineArchive_Lib.dll missing.\n"
            "- Source: open-source 'BEA-Library-Editor' by KillzXGaming on GitHub.\n"
            "- .NET assembly used via pythonnet (Core/5+/8 Windows, Mono/.NET Linux/macOS).\n"
            "Attempting to download latest version from GitHub..."
        )

        ok = download_bea_lib_latest_via_curl()
        if not ok or not is_bea_lib_available():
            raise RuntimeError(
                "BezelEngineArchive_Lib.dll installation failed.\n"
                "Check internet or download manually from:\n"
                "  https://github.com/KillzXGaming/BEA-Library-Editor/releases/latest\n"
                "Place 'BezelEngineArchive_Lib' folder under 'libs' and restart."
            )

    arch = platform.machine().lower()
    is_64 = "64" in arch

    native_paths = [str(BEA_LIB_ROOT)]
    if is_64 and (BEA_LIB_ROOT / "x64").is_dir():
        native_paths.append(str(BEA_LIB_ROOT / "x64"))
    elif not is_64 and (BEA_LIB_ROOT / "x86").is_dir():
        native_paths.append(str(BEA_LIB_ROOT / "x86"))

    os.environ["PATH"] = os.pathsep.join(native_paths) + os.pathsep + os.environ.get("PATH", "")

    # Silent load of dependencies
    syroot = BEA_LIB_ROOT / "Syroot.BinaryData.dll"
    if syroot.is_file():
        def load_syroot():
            clr.AddReference(str(syroot))
        silent_bea_operation(load_syroot)

    # Silent load of main DLL
    def load_main_dll():
        return clr.AddReference(str(BEA_DLL))
    asm = silent_bea_operation(load_main_dll)

    # Find type silently
    t = asm.GetType("BezelEngineArchive_Lib.BezelEngineArchive")
    if t is None:
        for typ in asm.GetTypes():
            if "BezelEngineArchive" in typ.FullName:
                t = typ
                break

    if t is None:
        raise RuntimeError(
            f"Could not find BezelEngineArchive type in {BEA_DLL}. Check DLL version."
        )

    return t

BezelEngineArchive = _init_bea_lib()

# ----------------------------------------------------------------------
# .NET <-> Python helpers
# ----------------------------------------------------------------------

def _net_bytes_to_py(data_net) -> bytes:
    if data_net is None:
        return b""
    return bytes(bytearray(data_net))

def _py_bytes_to_net(data: bytes):
    return Array[Byte](list(data))

def _safe_rel_path(name: str) -> str:
    rel = name.replace("\\", "/")
    while "../" in rel:
        rel = rel.replace("../", "")
    while "..\\" in rel:
        rel = rel.replace("..\\", "")
    return rel.lstrip("/")

# ----------------------------------------------------------------------
# ASST compression helpers (Zstd)
# ----------------------------------------------------------------------

def _is_entry_compressed(entry) -> bool:
    return bool(getattr(entry, "IsCompressed", False))

def _extract_entry_to_file(entry, dest_path: Path):
    data_comp = _net_bytes_to_py(entry.FileData)

    if _is_entry_compressed(entry):
        usize = getattr(entry, "UncompressedSize", None)
        if usize is not None and int(usize) > 0:
            data = _zstd_decompressor.decompress(data_comp, max_output_size=int(usize))
        else:
            data = _zstd_decompressor.decompress(data_comp)
    else:
        data = data_comp

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)

def _set_entry_from_uncompressed(entry, data: bytes):
    raw_len = len(data)

    if _is_entry_compressed(entry):
        cctx = zstd.ZstdCompressor(level=_zstd_compression_level)
        data_comp = cctx.compress(data)
        entry.FileData = _py_bytes_to_net(data_comp)

        if hasattr(entry, "FileSize"):
            entry.FileSize = len(data_comp)
        if hasattr(entry, "UncompressedSize"):
            entry.UncompressedSize = raw_len
        if hasattr(entry, "IsCompressed"):
            entry.IsCompressed = True
    else:
        entry.FileData = _py_bytes_to_net(data)
        if hasattr(entry, "FileSize"):
            entry.FileSize = raw_len
        if hasattr(entry, "UncompressedSize"):
            entry.UncompressedSize = raw_len
        if hasattr(entry, "IsCompressed"):
            entry.IsCompressed = False

# ----------------------------------------------------------------------
# Extraction / repack via BezelEngineArchive_Lib - SILENT
# ----------------------------------------------------------------------

def extract_bea(bea_path: str, out_dir: str) -> None:
    def _extract_silent():
        bea_path_p = Path(bea_path).resolve()
        out_dir_p = Path(out_dir).resolve()
        out_dir_p.mkdir(parents=True, exist_ok=True)
        
        bea = Activator.CreateInstance(BezelEngineArchive, str(bea_path_p))
        try:
            file_dict = bea.FileList
            for kv in file_dict:
                entry = kv.Value
                name = str(entry.FileName)
                rel = _safe_rel_path(name)
                dest = out_dir_p / rel
                if entry.FileData is None:
                    continue
                _extract_entry_to_file(entry, dest)
        finally:
            if hasattr(bea, "Dispose"):
                with suppress(Exception):
                    bea.Dispose()
            GC.Collect()
            GC.WaitForPendingFinalizers()
            gc.collect()
    
    silent_bea_operation(_extract_silent)

def repack_bea_from_folder(input_dir: str, template_bea: str, out_bea: str, work_root: str) -> None:
    """Safe repack with complete DLL log suppression"""
    def _repack_silent():
        input_dir_p = Path(input_dir).resolve()
        template_bea_p = Path(template_bea).resolve()
        out_bea_p = Path(out_bea).resolve()
        work_root_p = Path(work_root).resolve()
        
        work_root_p.mkdir(parents=True, exist_ok=True)
        work_bea = work_root_p / (template_bea_p.name + ".work")
        if work_bea.exists():
            work_bea.unlink()
        shutil.copy2(str(template_bea_p), str(work_bea))
        
        bea = Activator.CreateInstance(BezelEngineArchive, str(work_bea))
        try:
            file_dict = bea.FileList
            for kv in file_dict:
                entry = kv.Value
                name = str(entry.FileName)
                rel = _safe_rel_path(name)
                src = input_dir_p / rel
                if not src.is_file():
                    continue
                data = src.read_bytes()
                _set_entry_from_uncompressed(entry, data)
            
            tmp_out = out_bea_p.with_suffix(out_bea_p.suffix + ".tmp")
            fs_out = FileStream(str(tmp_out), FileMode.Create, FileAccess.Write, FileShare.Read)
            try:
                bea.Save(fs_out, False)
            finally:
                fs_out.Close()
        finally:
            if hasattr(bea, "Dispose"):
                with suppress(Exception):
                    bea.Dispose()
            GC.Collect()
            GC.WaitForPendingFinalizers()
            gc.collect()
        
        if out_bea_p.exists():
            out_bea_p.unlink()
        tmp_out.replace(out_bea_p)
        try:
            work_bea.unlink()
        except OSError:
            pass
    
    silent_bea_operation(_repack_silent)

# ----------------------------------------------------------------------
# High-level functions (Python prints preserved)
# ----------------------------------------------------------------------

def bea_archives_extractor(base_path, bea_files):
    base = Path(base_path).resolve()
    romfs = base / "ROMFS"
    core = base / "CORE"

    print("Extracting BEA files...")
    for bea_file in tqdm(bea_files, desc="Extracting BEA files", unit="file", leave=True):
        full_bea_path = romfs / "Archive" / f"{bea_file}.bea"
        if not full_bea_path.is_file():
            print(f"[ERR] Missing BEA file: {full_bea_path}")
            return 1

        output_dir = core / bea_file

        try:
            extract_bea(str(full_bea_path), str(output_dir))
        except Exception as e:
            print(f"[ERR] Error during extraction of {full_bea_path}: {e}")
            return 2

    return 0

def bea_archives_repacker(
    instructions: Dict[str, List[Dict]], BASE_PATH: str, OUTPUT_DIR: str
):
    BASE_PATH = Path(BASE_PATH).resolve()
    OUTPUT_DIR = Path(OUTPUT_DIR).resolve()

    romfs_dir = BASE_PATH / "ROMFS"
    out_archive_dir = OUTPUT_DIR / "romfs" / "Archive"
    out_archive_dir.mkdir(parents=True, exist_ok=True)

    print("Copying BEA files to output directory...")
    for file in tqdm(list(instructions.keys()), desc="Copying BEA files", unit="file", leave=True):
        src_bea = romfs_dir / "Archive" / f"{file}.bea"
        if not src_bea.is_file():
            print(f"[ERR] Missing BEA file for copy: {src_bea}")
            return 2

        dst_bea = out_archive_dir / f"{file}.bea"
        try:
            shutil.copy(str(src_bea), str(dst_bea))
        except Exception as e:
            print(f"[ERR] Error copying {src_bea} to {dst_bea}: {e}")
            return 2

    print("Modifying BEA files with BezelEngineArchive_Lib...")

    # Temp root for extracted content
    tmp_root = OUTPUT_DIR / "_bea_tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)

    # System temp dir for .work files
    work_root = Path(tempfile.mkdtemp(prefix="bea_work_"))

    try:
        for file in tqdm(list(instructions.keys()), desc="Repacking BEA files", unit="file", leave=True):
            bea_path = out_archive_dir / f"{file}.bea"
            tmp_dir = tmp_root / file

            try:
                extract_bea(str(bea_path), str(tmp_dir))
            except Exception as e:
                print(f"[ERR] Error extracting {bea_path}: {e}")
                return 2

            for files_instruction in instructions[file]:
                dest_rel = _safe_rel_path(files_instruction["destination"])
                src_path = Path(files_instruction["source"]).resolve()

                if not src_path.is_file():
                    print(f"[ERR] Missing source file: {src_path}")
                    return 2

                dest_path = tmp_dir / dest_rel
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy(str(src_path), str(dest_path))
                except Exception as e:
                    print(f"[ERR] Error replacing {dest_rel}: {e}")
                    return 2

            try:
                repack_bea_from_folder(str(tmp_dir), str(bea_path), str(bea_path), str(work_root))
            except Exception as e:
                print(f"[ERR] Error repacking {bea_path}: {e}")
                return 2

    finally:
        # Cleanup temp directories
        try:
            shutil.rmtree(tmp_root)
        except Exception:
            pass
        try:
            shutil.rmtree(work_root)
        except Exception:
            pass

    return 0
