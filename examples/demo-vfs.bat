@echo off
setlocal
cd /d "%~dp0.."
call run.bat --vfs examples\vfs\minimal --startup examples\scripts\stage2.txt --headless
call run.bat --vfs examples\vfs\files --startup examples\scripts\stage2.txt --headless
call run.bat --vfs examples\vfs\deep --startup examples\scripts\stage3.txt
call run.bat --vfs missing-directory --startup examples\scripts\stage2.txt --headless
