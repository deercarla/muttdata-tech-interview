@echo off

:: Activate virtual environment
call C:\Users\Carla\Desktop\Carla--de-Erausquin\env\Scripts\activate.bat

:: Set the current directory to where your script is located
cd /d %~dp0

:: Get today's date in YYYY-MM-DD format
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set YYYY=%datetime:~0,4%
set MM=%datetime:~4,2%
set DD=%datetime:~6,2%
set TODAY=%YYYY%-%MM%-%DD%

:: Run the script for today's date
python app.py bulk bitcoin ethereum cardano %TODAY% %TODAY% --pg

:: Optional: Add pause to see any error messages
pause