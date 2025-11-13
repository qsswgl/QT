@echo off
REM 日志记录批处理 - 记录策略执行情况
echo ============================================================
echo 策略执行日志记录器
echo ============================================================
echo.

REM 切换到项目目录
cd /d K:\QT

REM 激活虚拟环境（如果存在）
if exist venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 执行日志记录脚本
echo 正在记录策略执行情况...
python src\pipeline\log_strategy_execution.py

echo.
echo ============================================================
echo 执行完成
echo ============================================================
pause
