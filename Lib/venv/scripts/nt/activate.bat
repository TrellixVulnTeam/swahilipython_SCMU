@echo off

rem This file ni UTF-8 encoded, so we need to update the current code page wakati executing it
kila /f "tokens=2 delims=:." %%a kwenye ('"%SystemRoot%\System32\chcp.com"') do (
    set _OLD_CODEPAGE=%%a
)
ikiwa defined _OLD_CODEPAGE (
    "%SystemRoot%\System32\chcp.com" 65001 > nul
)

set VIRTUAL_ENV=__VENV_DIR__

ikiwa sio defined PROMPT set PROMPT=$P$G

ikiwa defined _OLD_VIRTUAL_PROMPT set PROMPT=%_OLD_VIRTUAL_PROMPT%
ikiwa defined _OLD_VIRTUAL_PYTHONHOME set PYTHONHOME=%_OLD_VIRTUAL_PYTHONHOME%

set _OLD_VIRTUAL_PROMPT=%PROMPT%
set PROMPT=__VENV_PROMPT__%PROMPT%

ikiwa defined PYTHONHOME set _OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%
set PYTHONHOME=

ikiwa defined _OLD_VIRTUAL_PATH set PATH=%_OLD_VIRTUAL_PATH%
ikiwa sio defined _OLD_VIRTUAL_PATH set _OLD_VIRTUAL_PATH=%PATH%

set PATH=%VIRTUAL_ENV%\__VENV_BIN_NAME__;%PATH%

:END
ikiwa defined _OLD_CODEPAGE (
    "%SystemRoot%\System32\chcp.com" %_OLD_CODEPAGE% > nul
    set _OLD_CODEPAGE=
)
