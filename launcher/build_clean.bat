@echo off
title Build Launcher EXE (Clean)
echo =============================
echo  Build CLEAN du launcher
echo =============================
echo.

REM On se met dans le dossier du script
cd /d "%~dp0"

REM Python du PATH (remplace par un chemin complet si besoin)
set "PYTHON_EXE=python"

echo [*] Verif Python...
"%PYTHON_EXE%" --version || (
    echo [ERREUR] Python introuvable a :
    echo %PYTHON_EXE%
    pause
    exit /b 1
)

echo.
echo [*] Nettoyage ancien build...
if exist dist rd /s /q dist
if exist build rd /s /q build
if exist launcher.spec del launcher.spec

echo.
echo [*] Build sans icone...
"%PYTHON_EXE%" -m PyInstaller --onefile --noconsole launcher.py

echo.
echo [*] FIN du build.
echo  Si tout s'est bien passe, ton exe est dans : dist\launcher.exe
echo.

pause
