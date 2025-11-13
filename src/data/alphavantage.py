"""Alpha Vantage data provider with rate limiting and error handling."""
from __future__ import annotations

import datetime as dt
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AlphaVantageConfig:
    """Configuration for Alpha Vantage API client."""
    
    api_key: str
    base_url: str = "https://www.alphavantage.co/query"
    rate_limit_delay: float = 12.0  # Free tier: 5 calls/min = 12s between calls
    timeout: int = 30
    max_retries: int = 3


class AlphaVantageClient:
    """Client for fetching stock data from Alpha Vantage API.
    
    Free tier limits:
    - 500 API calls per day
    - 5 API calls per minute
    
    Usage:
        config = AlphaVantageConfig(api_key="YOUR_API_KEY")
        client = AlphaVantageClient(config)
        data = client.fetch_daily_history("TSLA", outputsize="full")
    """
    
    def __init__(self, config: Optional[AlphaVantageConfig] = None) -> None:
        if config is None:
            api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key required. Set ALPHAVANTAGE_API_KEY environment variable or pass AlphaVantageConfig. "
                    "Get free key at: https://www.alphavantage.co/support/#api-key"
                )
            config = AlphaVantageConfig(api_key=api_key)
        
        self._config = config
        self._last_call_time: Optional[float] = None
    
    def fetch_daily_history(
        self,
        symbol: str,
        outputsize: str = "full",
        adjusted: bool = False,
    ) -> pd.DataFrame:
        """Fetch daily OHLCV data for a symbol.
        
        Args:
            symbol: Stock ticker (e.g., "TSLA")
            outputsize: "compact" (last 100 days) or "full" (20+ years)
            adjusted: If True, returns adjusted prices
            
        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        self._enforce_rate_limit()
        
        function = "TIME_SERIES_DAILY_ADJUSTED" if adjusted else "TIME_SERIES_DAILY"
        params = {
            "function": function,
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": self._config.api_key,
            "datatype": "json",
        }
        
        for attempt in range(self._config.max_retries):
            try:
                logger.info("Fetching %s data from Alpha Vantage (attempt %d/%d)", symbol, attempt + 1, self._config.max_retries)
                response = requests.get(
                    self._config.base_url,
                    params=params,
                    timeout=self._config.timeout,
                )
                response.raise_for_status()
                data = response.json()
                
                # Check for API errors
                if "Error Message" in data:
                    raise ValueError(f"API error: {data['Error Message']}")
                
                if "Note" in data:
                    # Rate limit message
                    logger.warning("Rate limit message: %s", data["Note"])
                    if attempt < self._config.max_retries - 1:
                        time.sleep(60)  # Wait 1 minute
                        continue
                    raise ValueError("Rate limit exceeded")
                
                # Parse time series data
                time_series_key = "Time Series (Daily)"
                if time_series_key not in data:
                    raise ValueError(f"Unexpected response format. Keys: {list(data.keys())}")
                
                return self._parse_daily_data(data[time_series_key], adjusted=adjusted)
                
            except requests.RequestException as e:
                logger.warning("Request failed: %s (attempt %d/%d)", e, attempt + 1, self._config.max_retries)
                if attempt < self._config.max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                else:
                    raise ValueError(f"Failed to fetch data after {self._config.max_retries} attempts") from e
        
        raise ValueError("Failed to fetch data")
    
    def _parse_daily_data(self, time_series: dict, adjusted: bool) -> pd.DataFrame:
        """Parse Alpha Vantage time series JSON into DataFrame."""
        records = []
        
        for date_str, values in time_series.items():
            record = {
                "date": date_str,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["5. adjusted close" if adjusted else "4. close"]),
                "volume": int(values["6. volume" if adjusted else "5. volume"]),
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"]).dt.date
        df = df.sort_values("date").reset_index(drop=True)
        
        logger.info("Parsed %d records from %s to %s", len(df), df.iloc[0]["date"], df.iloc[-1]["date"])
        return df
    
    def _enforce_rate_limit(self) -> None:
        """Ensure we don't exceed 5 calls per minute."""
        if self._last_call_time is not None:
            elapsed = time.time() - self._last_call_time
            if elapsed < self._config.rate_limit_delay:
                sleep_time = self._config.rate_limit_delay - elapsed
                logger.info("Rate limiting: sleeping %.1f seconds", sleep_time)
                time.sleep(sleep_time)
        
        self._last_call_time = time.time()


class AlphaVantageIngestor:
    """Ingest data from Alpha Vantage and save to CSV."""
    
    def __init__(self, client: AlphaVantageClient, output_path: Path) -> None:
        self._client = client
        self._output_path = output_path
    
    def run(self, symbol: str, outputsize: str = "full") -> dict:
        """Fetch and save data, merging with existing if present."""
        fetched = self._client.fetch_daily_history(symbol, outputsize=outputsize)
        
        if self._output_path.exists():
            existing = pd.read_csv(self._output_path)
            existing["date"] = pd.to_datetime(existing["date"]).dt.date
            combined = pd.concat([existing, fetched], ignore_index=True)
        else:
            combined = fetched
        
        combined.drop_duplicates(subset="date", keep="last", inplace=True)
        combined.sort_values(by="date", inplace=True)
        
        # Format dates as strings for CSV
        combined["date"] = combined["date"].astype(str)
        combined.to_csv(self._output_path, index=False)
        
        return {
            "rows_written": len(combined),
            "min_date": combined.iloc[0]["date"],
            "max_date": combined.iloc[-1]["date"],
        }
