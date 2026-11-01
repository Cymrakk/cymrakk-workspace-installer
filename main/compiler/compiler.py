import os
import shutil
import subprocess
import configparser
import pathlib
from datetime import datetime

def build_project():
    print("--- STARTING COMPILE ---")
    compiler_dir = os.path.dirname(os.path.abspath(__file__))
    main_dir = os.path.dirname(compiler_dir)
    root_dir = os.path.dirname(main_dir)
    
    src_dir = os.path.join(main_dir, "src")
    src_libs = os.path.join(src_dir, "libs")
    src_pathmap = os.path.join(src_dir, "pathmap.ini")
    src_cwsi = os.path.join(src_dir, "cwsi.py")
    
    timestamp = datetime.now().strftime("%d.%m.%Y_%H-%M")
    build_dir = os.path.join(root_dir, "build", timestamp)
    build_libs_dir = os.path.join(build_dir, "libs")
    
    output_exe_dir = os.path.join(build_libs_dir, "cymrakk", "cwsi")

    if not os.path.exists(src_pathmap):
        print(f"Error: {src_pathmap} not found!")
        return

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(src_pathmap, encoding='utf-8')
    
    embedded_map = {}
    libs_to_copy = set()
    
    if "LIBRARIES" in config:
        for key, value in config["LIBRARIES"].items():
            if value:
                p = pathlib.Path(value)
                if p.parts and p.parts[0] == "libs" and len(p.parts) > 1:
                    lib_name = p.parts[1]
                    libs_to_copy.add(lib_name)
                    rel_path = pathlib.Path("..") / ".." / "libs" / pathlib.Path(*p.parts[1:])
                    embedded_map[key] = str(rel_path)
                else:
                    embedded_map[key] = value

    if "MODULES" in config:
        for key, value in config["MODULES"].items():
            embedded_map[key] = value if value else ""

    shutil.rmtree(build_dir, ignore_errors=True)
    os.makedirs(build_libs_dir, exist_ok=True)

    for lib_name in libs_to_copy:
        specific_src_lib = os.path.join(src_libs, lib_name)
        if os.path.exists(specific_src_lib):
            shutil.copytree(specific_src_lib, os.path.join(build_libs_dir, lib_name), dirs_exist_ok=True)
            print(f"Copied library to build\\{timestamp}\\libs: {lib_name}")

    with open(src_cwsi, 'r', encoding='utf-8') as f:
        code = f.read()
    
    map_replacement = f"CWSI_LIBS_MAP = {repr(embedded_map)}"
    modified_code = code.replace("CWSI_LIBS_MAP = {}", map_replacement)
    
    temp_cwsi = os.path.join(src_dir, "cwsi_temp.py")
    with open(temp_cwsi, 'w', encoding='utf-8') as f:
        f.write(modified_code)

    os.chdir(src_dir)
    subprocess.run(["pyinstaller", "--onefile", "-y", "-n", "cwsi", "cwsi_temp.py"], check=True)

    final_exe_path = os.path.join(output_exe_dir, "cwsi.exe")
    os.makedirs(output_exe_dir, exist_ok=True)
    shutil.move(os.path.join(src_dir, "dist", "cwsi.exe"), final_exe_path)
    print(f"Moved cwsi.exe to build\\{timestamp}\\libs\\cymrakk\\cwsi\\")
    
    release_modules_dir = os.path.join(output_exe_dir, "modules")
    os.makedirs(release_modules_dir, exist_ok=True)
    
    for file_name in os.listdir(src_dir):
        if file_name.endswith(".py") and file_name not in ["cwsi.py", "cwsi_temp.py"]:
            shutil.copy(os.path.join(src_dir, file_name), os.path.join(release_modules_dir, file_name))
    print(f"Copied modules to build\\{timestamp}\\libs\\cymrakk\\cwsi\\modules\\")

    start_bat_path = os.path.join(build_dir, "start.bat")
    bat_content = (
        "@echo off\n"
        'start "" "%~dp0libs\\cymrakk\\cwsi\\cwsi.exe"\n'
        "exit\n"
    )
    with open(start_bat_path, "w", encoding="utf-8") as bat_file:
        bat_file.write(bat_content)
    print(f"Created start.bat in build\\{timestamp}\\")

    os.remove(temp_cwsi)
    shutil.rmtree(os.path.join(src_dir, "dist"), ignore_errors=True)
    shutil.rmtree(os.path.join(src_dir, "build"), ignore_errors=True)
    if os.path.exists(os.path.join(src_dir, "cwsi.spec")):
        os.remove(os.path.join(src_dir, "cwsi.spec"))
    
    print("--- COMPILE SUCCESSFUL ---")

if __name__ == "__main__":
    build_project()
