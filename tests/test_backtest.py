"""
回测引擎单元测试
"""
import unittest
from datetime import datetime, timedelta
import pandas as pd
from src.backtest.engine import (
    Backtester, BacktestAccount, Trade, TradeAction, 
    Position, BacktestMetrics
)


class TestBacktestAccount(unittest.TestCase):
    """测试回测账户功能"""
    
    def setUp(self):
        """初始化测试账户"""
        self.account = BacktestAccount(
            initial_cash=100000.0,
            commission_rate=0.001
        )
    
    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.account.cash, 100000.0)
        self.assertEqual(len(self.account.positions), 0)
        self.assertEqual(len(self.account.trades), 0)
    
    def test_buy_trade(self):
        """测试买入交易"""
        trade = Trade(
            date=datetime(2020, 1, 1),
            action=TradeAction.BUY,
            symbol="TSLA",
            quantity=10,
            price=100.0
        )
        
        success = self.account.execute_trade(trade, 100.0)
        
        self.assertTrue(success)
        self.assertLess(self.account.cash, 99000.0)  # 扣除佣金
        self.assertIn("TSLA", self.account.positions)
        self.assertEqual(self.account.positions["TSLA"].quantity, 10)
    
    def test_sell_trade(self):
        """测试卖出交易"""
        # 先买入
        buy_trade = Trade(
            date=datetime(2020, 1, 1),
            action=TradeAction.BUY,
            symbol="TSLA",
            quantity=10,
            price=100.0
        )
        self.account.execute_trade(buy_trade, 100.0)
        
        # 再卖出
        sell_trade = Trade(
            date=datetime(2020, 1, 2),
            action=TradeAction.SELL,
            symbol="TSLA",
            quantity=5,
            price=120.0
        )
        success = self.account.execute_trade(sell_trade, 120.0)
        
        self.assertTrue(success)
        self.assertEqual(self.account.positions["TSLA"].quantity, 5)
    
    def test_insufficient_cash(self):
        """测试资金不足"""
        trade = Trade(
            date=datetime(2020, 1, 1),
            action=TradeAction.BUY,
            symbol="TSLA",
            quantity=10000,
            price=100.0
        )
        
        success = self.account.execute_trade(trade, 100.0)
        self.assertFalse(success)
    
    def test_insufficient_position(self):
        """测试持仓不足"""
        trade = Trade(
            date=datetime(2020, 1, 1),
            action=TradeAction.SELL,
            symbol="TSLA",
            quantity=10,
            price=100.0
        )
        
        success = self.account.execute_trade(trade, 100.0)
        self.assertFalse(success)
    
    def test_total_equity(self):
        """测试总资产计算"""
        # 买入股票
        trade = Trade(
            date=datetime(2020, 1, 1),
            action=TradeAction.BUY,
            symbol="TSLA",
            quantity=100,
            price=100.0
        )
        self.account.execute_trade(trade, 100.0)
        
        # 计算总资产(假设价格涨到150)
        current_prices = {"TSLA": 150.0}
        total_equity = self.account.get_total_equity(current_prices)
        
        # 应该是: 剩余现金 + 持仓市值
        expected = self.account.cash + 100 * 150.0
        self.assertAlmostEqual(total_equity, expected, places=2)


class TestBacktester(unittest.TestCase):
    """测试回测引擎"""
    
    def create_sample_data(self):
        """创建样本数据"""
        dates = [datetime(2020, 1, 1) + timedelta(days=i) for i in range(100)]
        prices = [100.0 + i * 0.5 for i in range(100)]  # 价格逐步上涨
        
        return pd.DataFrame({
            'date': dates,
            'close': prices
        })
    
    def test_simple_backtest(self):
        """测试简单回测"""
        data = self.create_sample_data()
        
        # 创建简单的买入-持有-卖出信号
        signals = [
            (datetime(2020, 1, 2), TradeAction.BUY, 100),
            (datetime(2020, 4, 9), TradeAction.SELL, 100)
        ]
        
        backtester = Backtester(initial_cash=100000.0)
        metrics = backtester.run(data, signals)
        
        # 验证有交易发生
        self.assertGreater(len(backtester.account.trades), 0)
        
        # 验证有收益(价格上涨)
        self.assertGreater(metrics.total_return, 0)
    
    def test_no_signals(self):
        """测试无信号情况"""
        data = self.create_sample_data()
        signals = []
        
        backtester = Backtester(initial_cash=100000.0)
        metrics = backtester.run(data, signals)
        
        # 无交易,收益为0
        self.assertEqual(metrics.total_return, 0.0)
        self.assertEqual(metrics.total_trades, 0)
    
    def test_equity_curve(self):
        """测试资产净值曲线"""
        data = self.create_sample_data()
        signals = [
            (datetime(2020, 1, 2), TradeAction.BUY, 100)
        ]
        
        backtester = Backtester(initial_cash=100000.0)
        backtester.run(data, signals)
        
        equity_df = backtester.get_equity_curve()
        
        # 验证资产曲线长度
        self.assertEqual(len(equity_df), len(data))
        
        # 验证资产净值递增(因为价格上涨)
        self.assertGreater(equity_df['equity'].iloc[-1], equity_df['equity'].iloc[0])


if __name__ == '__main__':
    unittest.main()
