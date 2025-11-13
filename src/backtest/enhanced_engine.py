"""
增强回测引擎 - 包含止损和风险管理

在原有引擎基础上添加:
1. 固定止损 (Stop Loss)
2. 移动止损 (Trailing Stop)
3. 最大回撤限制
4. 动态仓位管理
"""
from dataclasses import dataclass
from typing import Optional
import pandas as pd
from datetime import datetime

from src.backtest.engine import (
    Backtester, BacktestAccount, Trade, TradeAction,
    BacktestMetrics
)


@dataclass
class RiskConfig:
    """风险控制配置"""
    # 止损设置
    stop_loss_pct: Optional[float] = None  # 固定止损百分比 (如 0.2 = -20%)
    trailing_stop_pct: Optional[float] = None  # 移动止损百分比
    
    # 回撤控制
    max_portfolio_drawdown: Optional[float] = None  # 最大组合回撤 (如 0.3 = -30%)
    
    # 仓位管理
    max_position_pct: float = 0.5  # 最大单笔持仓占比
    
    def __post_init__(self):
        """验证配置"""
        if self.stop_loss_pct and not (0 < self.stop_loss_pct <= 1):
            raise ValueError("stop_loss_pct 必须在 (0, 1] 区间")
        if self.trailing_stop_pct and not (0 < self.trailing_stop_pct <= 1):
            raise ValueError("trailing_stop_pct 必须在 (0, 1] 区间")
        if self.max_portfolio_drawdown and not (0 < self.max_portfolio_drawdown <= 1):
            raise ValueError("max_portfolio_drawdown 必须在 (0, 1] 区间")


