@echo off
chcp 65001 >nul
echo ====================================
echo   Music Button - Создание EXE файла
echo ====================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не найден!
    echo Установите Python с https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Проверка Python... OK
echo.

REM Установка зависимостей
echo [2/4] Установка зависимостей...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить зависимости!
    pause
    exit /b 1
)
echo Зависимости установлены... OK
echo.

REM Установка PyInstaller
echo [3/4] Установка PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось установить PyInstaller!
    pause
    exit /b 1
)
echo PyInstaller установлен... OK
echo.

REM Сборка EXE файла
echo [4/4] Создание EXE файла...
echo Это может занять несколько минут...
echo.

pyinstaller --onefile ^
            --windowed ^
            --name "MusicButton" ^
            --icon=NONE ^
            --hidden-import=pygame ^
            --hidden-import=pygame.mixer ^
            --exclude-module=tkinter.test ^
            --exclude-module=pygame.tests ^
            main.py

if %errorlevel% neq 0 (
    echo ОШИБКА: Не удалось создать EXE файл!
    pause
    exit /b 1
)

echo.
echo ====================================
echo   СБОРКА ЗАВЕРШЕНА УСПЕШНО!
echo ====================================
echo.
echo Готовый файл находится в папке: dist\MusicButton.exe
echo.
echo Вы можете скопировать этот файл в любое место
echo и запускать без установки Python!
echo.
echo Для распространения программы просто передайте
echo файл MusicButton.exe другим пользователям.
echo.
pause
