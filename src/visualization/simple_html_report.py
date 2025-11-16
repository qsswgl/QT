"""
生成单股票策略分析的交互式HTML5报告 (简化版)

专注于TSLA策略分析
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent  # 上两级到QT目录
sys.path.insert(0, str(project_root))


def generate_simple_html_report(symbol="TSLA"):
    """生成简单的HTML报告"""
    
    print("=" * 80)
    print(f"📊 生成{symbol}策略分析HTML报告")
    print("=" * 80)
    print()
    
    # 数据目录
    if symbol == "TSLA":
        data_dir = project_root
    else:
        data_dir = project_root / symbol
    
    daily_dir = data_dir / "backtest_results" / "daily"
    
    # 读取数据
    print("📂 读取数据文件...")
    signals_file = daily_dir / "signals_daily.csv"
    equity_file = daily_dir / "equity_curve_daily.csv"
    
    print(f"  检查路径: {signals_file}")
    print(f"  存在: {signals_file.exists()}")
    
    if not signals_file.exists() or not equity_file.exists():
        print(f"❌ 数据文件不存在: {symbol}")
        print(f"  signals: {signals_file.exists()}")
        print(f"  equity: {equity_file.exists()}")
        return None
    
    signals = pd.read_csv(signals_file)
    equity = pd.read_csv(equity_file)
    
    signals['date'] = pd.to_datetime(signals['date'])
    equity['date'] = pd.to_datetime(equity['date'])
    
    # 清理action列 (去掉"TradeAction."前缀)
    if 'action' in signals.columns:
        signals['action'] = signals['action'].str.replace('TradeAction.', '', regex=False)
    
    print(f"✅ 信号数: {len(signals)}, 资金曲线点数: {len(equity)}")
    
    # 计算统计数据
    print("\n📊 计算统计数据...")
    buy_signals = len(signals[signals['action'] == 'BUY'])
    sell_signals = len(signals[signals['action'] == 'SELL'])
    
    # 从资金曲线计算收益
    initial_equity = equity['equity'].iloc[0]
    final_equity = equity['equity'].iloc[-1]
    total_return = ((final_equity - initial_equity) / initial_equity * 100)
    max_equity = equity['equity'].max()
    min_equity = equity['equity'].min()
    
    # 计算最大回撤
    equity['cummax'] = equity['equity'].cummax()
    equity['drawdown'] = (equity['equity'] - equity['cummax']) / equity['cummax'] * 100
    max_drawdown = equity['drawdown'].min()
    
    print(f"  BUY信号: {buy_signals}, SELL信号: {sell_signals}")
    print(f"  总收益率: {total_return:.2f}%")
    print(f"  最大回撤: {max_drawdown:.2f}%")
    
    # 计算统计数据
    print("\n📊 计算统计数据...")
    buy_signals = len(signals[signals['action'] == 'BUY'])
    sell_signals = len(signals[signals['action'] == 'SELL'])
    
    profitable_trades = len(trades[trades['profit'] > 0])
    losing_trades = len(trades[trades['profit'] < 0])
    win_rate = (profitable_trades / len(trades) * 100) if len(trades) > 0 else 0
    
    total_profit = trades['profit'].sum()
    avg_profit = trades['profit'].mean()
    max_profit = trades['profit'].max()
    max_loss = trades['profit'].min()
    
    # 计算累计收益
    trades_sorted = trades.sort_values('entry_date').copy()
    trades_sorted['cumulative_profit'] = trades_sorted['profit'].cumsum()
    
    print(f"  胜率: {win_rate:.1f}%")
    print(f"  总盈亏: ${total_profit:.2f}")
    
    # 开始生成图表
    print("\n📈 生成图表...")
    
    # 1. 资金曲线
    print("  - 资金曲线图")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=trades_sorted['entry_date'],
        y=trades_sorted['cumulative_profit'],
        mode='lines+markers',
        name='累计盈亏',
        line=dict(color='#667eea', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    fig1.update_layout(
        title=f'{symbol} 策略资金曲线',
        xaxis_title='日期',
        yaxis_title='累计盈亏 ($)',
        template='plotly_white',
        height=400
    )
    
    # 2. 交易盈亏分布
    print("  - 交易盈亏分布图")
    fig2 = go.Figure()
    
    profitable = trades[trades['profit'] > 0]
    losing = trades[trades['profit'] < 0]
    
    fig2.add_trace(go.Scatter(
        x=profitable['entry_date'],
        y=profitable['profit'],
        mode='markers',
        name=f'盈利交易 ({len(profitable)}笔)',
        marker=dict(size=12, color='#00CC96', symbol='triangle-up', line=dict(width=1, color='white'))
    ))
    
    fig2.add_trace(go.Scatter(
        x=losing['entry_date'],
        y=losing['profit'],
        mode='markers',
        name=f'亏损交易 ({len(losing)}笔)',
        marker=dict(size=12, color='#EF553B', symbol='triangle-down', line=dict(width=1, color='white'))
    ))
    
    fig2.add_hline(y=0, line_dash="dash", line_color="gray")
    fig2.update_layout(
        title=f'{symbol} 交易盈亏分布',
        xaxis_title='交易日期',
        yaxis_title='盈亏金额 ($)',
        template='plotly_white',
        height=400
    )
    
    # 3. 信号类型分布
    print("  - 信号分布图")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=['BUY信号', 'SELL信号'],
        y=[buy_signals, sell_signals],
        marker_color=['#00CC96', '#EF553B'],
        text=[buy_signals, sell_signals],
        textposition='outside'
    ))
    fig3.update_layout(
        title=f'{symbol} 信号分布',
        yaxis_title='信号数量',
        template='plotly_white',
        height=400
    )
    
    # 4. 月度盈亏分析
    print("  - 月度盈亏分析")
    trades_sorted['month'] = trades_sorted['entry_date'].dt.to_period('M')
    monthly_profit = trades_sorted.groupby('month')['profit'].sum().reset_index()
    monthly_profit['month'] = monthly_profit['month'].astype(str)
    
    fig4 = go.Figure()
    colors = ['#00CC96' if p > 0 else '#EF553B' for p in monthly_profit['profit']]
    fig4.add_trace(go.Bar(
        x=monthly_profit['month'],
        y=monthly_profit['profit'],
        marker_color=colors,
        text=[f"${p:.0f}" for p in monthly_profit['profit']],
        textposition='outside'
    ))
    fig4.add_hline(y=0, line_dash="dash", line_color="gray")
    fig4.update_layout(
        title=f'{symbol} 月度盈亏',
        xaxis_title='月份',
        yaxis_title='盈亏 ($)',
        template='plotly_white',
        height=400
    )
    
    # 转换为HTML
    print("\n🔨 生成HTML页面...")
    chart1_html = fig1.to_html(full_html=False, include_plotlyjs=False, div_id="chart1")
    chart2_html = fig2.to_html(full_html=False, include_plotlyjs=False, div_id="chart2")
    chart3_html = fig3.to_html(full_html=False, include_plotlyjs=False, div_id="chart3")
    chart4_html = fig4.to_html(full_html=False, include_plotlyjs=False, div_id="chart4")
    
    # 构建完整HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{symbol} 策略分析报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .header h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 0.85em;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        
        .stat-card .value {{
            color: #333;
            font-size: 2em;
            font-weight: bold;
        }}
        
        .stat-card .positive {{
            color: #00CC96;
        }}
        
        .stat-card .negative {{
            color: #EF553B;
        }}
        
        .chart-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .chart-section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .footer {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {symbol} 策略分析报告</h1>
            <p class="subtitle">生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">总信号数</div>
                <div class="value">{len(signals)}</div>
            </div>
            <div class="stat-card">
                <div class="label">BUY信号</div>
                <div class="value">{buy_signals}</div>
            </div>
            <div class="stat-card">
                <div class="label">SELL信号</div>
                <div class="value">{sell_signals}</div>
            </div>
            <div class="stat-card">
                <div class="label">总交易数</div>
                <div class="value">{len(trades)}</div>
            </div>
            <div class="stat-card">
                <div class="label">盈利交易</div>
                <div class="value positive">{profitable_trades}</div>
            </div>
            <div class="stat-card">
                <div class="label">亏损交易</div>
                <div class="value negative">{losing_trades}</div>
            </div>
            <div class="stat-card">
                <div class="label">胜率</div>
                <div class="value">{win_rate:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="label">总盈亏</div>
                <div class="value {'positive' if total_profit > 0 else 'negative'}">${total_profit:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">平均盈亏</div>
                <div class="value">${avg_profit:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">最大盈利</div>
                <div class="value positive">${max_profit:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">最大亏损</div>
                <div class="value negative">${max_loss:.2f}</div>
            </div>
        </div>
        
        <div class="chart-section">
            <h2>📈 资金曲线</h2>
            {chart1_html}
        </div>
        
        <div class="chart-section">
            <h2>📊 交易盈亏分布</h2>
            {chart2_html}
        </div>
        
        <div class="chart-section">
            <h2>📋 信号分布</h2>
            {chart3_html}
        </div>
        
        <div class="chart-section">
            <h2>📅 月度盈亏</h2>
            {chart4_html}
        </div>
        
        <div class="footer">
            <p><strong>{symbol} 量化交易策略系统 v1.0</strong></p>
            <p>策略类型: 动量策略 (5日动量 + 20日趋势)</p>
            <p>数据来源: Yahoo Finance</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 保存文件
    output_file = project_root / f"{symbol}_strategy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print()
    print("=" * 80)
    print(f"✅ HTML报告已生成: {output_file}")
    print("=" * 80)
    
    return output_file


if __name__ == "__main__":
    import webbrowser
    
    # 生成TSLA报告
    report_file = generate_simple_html_report("TSLA")
    
    if report_file:
        print("\n💡 正在浏览器中打开报告...")
        webbrowser.open(str(report_file))
