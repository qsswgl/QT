"""
智能每日策略检查

功能:
1. 运行每日策略
2. 自动记录执行结果
3. 发送邮件通知
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import pandas as pd

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from analysis.strategy_analyzer import StrategyAnalyzer
from notification.email_service import EmailService


def run_daily_strategy(symbol: str) -> dict:
    """
    运行每日策略
    
    Args:
        symbol: 股票代码
        
    Returns:
        执行结果字典
    """
    print(f"\n{'=' * 80}")
    print(f"📈 运行 {symbol} 每日策略")
    print(f"{'=' * 80}")
    
    # 确定工作目录
    if symbol == "TSLA":
        work_dir = project_root
    else:
        work_dir = project_root / symbol
    
    # 运行策略脚本
    script_path = work_dir / "src" / "pipeline" / "daily_strategy.py"
    
    try:
        # 运行策略
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        
        print(output)
        
        # 读取结果
        signals_file = work_dir / "backtest_results" / "daily" / "signals_daily.csv"
        
        result_data = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "signals_count": 0,
            "new_signals_count": 0,
            "latest_signal_date": None,
            "latest_signal_action": None,
            "latest_signal_price": None,
            "error": None if success else output
        }
        
        if success and signals_file.exists():
            signals_df = pd.read_csv(signals_file)
            result_data["signals_count"] = len(signals_df)
            
            if len(signals_df) > 0:
                latest = signals_df.iloc[-1]
                result_data["latest_signal_date"] = str(latest['date'])
                result_data["latest_signal_action"] = latest['action']
                result_data["latest_signal_price"] = float(latest['price'])
                
                # 检查是否是新信号 (今天的)
                signal_date = pd.to_datetime(latest['date']).date()
                today = datetime.now().date()
                if signal_date == today:
                    result_data["new_signals_count"] = 1
        
        return result_data
        
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": str(e)
        }


def record_execution_result(symbol: str, result: dict):
    """
    记录执行结果
    
    Args:
        symbol: 股票代码
        result: 执行结果
    """
    analyzer = StrategyAnalyzer(symbol)
    
    analyzer.record_execution(
        strategy_type="daily",
        signals_count=result.get("signals_count", 0),
        new_signals_count=result.get("new_signals_count", 0),
        latest_signal_date=result.get("latest_signal_date"),
        latest_signal_action=result.get("latest_signal_action"),
        latest_signal_price=result.get("latest_signal_price"),
        notes=result.get("error", "")
    )


def send_daily_summary(results: list):
    """
    发送每日汇总邮件
    
    Args:
        results: 所有股票的执行结果列表
    """
    email_service = EmailService()
    
    # 构建邮件内容
    subject = f"📊 每日策略执行汇总 - {datetime.now().strftime('%Y-%m-%d')}"
    
    html_content = f"""
    <html>
    <body>
        <h2>📊 每日策略执行汇总</h2>
        <p><strong>执行时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr>
    """
    
    for result in results:
        symbol = result['symbol']
        success = result.get('success', False)
        
        status_icon = "✅" if success else "❌"
        status_text = "成功" if success else "失败"
        
        html_content += f"""
        <h3>{status_icon} {symbol} - {status_text}</h3>
        """
        
        if success:
            html_content += f"""
            <ul>
                <li><strong>总信号数:</strong> {result.get('signals_count', 0)}</li>
                <li><strong>新信号数:</strong> {result.get('new_signals_count', 0)}</li>
            """
            
            if result.get('latest_signal_date'):
                html_content += f"""
                <li><strong>最新信号:</strong> {result.get('latest_signal_date')} 
                    {result.get('latest_signal_action')} @ ${result.get('latest_signal_price', 0):.2f}</li>
                """
            
            html_content += "</ul>"
        else:
            html_content += f"""
            <p style="color: red;"><strong>错误信息:</strong></p>
            <pre>{result.get('error', 'Unknown error')}</pre>
            """
        
        html_content += "<hr>"
    
    html_content += """
    <p>详细信息请查看策略执行日志</p>
    </body>
    </html>
    """
    
    try:
        email_service.send_custom_email(
            subject=subject,
            html_content=html_content
        )
        print("\n✅ 邮件发送成功!")
    except Exception as e:
        print(f"\n❌ 邮件发送失败: {e}")


def main():
    """主函数"""
    print("=" * 80)
    print("📊 智能每日策略检查系统")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    symbols = ["TSLA", "NVDA", "INTC"]
    results = []
    
    # 运行所有股票的策略
    for symbol in symbols:
        result = run_daily_strategy(symbol)
        results.append(result)
        
        # 记录执行结果
        if result.get('success'):
            record_execution_result(symbol, result)
    
    # 发送汇总邮件
    print(f"\n{'=' * 80}")
    print("📧 发送每日汇总邮件")
    print(f"{'=' * 80}")
    send_daily_summary(results)
    
    print()
    print("=" * 80)
    print("✅ 每日策略检查完成!")
    print("=" * 80)


if __name__ == "__main__":
    main()
