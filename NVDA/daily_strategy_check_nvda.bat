@echo off
chcp 65001 > nul
echo ========================================
echo 📊 NVDA 日度策略检查 (每天1次)
echo ========================================
echo.

cd /d K:\QT

echo [步骤 1/4] 更新 NVDA 数据 (多数据源模式)...
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.update_data_multi_source NVDA --days 30 --output NVDA\data\sample_nvda.csv
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
echo [步骤 2/4] 运行NVDA日度策略...
echo ========================================
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.run_daily_strategy_nvda
echo.

if %errorlevel% neq 0 (
    echo ❌ 策略运行失败!
    pause
    exit /b 1
)

echo ========================================
echo [步骤 3/4] 发送邮件通知...
echo ========================================
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.run_daily_check_email_nvda
echo.

echo ========================================
echo [步骤 4/4] 记录策略执行日志...
echo ========================================
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.log_strategy_execution_nvda
echo.

echo ========================================
echo ✅ NVDA日度策略检查完成!
echo ========================================
echo.
echo 📧 邮件主题: [NVDA策略] 日度策略
echo 📂 信号文件: NVDA\backtest_results\daily\signals_daily.csv
echo 📝 执行日志: NVDA\STRATEGY_EXECUTION_LOG.md
echo.

pause
