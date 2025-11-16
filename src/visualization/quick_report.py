"""
最简化的HTML报告生成器 - 只使用资金曲线和信号数据
"""
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import webbrowser

def generate_report():
    # 读取数据
    base_dir = Path("k:/QT/backtest_results/daily")
    
    signals = pd.read_csv(base_dir / "signals_daily.csv")
    equity = pd.read_csv(base_dir / "equity_curve_daily.csv")
    
    signals['date'] = pd.to_datetime(signals['date'])
    equity['date'] = pd.to_datetime(equity['date'])
    
    # 清理action
    signals['action'] = signals['action'].str.replace('TradeAction.', '', regex=False)
    
    # 统计
    buy_count = len(signals[signals['action'] == 'BUY'])
    sell_count = len(signals[signals['action'] == 'SELL'])
    
    initial = equity['equity'].iloc[0]
    final = equity['equity'].iloc[-1]
    total_return = (final - initial) / initial * 100
    
    # 最大回撤
    equity['cummax'] = equity['equity'].cummax()
    equity['drawdown'] = (equity['equity'] - equity['cummax']) / equity['cummax'] * 100
    max_dd = equity['drawdown'].min()
    
    # 生成图表1: 资金曲线
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=equity['date'],
        y=equity['equity'],
        mode='lines',
        name='资金曲线',
        line=dict(color='#667eea', width=2),
        fill='tozeroy'
    ))
    fig1.update_layout(
        title='TSLA策略资金曲线',
        xaxis_title='日期',
        yaxis_title='资金 ($)',
        template='plotly_white',
        height=400
    )
    
    # 生成图表2: 信号分布
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=['BUY信号', 'SELL信号'],
        y=[buy_count, sell_count],
        marker_color=['#00CC96', '#EF553B'],
        text=[buy_count, sell_count],
        textposition='outside'
    ))
    fig2.update_layout(
        title='信号分布',
        yaxis_title='数量',
        template='plotly_white',
        height=400
    )
    
    # 生成图表3: 回撤曲线
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=equity['date'],
        y=equity['drawdown'],
        mode='lines',
        name='回撤',
        line=dict(color='#EF553B', width=2),
        fill='tozeroy'
    ))
    fig3.update_layout(
        title='回撤曲线',
        xaxis_title='日期',
        yaxis_title='回撤 (%)',
        template='plotly_white',
        height=400
    )
    
    # 准备信号表格数据 (最近30条)
    recent_signals = signals.tail(30).copy()
    recent_signals = recent_signals.sort_values('date', ascending=False)
    
    # 格式化日期和价格
    recent_signals['date_str'] = recent_signals['date'].dt.strftime('%Y-%m-%d')
    recent_signals['price_str'] = recent_signals['price'].apply(lambda x: f'${x:.2f}')
    
    # 生成信号表格HTML
    signals_table_html = ""
    for _, row in recent_signals.iterrows():
        action = row['action']
        action_class = 'buy-action' if action == 'BUY' else 'sell-action'
        action_icon = '📈' if action == 'BUY' else '📉'
        
        signals_table_html += f"""
        <tr>
            <td>{row['date_str']}</td>
            <td><span class="{action_class}">{action_icon} {action}</span></td>
            <td class="price-cell">{row['price_str']}</td>
            <td>{row['quantity']}</td>
            <td class="reason-cell">{row['reason']}</td>
        </tr>
        """
    
    # 生成HTML
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TSLA策略分析报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: white;
            border-radius: 15px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .header h1 {{ color: #333; font-size: 2.5em; margin-bottom: 10px; }}
        .stats {{
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
        }}
        .stat-card .label {{ color: #666; font-size: 0.85em; margin-bottom: 8px; }}
        .stat-card .value {{ color: #333; font-size: 2em; font-weight: bold; }}
        .positive {{ color: #00CC96; }}
        .negative {{ color: #EF553B; }}
        .chart {{ background: white; border-radius: 15px; padding: 30px; margin-bottom: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        
        /* 信号表格样式 */
        .signals-table {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .signals-table h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .buy-action {{
            color: #00CC96;
            font-weight: bold;
            padding: 5px 10px;
            background: rgba(0, 204, 150, 0.1);
            border-radius: 5px;
            display: inline-block;
        }}
        .sell-action {{
            color: #EF553B;
            font-weight: bold;
            padding: 5px 10px;
            background: rgba(239, 85, 59, 0.1);
            border-radius: 5px;
            display: inline-block;
        }}
        .price-cell {{
            font-weight: bold;
            color: #333;
            text-align: right;
        }}
        .reason-cell {{
            font-size: 0.9em;
            color: #666;
            max-width: 300px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 TSLA策略分析报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="label">总信号数</div>
                <div class="value">{len(signals)}</div>
            </div>
            <div class="stat-card">
                <div class="label">BUY信号</div>
                <div class="value positive">{buy_count}</div>
            </div>
            <div class="stat-card">
                <div class="label">SELL信号</div>
                <div class="value negative">{sell_count}</div>
            </div>
            <div class="stat-card">
                <div class="label">总收益率</div>
                <div class="value {'positive' if total_return > 0 else 'negative'}">{total_return:.2f}%</div>
            </div>
            <div class="stat-card">
                <div class="label">最大回撤</div>
                <div class="value negative">{max_dd:.2f}%</div>
            </div>
            <div class="stat-card">
                <div class="label">初始资金</div>
                <div class="value">${initial:,.0f}</div>
            </div>
            <div class="stat-card">
                <div class="label">最终资金</div>
                <div class="value {'positive' if final > initial else 'negative'}">${final:,.0f}</div>
            </div>
        </div>
        
        <div class="chart">
            {fig1.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="chart">
            {fig2.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="chart">
            {fig3.to_html(full_html=False, include_plotlyjs=False)}
        </div>
        
        <div class="signals-table">
            <h2>📋 最近30条策略信号</h2>
            <table>
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>操作</th>
                        <th>价格</th>
                        <th>数量</th>
                        <th>原因</th>
                    </tr>
                </thead>
                <tbody>
                    {signals_table_html}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    
    # 保存
    output = Path("k:/QT") / f"TSLA_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ HTML报告已生成!")
    print(f"📁 {output}")
    
    # 打开浏览器
    webbrowser.open(str(output))
    return output

if __name__ == "__main__":
    generate_report()
