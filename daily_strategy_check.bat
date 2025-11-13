@echo off
chcp 65001 > nul
echo ========================================
echo 📊 TSLA 日度策略检查 (每天1次)
echo ========================================
echo.

cd /d K:\QT

echo [步骤 1/3] 更新 TSLA 数据 (多数据源模式)...
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.update_data_multi_source TSLA --days 30
echo.

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ 数据更新失败 - 可能原因:
    echo    • 所有数据源都遇到频率限制
    echo    • 网络连接问题
    echo.
    echo 💡 提示: 可以配置备用数据源API密钥
    echo    查看文档: docs\multi_data_sources.md
    echo.
    echo ✓ 继续使用现有数据运行策略...
    echo.
    timeout /t 3 /nobreak >nul
)

echo ========================================
echo [步骤 2/3] 运行日度策略...
echo ========================================
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.run_daily_strategy
echo.

if %errorlevel% neq 0 (
    echo ❌ 策略运行失败!
    pause
    exit /b 1
)

echo ========================================
echo [步骤 3/3] 发送邮件通知...
echo ========================================
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.run_daily_check_email
echo.

echo ========================================
echo ✅ 日度策略检查完成!
echo ========================================
echo.
echo 📧 邮件主题: [TSLA策略] 日度策略
echo 📂 信号文件: backtest_results\daily\signals_daily.csv
echo.

pause
