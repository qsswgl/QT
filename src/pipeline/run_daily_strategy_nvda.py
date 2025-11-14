"""
NVDA日内交易策略 - 每天交易1次

针对NVDA (英伟达) 的日内动量策略:
1. 使用更短的时间窗口捕捉日内趋势
2. 每天最多交易1次(开盘或日内信号)
3. 日内平仓,不持仓过夜(降低隔夜风险)
4. 基于日内动量和成交量
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple
import pandas as pd
import numpy as np

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import CSVPriceLoader, PriceBar
from src.backtest.engine import Backtester, TradeAction


class DailyTradingStrategyNVDA:
    """NVDA日内交易策略 - 每天1次"""
    
    def __init__(
        self,
        initial_cash: float = 100000.0,
        position_pct: float = 0.6,  # 60%仓位
        momentum_window: int = 5,    # 5日动量
        trend_window: int = 20,      # 20日趋势过滤
        volume_threshold: float = 1.3,  # 成交量阈值(相对平均)
        profit_target: float = 0.05,    # 止盈5%
        stop_loss: float = 0.02         # 止损2%
    ):
        self.initial_cash = initial_cash
        self.position_pct = position_pct
        self.momentum_window = momentum_window
        self.trend_window = trend_window
        self.volume_threshold = volume_threshold
        self.profit_target = profit_target
        self.stop_loss = stop_loss
        self.symbol = "NVDA"
    
    def calculate_momentum(self, bars: List[PriceBar], current_idx: int) -> float:
        """计算短期动量"""
        if current_idx < self.momentum_window:
            return 0.0
        
        current_price = bars[current_idx].close
        prev_price = bars[current_idx - self.momentum_window].close
        
        momentum = (current_price - prev_price) / prev_price
        return momentum
    
    def check_volume_surge(self, bars: List[PriceBar], current_idx: int) -> bool:
        """检查成交量是否放大"""
        if current_idx < 20:
            return False
        
        avg_volume = np.mean([bars[i].volume for i in range(current_idx - 20, current_idx)])
        current_volume = bars[current_idx].volume
        
        return current_volume > avg_volume * self.volume_threshold
    
    def is_in_uptrend(self, bars: List[PriceBar], current_idx: int) -> bool:
        """判断是否处于上升趋势"""
        if current_idx < self.trend_window:
            return False
        
        recent_closes = [bars[i].close for i in range(
            current_idx - self.trend_window + 1, 
            current_idx + 1
        )]
        ma = np.mean(recent_closes)
        
        return bars[current_idx].close > ma
    
    def should_buy(self, bars: List[PriceBar], current_idx: int, has_position: bool) -> bool:
        """判断是否应该买入"""
        if has_position:
            return False
        
        if current_idx < self.trend_window:
            return False
        
        if not self.is_in_uptrend(bars, current_idx):
            return False
        
        momentum = self.calculate_momentum(bars, current_idx)
        volume_surge = self.check_volume_surge(bars, current_idx)
        
        return momentum > 0.03 and volume_surge
    
    def should_sell(
        self, 
        bars: List[PriceBar], 
        current_idx: int, 
        has_position: bool,
        entry_price: float = None
    ) -> Tuple[bool, str]:
        """判断是否应该卖出"""
        if not has_position:
            return False, ""
        
        current_price = bars[current_idx].close
        
        if entry_price:
            pnl_pct = (current_price - entry_price) / entry_price
            
            if pnl_pct > self.profit_target:
                return True, f"止盈 (盈利{pnl_pct:.2%})"
            
            if pnl_pct < -self.stop_loss:
                return True, f"止损 (亏损{pnl_pct:.2%})"
        
        momentum = self.calculate_momentum(bars, current_idx)
        if momentum < -0.02:
            return True, f"动量转负 ({momentum:.2%})"
        
        return False, ""
    
    def generate_signals(self, bars: List[PriceBar]) -> List[dict]:
        """生成交易信号"""
        signals = []
        current_cash = self.initial_cash
        current_position = 0
        entry_price = None
        last_trade_date = None
        
        for idx, bar in enumerate(bars):
            current_date = pd.Timestamp(bar.date)
            
            if last_trade_date and current_date.date() == last_trade_date.date():
                continue
            
            has_position = current_position > 0
            
            if has_position:
                should_sell, reason = self.should_sell(bars, idx, has_position, entry_price)
                
                if should_sell:
                    signals.append({
                        'date': current_date,
                        'action': TradeAction.SELL,
                        'quantity': current_position,
                        'reason': reason,
                        'price': bar.close
                    })
                    
                    proceeds = current_position * bar.close * 0.999
                    current_cash += proceeds
                    current_position = 0
                    entry_price = None
                    last_trade_date = current_date
                    continue
            
            if self.should_buy(bars, idx, has_position):
                position_value = current_cash * self.position_pct
                quantity = int(position_value / bar.close)
                
                if quantity > 0:
                    signals.append({
                        'date': current_date,
                        'action': TradeAction.BUY,
                        'quantity': quantity,
                        'reason': f"动量突破 + 成交量放大 (动量={self.calculate_momentum(bars, idx):.2%})",
                        'price': bar.close
                    })
                    
                    cost = quantity * bar.close * 1.001
                    current_cash -= cost
                    current_position = quantity
                    entry_price = bar.close
                    last_trade_date = current_date
        
        return signals
    
    def run_backtest(self, bars: List[PriceBar]) -> dict:
        """运行回测"""
        print("=" * 60)
        print(f"📊 {self.symbol} 日内交易策略回测 (每天1次)")
        print("=" * 60)
        print()
        
        print("⚙️  策略配置:")
        print(f"  股票代码: {self.symbol}")
        print(f"  仓位比例: {self.position_pct:.0%}")
        print(f"  动量窗口: {self.momentum_window}日")
        print(f"  趋势窗口: {self.trend_window}日")
        print(f"  成交量阈值: {self.volume_threshold:.1f}x平均")
        print(f"  止盈: {self.profit_target:.0%}")
        print(f"  止损: {self.stop_loss:.0%}")
        print(f"  交易频率: 每天最多1次")
        print()
        
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
        
        print("🎯 生成交易信号...")
        signals = self.generate_signals(bars)
        
        buy_signals = sum(1 for s in signals if s['action'] == TradeAction.BUY)
        sell_signals = sum(1 for s in signals if s['action'] == TradeAction.SELL)
        
        print(f"✓ 生成 {len(signals)} 个交易信号")
        print(f"  - BUY 信号: {buy_signals}")
        print(f"  - SELL 信号: {sell_signals}")
        print()
        
        signal_list = [(s['date'], s['action'], s['quantity']) for s in signals]
        
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
        
        self._print_results(metrics, backtester, bars, signals)
        self._save_results(metrics, backtester, signals, bars)
        
        return {
            'metrics': metrics,
            'backtester': backtester,
            'signals': signals
        }
    
    def _print_results(self, metrics, backtester, bars, signals):
        """打印回测结果"""
        print("=" * 60)
        print(f"📈 {self.symbol} 回测性能报告")
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
        
        total_days = len(bars)
        trades_per_year = (len(signals) / total_days) * 252
        
        print("【交易频率】")
        print(f"  回测天数:     {total_days:>10}")
        print(f"  总信号数:     {len(signals):>10}")
        print(f"  平均每年:     {trades_per_year:>10.1f} 次交易")
        print(f"  平均每周:     {trades_per_year/52:>10.1f} 次交易")
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
        
        results_dir = project_root / "NVDA" / "backtest_results" / "daily"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        equity_curve = backtester.get_equity_curve()
        equity_path = results_dir / "equity_curve_daily.csv"
        equity_curve.to_csv(equity_path, index=False)
        print(f"✓ 资产净值曲线: {equity_path}")
        
        trades_df = backtester.get_trades()
        if not trades_df.empty:
            trades_path = results_dir / "trades_daily.csv"
            trades_df.to_csv(trades_path, index=False)
            print(f"✓ 交易记录: {trades_path}")
        
        signals_df = pd.DataFrame(signals)
        if not signals_df.empty:
            signals_path = results_dir / "signals_daily.csv"
            signals_df.to_csv(signals_path, index=False)
            print(f"✓ 信号记录: {signals_path}")
        
        summary_path = results_dir / "summary_daily.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"{self.symbol} 日内交易策略回测报告 (每天1次)\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"回测日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"股票代码: {self.symbol}\n")
            f.write(f"数据范围: {bars[0].date} 至 {bars[-1].date}\n")
            f.write(f"总交易日: {len(bars)}\n\n")
            
            f.write("策略特点:\n")
            f.write("  1. 短期动量: 5日动量指标\n")
            f.write("  2. 成交量确认: 放量突破\n")
            f.write("  3. 日内交易: 每天最多1次\n")
            f.write("  4. 快速止盈止损: 5% / 2%\n\n")
            
            f.write("配置参数:\n")
            f.write(f"  仓位比例: {self.position_pct:.0%}\n")
            f.write(f"  动量窗口: {self.momentum_window}日\n")
            f.write(f"  成交量阈值: {self.volume_threshold:.1f}x\n\n")
            
            f.write("性能指标:\n")
            for key, value in metrics.to_dict().items():
                f.write(f"  {key}: {value}\n")
        
        print(f"✓ 总结报告: {summary_path}")
        print()
        
        print("=" * 60)
        print(f"✅ {self.symbol} 日内交易策略回测完成!")
        print("=" * 60)


def main():
    """主函数"""
    print("📂 加载NVDA历史数据...")
    data_path = project_root / "NVDA" / "data" / "sample_nvda.csv"
    
    if not data_path.exists():
        print(f"❌ 数据文件不存在: {data_path}")
        print("请先运行数据更新脚本获取NVDA数据")
        return None
    
    loader = CSVPriceLoader(data_path)
    bars = list(loader.load())
    print(f"✓ 已加载 {len(bars)} 条历史数据")
    print(f"  日期范围: {bars[0].date} 至 {bars[-1].date}")
    print()
    
    strategy = DailyTradingStrategyNVDA(
        initial_cash=100000.0,
        position_pct=0.6,
        momentum_window=5,
        trend_window=20,
        volume_threshold=1.3,
        profit_target=0.05,
        stop_loss=0.02
    )
    
    results = strategy.run_backtest(bars)
    
    return results


if __name__ == "__main__":
    main()
