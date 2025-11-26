"""
技术指标计算库
提供 RSI, ATR, MACD, Bollinger Bands 等常用指标计算
"""
import pandas as pd
import numpy as np

class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """
        计算相对强弱指数 (RSI)
        
        Args:
            series: 价格序列
            period: 计算周期 (默认14)
            
        Returns:
            RSI序列 (0-100)
        """
        delta = series.diff()
        
        # 分离上涨和下跌
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        # 计算平均涨跌幅 (使用Wilder平滑法)
        avg_gain = gain.ewm(com=period-1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period-1, min_periods=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        计算平均真实波幅 (ATR)
        用于衡量波动率和设置动态止损
        """
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """计算MACD指标"""
        exp1 = close.ewm(span=fast, adjust=False).mean()
        exp2 = close.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return macd, signal_line, histogram

    @staticmethod
    def calculate_bollinger_bands(close: pd.Series, period: int = 20, std_dev: int = 2):
        """计算布林带"""
        ma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        
        upper = ma + (std * std_dev)
        lower = ma - (std * std_dev)
        
        return upper, ma, lower
