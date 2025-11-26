@echo off
REM ============================================================
REM 日度策略定时执行脚本 - 开盘后10分钟执行
REM 
REM 执行时间: 美东时间 9:40 AM (北京时间 22:40/23:40)
REM 
REM 功能:
REM 1. 获取盘中实时报价
REM 2. 分析市场环境
REM 3. 运行3个策略(NVDA/TSLA/INTC)
REM 4. 推送邮件通知
REM ============================================================

echo ============================================================
echo 📊 日度策略自动执行 (开盘后10分钟)
echo ============================================================
echo 执行时间: %date% %time%
echo ============================================================
echo.

REM 切换到项目目录
cd /d K:\QT

REM 检查市场是否开盘
echo [步骤 1/4] 🔍 检查市场状态...
python -c "from src.utils.realtime_quotes_manager import RealtimeQuotesManager; mgr = RealtimeQuotesManager(); status = mgr.get_market_status(); print(f'{status[\"message\"]} - {status[\"current_time_beijing\"]}')"

echo.
echo [步骤 2/4] 📊 运行NVDA日度策略...
python src/pipeline/run_daily_check_email_nvda.py
echo.

echo [步骤 3/4] 📊 运行TSLA日度策略...
python src/pipeline/run_daily_check_email.py
echo.

echo [步骤 4/4] 📊 运行INTC日度策略...
python src/pipeline/run_daily_check_email_intc.py
echo.

echo ============================================================
echo ✅ 所有策略执行完成!
echo ============================================================
echo.
echo 💡 提示:
echo   - 已发送3封邮件至: qsswgl@gmail.com
echo   - 请检查邮箱查看每日策略报告
echo   - 如有交易信号,请及时在Firstrade执行
echo.

REM 保存日志
echo [%date% %time%] 日度策略执行完成 >> logs\daily_strategy_execution.log

pause
