import os
import sys
import importlib.util
from cwsi import CWSI_LIBS_MAP  # Importing the embedded map into the script's memory

def start(libs):
    """
    Main entry point. Called automatically by cwsi.exe.
    The 'libs' argument duplicates the path map for convenience.
    """
    print("--- CUSTOM MODULE STARTED ---")

    # Get the path directly and convert it to an absolute path
    # In pathmap.ini: example = libs\example\example.txt
    file_path = os.path.abspath(CWSI_LIBS_MAP["example"])
    print(f"Target file path: {file_path}")

    # =========================================================================
    # COMMENTED EXAMPLE: HOW TO TRANSFER CONTROL TO ANOTHER .PY SCRIPT
    # =========================================================================
    # # 1. Define the path to the next script (e.g., located in the same modules folder)
    # exe_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    # next_script_path = os.path.join(exe_dir, "modules", "next_module.py")
    #
    # # 2. Dynamically load it into memory
    # spec = importlib.util.spec_from_file_location("next_module", next_script_path)
    # next_module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(next_module)
    #
    # # 3. Pass control by calling its main entry function
    # if hasattr(next_module, "start"):
    #     next_module.start(CWSI_LIBS_MAP)
    # =========================================================================

    print("--- CUSTOM MODULE FINISHED ---")
    input("Press Enter to exit...")
