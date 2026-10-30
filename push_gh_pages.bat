@echo off
cd /d "%~dp0"
echo Reminder: Slovenian notebooks are the source. If you edited them, port the change to notebooks/en/ before deploying.
python tools\check_translation_sync.py
if not errorlevel 1 goto build
set /p ANSWER="Translation drift reported above. Continue anyway? (y/N) "
if /i not "%ANSWER%"=="y" (
    echo Aborted.
    exit /b 1
)

:build
call build_book.bat
if errorlevel 1 (echo build failed & exit /b 1)

ghp-import -n -p -f _site
if errorlevel 1 (echo ghp-import failed & exit /b 1)
