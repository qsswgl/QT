"""Data loading utilities for TSLA sample data."""
from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class PriceBar:
    """Represents a single OHLCV bar."""

    date: dt.date
    open: float
    high: float
    low: float
    close: float
    volume: int


class CSVPriceLoader:
    """Load OHLCV data from a CSV file.

    The CSV is expected to contain columns: date, open, high, low, close, volume.
    Dates should follow the ISO format (YYYY-MM-DD).
    """

    def __init__(self, csv_path: Path) -> None:
        self._path = csv_path
        if not self._path.exists():
            raise FileNotFoundError(f"CSV file not found: {self._path}")

    def load(self, limit: Optional[int] = None) -> List[PriceBar]:
        records: List[PriceBar] = []
        with self._path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                price_bar = PriceBar(
                    date=dt.date.fromisoformat(row["date"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=int(row["volume"]),
                )
                records.append(price_bar)
                if limit is not None and len(records) >= limit:
                    break
        return records

    def stream(self) -> Iterable[PriceBar]:
        """Stream price bars lazily."""
        with self._path.open("r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                yield PriceBar(
                    date=dt.date.fromisoformat(row["date"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=int(row["volume"]),
                )
