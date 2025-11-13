"""Update local TSLA dataset via yfinance."""
from __future__ import annotations

import argparse
import datetime as dt
import logging
from pathlib import Path

from src.data.providers import DailyBarIngestor, YFinanceClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch TSLA daily data and update CSV store.")
    parser.add_argument("symbol", nargs="?", default="TSLA", help="Ticker symbol to download")
    parser.add_argument("--period", default="3mo", help="yfinance period parameter when start is not provided")
    parser.add_argument("--start", type=_parse_date, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=_parse_date, help="End date (YYYY-MM-DD)")
    default_output = Path(__file__).resolve().parents[2] / "data" / "sample_tsla.csv"
    parser.add_argument("--output", default=str(default_output), help="Path to the CSV output file")
    return parser.parse_args()


def _parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ingestor = DailyBarIngestor(client=YFinanceClient(), output_path=output_path)
    logger.info("Fetching %s data into %s", args.symbol, output_path)
    result = ingestor.run(symbol=args.symbol, start=args.start, end=args.end, period=args.period)
    logger.info("Updated %s rows. Date range: %s → %s", result.rows_written, result.min_date, result.max_date)


if __name__ == "__main__":
    main()
