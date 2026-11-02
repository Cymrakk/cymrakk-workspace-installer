import ast
import configparser
import logging
import os
import pathlib
import shutil
import subprocess
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_file_imports(file_path: pathlib.Path) -> set:
    """Parses a file via AST and returns a set of top-level imported modules."""
    imports = set()
    if not file_path.exists():
        return imports
    try:
        tree = ast.parse(file_path.read_text(encoding='utf-8'), filename=str(file_path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    imports.add(node.module.split('.')[0])
    except Exception as e:
        logging.error(f"Failed to parse imports in {file_path}: {e}")
    return imports

def sync_imports(src_dir: pathlib.Path, modules_list: list, src_cwsi: pathlib.Path):
    if not src_cwsi.exists():
        return

    cwsi_imports = get_file_imports(src_cwsi)
    needed_imports = set()

    for mod_file in modules_list:
        needed_imports.update(get_file_imports(src_dir / mod_file))

    missing_imports = needed_imports - cwsi_imports - {'cwsi'}

    if missing_imports:
        try:
            original_content = src_cwsi.read_text(encoding='utf-8')
            import_lines = "".join(f"import {imp}\n" for imp in sorted(missing_imports))
            src_cwsi.write_text(import_lines + original_content, encoding='utf-8')
            logging.info(f"Synchronized missing imports to cwsi.py: {missing_imports}")
        except Exception as e:
            logging.error(f"Failed to update imports in cwsi.py: {e}")

def build_project():
    print("--- STARTING COMPILE ---")
    
    # Path resolution using pathlib
    compiler_dir = pathlib.Path(__file__).resolve().parent
    main_dir = compiler_dir.parent
    root_dir = main_dir.parent
    
    src_dir = main_dir / "src"
    src_libs = src_dir / "libs"
    src_pathmap = src_dir / "pathmap.ini"
    src_cwsi = src_dir / "cwsi.py"
    
    timestamp = datetime.now().strftime("%d.%m.%Y_%H-%M")
    build_dir = root_dir / "build" / timestamp
    build_libs_dir = build_dir / "libs"
    output_exe_dir = build_libs_dir / "cymrakk" / "cwsi"

    if not src_pathmap.exists():
        print(f"Error: {src_pathmap} not found!")
        return

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(src_pathmap, encoding='utf-8')
    
    embedded_map = {}
    libs_to_copy = set()
    modules_to_check = []
    
    if "LIBRARIES" in config:
        for key, value in config["LIBRARIES"].items():
            if value:
                p = pathlib.Path(value)
                if p.parts and p.parts[0] == "libs" and len(p.parts) > 1:
                    lib_name = p.parts[1]
                    libs_to_copy.add(lib_name)
                    rel_path = pathlib.Path("..") / ".." / ".." / p
                    embedded_map[key] = str(rel_path)
                else:
                    embedded_map[key] = value

    if "MODULES" in config:
        for key, value in config["MODULES"].items():
            embedded_map[key] = value if value else ""
            if key.endswith(".py"):
                modules_to_check.append(key)

    sync_imports(src_dir, modules_to_check, src_cwsi)

    shutil.rmtree(build_dir, ignore_errors=True)
    build_libs_dir.mkdir(parents=True, exist_ok=True)

    for lib_name in libs_to_copy:
        specific_src_lib = src_libs / lib_name
        if specific_src_lib.exists():
            shutil.copytree(specific_src_lib, build_libs_dir / lib_name, dirs_exist_ok=True)
            print(f"Copied library to build\\{timestamp}\\libs: {lib_name}")

    code = src_cwsi.read_text(encoding='utf-8')
    map_replacement = f"CWSI_LIBS_MAP = {repr(embedded_map)}"
    modified_code = code.replace("CWSI_LIBS_MAP = {}", map_replacement)
    
    temp_cwsi = src_dir / "cwsi_temp.py"
    temp_cwsi.write_text(modified_code, encoding='utf-8')

    try:
        subprocess.run(
            ["pyinstaller", "--onefile", "-y", "-n", "cwsi", "cwsi_temp.py"],
            cwd=str(src_dir), 
            check=True
        )

        output_exe_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_dir / "dist" / "cwsi.exe"), str(output_exe_dir / "cwsi.exe"))
        print(f"Moved cwsi.exe to build\\{timestamp}\\libs\\cymrakk\\cwsi\\")
        
        release_modules_dir = output_exe_dir / "modules"
        release_modules_dir.mkdir(parents=True, exist_ok=True)
        
        for file_path in src_dir.glob("*.py"):
            if file_path.name not in ["cwsi.py", "cwsi_temp.py"]:
                shutil.copy(file_path, release_modules_dir / file_path.name)
        print(f"Copied modules to build\\{timestamp}\\libs\\cymrakk\\cwsi\\modules\\")
        
        start_bat_path = build_dir / "start.bat"
        bat_content = "@echo off\nstart \"\" \"%~dp0libs\\cymrakk\\cwsi\\cwsi.exe\"\nexit\n"
        start_bat_path.write_text(bat_content, encoding="utf-8")
        print(f"Created start.bat in build\\{timestamp}\\")
        
        print("--- COMPILE SUCCESSFUL ---")

    finally:
        if temp_cwsi.exists():
            temp_cwsi.unlink()
        shutil.rmtree(src_dir / "dist", ignore_errors=True)
        shutil.rmtree(src_dir / "build", ignore_errors=True)
        
        spec_file = src_dir / "cwsi.spec"
        if spec_file.exists():
            spec_file.unlink()

if __name__ == "__main__":
    build_project()
