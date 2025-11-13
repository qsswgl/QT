@echo off
chcp 65001 > nul
echo ========================================
echo 📊 TSLA 策略每周检查 (邮件推送版)
echo ========================================
echo.

cd /d K:\QT

echo [步骤 1/2] 更新 TSLA 数据...
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.update_data TSLA --start 2010-06-29
echo.

if %errorlevel% neq 0 (
    echo ⚠️ 数据更新失败!
    echo.
    echo 可能原因:
    echo 1. 网络连接问题
    echo 2. Yahoo Finance 服务暂时不可用 (限流)
    echo.
    echo ℹ️  将使用现有历史数据继续运行策略...
    echo.
)

echo ========================================
echo [步骤 2/2] 运行策略并发送邮件...
echo ========================================
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.run_weekly_check_email
echo.

if %errorlevel% neq 0 (
    echo ❌ 策略运行失败!
    echo.
    echo 请检查错误信息
    pause
    exit /b 1
)

echo ========================================
echo ✅ 每周检查完成!
echo ========================================
echo.
echo 📧 邮件提醒:
echo    - 已发送至: qsoft@139.com
echo    - 请检查邮箱(包括垃圾邮件箱)
echo.
echo 📂 本地文件:
echo    - 信号: backtest_results\improved\signals_improved.csv
echo    - 报告: backtest_results\improved\summary_improved.txt
echo.
echo 💡 提示:
echo    - 如果有新信号,邮件中会有详细说明
echo    - 无新信号时也会收到确认邮件
echo    - 邮件发送失败时可查看本地文件
echo.

pause
