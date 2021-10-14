@echo off

python main.py %* || (set /p _="Press [Enter] to continue... ")
