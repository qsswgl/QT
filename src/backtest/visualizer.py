"""
回测可视化报告生成器

生成资产净值曲线、回撤曲线、月度收益热力图等图表
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def plot_equity_curve(equity_df: pd.DataFrame, output_path: Path):
    """绘制资产净值曲线"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(equity_df['date'], equity_df['equity'], linewidth=2, color='#2E86DE')
    ax.fill_between(equity_df['date'], equity_df['equity'], 
                     alpha=0.3, color='#2E86DE')
    
    # 标注起点和终点
    initial_equity = equity_df['equity'].iloc[0]
    final_equity = equity_df['equity'].iloc[-1]
    
    ax.scatter(equity_df['date'].iloc[0], initial_equity, 
              color='green', s=100, zorder=5, label=f'起点: ${initial_equity:,.0f}')
    ax.scatter(equity_df['date'].iloc[-1], final_equity, 
              color='red', s=100, zorder=5, label=f'终点: ${final_equity:,.0f}')
    
    ax.set_title('资产净值曲线', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('资产净值 ($)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=10)
    
    # 格式化日期轴
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_drawdown(equity_df: pd.DataFrame, output_path: Path):
    """绘制回撤曲线"""
    # 计算回撤
    equity_df['cummax'] = equity_df['equity'].cummax()
    equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax'] * 100
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.fill_between(equity_df['date'], equity_df['drawdown'], 0,
                     where=equity_df['drawdown'] < 0,
                     color='#E74C3C', alpha=0.5, label='回撤区域')
    ax.plot(equity_df['date'], equity_df['drawdown'], 
            linewidth=1.5, color='#E74C3C')
    
    # 标注最大回撤
    max_dd_idx = equity_df['drawdown'].idxmin()
    max_dd_date = equity_df.loc[max_dd_idx, 'date']
    max_dd_value = equity_df.loc[max_dd_idx, 'drawdown']
    
    ax.scatter(max_dd_date, max_dd_value, 
              color='darkred', s=100, zorder=5, 
              label=f'最大回撤: {max_dd_value:.2f}%')
    ax.annotate(f'{max_dd_value:.2f}%', 
                xy=(max_dd_date, max_dd_value),
                xytext=(10, -10), textcoords='offset points',
                fontsize=10, color='darkred',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
    
    ax.set_title('回撤曲线', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('日期', fontsize=12)
    ax.set_ylabel('回撤 (%)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower left', fontsize=10)
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
    
    # 格式化日期轴
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_monthly_returns(equity_df: pd.DataFrame, output_path: Path):
    """绘制月度收益热力图"""
    # 计算月度收益率
    equity_df['year'] = equity_df['date'].dt.year
    equity_df['month'] = equity_df['date'].dt.month
    
    # 按月分组,取最后一天的资产净值
    monthly = equity_df.groupby(['year', 'month'])['equity'].last().reset_index()
    monthly['returns'] = monthly['equity'].pct_change() * 100
    
    # 创建数据透视表
    pivot_table = monthly.pivot(index='year', columns='month', values='returns')
    
    # 绘制热力图
    fig, ax = plt.subplots(figsize=(14, max(8, len(pivot_table) * 0.4)))
    
    # 创建颜色映射
    cmap = plt.cm.RdYlGn
    im = ax.imshow(pivot_table.values, cmap=cmap, aspect='auto', 
                   vmin=-10, vmax=10)
    
    # 设置坐标轴
    ax.set_xticks(np.arange(12))
    ax.set_yticks(np.arange(len(pivot_table)))
    ax.set_xticklabels(['1月', '2月', '3月', '4月', '5月', '6月',
                        '7月', '8月', '9月', '10月', '11月', '12月'])
    ax.set_yticklabels(pivot_table.index)
    
    # 添加数值标注
    for i in range(len(pivot_table)):
        for j in range(12):
            value = pivot_table.iloc[i, j]
            if not pd.isna(value):
                text_color = 'white' if abs(value) > 5 else 'black'
                ax.text(j, i, f'{value:.1f}%', 
                       ha='center', va='center', 
                       color=text_color, fontsize=9)
    
    ax.set_title('月度收益率热力图', fontsize=16, fontweight='bold', pad=20)
    plt.colorbar(im, ax=ax, label='收益率 (%)')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_trades_distribution(trades_df: pd.DataFrame, output_path: Path):
    """绘制交易分布图"""
    if trades_df.empty:
        return
    
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. 交易类型分布
    ax1 = fig.add_subplot(gs[0, 0])
    action_counts = trades_df['action'].value_counts()
    colors = ['#27AE60' if action == 'BUY' else '#E74C3C' 
              for action in action_counts.index]
    ax1.bar(action_counts.index, action_counts.values, color=colors, alpha=0.7)
    ax1.set_title('交易类型分布', fontsize=12, fontweight='bold')
    ax1.set_ylabel('交易次数', fontsize=10)
    for i, v in enumerate(action_counts.values):
        ax1.text(i, v + 0.5, str(v), ha='center', va='bottom')
    
    # 2. 交易价格分布
    ax2 = fig.add_subplot(gs[0, 1])
    buy_prices = trades_df[trades_df['action'] == 'BUY']['price']
    sell_prices = trades_df[trades_df['action'] == 'SELL']['price']
    
    bins = 20
    ax2.hist(buy_prices, bins=bins, alpha=0.6, color='green', label='买入价格')
    ax2.hist(sell_prices, bins=bins, alpha=0.6, color='red', label='卖出价格')
    ax2.set_title('交易价格分布', fontsize=12, fontweight='bold')
    ax2.set_xlabel('价格 ($)', fontsize=10)
    ax2.set_ylabel('频数', fontsize=10)
    ax2.legend()
    
    # 3. 交易数量分布
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.hist(trades_df['quantity'], bins=15, color='#3498DB', alpha=0.7, edgecolor='black')
    ax3.set_title('交易数量分布', fontsize=12, fontweight='bold')
    ax3.set_xlabel('数量', fontsize=10)
    ax3.set_ylabel('频数', fontsize=10)
    ax3.axvline(trades_df['quantity'].mean(), color='red', 
               linestyle='--', linewidth=2, label=f"平均: {trades_df['quantity'].mean():.1f}")
    ax3.legend()
    
    # 4. 交易时间序列
    ax4 = fig.add_subplot(gs[1, 1])
    trades_df['date'] = pd.to_datetime(trades_df['date'])
    
    buy_trades = trades_df[trades_df['action'] == 'BUY']
    sell_trades = trades_df[trades_df['action'] == 'SELL']
    
    ax4.scatter(buy_trades['date'], buy_trades['price'], 
               color='green', marker='^', s=100, alpha=0.6, label='买入')
    ax4.scatter(sell_trades['date'], sell_trades['price'], 
               color='red', marker='v', s=100, alpha=0.6, label='卖出')
    
    ax4.set_title('交易时间序列', fontsize=12, fontweight='bold')
    ax4.set_xlabel('日期', fontsize=10)
    ax4.set_ylabel('价格 ($)', fontsize=10)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
    
    fig.suptitle('交易分布分析', fontsize=16, fontweight='bold', y=0.995)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_report(results_dir: Path):
    """生成完整的可视化报告"""
    print("📊 生成可视化报告...")
    print()
    
    # 读取数据
    equity_df = pd.read_csv(results_dir / "equity_curve.csv")
    equity_df['date'] = pd.to_datetime(equity_df['date'])
    
    trades_path = results_dir / "trades.csv"
    if trades_path.exists():
        trades_df = pd.read_csv(trades_path)
    else:
        trades_df = pd.DataFrame()
    
    # 创建图表目录
    charts_dir = results_dir / "charts"
    charts_dir.mkdir(exist_ok=True)
    
    # 生成各类图表
    print("  生成资产净值曲线...")
    plot_equity_curve(equity_df, charts_dir / "equity_curve.png")
    
    print("  生成回撤曲线...")
    plot_drawdown(equity_df.copy(), charts_dir / "drawdown.png")
    
    print("  生成月度收益热力图...")
    plot_monthly_returns(equity_df.copy(), charts_dir / "monthly_returns.png")
    
    if not trades_df.empty:
        print("  生成交易分布图...")
        plot_trades_distribution(trades_df, charts_dir / "trades_distribution.png")
    
    print()
    print(f"✅ 所有图表已保存到: {charts_dir}")
    print()
    print("生成的图表:")
    print("  - equity_curve.png         资产净值曲线")
    print("  - drawdown.png             回撤曲线")
    print("  - monthly_returns.png      月度收益热力图")
    if not trades_df.empty:
        print("  - trades_distribution.png  交易分布分析")


def main():
    project_root = Path(__file__).parent.parent.parent
    results_dir = project_root / "backtest_results"
    
    if not results_dir.exists():
        print("❌ 错误: 未找到回测结果目录")
        print("请先运行: python -m src.pipeline.run_backtest")
        return
    
    generate_report(results_dir)


if __name__ == "__main__":
    main()
