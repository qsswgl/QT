@echo off
chcp 65001 > nul
echo ================================
echo 测试 Gmail 邮件发送
echo ================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo 正在发送测试邮件...
python -m src.pipeline.test_daily_email

echo.
echo ================================
echo 测试完成
echo ================================
pause
