: << 'CMDBLOCK'
@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_NAME=%~1"
if exist "%ProgramFiles%\Git\bin\bash.exe" (
  "%ProgramFiles%\Git\bin\bash.exe" "%SCRIPT_DIR%%SCRIPT_NAME%"
  exit /b %errorlevel%
)
if exist "%ProgramFiles(x86)%\Git\bin\bash.exe" (
  "%ProgramFiles(x86)%\Git\bin\bash.exe" "%SCRIPT_DIR%%SCRIPT_NAME%"
  exit /b %errorlevel%
)
for /f "delims=" %%i in ('where bash 2^>nul') do (
  "%%i" "%SCRIPT_DIR%%SCRIPT_NAME%"
  exit /b %errorlevel%
)
exit /b 0
CMDBLOCK

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd -P)
SCRIPT_NAME=$1
exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}"
