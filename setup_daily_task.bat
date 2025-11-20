@echo off
REM ===================================
REM 设置 Windows 任务计划
REM 每个工作日自动执行日度策略检查
REM ===================================

echo.
echo ====================================
echo 🔧 设置 Windows 任务计划
echo ====================================
echo.

REM 删除已存在的任务（如果有）
echo 🗑️  删除旧任务（如果存在）...
schtasks /Delete /TN "QT_DailyStrategyCheck" /F >nul 2>&1

REM 创建新任务
echo 📝 创建新任务计划...
echo.
echo 任务名称: QT_DailyStrategyCheck
echo 执行时间: 每个工作日（周一至周五）早上 8:00
echo 执行脚本: K:\QT\daily_real_check.bat
echo.

schtasks /Create ^
  /TN "QT_DailyStrategyCheck" ^
  /TR "K:\QT\daily_real_check.bat" ^
  /SC WEEKLY ^
  /D MON,TUE,WED,THU,FRI ^
  /ST 08:00 ^
  /RL HIGHEST ^
  /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================
    echo ✅ 任务计划创建成功！
    echo ====================================
    echo.
    echo 📋 任务详情:
    echo   - 任务名称: QT_DailyStrategyCheck
    echo   - 执行时间: 工作日（周一-周五）08:00
    echo   - 执行脚本: K:\QT\daily_real_check.bat
    echo   - 权限级别: 最高权限
    echo.
    echo 💡 说明:
    echo   - 系统将在每个工作日早上8点自动执行策略检查
    echo   - 检查完成后会自动发送邮件到 qsswgl@gmail.com
    echo   - 时间设置为美股盘前（北京时间早上8点 = 美东晚上7点）
    echo.
    echo 🔍 查看任务:
    echo   schtasks /Query /TN "QT_DailyStrategyCheck" /V /FO LIST
    echo.
    echo 🗑️  删除任务:
    echo   schtasks /Delete /TN "QT_DailyStrategyCheck" /F
    echo.
    echo 🔧 手动运行任务:
    echo   schtasks /Run /TN "QT_DailyStrategyCheck"
    echo.
) else (
    echo.
    echo ====================================
    echo ❌ 任务计划创建失败！
    echo ====================================
    echo.
    echo 可能原因:
    echo   - 权限不足（请以管理员身份运行）
    echo   - 路径错误
    echo.
    echo 请以管理员身份重新运行此脚本
    echo.
)

pause
