@echo off
rem Build both language versions and assemble the site in _site\ (sl at root, en under en\).
cd /d "%~dp0"
rem jupyter-book always appends _build\ to --path-output, hence _build\sl\_build\html.
if exist lv_book\_build\sl\_build\html rmdir /s /q lv_book\_build\sl\_build\html
if exist lv_book\_build\en\_build\html rmdir /s /q lv_book\_build\en\_build\html
call jupyter-book build lv_book --path-output lv_book\_build\sl
if errorlevel 1 (echo jupyter-book build [sl] failed & exit /b 1)
call jupyter-book build lv_book --config "%~dp0lv_book\_config.en.yml" --toc "%~dp0lv_book\_toc.en.yml" --path-output lv_book\_build\en
if errorlevel 1 (echo jupyter-book build [en] failed & exit /b 1)

if exist _site rmdir /s /q _site
mkdir _site\en
xcopy /e /i /q /y lv_book\_build\sl\_build\html _site >nul
if errorlevel 1 (echo copy of sl html failed & exit /b 1)
xcopy /e /i /q /y lv_book\_build\en\_build\html _site\en >nul
if errorlevel 1 (echo copy of en html failed & exit /b 1)
type nul > _site\.nojekyll

echo.
echo Site assembled in _site\. Open locally:
echo   %~dp0_site\index.html
echo   %~dp0_site\en\index.html
