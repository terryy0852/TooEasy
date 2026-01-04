@echo off
echo Starting Flask Server...
cd /d "%~dp0"

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development
set FLASK_DEBUG=1

echo Flask App: %FLASK_APP%
echo Environment: %FLASK_ENV%
echo Starting server on http://127.0.0.1:5000

REM Start Flask development server
flask run --host=127.0.0.1 --port=5000 --debugger --reload

pause