@echo off
setlocal
cd /d "%~dp0.."
call run.bat --vfs examples\vfs\deep --startup examples\scripts\stage5.txt
call run.bat --vfs examples\vfs\deep --startup examples\scripts\stage5-chown-error.txt --headless
call run.bat --vfs examples\vfs\deep --startup examples\scripts\stage5-rm-error.txt --headless
call run.bat --vfs examples\vfs\deep --startup examples\scripts\success.txt --headless
