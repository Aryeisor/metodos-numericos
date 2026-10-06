@echo off
title Metodos Numericos - Detener
cd /d "%~dp0"
docker compose down
timeout /t 3 >nul
