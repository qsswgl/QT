"""
多数据源提供商 - 支持多个免费API相互补充

支持的数据源:
1. Yahoo Finance (yfinance) - 免费，无需API key，但有频率限制
2. Alpha Vantage - 免费，需要API key，每天500次请求
3. Twelve Data - 免费，需要API key，每天800次请求
4. Polygon.io - 免费层级，需要API key，有限制
5. 备用: 从CSV缓存读取

使用策略:
- 优先使用Yahoo Finance (速度快，无需注册)
- 失败时自动切换到其他数据源
- 支持数据合并和验证
"""

import datetime as dt
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import os

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


@dataclass
class DataSourceConfig:
    """数据源配置"""
    name: str
    enabled: bool = True
    priority: int = 1  # 优先级，数字越小优先级越高
    api_key: Optional[str] = None
    rate_limit_per_day: Optional[int] = None
    rate_limit_per_minute: Optional[int] = None


class YahooFinanceProvider:
    """Yahoo Finance 数据提供商"""
    
    def __init__(self):
        self.name = "Yahoo Finance"
    
    def fetch_data(
        self,
        symbol: str,
        start: Optional[dt.date] = None,
        end: Optional[dt.date] = None,
        period: str = "3mo",
    ) -> pd.DataFrame:
        """获取数据"""
        try:
            ticker = yf.Ticker(symbol)
            
            if start and end:
                data = ticker.history(
                    start=start.isoformat(),
                    end=end.isoformat(),
                    interval="1d",
                    auto_adjust=False
                )
            elif start:
                data = ticker.history(
                    start=start.isoformat(),
                    interval="1d",
                    auto_adjust=False
                )
            else:
                data = ticker.history(
                    period=period,
                    interval="1d",
                    auto_adjust=False
                )
            
            if data.empty:
                raise ValueError("No data received")
            
            # 标准化列名
            data = data.reset_index()
            data.columns = [col.lower() for col in data.columns]
            
            if 'date' in data.columns:
                data.rename(columns={'date': 'timestamp'}, inplace=True)
            
            data['timestamp'] = pd.to_datetime(data['timestamp']).dt.tz_localize(None)
            data['date'] = data['timestamp'].dt.date
            
            return data[['date', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.warning(f"{self.name} failed: {e}")
            raise


class AlphaVantageProvider:
    """Alpha Vantage 数据提供商
    
    免费API Key申请: https://www.alphavantage.co/support/#api-key
    限制: 每天500次请求, 每分钟5次请求
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.name = "Alpha Vantage"
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        
        if not self.api_key:
            logger.warning(f"{self.name}: No API key provided")
    
    def fetch_data(
        self,
        symbol: str,
        start: Optional[dt.date] = None,
        end: Optional[dt.date] = None,
        period: str = "3mo",
    ) -> pd.DataFrame:
        """获取数据"""
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not configured")
        
        try:
            import requests
            
            # Alpha Vantage API - 获取完整历史数据
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'outputsize': 'full',  # full = 20年数据, compact = 100天
                'apikey': self.api_key,
                'datatype': 'json'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data_json = response.json()
            
            if 'Error Message' in data_json:
                raise ValueError(f"API Error: {data_json['Error Message']}")
            
            if 'Note' in data_json:
                raise ValueError(f"Rate limit: {data_json['Note']}")
            
            if 'Time Series (Daily)' not in data_json:
                raise ValueError("No time series data in response")
            
            # 解析数据
            time_series = data_json['Time Series (Daily)']
            records = []
            
            for date_str, values in time_series.items():
                records.append({
                    'date': dt.datetime.strptime(date_str, '%Y-%m-%d').date(),
                    'open': float(values['1. open']),
                    'high': float(values['2. high']),
                    'low': float(values['3. low']),
                    'close': float(values['4. close']),
                    'volume': int(values['5. volume'])
                })
            
            df = pd.DataFrame(records)
            df = df.sort_values('date')
            
            # 筛选日期范围
            if start:
                df = df[df['date'] >= start]
            if end:
                df = df[df['date'] <= end]
            
            if df.empty:
                raise ValueError("No data after date filtering")
            
            logger.info(f"{self.name}: Successfully fetched {len(df)} rows")
            return df
            
        except ImportError:
            raise ValueError("requests library not installed. Run: pip install requests")
        except Exception as e:
            logger.warning(f"{self.name} failed: {e}")
            raise


class TwelveDataProvider:
    """Twelve Data 数据提供商
    
    免费API Key申请: https://twelvedata.com/pricing
    限制: 每天800次请求, 每分钟8次请求
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.name = "Twelve Data"
        self.api_key = api_key or os.getenv('TWELVE_DATA_API_KEY')
        
        if not self.api_key:
            logger.warning(f"{self.name}: No API key provided")
    
    def fetch_data(
        self,
        symbol: str,
        start: Optional[dt.date] = None,
        end: Optional[dt.date] = None,
        period: str = "3mo",
    ) -> pd.DataFrame:
        """获取数据"""
        if not self.api_key:
            raise ValueError("Twelve Data API key not configured")
        
        try:
            import requests
            
            # Twelve Data API
            url = "https://api.twelvedata.com/time_series"
            params = {
                'symbol': symbol,
                'interval': '1day',
                'apikey': self.api_key,
                'format': 'JSON',
                'outputsize': 5000  # 最多5000条
            }
            
            if start:
                params['start_date'] = start.isoformat()
            if end:
                params['end_date'] = end.isoformat()
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data_json = response.json()
            
            if 'status' in data_json and data_json['status'] == 'error':
                raise ValueError(f"API Error: {data_json.get('message', 'Unknown error')}")
            
            if 'values' not in data_json:
                raise ValueError("No values in response")
            
            # 解析数据
            records = []
            for item in data_json['values']:
                records.append({
                    'date': dt.datetime.strptime(item['datetime'], '%Y-%m-%d').date(),
                    'open': float(item['open']),
                    'high': float(item['high']),
                    'low': float(item['low']),
                    'close': float(item['close']),
                    'volume': int(item['volume'])
                })
            
            df = pd.DataFrame(records)
            df = df.sort_values('date')
            
            if df.empty:
                raise ValueError("No data received")
            
            logger.info(f"{self.name}: Successfully fetched {len(df)} rows")
            return df
            
        except ImportError:
            raise ValueError("requests library not installed. Run: pip install requests")
        except Exception as e:
            logger.warning(f"{self.name} failed: {e}")
            raise


class MultiSourceDataClient:
    """多数据源智能客户端 - 自动尝试多个数据源"""
    
    def __init__(
        self,
        alpha_vantage_key: Optional[str] = None,
        twelve_data_key: Optional[str] = None,
    ):
        """
        初始化多数据源客户端
        
        Args:
            alpha_vantage_key: Alpha Vantage API密钥
            twelve_data_key: Twelve Data API密钥
        """
        # 初始化所有提供商
        self.providers = [
            (1, YahooFinanceProvider()),  # 优先级1 - 最高
        ]
        
        # 添加其他提供商（如果有API key）
        if alpha_vantage_key or os.getenv('ALPHA_VANTAGE_API_KEY'):
            self.providers.append((2, AlphaVantageProvider(alpha_vantage_key)))
        
        if twelve_data_key or os.getenv('TWELVE_DATA_API_KEY'):
            self.providers.append((3, TwelveDataProvider(twelve_data_key)))
        
        # 按优先级排序
        self.providers.sort(key=lambda x: x[0])
        
        logger.info(f"Initialized with {len(self.providers)} data providers")
        for priority, provider in self.providers:
            logger.info(f"  Priority {priority}: {provider.name}")
    
    def fetch_daily_history(
        self,
        symbol: str,
        start: Optional[dt.date] = None,
        end: Optional[dt.date] = None,
        period: str = "3mo",
        max_retries_per_source: int = 2,
    ) -> pd.DataFrame:
        """
        从多个数据源获取历史数据，自动尝试备用源
        
        Args:
            symbol: 股票代码
            start: 开始日期
            end: 结束日期
            period: 时间周期（如果start/end未指定）
            max_retries_per_source: 每个数据源的最大重试次数
        
        Returns:
            标准化的DataFrame，包含 date, open, high, low, close, volume
        """
        last_error = None
        
        for priority, provider in self.providers:
            logger.info(f"Trying {provider.name} (priority {priority})...")
            
            for attempt in range(max_retries_per_source):
                try:
                    data = provider.fetch_data(symbol, start, end, period)
                    
                    if not data.empty:
                        logger.info(f"✓ Successfully fetched data from {provider.name}")
                        logger.info(f"  Date range: {data['date'].min()} to {data['date'].max()}")
                        logger.info(f"  Total rows: {len(data)}")
                        return data
                    
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"{provider.name} attempt {attempt + 1}/{max_retries_per_source} failed: {e}"
                    )
                    
                    if attempt < max_retries_per_source - 1:
                        wait_time = 5 * (attempt + 1)
                        logger.info(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
            
            # 尝试下一个数据源前等待
            if priority < len(self.providers):
                logger.info("Trying next data source...")
                time.sleep(2)
        
        # 所有数据源都失败
        raise ValueError(
            f"Failed to fetch data for {symbol} from all available sources. "
            f"Last error: {last_error}"
        )


def create_multi_source_client(config_path: Optional[Path] = None) -> MultiSourceDataClient:
    """
    创建多数据源客户端（便捷工厂函数）
    
    API密钥可以通过以下方式提供:
    1. 环境变量:
       - ALPHA_VANTAGE_API_KEY
       - TWELVE_DATA_API_KEY
    
    2. 配置文件 (暂不支持，待实现)
    
    Args:
        config_path: 配置文件路径（可选）
    
    Returns:
        配置好的 MultiSourceDataClient 实例
    """
    # 从环境变量读取API密钥
    alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    twelve_data_key = os.getenv('TWELVE_DATA_API_KEY')
    
    # TODO: 从配置文件读取（如果提供）
    if config_path and config_path.exists():
        logger.info(f"Loading config from {config_path}")
        # 实现配置文件读取
    
    return MultiSourceDataClient(
        alpha_vantage_key=alpha_vantage_key,
        twelve_data_key=twelve_data_key,
    )


# 便捷函数：获取单个股票的数据
def fetch_stock_data(
    symbol: str,
    start: Optional[dt.date] = None,
    end: Optional[dt.date] = None,
    period: str = "3mo",
) -> pd.DataFrame:
    """
    便捷函数：使用多数据源获取股票数据
    
    示例:
        # 获取最近3个月数据
        data = fetch_stock_data("TSLA")
        
        # 获取指定日期范围
        data = fetch_stock_data(
            "TSLA",
            start=dt.date(2024, 1, 1),
            end=dt.date(2024, 12, 31)
        )
    """
    client = create_multi_source_client()
    return client.fetch_daily_history(symbol, start, end, period)
