"""
策略对比可视化
"""
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def load_results():
    """加载三种策略的结果"""
    results = {}
    
    # 1. 原始策略
    original_path = project_root / "backtest_results" / "equity_curve.csv"
    if original_path.exists():
        results['原始策略\n(无风控)'] = pd.read_csv(original_path)
    
    # 2. 网格搜索最优
    enhanced_path = project_root / "backtest_results" / "enhanced" / "equity_curve_enhanced.csv"
    if enhanced_path.exists():
        results['网格搜索最优\n(严格止损)'] = pd.read_csv(enhanced_path)
    
    # 3. 改进策略
    improved_path = project_root / "backtest_results" / "improved" / "equity_curve_improved.csv"
    if improved_path.exists():
        results['改进策略\n(趋势+仓位)'] = pd.read_csv(improved_path)
    
    return results


def plot_comparison(results):
    """绘制对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('TSLA策略对比分析', fontsize=16, fontweight='bold')
    
    # 1. 资产净值曲线
    ax1 = axes[0, 0]
    for name, df in results.items():
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # 归一化到100,000起点
        normalized_equity = (df['equity'] / df['equity'].iloc[0]) * 100000
        
        ax1.plot(df['date'], normalized_equity, label=name, linewidth=2)
    
    ax1.set_title('资产净值曲线对比', fontsize=14, fontweight='bold')
    ax1.set_xlabel('日期')
    ax1.set_ylabel('资产净值 ($)')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=100000, color='gray', linestyle='--', alpha=0.5, label='初始资金')
    
    # 2. 收益率对比
    ax2 = axes[0, 1]
    metrics = {
        '原始策略\n(无风控)': {'总收益': 335.23, '年化': 10.09},
        '网格搜索最优\n(严格止损)': {'总收益': 33.92, '年化': 1.92},
        '改进策略\n(趋势+仓位)': {'总收益': 105.08, '年化': 4.79}
    }
    
    names = list(metrics.keys())
    total_returns = [metrics[n]['总收益'] for n in names]
    annual_returns = [metrics[n]['年化'] for n in names]
    
    x = range(len(names))
    width = 0.35
    
    bars1 = ax2.bar([i - width/2 for i in x], total_returns, width, label='总收益率 (%)', alpha=0.8)
    bars2 = ax2.bar([i + width/2 for i in x], annual_returns, width, label='年化收益率 (%)', alpha=0.8)
    
    ax2.set_title('收益率对比', fontsize=14, fontweight='bold')
    ax2.set_ylabel('收益率 (%)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(names)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=9)
    
    # 3. 风险指标对比
    ax3 = axes[1, 0]
    risk_metrics = {
        '原始策略\n(无风控)': {'最大回撤': -90.61, '夏普比率': 0.49},
        '网格搜索最优\n(严格止损)': {'最大回撤': -9.52, '夏普比率': -0.01},
        '改进策略\n(趋势+仓位)': {'最大回撤': -50.90, '夏普比率': 0.23}
    }
    
    max_drawdowns = [abs(risk_metrics[n]['最大回撤']) for n in names]
    sharpe_ratios = [risk_metrics[n]['夏普比率'] for n in names]
    
    ax3_twin = ax3.twinx()
    
    bars1 = ax3.bar([i - width/2 for i in x], max_drawdowns, width, 
                    label='最大回撤 (%)', color='red', alpha=0.6)
    bars2 = ax3_twin.bar([i + width/2 for i in x], sharpe_ratios, width, 
                         label='夏普比率', color='green', alpha=0.6)
    
    ax3.set_title('风险指标对比', fontsize=14, fontweight='bold')
    ax3.set_ylabel('最大回撤 (%)', color='red')
    ax3_twin.set_ylabel('夏普比率', color='green')
    ax3.set_xticks(x)
    ax3.set_xticklabels(names)
    ax3.set_ylim(0, max(max_drawdowns) * 1.2)
    ax3_twin.set_ylim(min(sharpe_ratios) - 0.2, max(sharpe_ratios) + 0.2)
    
    # 添加图例
    lines1, labels1 = ax3.get_legend_handles_labels()
    lines2, labels2 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bar in bars1:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%',
                ha='center', va='bottom', fontsize=9, color='red')
    
    for bar in bars2:
        height = bar.get_height()
        ax3_twin.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.2f}',
                     ha='center', va='bottom', fontsize=9, color='green')
    
    # 4. 交易统计对比
    ax4 = axes[1, 1]
    trade_metrics = {
        '原始策略\n(无风控)': {'总交易': 47, '胜率': 61.70},
        '网格搜索最优\n(严格止损)': {'总交易': 10, '胜率': 50.00},
        '改进策略\n(趋势+仓位)': {'总交易': 1, '胜率': 100.00}
    }
    
    total_trades = [trade_metrics[n]['总交易'] for n in names]
    win_rates = [trade_metrics[n]['胜率'] for n in names]
    
    ax4_twin = ax4.twinx()
    
    bars1 = ax4.bar([i - width/2 for i in x], total_trades, width, 
                    label='总交易次数', color='blue', alpha=0.6)
    bars2 = ax4_twin.bar([i + width/2 for i in x], win_rates, width, 
                         label='胜率 (%)', color='orange', alpha=0.6)
    
    ax4.set_title('交易统计对比', fontsize=14, fontweight='bold')
    ax4.set_ylabel('总交易次数', color='blue')
    ax4_twin.set_ylabel('胜率 (%)', color='orange')
    ax4.set_xticks(x)
    ax4.set_xticklabels(names)
    ax4.set_ylim(0, max(total_trades) * 1.2)
    ax4_twin.set_ylim(0, 110)
    
    # 添加图例
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 添加数值标签
    for bar in bars1:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=9, color='blue')
    
    for bar in bars2:
        height = bar.get_height()
        ax4_twin.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.1f}%',
                     ha='center', va='bottom', fontsize=9, color='orange')
    
    plt.tight_layout()
    
    # 保存图片
    output_path = project_root / "backtest_results" / "strategy_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ 对比图已保存: {output_path}")
    
    plt.show()


def print_summary():
    """打印总结"""
    print()
    print("=" * 80)
    print("📊 策略对比总结")
    print("=" * 80)
    print()
    
    print("【核心发现】")
    print()
    print("1. 原始策略 (无风控):")
    print("   ✅ 最高收益 335%,但风险不可接受 (-90%回撤)")
    print("   ❌ 不适合实战")
    print()
    
    print("2. 网格搜索最优 (严格止损):")
    print("   ✅ 最小回撤 -9.5%,风控优秀")
    print("   ❌ 收益过低 33%,不如指数基金")
    print("   ❌ 止损机制不适合TSLA高波动特性")
    print()
    
    print("3. 改进策略 (趋势+仓位): ⭐ 推荐")
    print("   ✅ 平衡收益与风险: 105%收益 + 50%回撤")
    print("   ✅ 100%胜率,正夏普比率 0.23")
    print("   ✅ 适合长期持有高波动成长股")
    print()
    
    print("【投资建议】")
    print()
    print("对于TSLA这类高波动成长股:")
    print("  • 趋势确认 > 频繁交易")
    print("  • 长期持有 > 短期止损")
    print("  • 仓位控制 > 满仓操作")
    print("  • 承受波动 = 享受收益")
    print()
    
    print("=" * 80)


def main():
    """主函数"""
    print()
    print("=" * 80)
    print("📈 加载策略对比数据...")
    print("=" * 80)
    print()
    
    results = load_results()
    
    if len(results) == 0:
        print("❌ 未找到任何回测结果文件")
        print("   请先运行以下脚本:")
        print("   1. python -m src.pipeline.run_backtest")
        print("   2. python -m src.pipeline.run_enhanced_backtest")
        print("   3. python -m src.pipeline.run_improved_strategy")
        return
    
    print(f"✓ 已加载 {len(results)} 种策略结果:")
    for name in results.keys():
        print(f"  • {name}")
    print()
    
    print("📊 生成对比图表...")
    plot_comparison(results)
    
    print_summary()
    
    print()
    print("✅ 对比分析完成!")
    print()
    print("📖 查看详细报告: STRATEGY_COMPARISON_REPORT.md")
    print()


if __name__ == "__main__":
    main()
