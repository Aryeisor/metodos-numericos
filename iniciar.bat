@echo off
title Metodos Numericos - Iniciar
cd /d "%~dp0"

docker info >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Docker Desktop no esta iniciado.
    echo  Abrelo, espera a que diga "Engine running" y vuelve a ejecutar este archivo.
    echo.
    pause
    exit /b 1
)

echo Iniciando la aplicacion (la primera vez tarda varios minutos)...
docker compose up -d --wait --wait-timeout 300
if errorlevel 1 (
    echo.
    echo  La aplicacion no pudo iniciarse. Revisa los logs con:
    echo      docker compose logs backend
    echo.
    pause
    exit /b 1
)

echo Lista en http://localhost:8080
start "" http://localhost:8080
timeout /t 3 >nul
