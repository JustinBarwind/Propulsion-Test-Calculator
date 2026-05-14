@echo off

echo =====================================
echo  Rocket Thrust Test Starting...
echo =====================================

REM activate virtual environment
call venv\Scripts\activate

REM run main script
python main.py

echo.
echo =====================================
echo  Test Complete
echo =====================================
pause
