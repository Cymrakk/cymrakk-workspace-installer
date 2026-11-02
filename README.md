# Cymrakk WorkSpace Installer (CWSI)

A lightweight, automated bootstrap installer for quick development workspace deployment and environment setup on Windows.

# 🚀 How to Build the Program

Follow these simple steps to compile and build the **CWSI** project on your Windows machine.

> 💡 **Prerequisite:** Make sure you have `Python 3.x` and `Git` installed on your system.

### 🛠️ Step-by-Step Guide
1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/Cymrakk/cymrakk-workspace-installer
   ```

2. **Navigate** to the project root directory:
   ```cmd
   cd cymrakk-workspace-installer
   ```

3. **Install required dependencies** via `pip`:
   ```cmd
   pip install pyinstaller colorama
   ```
   
4. **Run the build script** to compile the program:
   * **For Git Bash:**
     ```bash
     ./build.bat
     ```
   * **For Command Prompt (CMD) / PowerShell:**
     ```cmd
     build.bat
     ```

---
> 📂 **Note:** Once the build process finishes, you will find your compiled executable and assets inside the `build` folder at the root directory, organized inside a timestamped folder named `DD.MM.YYYY_HH-MM`.

> ⚠️ **Windows Note:** If pyinstaller commands are not recognized, ensure your Python Scripts path is added to your Windows Environment Variables or try opening your Command Prompt (CMD) as an Administrator.

