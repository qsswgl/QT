"""
真实持仓管理工具
从配置文件读取Firstrade账户的真实持仓信息
"""
import json
from pathlib import Path
from typing import Dict, Optional
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class RealPortfolioManager:
    """真实持仓管理器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化持仓管理器
        
        Args:
            config_path: 持仓配置文件路径,默认为 config/real_portfolio.json
        """
        if config_path is None:
            self.config_path = project_root / "config" / "real_portfolio.json"
        else:
            self.config_path = config_path
    
    def load_portfolio(self) -> dict:
        """
        加载完整持仓配置
        
        Returns:
            dict: 完整的持仓配置
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"持仓配置文件不存在: {self.config_path}\n"
                f"请先创建配置文件或手动输入持仓信息"
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_position(self, symbol: str, current_price: float = None) -> dict:
        """
        获取指定股票的持仓信息
        
        Args:
            symbol: 股票代码
            current_price: 当前价格(如果提供,会重新计算市值和盈亏)
        
        Returns:
            dict: 持仓信息 {symbol, quantity, avg_price, current_price, market_value, profit_loss, profit_loss_pct}
        """
        portfolio = self.load_portfolio()
        positions = portfolio.get('positions', {})
        
        if symbol not in positions:
            # 没有持仓
            return {
                'symbol': symbol,
                'quantity': 0,
                'avg_price': 0,
                'current_price': current_price or 0,
                'market_value': 0,
                'profit_loss': 0,
                'profit_loss_pct': 0
            }
        
        position = positions[symbol]
        quantity = position.get('quantity', 0)
        avg_price = position.get('avg_price', 0)
        
        # 使用提供的当前价格,或配置文件中的价格
        if current_price is None:
            current_price = position.get('current_price', avg_price)
        
        # 计算市值和盈亏
        market_value = quantity * current_price
        cost_basis = quantity * avg_price
        profit_loss = market_value - cost_basis
        profit_loss_pct = (profit_loss / cost_basis * 100) if cost_basis > 0 else 0
        
        return {
            'symbol': symbol,
            'quantity': int(quantity),
            'avg_price': avg_price,
            'current_price': current_price,
            'market_value': market_value,
            'profit_loss': profit_loss,
            'profit_loss_pct': profit_loss_pct
        }
    
    def get_all_positions(self, prices: Dict[str, float] = None) -> Dict[str, dict]:
        """
        获取所有持仓信息
        
        Args:
            prices: 最新价格字典 {symbol: price}
        
        Returns:
            Dict[str, dict]: 所有持仓信息
        """
        portfolio = self.load_portfolio()
        positions = portfolio.get('positions', {})
        
        result = {}
        for symbol, position_data in positions.items():
            current_price = None
            if prices and symbol in prices:
                current_price = prices[symbol]
            
            result[symbol] = self.get_position(symbol, current_price)
        
        return result
    
    def update_position(
        self, 
        symbol: str, 
        quantity: int = None,
        avg_price: float = None,
        current_price: float = None
    ):
        """
        更新持仓信息(手动维护)
        
        Args:
            symbol: 股票代码
            quantity: 持仓数量
            avg_price: 平均成本
            current_price: 当前价格
        """
        portfolio = self.load_portfolio()
        
        if symbol not in portfolio['positions']:
            portfolio['positions'][symbol] = {
                'symbol': symbol,
                'quantity': 0,
                'avg_price': 0,
                'current_price': 0,
                'market_value': 0,
                'cost_basis': 0,
                'unrealized_pnl': 0,
                'unrealized_pnl_pct': 0
            }
        
        position = portfolio['positions'][symbol]
        
        # 更新字段
        if quantity is not None:
            position['quantity'] = quantity
        if avg_price is not None:
            position['avg_price'] = avg_price
        if current_price is not None:
            position['current_price'] = current_price
        
        # 重新计算
        qty = position['quantity']
        avg = position['avg_price']
        cur = position['current_price']
        
        position['market_value'] = qty * cur
        position['cost_basis'] = qty * avg
        position['unrealized_pnl'] = position['market_value'] - position['cost_basis']
        position['unrealized_pnl_pct'] = (
            (position['unrealized_pnl'] / position['cost_basis'] * 100) 
            if position['cost_basis'] > 0 else 0
        )
        
        # 保存
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已更新 {symbol} 持仓信息")
        print(f"   持仓: {qty} 股 @ ${avg:.2f}")
        print(f"   市值: ${position['market_value']:,.2f}")
        print(f"   盈亏: ${position['unrealized_pnl']:,.2f} ({position['unrealized_pnl_pct']:.2f}%)")
    
    def get_account_summary(self) -> dict:
        """
        获取账户总览
        
        Returns:
            dict: 账户信息
        """
        portfolio = self.load_portfolio()
        return portfolio.get('account', {})


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("真实持仓管理器测试")
    print("=" * 60)
    print()
    
    manager = RealPortfolioManager()
    
    # 测试1: 读取NVDA持仓
    print("测试1: 读取NVDA持仓")
    nvda_pos = manager.get_position('NVDA', current_price=155.00)
    print(f"  持仓: {nvda_pos['quantity']} 股")
    print(f"  成本: ${nvda_pos['avg_price']:.2f}")
    print(f"  现价: ${nvda_pos['current_price']:.2f}")
    print(f"  市值: ${nvda_pos['market_value']:,.2f}")
    print(f"  盈亏: ${nvda_pos['profit_loss']:,.2f} ({nvda_pos['profit_loss_pct']:.2f}%)")
    print()
    
    # 测试2: 读取TSLA持仓
    print("测试2: 读取TSLA持仓")
    tsla_pos = manager.get_position('TSLA', current_price=420.00)
    print(f"  持仓: {tsla_pos['quantity']} 股")
    print(f"  成本: ${tsla_pos['avg_price']:.2f}")
    print(f"  现价: ${tsla_pos['current_price']:.2f}")
    print(f"  市值: ${tsla_pos['market_value']:,.2f}")
    print(f"  盈亏: ${tsla_pos['profit_loss']:,.2f} ({tsla_pos['profit_loss_pct']:.2f}%)")
    print()
    
    # 测试3: 读取INTC持仓
    print("测试3: 读取INTC持仓")
    intc_pos = manager.get_position('INTC', current_price=40.00)
    print(f"  持仓: {intc_pos['quantity']} 股")
    print(f"  成本: ${intc_pos['avg_price']:.2f}")
    print(f"  现价: ${intc_pos['current_price']:.2f}")
    print(f"  市值: ${intc_pos['market_value']:,.2f}")
    print(f"  盈亏: ${intc_pos['profit_loss']:,.2f} ({intc_pos['profit_loss_pct']:.2f}%)")
    print()
    
    # 测试4: 读取账户总览
    print("测试4: 读取账户总览")
    account = manager.get_account_summary()
    print(f"  券商: {account.get('broker')}")
    print(f"  账号: {account.get('account_number')}")
    print(f"  总值: ${account.get('total_value', 0):,.2f}")
    print(f"  现金: ${account.get('cash', 0):,.2f}")
    print()
    
    print("=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)
