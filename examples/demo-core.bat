@echo off
setlocal
cd /d "%~dp0.."
call run.bat --vfs examples\vfs\deep --startup examples\scripts\stage4.txt
call run.bat --vfs examples\vfs\deep --startup examples\scripts\stage4-cal-error.txt --headless
call run.bat --vfs examples\vfs\deep --startup examples\scripts\stage4-ls-error.txt --headless
