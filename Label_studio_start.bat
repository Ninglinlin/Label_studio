
@echo off
call conda activate label-studio
cd /d D:\datasets

set SENTRY_DSN=
set LABEL_STUDIO_DISABLE_SENTRY=1
concurrently "python http_server.py" "label-studio-ml start D:\Codes\LMM\Label_studio\doubao_mlbackend --port 9090" "label-studio"

pause