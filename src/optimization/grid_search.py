"""
策略参数网格搜索优化

通过遍历参数空间,找到最优参数组合
"""
import sys
from pathlib import Path
from datetime import datetime
from itertools import product
from typing import List, Dict, Any
import pandas as pd
from dataclasses import dataclass, asdict

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import CSVPriceLoader
from src.signals.momentum import MomentumSignalModel, TradeAction as SignalAction
from src.portfolio.allocator import PositionAllocator, RiskBudget
from src.backtest.enhanced_engine import EnhancedBacktester, RiskConfig, TradeAction


@dataclass
class ParameterSet:
    """参数集合"""
    # 策略参数
    short_window: int
    long_window: int
    threshold: float
    max_trades_per_week: int
    
    # 风险参数
    stop_loss_pct: float
    trailing_stop_pct: float
    max_position_pct: float
    
    def __str__(self):
        return (f"SW={self.short_window}, LW={self.long_window}, "
                f"TH={self.threshold:.2f}, TPW={self.max_trades_per_week}, "
                f"SL={self.stop_loss_pct:.1%}, TS={self.trailing_stop_pct:.1%}")


@dataclass
class OptimizationResult:
    """优化结果"""
    params: ParameterSet
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        result = asdict(self.params)
        result.update({
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'total_trades': self.total_trades,
        })
        return result


