"""
回测引擎核心模块

负责模拟历史交易执行和性能统计
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import pandas as pd
import numpy as np


class TradeAction(Enum):
    """交易动作"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class Trade:
    """单笔交易记录"""
    date: datetime
    action: TradeAction
    symbol: str
    quantity: int
    price: float
    commission: float = 0.0
    
    @property
    def total_cost(self) -> float:
        """总成本(含佣金)"""
        return abs(self.quantity * self.price) + self.commission
    
    @property
    def side(self) -> str:
        """交易方向"""
        return "BUY" if self.action == TradeAction.BUY else "SELL"


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    quantity: int
    avg_cost: float
    
    @property
    def market_value(self) -> float:
        """持仓市值"""
        return self.quantity * self.avg_cost
    
    def update(self, trade: Trade):
        """更新持仓"""
        if trade.action == TradeAction.BUY:
            # 买入:加权平均成本
            total_cost = self.market_value + trade.total_cost
            self.quantity += trade.quantity
            self.avg_cost = total_cost / self.quantity if self.quantity > 0 else 0
        elif trade.action == TradeAction.SELL:
            # 卖出:减少持仓
            self.quantity -= trade.quantity
            if self.quantity <= 0:
                self.quantity = 0
                self.avg_cost = 0


@dataclass
class BacktestAccount:
    """回测账户"""
    initial_cash: float
    cash: float = field(default=0.0)
    positions: Dict[str, Position] = field(default_factory=dict)
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[tuple[datetime, float]] = field(default_factory=list)
    commission_rate: float = 0.001  # 0.1% 佣金率
    
    def __post_init__(self):
        if self.cash == 0.0:
            self.cash = self.initial_cash
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """获取持仓"""
        return self.positions.get(symbol)
    
    def execute_trade(self, trade: Trade, current_price: float):
        """执行交易"""
        # 计算佣金
        trade.commission = trade.total_cost * self.commission_rate
        
        if trade.action == TradeAction.BUY:
            # 检查现金是否足够
            total_cost = trade.total_cost
            if self.cash < total_cost:
                print(f"⚠️  资金不足: 需要 ${total_cost:.2f}, 可用 ${self.cash:.2f}")
                return False
            
            # 扣除现金
            self.cash -= total_cost
            
            # 更新持仓
            if trade.symbol not in self.positions:
                self.positions[trade.symbol] = Position(trade.symbol, 0, 0.0)
            self.positions[trade.symbol].update(trade)
            
        elif trade.action == TradeAction.SELL:
            # 检查持仓是否足够
            position = self.get_position(trade.symbol)
            if not position or position.quantity < trade.quantity:
                print(f"⚠️  持仓不足: {trade.symbol}")
                return False
            
            # 增加现金
            proceeds = trade.quantity * trade.price - trade.commission
            self.cash += proceeds
            
            # 更新持仓
            position.update(trade)
            if position.quantity == 0:
                del self.positions[trade.symbol]
        
        # 记录交易
        self.trades.append(trade)
        return True
    
    def get_total_equity(self, current_prices: Dict[str, float]) -> float:
        """计算总资产"""
        positions_value = sum(
            pos.quantity * current_prices.get(pos.symbol, pos.avg_cost)
            for pos in self.positions.values()
        )
        return self.cash + positions_value
    
    def record_equity(self, date: datetime, equity: float):
        """记录资产净值"""
        self.equity_curve.append((date, equity))


@dataclass
class BacktestMetrics:
    """回测性能指标"""
    total_return: float  # 总收益率
    annual_return: float  # 年化收益率
    sharpe_ratio: float  # 夏普比率
    max_drawdown: float  # 最大回撤
    win_rate: float  # 胜率
    total_trades: int  # 总交易次数
    profit_trades: int  # 盈利交易数
    loss_trades: int  # 亏损交易数
    avg_profit: float  # 平均盈利
    avg_loss: float  # 平均亏损
    profit_factor: float  # 盈亏比
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "总收益率": f"{self.total_return:.2%}",
            "年化收益率": f"{self.annual_return:.2%}",
            "夏普比率": f"{self.sharpe_ratio:.2f}",
            "最大回撤": f"{self.max_drawdown:.2%}",
            "胜率": f"{self.win_rate:.2%}",
            "总交易次数": self.total_trades,
            "盈利交易": self.profit_trades,
            "亏损交易": self.loss_trades,
            "平均盈利": f"${self.avg_profit:.2f}",
            "平均亏损": f"${self.avg_loss:.2f}",
            "盈亏比": f"{self.profit_factor:.2f}",
        }


