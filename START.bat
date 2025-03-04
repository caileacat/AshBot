@echo off
title AshBot Direct Launch
echo Killing existing Python processes...

:: Kill any running Python processes
taskkill /F /IM python.exe 2>nul

:: Change directory to the bot folder (Modify this if needed)
cd /d "%~dp0"

:: Check if the virtual environment exists
if not exist .venv\Scripts\activate (
    echo Virtual environment not found! Please set up .venv first.
    pause
    exit
)

:: Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

:: Start the bot directly
echo Starting AshBot...
python ashBot.py

:: Keep the window open if the bot crashes
echo AshBot has stopped running.
pause
