@echo off
title Metodos Numericos - Reconstruir
cd /d "%~dp0"

docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Docker Desktop no esta iniciado. Abrelo y vuelve a ejecutar este archivo.
    echo.
    pause
    exit /b 1
)

echo Reconstruyendo las imagenes con el codigo actual...
docker compose up -d --build --wait --wait-timeout 300
if errorlevel 1 (
    echo.
    echo  Fallo la reconstruccion. Revisa el mensaje de arriba.
    pause
    exit /b 1
)
echo Lista en http://localhost:8080
start "" http://localhost:8080
timeout /t 3 >nul
