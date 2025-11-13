"""Format Yahoo Finance downloaded CSV to match our schema."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def format_yahoo_csv(input_path: Path, output_path: Path) -> None:
    """Convert Yahoo Finance CSV format to our standardized format.
    
    Yahoo format: Date,Open,High,Low,Close,Adj Close,Volume
    Our format: date,open,high,low,close,volume
    """
    logger.info("Reading %s", input_path)
    df = pd.read_csv(input_path)
    
    # Rename columns to lowercase and remove 'Adj Close'
    column_mapping = {
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    
    df = df.rename(columns=column_mapping)
    df = df[["date", "open", "high", "low", "close", "volume"]]
    
    # Sort by date ascending
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    
    # Remove any rows with missing data
    df = df.dropna()
    
    logger.info("Formatted %d rows", len(df))
    logger.info("Date range: %s to %s", df.iloc[0]["date"], df.iloc[-1]["date"])
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Saved to %s", output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Format Yahoo Finance CSV")
    parser.add_argument(
        "--input",
        default="data/TSLA.csv",
        help="Path to downloaded Yahoo Finance CSV",
    )
    parser.add_argument(
        "--output",
        default="data/sample_tsla.csv",
        help="Path to output formatted CSV",
    )
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error("Input file not found: %s", input_path)
        logger.info("Please download TSLA data from Yahoo Finance first")
        logger.info("See docs/manual_data_download.md for instructions")
        return
    
    format_yahoo_csv(input_path, output_path)


if __name__ == "__main__":
    main()
