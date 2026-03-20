@echo off
setlocal enabledelayedexpansion
rem Türkçe karakter ve emoji uyumu için cmd ayarları
reg add "HKCU\Console" /v FaceName /t REG_SZ /d "Consolas" /f >nul 2>&1
reg add "HKCU\Console" /v CodePage /t REG_DWORD /d 65001 /f >nul 2>&1
chcp 65001 >nul

rem Hacker teması: siyah arkaplan, yeşil yazı
color 0A

echo USB Hub - Kurulum baslasin mi? (E/H)
set /p choice=
if /i "%choice%" neq "E" (
    echo Kurulum iptal edildi.
    exit /b
)
timeout /t 5
echo USB Hub - kuruluyor

echo [                    ] 0%%
set /a _progress=0
:progressLoop
if %_progress% GEQ 20 goto progressDone
set /a _progress+=1
set /a _filled=_progress
set /a _empty=20-_filled
set "_bar=["
for /l %%i in (1,1,%_filled%) do set "_bar=!_bar!#"
for /l %%i in (1,1,%_empty%) do set "_bar=!_bar! "
set "_bar=!_bar!] %_progress%%%%"
<nul set /p =!_bar!
ping -n 1 127.0.0.1 >nul
goto progressLoop
:progressDone
echo.

pip install pywebview pyinstaller --quiet

echo Derleniyor...
python -m PyInstaller --onefile --noconsole --name "USBHub" --add-data "index.html;." app.py

echo.
echo kurulum tamamlandi.
echo Dist klasorundeki USBHub.exe dosyasini caliştirabilirsiniz.
pause
