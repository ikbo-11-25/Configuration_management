@echo off
setlocal
cd /d "%~dp0.."
call run.bat --vfs examples\vfs\deep --startup examples\scripts\stage2.txt
call run.bat --vfs examples\vfs\deep --startup examples\scripts\stage2-error.txt --headless
call run.bat --vfs examples\vfs\deep --startup missing.txt --headless
call run.bat --unknown
