@echo off
chcp 65001 > nul
echo ========================================
echo 📊 TSLA 策略每周检查
echo ========================================
echo.

cd /d K:\QT

echo [步骤 1/3] 更新 TSLA 数据...
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
    echo    (如果数据较旧,信号可能不准确)
    echo.
)

echo ========================================
echo [步骤 2/3] 运行改进策略...
echo ========================================
echo.
k:/QT/.venv/Scripts/python.exe -m src.pipeline.run_improved_strategy
echo.

if %errorlevel% neq 0 (
    echo ❌ 策略运行失败!
    pause
    exit /b 1
)

echo ========================================
echo [步骤 3/3] 检查交易信号...
echo ========================================
echo.

set SIGNAL_FILE=backtest_results\improved\signals_improved.csv

if not exist "%SIGNAL_FILE%" (
    echo ❌ 未找到信号文件!
    echo 位置: %SIGNAL_FILE%
    pause
    exit /b 1
)

echo ✓ 信号文件已生成
echo.
echo 📂 信号文件位置:
echo    %SIGNAL_FILE%
echo.

REM 显示最后几行信号
echo 📋 最新信号:
echo ----------------------------------------
powershell -Command "Get-Content '%SIGNAL_FILE%' -Tail 3"
echo ----------------------------------------
echo.

echo ========================================
echo ✅ 每周检查完成!
echo ========================================
echo.
echo 📌 下一步:
echo.
echo 1. 打开信号文件: backtest_results\improved\signals_improved.csv
echo 2. 检查最新信号的日期是否是本周
echo 3. 如果有新信号:
echo    - 记录动作 (BUY/SELL)
echo    - 记录数量
echo    - 在 Firstrade 执行交易
echo.
echo 4. 如果没有新信号:
echo    - 无需操作
echo    - 下周继续检查
echo.

echo 按任意键打开信号文件...
pause > nul

start "" "%SIGNAL_FILE%"

echo.
echo 感谢使用! 下周见! 👋
echo.
pause
