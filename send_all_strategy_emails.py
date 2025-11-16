"""
手动发送三支股票的日度策略邮件
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.notification.email_service import EmailService


def send_stock_summary(symbol: str, base_path: Path):
    """发送指定股票的策略总结邮件"""
    print(f"\n{'='*60}")
    print(f"📧 发送 {symbol} 日度策略邮件")
    print(f"{'='*60}")
    
    # 读取信号文件
    signal_file = base_path / "backtest_results" / "daily" / "signals_daily.csv"
    
    if not signal_file.exists():
        print(f"⚠️ {symbol} 信号文件不存在,跳过")
        return False
    
    signals_df = pd.read_csv(signal_file)
    signals_df['date'] = pd.to_datetime(signals_df['date'])
    
    # 获取最新信号
    latest_signal = None
    if not signals_df.empty:
        latest = signals_df.iloc[-1]
        latest_signal = {
            'date': latest['date'].strftime('%Y-%m-%d'),
            'action': latest['action'].replace('TradeAction.', ''),
            'quantity': int(latest['quantity']),
            'price': float(latest['price']),
            'reason': latest['reason']
        }
    
    # 读取资金曲线
    equity_file = base_path / "backtest_results" / "daily" / "equity_curve_daily.csv"
    if equity_file.exists():
        equity_df = pd.read_csv(equity_file)
        if not equity_df.empty:
            initial_equity = equity_df['equity'].iloc[0]
            final_equity = equity_df['equity'].iloc[-1]
            total_return = ((final_equity - initial_equity) / initial_equity) * 100
        else:
            total_return = 0
    else:
        total_return = 0
    
    # 发送邮件
    service = EmailService()
    
    # 构建邮件主题和内容
    subject = f"[{symbol}策略] 📊 日度策略回测完成"
    
    body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .content {{
            background: #f9f9f9;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 0 0 10px 10px;
        }}
        .info-box {{
            background: white;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }}
        .stat-item {{
            margin: 10px 0;
            padding: 10px;
            background: #f5f5f5;
            border-radius: 5px;
        }}
        .label {{
            font-weight: bold;
            color: #555;
            display: inline-block;
            width: 150px;
        }}
        .value {{
            color: #333;
            font-weight: bold;
        }}
        .positive {{
            color: #00AA00;
        }}
        .negative {{
            color: #FF0000;
        }}
        .footer {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 {symbol} 日度策略回测完成</h1>
        <p>策略执行报告</p>
    </div>
    
    <div class="content">
        <div class="info-box">
            <h3>📈 策略信息</h3>
            <div class="stat-item">
                <span class="label">股票代码:</span>
                <span class="value">{symbol}</span>
            </div>
            <div class="stat-item">
                <span class="label">总信号数:</span>
                <span class="value">{len(signals_df)}</span>
            </div>
            <div class="stat-item">
                <span class="label">总收益率:</span>
                <span class="value {'positive' if total_return > 0 else 'negative'}">{total_return:+.2f}%</span>
            </div>
        </div>
"""
    
    if latest_signal:
        action_color = "#00AA00" if latest_signal['action'] == 'BUY' else "#FF0000"
        body += f"""
        <div class="info-box" style="border-left-color: {action_color};">
            <h3>🚨 最新信号</h3>
            <div class="stat-item">
                <span class="label">日期:</span>
                <span class="value">{latest_signal['date']}</span>
            </div>
            <div class="stat-item">
                <span class="label">动作:</span>
                <span class="value" style="color: {action_color};">{latest_signal['action']}</span>
            </div>
            <div class="stat-item">
                <span class="label">价格:</span>
                <span class="value">${latest_signal['price']:.2f}</span>
            </div>
            <div class="stat-item">
                <span class="label">数量:</span>
                <span class="value">{latest_signal['quantity']:,}</span>
            </div>
            <div class="stat-item">
                <span class="label">原因:</span>
                <span class="value">{latest_signal['reason']}</span>
            </div>
        </div>
"""
    
    body += f"""
        <div style="margin-top: 20px; padding: 15px; background: #e8f4f8; border-radius: 5px;">
            <p style="margin: 0;">
                ℹ️ <strong>当前状态</strong>: 策略已执行完成,详细报告请查看系统
            </p>
        </div>
    </div>
    
    <div class="footer">
        <p>📅 发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>🤖 {symbol} 日度策略自动推送系统</p>
    </div>
</body>
</html>
"""
    
    # 发送邮件
    success = service._send_email(subject, body)
    
    if success:
        print(f"✅ {symbol} 邮件发送成功!")
    else:
        print(f"❌ {symbol} 邮件发送失败!")
    
    return success


def main():
    """主函数 - 发送所有股票的邮件"""
    print("="*60)
    print("📧 批量发送日度策略邮件")
    print("="*60)
    
    stocks = [
        ("TSLA", project_root),
        ("NVDA", project_root / "NVDA"),
        ("INTC", project_root / "INTC")
    ]
    
    results = {}
    
    for symbol, base_path in stocks:
        success = send_stock_summary(symbol, base_path)
        results[symbol] = success
    
    print(f"\n{'='*60}")
    print("📊 发送结果汇总")
    print(f"{'='*60}")
    
    for symbol, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{symbol}: {status}")
    
    print(f"\n收件人: qsswgl@gmail.com")
    print("="*60)


if __name__ == "__main__":
    main()
