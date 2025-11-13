@echo off
chcp 65001 > nul
echo ========================================
echo 测试多数据源系统
echo ========================================
echo.

cd /d "%~dp0"
call .venv\Scripts\activate.bat

echo 正在测试多数据源数据获取...
echo.
python -m src.pipeline.update_data_multi_source TSLA --days 10

echo.
echo ========================================
echo 测试完成
echo ========================================
pause