class EnhancedBacktester(Backtester):
    """增强回测引擎 - 包含风险管理"""
    
    def __init__(
        self,
        initial_cash: float = 100000.0,
        commission_rate: float = 0.001,
        risk_free_rate: float = 0.02,
        risk_config: Optional[RiskConfig] = None
    ):
        super().__init__(initial_cash, commission_rate, risk_free_rate)
        self.risk_config = risk_config or RiskConfig()
        
        # 止损跟踪
        self.position_entry_prices: dict = {}  # {symbol: entry_price}
        self.position_highest_prices: dict = {}  # {symbol: highest_price} 用于移动止损
        
        # 回撤跟踪
        self.peak_equity: float = initial_cash
        
        # 统计
        self.stop_loss_exits: int = 0
        self.trailing_stop_exits: int = 0
        self.drawdown_stops: int = 0
    
    def run(
        self,
        price_data: pd.DataFrame,
        signals: list[tuple[datetime, TradeAction, int]]
    ) -> BacktestMetrics:
        """运行增强回测"""
        # 转换信号为字典
        signal_dict = {date: (action, qty) for date, action, qty in signals}
        
        # 确保价格数据按日期排序
        price_data = price_data.sort_values('date').reset_index(drop=True)
        
        # 遍历每个交易日
        for idx, row in price_data.iterrows():
            self.current_date = row['date']
            current_price = row['close']
            symbol = "TSLA"
            
            # 1. 检查风险控制(在执行新信号前)
            self._check_risk_controls(symbol, current_price)
            
            # 2. 更新峰值资产(用于回撤计算)
            current_equity = self.account.get_total_equity({symbol: current_price})
            if current_equity > self.peak_equity:
                self.peak_equity = current_equity
            
            # 3. 检查是否有新信号
            if self.current_date in signal_dict:
                action, quantity = signal_dict[self.current_date]
                
                # 检查最大回撤限制
                if self._should_halt_trading(current_equity):
                    print(f"⚠️  {self.current_date.date()}: 达到最大回撤限制,暂停交易")
                    continue
                
                if action != TradeAction.HOLD:
                    # 调整仓位大小(考虑最大持仓限制)
                    adjusted_qty = self._adjust_position_size(
                        quantity, current_price, action
                    )
                    
                    if adjusted_qty > 0:
                        trade = Trade(
                            date=self.current_date,
                            action=action,
                            symbol=symbol,
                            quantity=adjusted_qty,
                            price=current_price
                        )
                        success = self.account.execute_trade(trade, current_price)
                        
                        # 记录建仓价格
                        if success and action == TradeAction.BUY:
                            self.position_entry_prices[symbol] = current_price
                            self.position_highest_prices[symbol] = current_price
            
            # 4. 更新移动止损的最高价
            if symbol in self.position_highest_prices:
                if current_price > self.position_highest_prices[symbol]:
                    self.position_highest_prices[symbol] = current_price
            
            # 5. 记录当日资产净值
            equity = self.account.get_total_equity({symbol: current_price})
            self.account.record_equity(self.current_date, equity)
        
        # 计算并返回性能指标
        metrics = self._calculate_metrics()
        
        # 打印风控统计
        if self.stop_loss_exits > 0 or self.trailing_stop_exits > 0 or self.drawdown_stops > 0:
            print(f"\n📊 风险控制统计:")
            print(f"  固定止损触发: {self.stop_loss_exits} 次")
            print(f"  移动止损触发: {self.trailing_stop_exits} 次")
            print(f"  回撤限制触发: {self.drawdown_stops} 次")
        
        return metrics
    
    def _check_risk_controls(self, symbol: str, current_price: float):
        """检查并执行风险控制"""
        position = self.account.get_position(symbol)
        if not position or position.quantity == 0:
            return
        
        entry_price = self.position_entry_prices.get(symbol)
        if not entry_price:
            return
        
        # 1. 固定止损检查
        if self.risk_config.stop_loss_pct:
            loss_pct = (current_price - entry_price) / entry_price
            if loss_pct <= -self.risk_config.stop_loss_pct:
                print(f"🛑 {self.current_date.date()}: 触发固定止损 "
                      f"({loss_pct:.2%}), 平仓 {position.quantity} 股 @ ${current_price:.2f}")
                self._execute_stop_loss(symbol, position.quantity, current_price)
                self.stop_loss_exits += 1
                return
        
        # 2. 移动止损检查
        if self.risk_config.trailing_stop_pct:
            highest_price = self.position_highest_prices.get(symbol, entry_price)
            trailing_loss_pct = (current_price - highest_price) / highest_price
            
            if trailing_loss_pct <= -self.risk_config.trailing_stop_pct:
                print(f"🛑 {self.current_date.date()}: 触发移动止损 "
                      f"(从峰值${highest_price:.2f}回落{trailing_loss_pct:.2%}), "
                      f"平仓 {position.quantity} 股 @ ${current_price:.2f}")
                self._execute_stop_loss(symbol, position.quantity, current_price)
                self.trailing_stop_exits += 1
                return
    
    def _execute_stop_loss(self, symbol: str, quantity: int, price: float):
        """执行止损平仓"""
        trade = Trade(
            date=self.current_date,
            action=TradeAction.SELL,
            symbol=symbol,
            quantity=quantity,
            price=price
        )
        success = self.account.execute_trade(trade, price)
        
        if success:
            # 清除跟踪数据
            self.position_entry_prices.pop(symbol, None)
            self.position_highest_prices.pop(symbol, None)
    
    def _should_halt_trading(self, current_equity: float) -> bool:
        """检查是否应暂停交易(因达到最大回撤限制)"""
        if not self.risk_config.max_portfolio_drawdown:
            return False
        
        current_drawdown = (current_equity - self.peak_equity) / self.peak_equity
        
        if current_drawdown <= -self.risk_config.max_portfolio_drawdown:
            self.drawdown_stops += 1
            return True
        
        return False
    
    def _adjust_position_size(
        self, 
        quantity: int, 
        price: float, 
        action: TradeAction
    ) -> int:
        """调整仓位大小(考虑最大持仓限制)"""
        if action != TradeAction.BUY:
            return quantity
        
        # 计算最大可买入金额
        max_amount = self.account.cash * self.risk_config.max_position_pct
        max_quantity = int(max_amount / price)
        
        # 返回较小值
        return min(quantity, max_quantity)
    
    def get_risk_stats(self) -> dict:
        """获取风险控制统计"""
        return {
            "固定止损触发次数": self.stop_loss_exits,
            "移动止损触发次数": self.trailing_stop_exits,
            "回撤限制触发次数": self.drawdown_stops,
            "峰值资产": self.peak_equity,
        }
