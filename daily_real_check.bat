@echo off
REM ===================================
REM 每日实时策略检查（带邮件通知）
REM ===================================
echo.
echo ====================================
echo 📊 每日实时策略检查
echo ====================================
echo 开始时间: %date% %time%
echo.

cd /d K:\QT

echo [1/3] 检查 TSLA 实时策略...
.\.venv\Scripts\python.exe src\pipeline\run_daily_check_email.py
echo.

echo [2/3] 检查 NVDA 实时策略...
.\.venv\Scripts\python.exe src\pipeline\run_daily_check_email_nvda.py
echo.

echo [3/3] 检查 INTC 实时策略...
.\.venv\Scripts\python.exe src\pipeline\run_daily_check_email_intc.py
echo.

echo ====================================
echo ✅ 所有实时策略检查完成！
echo ====================================
echo 结束时间: %date% %time%
echo.
echo 💡 请查收邮件：qsswgl@gmail.com
echo.

pause
