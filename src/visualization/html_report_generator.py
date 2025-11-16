"""
生成策略分析的交互式HTML5报告

功能:
1. 读取策略执行记录和交易数据
2. 生成交互式图表 (使用 Plotly)
3. 创建美观的HTML5页面
4. 支持多维度分析和对比
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from analysis.strategy_analyzer import StrategyAnalyzer


class HTMLReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self):
        self.symbols = ["TSLA", "NVDA", "INTC"]
        self.analyzers = {
            symbol: StrategyAnalyzer(symbol) for symbol in self.symbols
        }
        self.colors = {
            "TSLA": "#E31937",  # 特斯拉红
            "NVDA": "#76B900",  # 英伟达绿
            "INTC": "#0071C5"   # 英特尔蓝
        }
    
    def generate_equity_curve_chart(self, symbol: str, strategy_type: str = "daily") -> go.Figure:
        """生成资金曲线图"""
        analyzer = self.analyzers[symbol]
        trades = analyzer.load_trades(strategy_type)
        
        if len(trades) == 0:
            return None
        
        # 计算累计收益
        trades = trades.sort_values('entry_date')
        trades['cumulative_profit'] = trades['profit'].cumsum()
        trades['cumulative_return'] = (trades['cumulative_profit'] / 100000 * 100)  # 假设初始资金10万
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trades['entry_date'],
            y=trades['cumulative_return'],
            mode='lines+markers',
            name=f'{symbol} 累计收益率',
            line=dict(color=self.colors[symbol], width=3),
            marker=dict(size=6),
            hovertemplate='<b>日期</b>: %{x}<br>' +
                         '<b>累计收益率</b>: %{y:.2f}%<br>' +
                         '<extra></extra>'
        ))
        
        fig.update_layout(
            title=f'{symbol} - {strategy_type.upper()}策略资金曲线',
            xaxis_title='日期',
            yaxis_title='累计收益率 (%)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def generate_signal_distribution_chart(self) -> go.Figure:
        """生成信号分布图"""
        signal_data = []
        
        for symbol in self.symbols:
            analyzer = self.analyzers[symbol]
            
            for strategy_type in ["daily", "weekly"]:
                signals = analyzer.load_signals(strategy_type)
                
                if len(signals) > 0:
                    buy_count = len(signals[signals['action'] == 'BUY'])
                    sell_count = len(signals[signals['action'] == 'SELL'])
                    
                    signal_data.append({
                        'symbol': symbol,
                        'strategy': strategy_type,
                        'BUY': buy_count,
                        'SELL': sell_count
                    })
        
        if not signal_data:
            # 如果没有数据,返回空图表
            fig = go.Figure()
            fig.add_annotation(
                text="暂无信号数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="gray")
            )
            fig.update_layout(
                title='信号分布统计',
                template='plotly_white',
                height=400
            )
            return fig
        
        df = pd.DataFrame(signal_data)
        
        fig = go.Figure()
        
        # BUY信号
        fig.add_trace(go.Bar(
            name='BUY信号',
            x=[f"{row['symbol']}-{row['strategy']}" for _, row in df.iterrows()],
            y=df['BUY'],
            marker_color='#00CC96',
            text=df['BUY'],
            textposition='outside'
        ))
        
        # SELL信号
        fig.add_trace(go.Bar(
            name='SELL信号',
            x=[f"{row['symbol']}-{row['strategy']}" for _, row in df.iterrows()],
            y=df['SELL'],
            marker_color='#EF553B',
            text=df['SELL'],
            textposition='outside'
        ))
        
        fig.update_layout(
            title='信号分布统计',
            xaxis_title='股票-策略类型',
            yaxis_title='信号数量',
            barmode='group',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def generate_win_rate_chart(self) -> go.Figure:
        """生成胜率对比图"""
        win_rate_data = []
        
        for symbol in self.symbols:
            analyzer = self.analyzers[symbol]
            
            for strategy_type in ["daily", "weekly"]:
                trades = analyzer.load_trades(strategy_type)
                
                if len(trades) > 0:
                    win_rate = (len(trades[trades['profit'] > 0]) / len(trades) * 100)
                    win_rate_data.append({
                        'symbol': symbol,
                        'strategy': strategy_type,
                        'win_rate': win_rate
                    })
        
        if not win_rate_data:
            # 如果没有数据,返回空图表
            fig = go.Figure()
            fig.add_annotation(
                text="暂无交易数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="gray")
            )
            fig.update_layout(
                title='策略胜率对比',
                template='plotly_white',
                height=400
            )
            return fig
        
        df = pd.DataFrame(win_rate_data)
        
        fig = go.Figure()
        
        for symbol in self.symbols:
            symbol_data = df[df['symbol'] == symbol]
            
            if len(symbol_data) > 0:
                fig.add_trace(go.Bar(
                    name=symbol,
                    x=symbol_data['strategy'],
                    y=symbol_data['win_rate'],
                    marker_color=self.colors[symbol],
                    text=[f"{v:.1f}%" for v in symbol_data['win_rate']],
                    textposition='outside'
                ))
        
        # 添加参考线
        fig.add_hline(y=50, line_dash="dash", line_color="gray", 
                     annotation_text="50%基准线")
        
        fig.update_layout(
            title='策略胜率对比',
            xaxis_title='策略类型',
            yaxis_title='胜率 (%)',
            barmode='group',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def generate_profit_comparison_chart(self) -> go.Figure:
        """生成盈亏对比图"""
        profit_data = []
        
        for symbol in self.symbols:
            analyzer = self.analyzers[symbol]
            
            for strategy_type in ["daily", "weekly"]:
                trades = analyzer.load_trades(strategy_type)
                
                if len(trades) > 0:
                    total_profit = trades['profit'].sum()
                    avg_profit = trades['profit'].mean()
                    
                    profit_data.append({
                        'symbol': symbol,
                        'strategy': strategy_type,
                        'total_profit': total_profit,
                        'avg_profit': avg_profit
                    })
        
        if not profit_data:
            # 如果没有数据,返回空图表
            fig = go.Figure()
            fig.add_annotation(
                text="暂无盈亏数据",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20, color="gray")
            )
            fig.update_layout(
                title='盈亏分析',
                template='plotly_white',
                height=400
            )
            return fig
        
        df = pd.DataFrame(profit_data)
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('总盈亏对比', '平均每笔盈亏'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # 总盈亏
        for symbol in self.symbols:
            symbol_data = df[df['symbol'] == symbol]
            
            if len(symbol_data) > 0:
                fig.add_trace(
                    go.Bar(
                        name=symbol,
                        x=symbol_data['strategy'],
                        y=symbol_data['total_profit'],
                        marker_color=self.colors[symbol],
                        text=[f"${v:.0f}" for v in symbol_data['total_profit']],
                        textposition='outside',
                        showlegend=True
                    ),
                    row=1, col=1
                )
        
        # 平均盈亏
        for symbol in self.symbols:
            symbol_data = df[df['symbol'] == symbol]
            
            if len(symbol_data) > 0:
                fig.add_trace(
                    go.Bar(
                        name=symbol,
                        x=symbol_data['strategy'],
                        y=symbol_data['avg_profit'],
                        marker_color=self.colors[symbol],
                        text=[f"${v:.2f}" for v in symbol_data['avg_profit']],
                        textposition='outside',
                        showlegend=False
                    ),
                    row=1, col=2
                )
        
        fig.update_xaxes(title_text="策略类型", row=1, col=1)
        fig.update_xaxes(title_text="策略类型", row=1, col=2)
        fig.update_yaxes(title_text="总盈亏 ($)", row=1, col=1)
        fig.update_yaxes(title_text="平均盈亏 ($)", row=1, col=2)
        
        fig.update_layout(
            title_text='盈亏分析',
            template='plotly_white',
            height=400,
            barmode='group'
        )
        
        return fig
    
    def generate_trade_distribution_chart(self, symbol: str, strategy_type: str = "daily") -> go.Figure:
        """生成交易盈亏分布图"""
        analyzer = self.analyzers[symbol]
        trades = analyzer.load_trades(strategy_type)
        
        if len(trades) == 0:
            return None
        
        fig = go.Figure()
        
        # 盈利交易
        profitable = trades[trades['profit'] > 0]
        fig.add_trace(go.Scatter(
            x=profitable['entry_date'],
            y=profitable['profit'],
            mode='markers',
            name='盈利交易',
            marker=dict(
                size=10,
                color='#00CC96',
                symbol='triangle-up',
                line=dict(width=1, color='white')
            ),
            hovertemplate='<b>日期</b>: %{x}<br>' +
                         '<b>盈利</b>: $%{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        # 亏损交易
        losing = trades[trades['profit'] < 0]
        fig.add_trace(go.Scatter(
            x=losing['entry_date'],
            y=losing['profit'],
            mode='markers',
            name='亏损交易',
            marker=dict(
                size=10,
                color='#EF553B',
                symbol='triangle-down',
                line=dict(width=1, color='white')
            ),
            hovertemplate='<b>日期</b>: %{x}<br>' +
                         '<b>亏损</b>: $%{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig.update_layout(
            title=f'{symbol} - {strategy_type.upper()}策略交易盈亏分布',
            xaxis_title='交易日期',
            yaxis_title='盈亏金额 ($)',
            template='plotly_white',
            height=400,
            hovermode='closest'
        )
        
        return fig
    
    def generate_monthly_performance_chart(self) -> go.Figure:
        """生成月度表现对比"""
        monthly_data = []
        
        for symbol in self.symbols:
            analyzer = self.analyzers[symbol]
            
            # 获取月度分析数据
            analysis = analyzer.analyze_month()
            
            monthly_data.append({
                'symbol': symbol,
                'daily_win_rate': analysis['daily_strategy']['win_rate'],
                'weekly_win_rate': analysis['weekly_strategy']['win_rate'],
                'daily_profit': analysis['daily_strategy']['total_profit'],
                'weekly_profit': analysis['weekly_strategy']['total_profit']
            })
        
        df = pd.DataFrame(monthly_data)
        
        # 创建雷达图
        categories = ['日度胜率', '周度胜率', '日度盈利', '周度盈利']
        
        fig = go.Figure()
        
        for _, row in df.iterrows():
            symbol = row['symbol']
            
            # 归一化数据 (0-100)
            values = [
                row['daily_win_rate'],
                row['weekly_win_rate'],
                min(100, max(0, 50 + row['daily_profit'] / 100)),  # 盈利归一化
                min(100, max(0, 50 + row['weekly_profit'] / 100))
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],  # 闭合图形
                theta=categories + [categories[0]],
                fill='toself',
                name=symbol,
                line=dict(color=self.colors[symbol], width=2),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            title='月度综合表现对比',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def generate_html_report(self, output_file: str = None):
        """生成完整的HTML报告"""
        
        if output_file is None:
            output_file = project_root / f"strategy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        else:
            output_file = Path(output_file)
        
        print("=" * 80)
        print("📊 生成策略分析HTML报告")
        print("=" * 80)
        print()
        
        # 生成各种图表
        print("📈 生成图表...")
        
        charts = []
        
        # 1. 信号分布
        print("  - 信号分布图")
        charts.append(("signal_dist", self.generate_signal_distribution_chart()))
        
        # 2. 胜率对比
        print("  - 胜率对比图")
        charts.append(("win_rate", self.generate_win_rate_chart()))
        
        # 3. 盈亏对比
        print("  - 盈亏对比图")
        charts.append(("profit", self.generate_profit_comparison_chart()))
        
        # 4. 月度表现雷达图
        print("  - 月度表现雷达图")
        charts.append(("monthly", self.generate_monthly_performance_chart()))
        
        # 5. 每个股票的资金曲线和交易分布
        for symbol in self.symbols:
            print(f"  - {symbol} 资金曲线图")
            equity_fig = self.generate_equity_curve_chart(symbol, "daily")
            if equity_fig:
                charts.append((f"{symbol}_equity", equity_fig))
            
            print(f"  - {symbol} 交易分布图")
            trade_fig = self.generate_trade_distribution_chart(symbol, "daily")
            if trade_fig:
                charts.append((f"{symbol}_trades", trade_fig))
        
        # 获取统计数据
        print("\n📊 收集统计数据...")
        stats = self._collect_statistics()
        
        # 构建HTML
        print("\n🔨 构建HTML页面...")
        html_content = self._build_html(charts, stats)
        
        # 保存文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print()
        print("=" * 80)
        print(f"✅ HTML报告已生成: {output_file}")
        print("=" * 80)
        print()
        print("💡 提示: 在浏览器中打开查看交互式图表")
        
        return output_file
    
    def _collect_statistics(self) -> dict:
        """收集统计数据"""
        stats = {
            'symbols': {},
            'overall': {
                'total_signals': 0,
                'total_trades': 0,
                'total_profit': 0,
                'avg_win_rate': 0
            }
        }
        
        win_rates = []
        
        for symbol in self.symbols:
            analyzer = self.analyzers[symbol]
            
            daily_signals = analyzer.load_signals("daily")
            weekly_signals = analyzer.load_signals("weekly")
            daily_trades = analyzer.load_trades("daily")
            weekly_trades = analyzer.load_trades("weekly")
            
            daily_win_rate = 0
            if len(daily_trades) > 0:
                daily_win_rate = len(daily_trades[daily_trades['profit'] > 0]) / len(daily_trades) * 100
                win_rates.append(daily_win_rate)
            
            weekly_win_rate = 0
            if len(weekly_trades) > 0:
                weekly_win_rate = len(weekly_trades[weekly_trades['profit'] > 0]) / len(weekly_trades) * 100
                win_rates.append(weekly_win_rate)
            
            stats['symbols'][symbol] = {
                'daily': {
                    'signals': len(daily_signals),
                    'trades': len(daily_trades),
                    'profit': daily_trades['profit'].sum() if len(daily_trades) > 0 else 0,
                    'win_rate': daily_win_rate
                },
                'weekly': {
                    'signals': len(weekly_signals),
                    'trades': len(weekly_trades),
                    'profit': weekly_trades['profit'].sum() if len(weekly_trades) > 0 else 0,
                    'win_rate': weekly_win_rate
                }
            }
            
            stats['overall']['total_signals'] += len(daily_signals) + len(weekly_signals)
            stats['overall']['total_trades'] += len(daily_trades) + len(weekly_trades)
            stats['overall']['total_profit'] += stats['symbols'][symbol]['daily']['profit'] + stats['symbols'][symbol]['weekly']['profit']
        
        if win_rates:
            stats['overall']['avg_win_rate'] = sum(win_rates) / len(win_rates)
        
        return stats
    
    def _build_html(self, charts: list, stats: dict) -> str:
        """构建HTML内容"""
        
        # 转换图表为HTML
        chart_htmls = []
        for chart_id, fig in charts:
            if fig is not None:
                chart_html = fig.to_html(
                    full_html=False,
                    include_plotlyjs=False,
                    div_id=chart_id
                )
                chart_htmls.append(chart_html)
        
        # 构建完整HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>策略分析报告 - {datetime.now().strftime('%Y年%m月%d日')}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }}
        
        .stat-card .label {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card .value {{
            color: #333;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card .change {{
            color: #00CC96;
            font-size: 0.9em;
        }}
        
        .stat-card .change.negative {{
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
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .symbol-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .symbol-section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .symbol-stats {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .strategy-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #667eea;
        }}
        
        .strategy-card h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .strategy-card .metric {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            color: #666;
        }}
        
        .strategy-card .metric .value {{
            font-weight: bold;
            color: #333;
        }}
        
        .footer {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-top: 30px;
        }}
        
        .footer p {{
            color: #666;
            margin-bottom: 10px;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .symbol-stats {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 量化交易策略分析报告</h1>
            <p class="subtitle">生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </div>
        
        <!-- Overall Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">总信号数</div>
                <div class="value">{stats['overall']['total_signals']}</div>
            </div>
            <div class="stat-card">
                <div class="label">总交易次数</div>
                <div class="value">{stats['overall']['total_trades']}</div>
            </div>
            <div class="stat-card">
                <div class="label">总盈亏</div>
                <div class="value">${stats['overall']['total_profit']:.2f}</div>
                <div class="change {'negative' if stats['overall']['total_profit'] < 0 else ''}">
                    {'📉 亏损' if stats['overall']['total_profit'] < 0 else '📈 盈利'}
                </div>
            </div>
            <div class="stat-card">
                <div class="label">平均胜率</div>
                <div class="value">{stats['overall']['avg_win_rate']:.1f}%</div>
                <div class="change">
                    {'✅ 优秀' if stats['overall']['avg_win_rate'] >= 60 else '⚠️ 需改进' if stats['overall']['avg_win_rate'] < 45 else '✅ 良好'}
                </div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="chart-section">
            <h2>📊 综合分析</h2>
            {''.join(chart_htmls[:4])}
        </div>
        
        <!-- Individual Symbol Analysis -->
"""
        
        # 为每个股票添加详细分析
        chart_index = 4
        for symbol in self.symbols:
            symbol_stats = stats['symbols'][symbol]
            
            html += f"""
        <div class="symbol-section" style="border-top: 5px solid {self.colors[symbol]};">
            <h2>{symbol} 详细分析</h2>
            
            <div class="symbol-stats">
                <div class="strategy-card">
                    <h3>📈 日度策略</h3>
                    <div class="metric">
                        <span>信号数量:</span>
                        <span class="value">{symbol_stats['daily']['signals']}</span>
                    </div>
                    <div class="metric">
                        <span>交易次数:</span>
                        <span class="value">{symbol_stats['daily']['trades']}</span>
                    </div>
                    <div class="metric">
                        <span>胜率:</span>
                        <span class="value">{symbol_stats['daily']['win_rate']:.1f}%</span>
                    </div>
                    <div class="metric">
                        <span>总盈亏:</span>
                        <span class="value" style="color: {'#EF553B' if symbol_stats['daily']['profit'] < 0 else '#00CC96'};">
                            ${symbol_stats['daily']['profit']:.2f}
                        </span>
                    </div>
                </div>
                
                <div class="strategy-card" style="border-left-color: #764ba2;">
                    <h3>📊 周度策略</h3>
                    <div class="metric">
                        <span>信号数量:</span>
                        <span class="value">{symbol_stats['weekly']['signals']}</span>
                    </div>
                    <div class="metric">
                        <span>交易次数:</span>
                        <span class="value">{symbol_stats['weekly']['trades']}</span>
                    </div>
                    <div class="metric">
                        <span>胜率:</span>
                        <span class="value">{symbol_stats['weekly']['win_rate']:.1f}%</span>
                    </div>
                    <div class="metric">
                        <span>总盈亏:</span>
                        <span class="value" style="color: {'#EF553B' if symbol_stats['weekly']['profit'] < 0 else '#00CC96'};">
                            ${symbol_stats['weekly']['profit']:.2f}
                        </span>
                    </div>
                </div>
            </div>
            
            {chart_htmls[chart_index] if chart_index < len(chart_htmls) else ''}
            {chart_htmls[chart_index + 1] if chart_index + 1 < len(chart_htmls) else ''}
        </div>
"""
            chart_index += 2
        
        # Footer
        html += f"""
        <!-- Footer -->
        <div class="footer">
            <p><strong>量化交易策略系统 v1.0</strong></p>
            <p>策略类型: 动量策略 (日度 + 周度)</p>
            <p>数据来源: Yahoo Finance</p>
            <p>报告生成: 自动化分析系统</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html


def main():
    """主函数"""
    generator = HTMLReportGenerator()
    report_file = generator.generate_html_report()
    
    # 自动在浏览器中打开
    import webbrowser
    webbrowser.open(str(report_file))


if __name__ == "__main__":
    main()
