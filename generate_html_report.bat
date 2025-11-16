@echo off
chcp 65001 >nul
echo ============================================================
echo 📊 生成策略分析HTML图形报告
echo ============================================================
echo.

echo [INFO] 激活Python虚拟环境...
call .venv\Scripts\activate.bat

echo.
echo [INFO] 生成交互式HTML图形报告...
python src\visualization\quick_report.py

echo.
echo ============================================================
echo ✅ HTML报告生成完成!
echo ============================================================
echo.
echo 💡 报告已自动在浏览器中打开
echo 📁 文件位置: TSLA_report_*.html
echo.
echo 报告包含:
echo   - 📈 资金曲线图
echo   - 📊 信号分布图
echo   - 📉 回撤曲线图
echo   - 📋 关键统计数据
echo.
pause
