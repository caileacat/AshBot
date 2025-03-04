@echo off
title AshBot Watchdog
echo Killing existing Python processes...

:: Kill any running Python processes
taskkill /F /IM python.exe 2>nul

:: Change directory to the bot folder (Modify this if needed)
cd /d "%~dp0"

:: Check if we're in the virtual environment
if not exist .venv\Scripts\activate (
    echo Virtual environment not found! Please set up .venv first.
    pause
    exit
)

:: Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

:: Start the watchdog script
echo Starting Watchdog...
python watchdog_script.py

:: Keep the window open if Watchdog crashes
echo Watchdog has stopped running.
pause