class Backtester:
    """回测引擎"""
    
    def __init__(
        self,
        initial_cash: float = 100000.0,
        commission_rate: float = 0.001,
        risk_free_rate: float = 0.02  # 无风险利率(年化)
    ):
        self.account = BacktestAccount(
            initial_cash=initial_cash,
            commission_rate=commission_rate
        )
        self.risk_free_rate = risk_free_rate
        self.current_date: Optional[datetime] = None
    
    def run(
        self,
        price_data: pd.DataFrame,
        signals: List[tuple[datetime, TradeAction, int]]
    ) -> BacktestMetrics:
        """
        运行回测
        
        Args:
            price_data: 价格数据 DataFrame (需包含 date, close 列)
            signals: 交易信号列表 [(日期, 动作, 数量), ...]
        
        Returns:
            回测性能指标
        """
        # 转换信号为字典便于查询
        signal_dict = {date: (action, qty) for date, action, qty in signals}
        
        # 确保价格数据按日期排序
        price_data = price_data.sort_values('date').reset_index(drop=True)
        
        # 遍历每个交易日
        for idx, row in price_data.iterrows():
            self.current_date = row['date']
            current_price = row['close']
            symbol = "TSLA"  # 当前只支持单股票
            
            # 检查是否有信号
            if self.current_date in signal_dict:
                action, quantity = signal_dict[self.current_date]
                
                if action != TradeAction.HOLD:
                    trade = Trade(
                        date=self.current_date,
                        action=action,
                        symbol=symbol,
                        quantity=quantity,
                        price=current_price
                    )
                    self.account.execute_trade(trade, current_price)
            
            # 记录当日资产净值
            equity = self.account.get_total_equity({symbol: current_price})
            self.account.record_equity(self.current_date, equity)
        
        # 计算性能指标
        return self._calculate_metrics()
    
    def _calculate_metrics(self) -> BacktestMetrics:
        """计算回测指标"""
        if not self.account.equity_curve:
            raise ValueError("没有资产净值数据")
        
        # 转换为 DataFrame
        equity_df = pd.DataFrame(
            self.account.equity_curve,
            columns=['date', 'equity']
        )
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        # 总收益率
        initial_equity = self.account.initial_cash
        final_equity = equity_df['equity'].iloc[-1]
        total_return = (final_equity - initial_equity) / initial_equity
        
        # 年化收益率
        days = (equity_df['date'].iloc[-1] - equity_df['date'].iloc[0]).days
        years = days / 365.25
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 夏普比率
        daily_returns = equity_df['returns'].dropna()
        if len(daily_returns) > 0 and daily_returns.std() > 0:
            excess_returns = daily_returns - (self.risk_free_rate / 252)
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / daily_returns.std()
        else:
            sharpe_ratio = 0.0
        
        # 最大回撤
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = abs(equity_df['drawdown'].min())
        
        # 交易统计
        trades = self.account.trades
        total_trades = len(trades)
        
        if total_trades == 0:
            return BacktestMetrics(
                total_return=total_return,
                annual_return=annual_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=0.0,
                total_trades=0,
                profit_trades=0,
                loss_trades=0,
                avg_profit=0.0,
                avg_loss=0.0,
                profit_factor=0.0
            )
        
        # 计算每笔交易的盈亏
        trade_pnls = []
        for i in range(len(trades)):
            if trades[i].action == TradeAction.SELL and i > 0:
                # 找到对应的买入交易
                for j in range(i - 1, -1, -1):
                    if trades[j].action == TradeAction.BUY:
                        pnl = (trades[i].price - trades[j].price) * trades[i].quantity - trades[i].commission - trades[j].commission
                        trade_pnls.append(pnl)
                        break
        
        if not trade_pnls:
            win_rate = 0.0
            profit_trades = 0
            loss_trades = 0
            avg_profit = 0.0
            avg_loss = 0.0
            profit_factor = 0.0
        else:
            profit_trades = sum(1 for pnl in trade_pnls if pnl > 0)
            loss_trades = sum(1 for pnl in trade_pnls if pnl < 0)
            win_rate = profit_trades / len(trade_pnls) if trade_pnls else 0
            
            profits = [pnl for pnl in trade_pnls if pnl > 0]
            losses = [abs(pnl) for pnl in trade_pnls if pnl < 0]
            
            avg_profit = np.mean(profits) if profits else 0
            avg_loss = np.mean(losses) if losses else 0
            
            total_profit = sum(profits) if profits else 0
            total_loss = sum(losses) if losses else 0
            profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        return BacktestMetrics(
            total_return=total_return,
            annual_return=annual_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=len(trade_pnls),
            profit_trades=profit_trades,
            loss_trades=loss_trades,
            avg_profit=avg_profit,
            avg_loss=avg_loss,
            profit_factor=profit_factor
        )
    
    def get_equity_curve(self) -> pd.DataFrame:
        """获取资产净值曲线"""
        return pd.DataFrame(
            self.account.equity_curve,
            columns=['date', 'equity']
        )
    
    def get_trades(self) -> pd.DataFrame:
        """获取交易记录"""
        if not self.account.trades:
            return pd.DataFrame()
        
        return pd.DataFrame([
            {
                'date': t.date,
                'action': t.action.value,
                'symbol': t.symbol,
                'quantity': t.quantity,
                'price': t.price,
                'commission': t.commission,
                'total': t.total_cost
            }
            for t in self.account.trades
        ])
