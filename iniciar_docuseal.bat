@echo off
title DocuSeal - Servidor Local
setlocal

set "APP_DIR=%~dp0"
set "DATA_DIR=%LOCALAPPDATA%\DocuSealDados"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

set "PATH=%APP_DIR%ruby\bin;%APP_DIR%ruby\msys64\usr\bin;%PATH%"
set "RAILS_ENV=production"
set "SECRET_KEY_BASE=docuseal_windows_local_secret_key_2026_artur"
set "DATABASE_URL=sqlite3:%DATA_DIR:\=/%/docuseal.sqlite3"
set "STORAGE_PATH=%DATA_DIR%\storage"
set "PORT=3000"
set "RAILS_SERVE_STATIC_FILES=true"
set "RAILS_LOG_TO_STDOUT=true"

cd /d "%APP_DIR%app"
echo Preparando banco de dados do DocuSeal...
call bundle exec rails db:prepare

echo Abrindo DocuSeal no navegador (http://localhost:3000)...
start "" cmd /c "timeout /t 4 /nobreak >nul && start http://localhost:3000"
call bundle exec puma -C config/puma.rb