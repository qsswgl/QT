"""
回测运行脚本

使用历史数据运行策略回测,评估性能表现
"""
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import CSVPriceLoader
from src.signals.momentum import MomentumSignalModel
from src.backtest.engine import Backtester, TradeAction
import pandas as pd


def main():
    print("=" * 60)
    print("📊 特斯拉(TSLA)量化策略回测")
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
            'date': pd.Timestamp(bar.date),  # 转换为 Timestamp
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        }
        for bar in bars
    ])
    
    # 2. 生成交易信号
    print("🎯 生成交易信号...")
    signal_model = MomentumSignalModel(
        short_window=3,
        long_window=6,
        threshold=0.3
    )
    
    decisions = signal_model.generate(bars)
    print(f"✓ 生成 {len(decisions)} 个候选信号")
    
    # 筛选为每周2次
    filtered_decisions = signal_model.filter_trading_slots(decisions, max_trades_per_week=2)
    print(f"✓ 筛选后剩余 {len(filtered_decisions)} 个交易信号")
    
    # 统计信号分布
    from src.signals.momentum import TradeAction as SignalAction
    buy_signals = sum(1 for d in filtered_decisions if d.action == SignalAction.BUY)
    sell_signals = sum(1 for d in filtered_decisions if d.action == SignalAction.SELL)
    print(f"  - BUY 信号: {buy_signals}")
    print(f"  - SELL 信号: {sell_signals}")
    print()
    
    # 3. 转换信号格式用于回测
    print("🔄 准备回测信号...")
    from src.signals.momentum import TradeAction as SignalAction
    from src.portfolio.allocator import PositionAllocator, RiskBudget
    
    # 使用仓位分配器计算交易数量
    allocator = PositionAllocator(symbol="TSLA", risk_budget=RiskBudget(capital=100_000))
    
    signals = []
    for decision in filtered_decisions:
        # 获取建议仓位
        plan = allocator.propose(decision)
        if not plan:
            continue
        
        # 转换动作
        if decision.action == SignalAction.BUY:
            action = TradeAction.BUY
        elif decision.action == SignalAction.SELL:
            action = TradeAction.SELL
        else:
            continue
        
        # 使用计划的仓位数量
        quantity = plan.quantity
        if quantity > 0:
            signals.append((pd.Timestamp(decision.bar.date), action, quantity))
    
    print(f"✓ 准备 {len(signals)} 个有效交易信号")
    print()
    
    # 4. 运行回测
    print("🚀 开始回测...")
    print("-" * 60)
    
    backtester = Backtester(
        initial_cash=100000.0,  # 初始资金 $100,000
        commission_rate=0.001,   # 0.1% 佣金率
        risk_free_rate=0.02      # 2% 无风险利率
    )
    
    # 注意:如果只有SELL信号,在回测开始时建立初始仓位
    if signals and all(action == TradeAction.SELL for _, action, _ in signals):
        print("⚠️  警告: 只检测到卖出信号,在回测开始时建立初始仓位")
        # 在第一个交易日建立仓位
        initial_price = price_df['close'].iloc[0]
        initial_date = price_df['date'].iloc[0]
        initial_quantity = int(backtester.account.initial_cash * 0.2 / initial_price)  # 投入20%资金
        
        # 手动创建初始买入
        from src.backtest.engine import Trade
        initial_trade = Trade(
            date=initial_date,
            action=TradeAction.BUY,
            symbol="TSLA",
            quantity=initial_quantity,
            price=initial_price
        )
        backtester.account.execute_trade(initial_trade, initial_price)
        print(f"  初始建仓: {initial_quantity} 股 @ ${initial_price:.2f}")
        print()
    
    metrics = backtester.run(price_df, signals)
    
    print("✓ 回测完成!")
    print()
    
    # 5. 显示回测结果
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
    
    # 6. 显示最终账户状态
    equity_curve = backtester.get_equity_curve()
    final_equity = equity_curve['equity'].iloc[-1]
    initial_equity = backtester.account.initial_cash
    
    print("【账户状态】")
    print(f"  初始资金:     ${initial_equity:>10,.2f}")
    print(f"  最终资产:     ${final_equity:>10,.2f}")
    print(f"  绝对收益:     ${final_equity - initial_equity:>10,.2f}")
    print()
    
    # 7. 保存详细结果
    print("💾 保存结果...")
    
    # 保存资产净值曲线
    equity_path = project_root / "backtest_results" / "equity_curve.csv"
    equity_path.parent.mkdir(exist_ok=True)
    equity_curve.to_csv(equity_path, index=False)
    print(f"✓ 资产净值曲线: {equity_path}")
    
    # 保存交易记录
    trades_df = backtester.get_trades()
    if not trades_df.empty:
        trades_path = project_root / "backtest_results" / "trades.csv"
        trades_df.to_csv(trades_path, index=False)
        print(f"✓ 交易记录: {trades_path}")
    
    # 保存性能指标
    metrics_path = project_root / "backtest_results" / "metrics.txt"
    with open(metrics_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("特斯拉(TSLA)量化策略回测报告\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"回测日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据范围: {bars[0].date} 至 {bars[-1].date}\n")
        f.write(f"总交易日: {len(bars)}\n\n")
        
        for key, value in metrics.to_dict().items():
            f.write(f"{key}: {value}\n")
    
    print(f"✓ 性能指标: {metrics_path}")
    print()
    
    print("=" * 60)
    print("✅ 回测完成!所有结果已保存到 backtest_results/ 目录")
    print("=" * 60)


if __name__ == "__main__":
    main()
