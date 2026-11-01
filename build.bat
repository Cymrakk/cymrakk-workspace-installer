@echo off
title CWSI Project Compiler
set ROOT_DIR=%~dp0
set COMPILER_PATH=%ROOT_DIR%main\compiler\compiler.py

echo ==================================================
echo  Starting CWSI Build Process
echo ==================================================
echo Root Dir:     %ROOT_DIR%
echo Compiler:     %COMPILER_PATH%
echo --------------------------------------------------

if not exist "%COMPILER_PATH%" (
    echo [ERROR] compiler.py not found at: %COMPILER_PATH%
    goto error
)

python "%COMPILER_PATH%"
if %errorlevel% neq 0 goto error

echo ==================================================
echo  [SUCCESS] Build finished successfully!
echo ==================================================
pause
exit /b 0

:error
echo ==================================================
echo  [FAILED] Something went wrong during the build.
echo ==================================================
pause
exit /b 1
