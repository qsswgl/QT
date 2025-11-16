@echo off
chcp 65001 >nul
echo ============================================================
echo � 智能每日策略检查系统
echo ============================================================
echo.

echo [INFO] 激活Python虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo [INFO] 运行三个股票的每日策略并自动记录结果...
python src\pipeline\smart_daily_check.py

echo.
echo ============================================================
echo ✅ 每日检查完成!
echo ============================================================
echo.
echo 📁 结果文件:
echo    - 执行记录: strategy_execution_records.json
echo    - 策略信号: backtest_results\daily\signals_daily.csv
echo    - 交易记录: backtest_results\daily\trades_daily.csv
echo.
pause
