@echo off
REM ===================================
REM 任务计划管理菜单
REM ===================================

:MENU
cls
echo.
echo ====================================
echo    📅 QT 任务计划管理菜单
echo ====================================
echo.
echo 当前任务: QT_DailyStrategyCheck
echo.
echo [1] 查看任务详情
echo [2] 立即运行任务（测试）
echo [3] 启用任务
echo [4] 禁用任务
echo [5] 删除任务
echo [6] 修改执行时间
echo [7] 查看运行历史
echo [0] 退出
echo.
echo ====================================
set /p choice=请选择操作 (0-7): 

if "%choice%"=="1" goto INFO
if "%choice%"=="2" goto RUN
if "%choice%"=="3" goto ENABLE
if "%choice%"=="4" goto DISABLE
if "%choice%"=="5" goto DELETE
if "%choice%"=="6" goto CHANGE_TIME
if "%choice%"=="7" goto HISTORY
if "%choice%"=="0" goto EXIT
goto MENU

:INFO
cls
echo.
echo ====================================
echo 📋 任务详情
echo ====================================
echo.
schtasks /Query /TN "QT_DailyStrategyCheck" /FO LIST /V
echo.
pause
goto MENU

:RUN
cls
echo.
echo ====================================
echo ▶️  运行任务
echo ====================================
echo.
echo 正在启动任务...
schtasks /Run /TN "QT_DailyStrategyCheck"
echo.
echo ✅ 任务已启动！
echo.
echo 请稍后查收邮件：qsswgl@gmail.com
echo.
pause
goto MENU

:ENABLE
cls
echo.
echo ====================================
echo ✅ 启用任务
echo ====================================
echo.
schtasks /Change /TN "QT_DailyStrategyCheck" /ENABLE
echo.
echo ✅ 任务已启用！
echo 将在工作日早上08:00自动运行
echo.
pause
goto MENU

:DISABLE
cls
echo.
echo ====================================
echo ⏸️  禁用任务
echo ====================================
echo.
schtasks /Change /TN "QT_DailyStrategyCheck" /DISABLE
echo.
echo ⏸️  任务已禁用！
echo 不会自动运行，可以手动启用
echo.
pause
goto MENU

:DELETE
cls
echo.
echo ====================================
echo 🗑️  删除任务
echo ====================================
echo.
echo ⚠️  警告: 此操作将永久删除任务计划！
echo.
set /p confirm=确认删除? (Y/N): 
if /i "%confirm%"=="Y" (
    schtasks /Delete /TN "QT_DailyStrategyCheck" /F
    echo.
    echo ✅ 任务已删除！
    echo.
    echo 如需重新创建，请运行: setup_daily_task.bat
    echo.
    pause
    goto EXIT
) else (
    echo.
    echo 已取消删除
    echo.
    pause
    goto MENU
)

:CHANGE_TIME
cls
echo.
echo ====================================
echo ⏰ 修改执行时间
echo ====================================
echo.
echo 当前执行时间: 08:00
echo.
echo 建议时间选项:
echo   [1] 07:00 - 早上7点（更早收到信号）
echo   [2] 08:00 - 早上8点（当前设置）
echo   [3] 09:00 - 早上9点（稍晚一些）
echo   [4] 21:00 - 晚上9点（美股开盘前）
echo   [5] 22:00 - 晚上10点（美股开盘时）
echo   [0] 取消
echo.
set /p time_choice=请选择 (0-5): 

if "%time_choice%"=="1" set new_time=07:00
if "%time_choice%"=="2" set new_time=08:00
if "%time_choice%"=="3" set new_time=09:00
if "%time_choice%"=="4" set new_time=21:00
if "%time_choice%"=="5" set new_time=22:00
if "%time_choice%"=="0" goto MENU

if defined new_time (
    echo.
    echo 正在修改执行时间为: %new_time%
    schtasks /Change /TN "QT_DailyStrategyCheck" /ST %new_time%
    echo.
    echo ✅ 执行时间已修改为: %new_time%
    echo.
    pause
) else (
    echo.
    echo ❌ 无效选择
    echo.
    pause
)
goto MENU

:HISTORY
cls
echo.
echo ====================================
echo 📊 运行历史
echo ====================================
echo.
echo 最近运行记录:
echo.
schtasks /Query /TN "QT_DailyStrategyCheck" /FO TABLE
echo.
echo 提示: 要查看详细日志，请打开"事件查看器"
echo   路径: Windows 日志 > 应用程序
echo   来源: Task Scheduler
echo.
pause
goto MENU

:EXIT
cls
echo.
echo ====================================
echo 👋 再见！
echo ====================================
echo.
echo 任务将继续在后台运行
echo 每个工作日早上自动执行策略检查
echo.
exit
