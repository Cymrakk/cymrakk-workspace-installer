import os
import sys
import importlib.util
import urllib.request
import ssl
import types
import colorama
from colorama import Fore, Style
colorama.init(convert=True, autoreset=True)


CWSI_VERSION = "0.2.0"
VERSION_CWSI_URL = "https://raw.githubusercontent.com/Cymrakk/cymrakk-workspace-installer/refs/heads/main/version.txt"
GITHUB_CWSI_URL_RELEASE  = "https://github.com/Cymrakk/cymrakk-workspace-installer/releases"
GITHUB_CWSI_URL_SRC  = "https://github.com/Cymrakk/cymrakk-workspace-installer"

CWSI_RED = Fore.RED + Style.BRIGHT
CWSI_YELLOW = Fore.YELLOW + Style.BRIGHT
CWSI_WHITE = Fore.WHITE + Style.BRIGHT 

CWSI_LIBS_MAP = {}

cwsi_module = types.ModuleType('cwsi')
cwsi_module.CWSI_LIBS_MAP = CWSI_LIBS_MAP
sys.modules['cwsi'] = cwsi_module

try:
    # --------------------------------------
    if not getattr(sys, 'frozen', False):
        # input("\nPress Enter to exit...")
        sys.exit(1)
    # --------------------------------------
    
    # START
    print(f"{CWSI_WHITE}CWSI VERSION {CWSI_YELLOW}{CWSI_VERSION} {CWSI_WHITE}was started!")
    
    # ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)    # old
    ctx = ssl.create_default_context()              # new
    
    print(f"{CWSI_WHITE}Checking for updates...")
    try:
        with urllib.request.urlopen(VERSION_CWSI_URL, context=ctx) as response:
            remote_version = response.read().decode('utf-8').strip()
            
            if remote_version != CWSI_VERSION:
                print(f"\n{CWSI_RED}You are using an outdated version of CWSI! (Local: {CWSI_VERSION} | Server: {remote_version})")
                print(f"{CWSI_YELLOW}We recommend updating to the latest version on {CWSI_WHITE}GitHub:")
                print(f"{CWSI_YELLOW}--> {CWSI_WHITE}{GITHUB_CWSI_URL_RELEASE }\n")
                print(f"{CWSI_YELLOW}The source code of the {CWSI_WHITE}CWSI project {CWSI_YELLOW}is available on {CWSI_WHITE}GitHub:")
                print(f"{CWSI_YELLOW}--> {CWSI_WHITE}{GITHUB_CWSI_URL_SRC}\n")
            else:
                print(f"{CWSI_YELLOW}You are using the latest version of {CWSI_WHITE}CWSI{CWSI_YELLOW}.\n")
                print(f"{CWSI_YELLOW}The source code of the {CWSI_WHITE}CWSI project {CWSI_YELLOW}is available on {CWSI_WHITE}GitHub:")
                print(f"{CWSI_YELLOW}--> {CWSI_WHITE}{GITHUB_CWSI_URL_SRC}\n")
    except Exception:
        print("Skipping update check (unable to reach server).")

    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    modules_dir = os.path.join(exe_dir, "modules")
    
    if modules_dir not in sys.path:
        sys.path.insert(0, modules_dir)
    if exe_dir not in sys.path:
        sys.path.insert(1, exe_dir)

    main_module_file = None
    for key, value in CWSI_LIBS_MAP.items():
        if value == "MAIN":
            main_module_file = key
            break

    if not main_module_file:
        raise Exception(f"{CWSI_WHITE}Error: {CWSI_RED}001 (Main module not found in config)") 

    full_module_path = os.path.join(modules_dir, main_module_file)

    if not os.path.exists(full_module_path):
        raise FileNotFoundError(f"{CWSI_WHITE}Error: {CWSI_RED}002 (Main module file missing)") 

    module_name = os.path.splitext(main_module_file)[0]
    spec = importlib.util.spec_from_file_location(module_name, full_module_path)
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)

    if hasattr(main_module, "start"):
        main_module.start(CWSI_LIBS_MAP)
    else:
        raise AttributeError(f"{CWSI_WHITE}Error: {CWSI_RED}003 (Start function missing in main module)") 

except Exception as e:
    print(f"\n{e}{Style.RESET_ALL}")
    input("\nPress Enter to exit...")
    sys.exit(1)
