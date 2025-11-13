"""
增强回测运行脚本 - 包含止损机制

使用历史数据运行策略回测,包含风险控制
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import CSVPriceLoader
from src.signals.momentum import MomentumSignalModel, TradeAction as SignalAction
from src.portfolio.allocator import PositionAllocator, RiskBudget
from src.backtest.enhanced_engine import EnhancedBacktester, RiskConfig, TradeAction
import pandas as pd


def run_backtest_with_config(
    short_window: int = 2,
    long_window: int = 5,
    threshold: float = 0.20,
    max_trades_per_week: int = 2,
    stop_loss_pct: float = 0.20,
    trailing_stop_pct: float = 0.15,
    max_position_pct: float = 0.5,
    initial_cash: float = 100000.0
):
    """
    使用指定配置运行回测
    
    Args:
        short_window: 短期均线窗口
        long_window: 长期均线窗口
        threshold: 动量阈值
        max_trades_per_week: 每周最大交易次数
        stop_loss_pct: 固定止损百分比 (0.20 = -20%)
        trailing_stop_pct: 移动止损百分比
        max_position_pct: 最大持仓比例
        initial_cash: 初始资金
    """
    print("=" * 60)
    print("📊 特斯拉(TSLA)增强策略回测 (含止损)")
    print("=" * 60)
    print()
    
    # 1. 加载历史数据
    print("📂 加载历史数据...")
    data_path = project_root / "data" / "sample_tsla.csv"
    loader = CSVPriceLoader(data_path)
    bars = list(loader.load())
    print(f"✓ 已加载 {len(bars)} 条历史数据")
    print(f"  日期范围: {bars[0].date} 至 {bars[-1].date}")
    print()
    
    # 转换为 DataFrame
    price_df = pd.DataFrame([
        {
            'date': pd.Timestamp(bar.date),
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        }
        for bar in bars
    ])
    
    # 2. 显示策略配置
    print("⚙️  策略配置:")
    print(f"  短期窗口: {short_window} 日")
    print(f"  长期窗口: {long_window} 日")
    print(f"  动量阈值: {threshold:.0%}")
    print(f"  交易频率: 每周 {max_trades_per_week} 次")
    print()
    
    print("🛡️  风险控制:")
    print(f"  固定止损: {stop_loss_pct:.0%}")
    print(f"  移动止损: {trailing_stop_pct:.0%}")
    print(f"  最大持仓: {max_position_pct:.0%}")
    print()
    
    # 3. 生成交易信号
    print("🎯 生成交易信号...")
    signal_model = MomentumSignalModel(
        short_window=short_window,
        long_window=long_window,
        threshold=threshold
    )
    
    decisions = signal_model.generate(bars)
    print(f"✓ 生成 {len(decisions)} 个候选信号")
    
    # 筛选
    filtered_decisions = signal_model.filter_trading_slots(
        decisions, 
        max_trades_per_week=max_trades_per_week
    )
    print(f"✓ 筛选后剩余 {len(filtered_decisions)} 个交易信号")
    
    # 统计信号分布
    buy_signals = sum(1 for d in filtered_decisions if d.action == SignalAction.BUY)
    sell_signals = sum(1 for d in filtered_decisions if d.action == SignalAction.SELL)
    print(f"  - BUY 信号: {buy_signals}")
    print(f"  - SELL 信号: {sell_signals}")
    print()
    
    # 4. 转换信号格式
    print("🔄 准备回测信号...")
    allocator = PositionAllocator(
        symbol="TSLA",
        risk_budget=RiskBudget(capital=initial_cash)
    )
    
    signals = []
    for decision in filtered_decisions:
        plan = allocator.propose(decision)
        if not plan:
            continue
        
        if decision.action == SignalAction.BUY:
            action = TradeAction.BUY
        elif decision.action == SignalAction.SELL:
            action = TradeAction.SELL
        else:
            continue
        
        if plan.quantity > 0:
            signals.append((pd.Timestamp(decision.bar.date), action, plan.quantity))
    
    print(f"✓ 准备 {len(signals)} 个有效交易信号")
    print()
    
    # 5. 配置风险控制
    risk_config = RiskConfig(
        stop_loss_pct=stop_loss_pct,
        trailing_stop_pct=trailing_stop_pct,
        max_position_pct=max_position_pct
    )
    
    # 6. 运行回测
    print("🚀 开始回测...")
    print("-" * 60)
    
    backtester = EnhancedBacktester(
        initial_cash=initial_cash,
        commission_rate=0.001,
        risk_free_rate=0.02,
        risk_config=risk_config
    )
    
    # 初始建仓逻辑(如果需要)
    if signals and all(action == TradeAction.SELL for _, action, _ in signals):
        print("⚠️  警告: 只检测到卖出信号,在回测开始时建立初始仓位")
        initial_price = price_df['close'].iloc[0]
        initial_date = price_df['date'].iloc[0]
        initial_quantity = int(backtester.account.initial_cash * max_position_pct / initial_price)
        
        from src.backtest.engine import Trade
        initial_trade = Trade(
            date=initial_date,
            action=TradeAction.BUY,
            symbol="TSLA",
            quantity=initial_quantity,
            price=initial_price
        )
        backtester.account.execute_trade(initial_trade, initial_price)
        backtester.position_entry_prices["TSLA"] = initial_price
        backtester.position_highest_prices["TSLA"] = initial_price
        print(f"  初始建仓: {initial_quantity} 股 @ ${initial_price:.2f}")
        print()
    
    metrics = backtester.run(price_df, signals)
    
    print("-" * 60)
    print("✓ 回测完成!")
    print()
    
    # 7. 显示回测结果
    print("=" * 60)
    print("📈 回测性能报告")
    print("=" * 60)
    print()
    
    print("【收益指标】")
    print(f"  总收益率:     {metrics.total_return:>10.2%}")
    print(f"  年化收益率:   {metrics.annual_return:>10.2%}")
    print()
    
    print("【风险指标】")
    print(f"  夏普比率:     {metrics.sharpe_ratio:>10.2f}")
    print(f"  最大回撤:     {metrics.max_drawdown:>10.2%}")
    print()
    
    print("【交易统计】")
    print(f"  总交易次数:   {metrics.total_trades:>10}")
    print(f"  盈利交易:     {metrics.profit_trades:>10}")
    print(f"  亏损交易:     {metrics.loss_trades:>10}")
    print(f"  胜率:         {metrics.win_rate:>10.2%}")
    print()
    
    print("【盈亏分析】")
    print(f"  平均盈利:     ${metrics.avg_profit:>9.2f}")
    print(f"  平均亏损:     ${metrics.avg_loss:>9.2f}")
    print(f"  盈亏比:       {metrics.profit_factor:>10.2f}")
    print()
    
    # 显示风险控制统计
    risk_stats = backtester.get_risk_stats()
    print("【风险控制】")
    for key, value in risk_stats.items():
        if isinstance(value, float):
            print(f"  {key:20s} ${value:>10,.2f}")
        else:
            print(f"  {key:20s} {value:>10}")
    print()
    
    # 8. 显示最终账户状态
    equity_curve = backtester.get_equity_curve()
    final_equity = equity_curve['equity'].iloc[-1]
    
    print("【账户状态】")
    print(f"  初始资金:     ${initial_cash:>10,.2f}")
    print(f"  最终资产:     ${final_equity:>10,.2f}")
    print(f"  绝对收益:     ${final_equity - initial_cash:>10,.2f}")
    print()
    
    # 9. 保存结果
    print("💾 保存结果...")
    
    results_dir = project_root / "backtest_results" / "enhanced"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存资产净值曲线
    equity_path = results_dir / "equity_curve_enhanced.csv"
    equity_curve.to_csv(equity_path, index=False)
    print(f"✓ 资产净值曲线: {equity_path}")
    
    # 保存交易记录
    trades_df = backtester.get_trades()
    if not trades_df.empty:
        trades_path = results_dir / "trades_enhanced.csv"
        trades_df.to_csv(trades_path, index=False)
        print(f"✓ 交易记录: {trades_path}")
    
    # 保存配置和指标
    config_path = results_dir / "config_and_metrics.txt"
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("增强策略回测报告 (含止损)\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"回测日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据范围: {bars[0].date} 至 {bars[-1].date}\n")
        f.write(f"总交易日: {len(bars)}\n\n")
        
        f.write("策略配置:\n")
        f.write(f"  短期窗口: {short_window}\n")
        f.write(f"  长期窗口: {long_window}\n")
        f.write(f"  动量阈值: {threshold}\n")
        f.write(f"  交易频率: 每周{max_trades_per_week}次\n\n")
        
        f.write("风险控制:\n")
        f.write(f"  固定止损: {stop_loss_pct:.1%}\n")
        f.write(f"  移动止损: {trailing_stop_pct:.1%}\n")
        f.write(f"  最大持仓: {max_position_pct:.1%}\n\n")
        
        f.write("性能指标:\n")
        for key, value in metrics.to_dict().items():
            f.write(f"  {key}: {value}\n")
        
        f.write("\n风险统计:\n")
        for key, value in risk_stats.items():
            f.write(f"  {key}: {value}\n")
    
    print(f"✓ 配置和指标: {config_path}")
    print()
    
    print("=" * 60)
    print("✅ 增强回测完成!")
    print("=" * 60)
    
    return metrics, backtester


def main():
    """主函数 - 使用优化后的参数"""
    # 使用改进的参数
    metrics, backtester = run_backtest_with_config(
        short_window=2,          # 更短的短期窗口,提高反应速度
        long_window=5,           # 缩短长期窗口
        threshold=0.20,          # 降低阈值,增加信号
        max_trades_per_week=2,
        stop_loss_pct=0.20,      # 20% 固定止损
        trailing_stop_pct=0.15,  # 15% 移动止损
        max_position_pct=0.5,    # 50% 最大持仓
        initial_cash=100000.0
    )


if __name__ == "__main__":
    main()
