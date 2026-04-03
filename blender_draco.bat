@echo off
:: Blender Draco Compression - Windows Launcher
:: Usage: blender_draco.bat [options] input_file
:: 
:: Options:
::   -i FILE       Input file
::   -o FILE       Output file (default: input_compressed.glb)
::   --draco-level N    Compression level 0-10 (default: 7)
::   --resize-textures  Enable texture resizing (default)
::   --no-resize        Disable texture resizing
::   --texture-size N   Max texture size (default: 512)
::   --batch            Batch mode (input is directory)
::   --output-dir DIR   Output directory for batch mode
::   --format glb|gltf  Output format (default: glb)
::   -q, --quiet        Quiet mode
::   -h, --help         Show help
::
:: Examples:
::   blender_draco.bat model.glb
::   blender_draco.bat -i model.glb -o compressed.glb --draco-level 10
::   blender_draco.bat --batch .\models\ --output-dir .\compressed\

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

set "BLENDER_PATHS[0]=C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
set "BLENDER_PATHS[1]=C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
set "BLENDER_PATHS[2]=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
set "BLENDER_PATHS[3]=C:\Program Files\Blender Foundation\Blender 4.1\blender.exe"
set "BLENDER_PATHS[4]=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
set "BLENDER_PATHS[5]=C:\Program Files\Blender Foundation\Blender 3.6\blender.exe"
set "BLENDER_PATHS[6]=C:\Program Files\Blender Foundation\Blender 3.5\blender.exe"
set "BLENDER_PATHS[7]=C:\Program Files\Blender Foundation\Blender 3.4\blender.exe"
set "BLENDER_PATHS[8]=C:\Program Files\Blender Foundation\Blender 3.3\blender.exe"
set "BLENDER_PATHS[9]=%LOCALAPPDATA%\Programs\Blender Foundation\Blender 4.4\blender.exe"
set "BLENDER_PATHS[10]=%LOCALAPPDATA%\Programs\Blender Foundation\Blender 4.3\blender.exe"
set "BLENDER_PATHS[11]=%LOCALAPPDATA%\Programs\Blender Foundation\Blender 4.2\blender.exe"
set "BLENDER_PATHS[12]=%LOCALAPPDATA%\Programs\Blender Foundation\Blender 4.0\blender.exe"
set "BLENDER_PATHS[13]=%LOCALAPPDATA%\Programs\Blender Foundation\Blender 3.6\blender.exe"

if not "%BLENDER_PATH%"=="" (
    set "BLENDER_EXE=%BLENDER_PATH%"
    goto :find_blender
)

set "BLENDER_EXE="
for /L %%i in (0,1,13) do (
    if "!BLENDER_PATHS[%%i]!"=="" (
        if exist "!BLENDER_PATHS[%%i]!" (
            set "BLENDER_EXE=!BLENDER_PATHS[%%i]!"
            goto :found_blender
        )
    )
)

:find_blender
if exist "%BLENDER_EXE%" goto :found_blender

:: Try to find Blender in PATH
where blender >nul 2>&1
if %ERRORLEVEL%==0 (
    for /f "delims=" %%i in ('where blender') do (
        set "BLENDER_EXE=%%i"
        goto :found_blender
    )
)

echo Error: Blender not found!
echo.
echo Please either:
echo   1. Install Blender from https://blender.org
echo   2. Set BLENDER_PATH environment variable
echo   3. Edit this script to add your Blender path
echo.
pause
exit /b 1

:found_blender
echo Using Blender: %BLENDER_EXE%

set "COMPRESS_SCRIPT=%SCRIPT_DIR%\compress.py"

if not exist "%COMPRESS_SCRIPT%" (
    echo Error: compress.py not found in %SCRIPT_DIR%
    pause
    exit /b 1
)

:: Build command
set "CMD=%BLENDER_EXE% --background --python "%COMPRESS_SCRIPT%" --"

:: Parse arguments
:set_args
if "%~1"=="" goto :run_cmd

if /i "%~1"=="-i" (
    set "CMD=%CMD% -i %~2"
    shift
    shift
    goto :set_args
)

if /i "%~1"=="-o" (
    set "CMD=%CMD% -o %~2"
    shift
    shift
    goto :set_args
)

if /i "%~1"=="-d" (
    set "CMD=%CMD% --output-dir %~2"
    shift
    shift
    goto :set_args
)

if /i "%~1"=="--output-dir" (
    set "CMD=%CMD% --output-dir %~2"
    shift
    shift
    goto :set_args
)

if /i "%~1"=="--draco-level" (
    set "CMD=%CMD% --draco-level %~2"
    shift
    shift
    goto :set_args
)

if /i "%~1"=="--texture-size" (
    set "CMD=%CMD% --texture-size %~2"
    shift
    shift
    goto :set_args
)

if /i "%~1"=="--format" (
    set "CMD=%CMD% --format %~2"
    shift
    shift
    goto :set_args
)

if /i "%~1"=="--batch" (
    set "CMD=%CMD% --batch"
    shift
    goto :set_args
)

if /i "%~1"=="--resize-textures" (
    set "CMD=%CMD% --resize-textures"
    shift
    goto :set_args
)

if /i "%~1"=="--no-resize" (
    set "CMD=%CMD% --no-resize"
    shift
    goto :set_args
)

if /i "%~1"=="-q" (
    set "CMD=%CMD% -q"
    shift
    goto :set_args
)

if /i "%~1"=="--quiet" (
    set "CMD=%CMD% --quiet"
    shift
    goto :set_args
)

if /i "%~1"=="-h" (
    set "CMD=%CMD% -h"
    shift
    goto :run_cmd
)

if /i "%~1"=="--help" (
    set "CMD=%CMD% --help"
    shift
    goto :run_cmd
)

:: Check if it looks like a file/dir (not an option)
echo %~1 | findstr /b /c:"-" >nul
if ERRORLEVEL 1 (
    set "CMD=%CMD% "%~1""
    shift
    goto :set_args
)

:: Unknown option, pass through
set "CMD=%CMD% %1"
shift
goto :set_args

:run_cmd
echo.
%CMD%
set ERROR_CODE=%ERRORLEVEL%

if %ERROR_CODE% neq 0 (
    echo.
    echo Compression failed with error code %ERROR_CODE%
)

endlocal
exit /b %ERROR_CODE%