class ParameterOptimizer:
    """参数优化器"""
    
    def __init__(self, price_data: pd.DataFrame, initial_cash: float = 100000.0):
        self.price_data = price_data
        self.initial_cash = initial_cash
        self.results: List[OptimizationResult] = []
    
    def grid_search(
        self,
        short_windows: List[int],
        long_windows: List[int],
        thresholds: List[float],
        trades_per_week: List[int],
        stop_loss_pcts: List[float],
        trailing_stop_pcts: List[float],
        max_position_pcts: List[float] = [0.5],
        verbose: bool = True
    ) -> pd.DataFrame:
        """
        网格搜索最优参数
        
        Args:
            short_windows: 短期窗口列表
            long_windows: 长期窗口列表
            thresholds: 阈值列表
            trades_per_week: 每周交易次数列表
            stop_loss_pcts: 止损百分比列表
            trailing_stop_pcts: 移动止损百分比列表
            max_position_pcts: 最大持仓比例列表
            verbose: 是否显示详细信息
        
        Returns:
            结果DataFrame
        """
        # 生成所有参数组合
        param_combinations = list(product(
            short_windows, long_windows, thresholds, trades_per_week,
            stop_loss_pcts, trailing_stop_pcts, max_position_pcts
        ))
        
        total = len(param_combinations)
        print(f"🔍 开始网格搜索: 共 {total} 个参数组合\n")
        
        # 转换价格数据为bars
        from src.data.loader import PriceBar
        bars = [
            PriceBar(
                date=row['date'].date(),
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row['volume']
            )
            for _, row in self.price_data.iterrows()
        ]
        
        # 遍历所有组合
        for idx, (sw, lw, th, tpw, sl, ts, mp) in enumerate(param_combinations, 1):
            # 跳过无效组合
            if sw >= lw:
                continue
            
            params = ParameterSet(
                short_window=sw,
                long_window=lw,
                threshold=th,
                max_trades_per_week=tpw,
                stop_loss_pct=sl,
                trailing_stop_pct=ts,
                max_position_pct=mp
            )
            
            if verbose and idx % 10 == 0:
                print(f"  进度: {idx}/{total} ({idx/total:.1%})")
            
            try:
                result = self._backtest_with_params(bars, params)
                self.results.append(result)
            except Exception as e:
                if verbose:
                    print(f"  ⚠️  参数 {params} 测试失败: {e}")
                continue
        
        print(f"\n✅ 网格搜索完成! 成功测试 {len(self.results)}/{total} 个组合\n")
        
        # 转换为DataFrame
        return self._results_to_dataframe()
    
    def _backtest_with_params(
        self, 
        bars: List,
        params: ParameterSet
    ) -> OptimizationResult:
        """使用指定参数运行回测"""
        # 1. 生成信号
        model = MomentumSignalModel(
            short_window=params.short_window,
            long_window=params.long_window,
            threshold=params.threshold
        )
        decisions = model.generate(bars)
        filtered_decisions = model.filter_trading_slots(
            decisions, 
            max_trades_per_week=params.max_trades_per_week
        )
        
        # 2. 转换信号
        allocator = PositionAllocator(
            symbol="TSLA",
            risk_budget=RiskBudget(capital=self.initial_cash)
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
        
        # 3. 运行回测
        risk_config = RiskConfig(
            stop_loss_pct=params.stop_loss_pct,
            trailing_stop_pct=params.trailing_stop_pct,
            max_position_pct=params.max_position_pct
        )
        
        backtester = EnhancedBacktester(
            initial_cash=self.initial_cash,
            commission_rate=0.001,
            risk_config=risk_config
        )
        
        metrics = backtester.run(self.price_data, signals)
        
        # 4. 返回结果
        return OptimizationResult(
            params=params,
            total_return=metrics.total_return,
            annual_return=metrics.annual_return,
            sharpe_ratio=metrics.sharpe_ratio,
            max_drawdown=metrics.max_drawdown,
            win_rate=metrics.win_rate,
            total_trades=metrics.total_trades
        )
    
    def _results_to_dataframe(self) -> pd.DataFrame:
        """转换结果为DataFrame"""
        if not self.results:
            return pd.DataFrame()
        
        data = [r.to_dict() for r in self.results]
        return pd.DataFrame(data)
    
    def get_top_results(
        self, 
        n: int = 10,
        sort_by: str = 'sharpe_ratio',
        ascending: bool = False
    ) -> pd.DataFrame:
        """获取Top N结果"""
        df = self._results_to_dataframe()
        if df.empty:
            return df
        
        return df.sort_values(sort_by, ascending=ascending).head(n)


def main():
    """运行参数优化"""
    print("=" * 70)
    print("🔬 策略参数优化 - 网格搜索")
    print("=" * 70)
    print()
    
    # 1. 加载数据
    print("📂 加载历史数据...")
    data_path = project_root / "data" / "sample_tsla.csv"
    
    # 读取CSV
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"✓ 已加载 {len(df)} 条数据")
    print(f"  日期范围: {df['date'].min().date()} 至 {df['date'].max().date()}")
    print()
    
    # 2. 定义搜索空间
    print("🎯 定义参数搜索空间...")
    search_space = {
        'short_windows': [2, 3, 4],
        'long_windows': [5, 6, 8],
        'thresholds': [0.15, 0.20, 0.30],
        'trades_per_week': [2],
        'stop_loss_pcts': [0.15, 0.20, 0.25],  # -15%, -20%, -25%
        'trailing_stop_pcts': [0.15, 0.20, 0.25],
        'max_position_pcts': [0.5]
    }
    
    for key, values in search_space.items():
        print(f"  {key}: {values}")
    print()
    
    # 3. 运行优化
    optimizer = ParameterOptimizer(df, initial_cash=100000.0)
    
    results_df = optimizer.grid_search(
        short_windows=search_space['short_windows'],
        long_windows=search_space['long_windows'],
        thresholds=search_space['thresholds'],
        trades_per_week=search_space['trades_per_week'],
        stop_loss_pcts=search_space['stop_loss_pcts'],
        trailing_stop_pcts=search_space['trailing_stop_pcts'],
        max_position_pcts=search_space['max_position_pcts'],
        verbose=True
    )
    
    # 4. 显示结果
    if results_df.empty:
        print("❌ 没有有效结果")
        return
    
    print("=" * 70)
    print("📊 优化结果")
    print("=" * 70)
    print()
    
    # 按不同指标排序
    metrics = [
        ('sharpe_ratio', '夏普比率', False),
        ('total_return', '总收益率', False),
        ('max_drawdown', '最大回撤', True),
    ]
    
    for metric, name, ascending in metrics:
        print(f"\n🏆 按{name}排序 Top 5:")
        print("-" * 70)
        
        top_results = optimizer.get_top_results(n=5, sort_by=metric, ascending=ascending)
        
        for idx, row in top_results.iterrows():
            print(f"\n#{list(top_results.index).index(idx) + 1}:")
            print(f"  策略参数: SW={row['short_window']}, LW={row['long_window']}, "
                  f"TH={row['threshold']:.2f}, TPW={row['max_trades_per_week']}")
            print(f"  风险参数: SL={row['stop_loss_pct']:.1%}, TS={row['trailing_stop_pct']:.1%}")
            print(f"  总收益率: {row['total_return']:.2%}")
            print(f"  年化收益: {row['annual_return']:.2%}")
            print(f"  夏普比率: {row['sharpe_ratio']:.2f}")
            print(f"  最大回撤: {row['max_drawdown']:.2%}")
            print(f"  胜率: {row['win_rate']:.2%}")
            print(f"  交易次数: {row['total_trades']}")
    
    # 5. 保存结果
    output_dir = project_root / "optimization_results"
    output_dir.mkdir(exist_ok=True)
    
    results_path = output_dir / f"grid_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    results_df.to_csv(results_path, index=False, encoding='utf-8-sig')
    
    print(f"\n\n💾 完整结果已保存到: {results_path}")
    print(f"   共 {len(results_df)} 个有效参数组合")
    
    print("\n" + "=" * 70)
    print("✅ 参数优化完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
