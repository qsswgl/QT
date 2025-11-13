@echo off
REM 每周策略回顾批处理 - 分析过去7天的策略执行情况
echo ============================================================
echo 每周策略回顾分析
echo ============================================================
echo.

REM 切换到项目目录
cd /d K:\QT

REM 激活虚拟环境（如果存在）
if exist .venv\Scripts\activate.bat (
    echo 激活虚拟环境...
    call .venv\Scripts\activate.bat
)

REM 执行周回顾脚本
echo 正在分析过去7天的策略执行情况...
python src\pipeline\weekly_strategy_review.py

echo.
echo ============================================================
echo 执行完成
echo ============================================================
echo.
echo 提示: 请查看 STRATEGY_EXECUTION_LOG.md 中的周回顾报告
echo       根据分析结果调整策略参数
echo.
pause
