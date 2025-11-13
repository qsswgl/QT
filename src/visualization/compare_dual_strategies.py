"""
比较周度策略和日度策略的性能
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import matplotlib.dates as mdates

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_strategy_data():
    """加载两个策略的数据"""
    base_path = Path(__file__).parent.parent.parent
    
    # 周度策略数据
    weekly_equity = pd.read_csv(base_path / "backtest_results/improved/equity_curve_improved.csv")
    weekly_equity['date'] = pd.to_datetime(weekly_equity['date'])
    weekly_signals = pd.read_csv(base_path / "backtest_results/improved/signals_improved.csv")
    weekly_signals['date'] = pd.to_datetime(weekly_signals['date'])
    
    # 日度策略数据
    daily_equity = pd.read_csv(base_path / "backtest_results/daily/equity_curve_daily.csv")
    daily_equity['date'] = pd.to_datetime(daily_equity['date'])
    daily_signals = pd.read_csv(base_path / "backtest_results/daily/signals_daily.csv")
    daily_signals['date'] = pd.to_datetime(daily_signals['date'])
    
    return {
        'weekly': {'equity': weekly_equity, 'signals': weekly_signals},
        'daily': {'equity': daily_equity, 'signals': daily_signals}
    }

def plot_equity_comparison(data):
    """绘制权益曲线对比"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))
    
    # 图1: 权益曲线对比
    ax1.plot(data['weekly']['equity']['date'], 
             data['weekly']['equity']['equity'],
             label='周度策略 (趋势跟踪)', color='#2E86AB', linewidth=2)
    ax1.plot(data['daily']['equity']['date'],
             data['daily']['equity']['equity'],
             label='日度策略 (动量交易)', color='#A23B72', linewidth=2)
    ax1.axhline(y=100000, color='gray', linestyle='--', alpha=0.5, label='初始资金')
    
    ax1.set_title('📈 双策略权益曲线对比 (2010-2025)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('日期', fontsize=12)
    ax1.set_ylabel('账户价值 ($)', fontsize=12)
    ax1.legend(loc='upper left', fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # 图2: 回撤对比
    weekly_equity = data['weekly']['equity'].copy()
    daily_equity = data['daily']['equity'].copy()
    
    weekly_equity['cummax'] = weekly_equity['equity'].cummax()
    weekly_equity['drawdown'] = (weekly_equity['equity'] - weekly_equity['cummax']) / weekly_equity['cummax'] * 100
    
    daily_equity['cummax'] = daily_equity['equity'].cummax()
    daily_equity['drawdown'] = (daily_equity['equity'] - daily_equity['cummax']) / daily_equity['cummax'] * 100
    
    ax2.fill_between(weekly_equity['date'], 0, weekly_equity['drawdown'],
                     alpha=0.4, color='#2E86AB', label='周度策略')
    ax2.fill_between(daily_equity['date'], 0, daily_equity['drawdown'],
                     alpha=0.4, color='#A23B72', label='日度策略')
    
    ax2.set_title('📉 回撤对比', fontsize=14, fontweight='bold')
    ax2.set_xlabel('日期', fontsize=12)
    ax2.set_ylabel('回撤 (%)', fontsize=12)
    ax2.legend(loc='lower left', fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # 图3: 交易次数统计
    weekly_trades = data['weekly']['signals']
    daily_trades = data['daily']['signals']
    
    weekly_by_year = weekly_trades.groupby(weekly_trades['date'].dt.year).size()
    daily_by_year = daily_trades.groupby(daily_trades['date'].dt.year).size()
    
    years = sorted(set(weekly_by_year.index) | set(daily_by_year.index))
    weekly_counts = [weekly_by_year.get(year, 0) for year in years]
    daily_counts = [daily_by_year.get(year, 0) for year in years]
    
    x = np.arange(len(years))
    width = 0.35
    
    ax3.bar(x - width/2, weekly_counts, width, label='周度策略', color='#2E86AB', alpha=0.8)
    ax3.bar(x + width/2, daily_counts, width, label='日度策略', color='#A23B72', alpha=0.8)
    
    ax3.set_title('📊 年度交易次数对比', fontsize=14, fontweight='bold')
    ax3.set_xlabel('年份', fontsize=12)
    ax3.set_ylabel('信号次数', fontsize=12)
    ax3.set_xticks(x)
    ax3.set_xticklabels(years, rotation=45)
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # 保存图表
    output_path = Path(__file__).parent.parent.parent / "backtest_results/dual_strategy_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 对比图表已保存: {output_path}")
    
    return fig

def print_comparison_table(data):
    """打印对比统计表格"""
    weekly_equity = data['weekly']['equity']
    daily_equity = data['daily']['equity']
    weekly_signals = data['weekly']['signals']
    daily_signals = data['daily']['signals']
    
    # 计算指标
    weekly_return = (weekly_equity['equity'].iloc[-1] - 100000) / 100000 * 100
    daily_return = (daily_equity['equity'].iloc[-1] - 100000) / 100000 * 100
    
    weekly_max_dd = ((weekly_equity['equity'] - weekly_equity['equity'].cummax()) / 
                     weekly_equity['equity'].cummax() * 100).min()
    daily_max_dd = ((daily_equity['equity'] - daily_equity['equity'].cummax()) / 
                    daily_equity['equity'].cummax() * 100).min()
    
    weekly_trades = len(weekly_signals)
    daily_trades = len(daily_signals)
    
    print("\n" + "="*80)
    print("📊 双策略性能对比总结")
    print("="*80)
    
    print(f"\n{'指标':<20} {'周度策略':<25} {'日度策略':<25}")
    print("-" * 80)
    print(f"{'策略类型':<20} {'趋势跟踪 (长线)':<25} {'动量交易 (短线)':<25}")
    print(f"{'总收益率':<20} {f'{weekly_return:.2f}%':<25} {f'{daily_return:.2f}%':<25}")
    print(f"{'最大回撤':<20} {f'{weekly_max_dd:.2f}%':<25} {f'{daily_max_dd:.2f}%':<25}")
    print(f"{'总信号数':<20} {f'{weekly_trades}':<25} {f'{daily_trades}':<25}")
    print(f"{'平均年信号数':<20} {f'{weekly_trades/15:.1f}':<25} {f'{daily_trades/15:.1f}':<25}")
    print(f"{'回测期间':<20} {'2010-2025 (15年)':<25} {'2010-2025 (15年)':<25}")
    
    print("\n" + "-" * 80)
    print("💡 策略特点:")
    print("-" * 80)
    print("\n【周度策略】")
    print("  ✅ 优势: 收益率高 (105%), 交易频率极低, 适合长期投资")
    print("  ⚠️  风险: 回撤较大 (-50%), 需要耐心持有")
    print("  🎯 适合: 保守投资者, 上班族, 不想频繁操作的人")
    
    print("\n【日度策略】")
    print("  ✅ 优势: 交易频率适中 (年均22次), 有止盈止损保护")
    print("  ⚠️  风险: 收益率较低 (8.84%), 回撤仍然较大 (-45%)")
    print("  🎯 适合: 积极交易者, 喜欢短期波段的人")
    
    print("\n" + "-" * 80)
    print("💡 组合建议:")
    print("-" * 80)
    print("  • 分配方案: 周度策略 60% + 日度策略 30% + 现金 10%")
    print("  • 优先级: 周度策略为主 (捕捉大趋势), 日度策略为辅 (增加收益)")
    print("  • 资金管理: 两个策略使用不同资金池, 避免冲突")
    print("=" * 80 + "\n")

def main():
    """主函数"""
    print("🔍 加载策略数据...")
    data = load_strategy_data()
    
    print("📊 生成对比图表...")
    plot_equity_comparison(data)
    
    print_comparison_table(data)
    
    print("✅ 双策略对比分析完成!")
    print("\n📁 查看图表:")
    print("   K:\\QT\\backtest_results\\dual_strategy_comparison.png")

if __name__ == "__main__":
    main()
