@echo off
python -m PyInstaller Oszust_OS_Music_Tools.py ^
    --noconsole ^
    --add-data "data;data" ^
    --add-data "AutoUpdater.py;." ^
    --add-data "Oszust_OS_Music_Tools.py;."