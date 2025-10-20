@echo off
REM runserver.bat — starts Django dev server using project venv Python
REM Usage: runserver.bat [optional additional manage.py args]
REM Wrapper to ensure double-click behavior matches the visible runner.
REM Forward any args to the visible runner.
START "Run Django (visible)" "%~dp0runserver_visible.bat" %*
