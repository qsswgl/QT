"""Market data providers and ingestion workflow."""
from __future__ import annotations

import datetime as dt
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import yfinance as yf

from src.data.loader import PriceBar

logger = logging.getLogger(__name__)

DownloadFn = Callable[..., pd.DataFrame]


class YFinanceClient:
    """Thin wrapper around `yfinance` for easier testing."""

    def __init__(self, download_fn: Optional[DownloadFn] = None) -> None:
        self._download = download_fn or yf.download
        self._use_ticker_api = download_fn is None  # Use Ticker API for real downloads

    def fetch_daily_history(
        self,
        symbol: str,
        start: Optional[dt.date] = None,
        end: Optional[dt.date] = None,
        period: str = "3mo",
        max_retries: int = 3,
        retry_delay: float = 10.0,  # 增加延迟到10秒
    ) -> pd.DataFrame:
        last_error = None
        for attempt in range(max_retries):
            try:
                if self._use_ticker_api:
                    # Use Ticker API which is more reliable for large date ranges
                    ticker = yf.Ticker(symbol)
                    if start and end:
                        data = ticker.history(start=start.isoformat(), end=end.isoformat(), interval="1d", auto_adjust=False)
                    elif start:
                        data = ticker.history(start=start.isoformat(), interval="1d", auto_adjust=False)
                    elif period:
                        data = ticker.history(period=period, interval="1d", auto_adjust=False)
                    else:
                        data = ticker.history(period="3mo", interval="1d", auto_adjust=False)
                else:
                    # Use download function (for testing)
                    params = {
                        "tickers": symbol,
                        "interval": "1d",
                        "auto_adjust": False,
                        "progress": False,
                        "threads": False,
                    }
                    if start:
                        params["start"] = start.isoformat()
                    if end:
                        params["end"] = end.isoformat()
                    if period and "start" not in params:
                        params["period"] = period
                    data = self._download(**params)
                
                if not data.empty:
                    break
                logger.warning("Empty data received for %s, attempt %d/%d", symbol, attempt + 1, max_retries)
            except Exception as e:
                last_error = e
                logger.warning("Download failed for %s: %s, attempt %d/%d", symbol, e, attempt + 1, max_retries)
            
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                logger.info("Waiting %d seconds before retry...", wait_time)
                time.sleep(wait_time)
        else:
            raise ValueError(f"No data received for {symbol} after {max_retries} attempts") from last_error
        
        if data.empty:
            raise ValueError(f"No data received for {symbol}")

        if isinstance(data.columns, pd.MultiIndex):
            # yfinance returns multi-index columns for multiple tickers; select the first level.
            data = data.xs(symbol, axis="columns", level=0)

        data = data.reset_index().rename(columns=str.lower)
        data.rename(columns={"date": "timestamp"}, inplace=True)
        data["timestamp"] = pd.to_datetime(data["timestamp"]).dt.tz_localize(None)
        data["date"] = data["timestamp"].dt.date
        data = data[["date", "open", "high", "low", "close", "volume"]]
        return data


@dataclass(frozen=True)
class IngestionResult:
    rows_written: int
    min_date: dt.date
    max_date: dt.date


class DailyBarIngestor:
    """Fetch and persist daily OHLCV bars to CSV with deduplication."""

    def __init__(self, client: YFinanceClient, output_path: Path) -> None:
        self._client = client
        self._output_path = output_path

    def run(
        self,
        symbol: str,
        start: Optional[dt.date] = None,
        end: Optional[dt.date] = None,
        period: str = "3mo",
    ) -> IngestionResult:
        fetched = self._client.fetch_daily_history(symbol, start=start, end=end, period=period)
        formatted = _format_for_csv(fetched)

        if self._output_path.exists():
            existing = pd.read_csv(self._output_path)
            combined = pd.concat([existing, formatted], ignore_index=True)
        else:
            combined = formatted

        combined.drop_duplicates(subset="date", keep="last", inplace=True)
        combined.sort_values(by="date", inplace=True)
        combined.to_csv(self._output_path, index=False)

        return IngestionResult(
            rows_written=len(combined),
            min_date=dt.date.fromisoformat(combined.iloc[0]["date"]),
            max_date=dt.date.fromisoformat(combined.iloc[-1]["date"]),
        )

    @staticmethod
    def to_price_bars(frame: pd.DataFrame) -> list[PriceBar]:
        bars: list[PriceBar] = []
        for row in frame.itertuples(index=False):
            bars.append(
                PriceBar(
                    date=row.date if isinstance(row.date, dt.date) else dt.date.fromisoformat(row.date),
                    open=float(row.open),
                    high=float(row.high),
                    low=float(row.low),
                    close=float(row.close),
                    volume=int(row.volume),
                )
            )
        return bars


def _format_for_csv(data: pd.DataFrame) -> pd.DataFrame:
    formatted = data.copy()
    formatted["date"] = formatted["date"].astype(str)
    formatted[["open", "high", "low", "close"]] = formatted[["open", "high", "low", "close"]].astype(float)
    formatted["volume"] = formatted["volume"].astype(int)
    return formatted
