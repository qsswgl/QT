"""
改进策略 - 趋势跟踪 + 仓位管理 (无止损)

针对TSLA等高波动成长股的优化策略:
1. 趋势确认: 只在明确上升趋势中做多
2. 分批建仓: 降低单次入场风险
3. 动态仓位: 根据信号强度调整仓位
4. 去除止损: 避免被正常波动止损出局
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import CSVPriceLoader, PriceBar
from src.signals.momentum import MomentumSignalModel, TradeAction as SignalAction
from src.backtest.engine import Backtester, TradeAction
import pandas as pd
import numpy as np


class ImprovedStrategy:
    """改进策略 - 趋势跟踪 + 动态仓位"""
    
    def __init__(
        self,
        initial_cash: float = 100000.0,
        max_position_pct: float = 0.6,  # 提高到60%
        trend_filter_window: int = 50,   # 50日趋势线
        position_scaling: bool = True     # 启用仓位缩放
    ):
        self.initial_cash = initial_cash
        self.max_position_pct = max_position_pct
        self.trend_filter_window = trend_filter_window
        self.position_scaling = position_scaling
    
    def has_uptrend(self, bars: List[PriceBar], current_idx: int) -> bool:
        """
        判断是否处于上升趋势
        
        条件: 当前价格 > 50日均线 且 50日均线向上
        """
        if current_idx < self.trend_filter_window:
            return False
        
        # 计算50日均线
        recent_closes = [bars[i].close for i in range(
            current_idx - self.trend_filter_window + 1, 
            current_idx + 1
        )]
        ma50 = np.mean(recent_closes)
        
        # 计算前一天的50日均线
        if current_idx < self.trend_filter_window + 1:
            return bars[current_idx].close > ma50
        
        prev_closes = [bars[i].close for i in range(
            current_idx - self.trend_filter_window, 
            current_idx
        )]
        prev_ma50 = np.mean(prev_closes)
        
        current_price = bars[current_idx].close
        
        # 价格在均线上方 且 均线向上
        return current_price > ma50 and ma50 > prev_ma50
    
    def calculate_position_size(
        self, 
        signal_score: float, 
        current_price: float,
        current_cash: float
    ) -> int:
        """
        根据信号强度计算仓位大小
        
        信号越强,仓位越大 (但不超过最大限制)
        """
        if not self.position_scaling:
            # 固定仓位
            position_value = current_cash * self.max_position_pct
            return int(position_value / current_price)
        
        # 动态仓位: 信号强度 × 最大仓位
        # signal_score 范围通常是 0-1,我们放大到 0.3-1.0
        scaled_score = min(1.0, max(0.3, abs(signal_score)))
        position_pct = scaled_score * self.max_position_pct
        
        position_value = current_cash * position_pct
        return int(position_value / current_price)
    
    def generate_signals(self, bars: List[PriceBar]) -> List[dict]:
        """
        生成交易信号
        
        返回: [{date, action, quantity, reason}, ...]
        """
        # 1. 使用动量模型生成初始信号
        model = MomentumSignalModel(
            short_window=3,
            long_window=10,  # 稍长的长期窗口
            threshold=0.25    # 稍高的阈值,减少噪音
        )
        
        decisions = model.generate(bars)
        filtered_decisions = model.filter_trading_slots(
            decisions, 
            max_trades_per_week=2
        )
        
        # 2. 应用趋势过滤和仓位计算
        signals = []
        current_cash = self.initial_cash
        current_position = 0
        
        for decision in filtered_decisions:
            # 找到当前bar的索引
            current_idx = next(
                (i for i, bar in enumerate(bars) if bar.date == decision.bar.date),
                None
            )
            
            if current_idx is None:
                continue
            
            # 买入信号
            if decision.action == SignalAction.BUY:
                # 趋势过滤: 只在上升趋势买入
                if not self.has_uptrend(bars, current_idx):
                    continue
                
                # 计算仓位
                quantity = self.calculate_position_size(
                    decision.score,
                    decision.bar.close,
                    current_cash
                )
                
                if quantity > 0:
                    signals.append({
                        'date': pd.Timestamp(decision.bar.date),
                        'action': TradeAction.BUY,
                        'quantity': quantity,
                        'reason': f"趋势确认 + {decision.reason}"
                    })
                    
                    # 更新模拟状态
                    cost = quantity * decision.bar.close * 1.001  # 含佣金
                    current_cash -= cost
                    current_position += quantity
            
            # 卖出信号
            elif decision.action == SignalAction.SELL:
                if current_position > 0:
                    # 全部卖出或部分卖出
                    sell_quantity = current_position
                    
                    signals.append({
                        'date': pd.Timestamp(decision.bar.date),
                        'action': TradeAction.SELL,
                        'quantity': sell_quantity,
                        'reason': decision.reason
                    })
                    
                    # 更新模拟状态
                    proceeds = sell_quantity * decision.bar.close * 0.999  # 扣佣金
                    current_cash += proceeds
                    current_position = 0
        
        return signals
    
    def run_backtest(self, bars: List[PriceBar]) -> dict:
        """运行回测"""
        print("=" * 60)
        print("📊 改进策略回测 (趋势跟踪 + 动态仓位)")
        print("=" * 60)
        print()
        
        print("⚙️  策略配置:")
        print(f"  最大仓位: {self.max_position_pct:.0%}")
        print(f"  趋势过滤: {self.trend_filter_window}日均线")
        print(f"  动态仓位: {'启用' if self.position_scaling else '禁用'}")
        print(f"  止损机制: 无 (适合长期持有)")
        print()
        
        # 转换为DataFrame
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
        
        # 生成信号
        print("🎯 生成交易信号...")
        signals = self.generate_signals(bars)
        
        buy_signals = sum(1 for s in signals if s['action'] == TradeAction.BUY)
        sell_signals = sum(1 for s in signals if s['action'] == TradeAction.SELL)
        
        print(f"✓ 生成 {len(signals)} 个交易信号")
        print(f"  - BUY 信号: {buy_signals}")
        print(f"  - SELL 信号: {sell_signals}")
        print()
        
        # 转换信号格式
        signal_list = [(s['date'], s['action'], s['quantity']) for s in signals]
        
        # 运行回测
        print("🚀 开始回测...")
        print("-" * 60)
        
        backtester = Backtester(
            initial_cash=self.initial_cash,
            commission_rate=0.001,
            risk_free_rate=0.02
        )
        
        metrics = backtester.run(price_df, signal_list)
        
        print("-" * 60)
        print("✓ 回测完成!")
        print()
        
        # 显示结果
        self._print_results(metrics, backtester, bars)
        
        # 保存结果
        self._save_results(metrics, backtester, signals, bars)
        
        return {
            'metrics': metrics,
            'backtester': backtester,
            'signals': signals
        }
    
    def _print_results(self, metrics, backtester, bars):
        """打印回测结果"""
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
        
        equity_curve = backtester.get_equity_curve()
        final_equity = equity_curve['equity'].iloc[-1]
        
        print("【账户状态】")
        print(f"  初始资金:     ${self.initial_cash:>10,.2f}")
        print(f"  最终资产:     ${final_equity:>10,.2f}")
        print(f"  绝对收益:     ${final_equity - self.initial_cash:>10,.2f}")
        print()
    
    def _save_results(self, metrics, backtester, signals, bars):
        """保存回测结果"""
        print("💾 保存结果...")
        
        results_dir = project_root / "backtest_results" / "improved"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存资产净值曲线
        equity_curve = backtester.get_equity_curve()
        equity_path = results_dir / "equity_curve_improved.csv"
        equity_curve.to_csv(equity_path, index=False)
        print(f"✓ 资产净值曲线: {equity_path}")
        
        # 保存交易记录
        trades_df = backtester.get_trades()
        if not trades_df.empty:
            trades_path = results_dir / "trades_improved.csv"
            trades_df.to_csv(trades_path, index=False)
            print(f"✓ 交易记录: {trades_path}")
        
        # 保存详细信号
        signals_df = pd.DataFrame(signals)
        if not signals_df.empty:
            signals_path = results_dir / "signals_improved.csv"
            signals_df.to_csv(signals_path, index=False)
            print(f"✓ 信号记录: {signals_path}")
        
        # 保存配置和指标
        summary_path = results_dir / "summary_improved.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("改进策略回测报告 (趋势跟踪 + 动态仓位)\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"回测日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据范围: {bars[0].date} 至 {bars[-1].date}\n")
            f.write(f"总交易日: {len(bars)}\n\n")
            
            f.write("策略特点:\n")
            f.write("  1. 趋势过滤: 只在上升趋势做多\n")
            f.write("  2. 动态仓位: 根据信号强度调整\n")
            f.write("  3. 无止损: 避免被正常波动清除\n")
            f.write("  4. 适用场景: 长期上涨的高波动股\n\n")
            
            f.write("配置参数:\n")
            f.write(f"  最大仓位: {self.max_position_pct:.0%}\n")
            f.write(f"  趋势窗口: {self.trend_filter_window}日\n")
            f.write(f"  动态仓位: {'是' if self.position_scaling else '否'}\n\n")
            
            f.write("性能指标:\n")
            for key, value in metrics.to_dict().items():
                f.write(f"  {key}: {value}\n")
        
        print(f"✓ 总结报告: {summary_path}")
        print()
        
        print("=" * 60)
        print("✅ 改进策略回测完成!")
        print("=" * 60)


def main():
    """主函数"""
    # 加载数据
    print("📂 加载历史数据...")
    data_path = project_root / "data" / "sample_tsla.csv"
    loader = CSVPriceLoader(data_path)
    bars = list(loader.load())
    print(f"✓ 已加载 {len(bars)} 条历史数据")
    print(f"  日期范围: {bars[0].date} 至 {bars[-1].date}")
    print()
    
    # 创建并运行改进策略
    strategy = ImprovedStrategy(
        initial_cash=100000.0,
        max_position_pct=0.6,      # 60% 最大仓位
        trend_filter_window=50,     # 50日趋势线
        position_scaling=True       # 启用动态仓位
    )
    
    results = strategy.run_backtest(bars)
    
    return results


if __name__ == "__main__":
    main()
