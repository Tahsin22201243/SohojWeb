@echo off
REM runserver_visible.bat — opens a new cmd window and runs Django dev server using venv python
REM Then polls the server and opens the default browser when ready.
SET PY_PATH=D:\SohojWeb\venv\Scripts\python.exe
+SET MANAGE=manage.py
+
START "Django Server" cmd /k "%PY_PATH% %MANAGE% runserver"
+
REM Poll localhost until server responds, then open the browser.
powershell -NoProfile -Command "for (;;) { try { $r = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/' -TimeoutSec 2; if ($r.StatusCode -eq 200) { break } } catch { } Start-Sleep -Seconds 1 }; Start-Process 'http://127.0.0.1:8000/'"
