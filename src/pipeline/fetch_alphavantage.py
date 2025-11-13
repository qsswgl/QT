"""Fetch TSLA data using Alpha Vantage API."""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.data.alphavantage import AlphaVantageClient, AlphaVantageConfig, AlphaVantageIngestor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch stock data from Alpha Vantage API",
        epilog="Get your free API key at: https://www.alphavantage.co/support/#api-key",
    )
    parser.add_argument("symbol", nargs="?", default="TSLA", help="Stock ticker symbol")
    parser.add_argument(
        "--api-key",
        help="Alpha Vantage API key (or set ALPHAVANTAGE_API_KEY env var)",
    )
    parser.add_argument(
        "--outputsize",
        choices=["compact", "full"],
        default="full",
        help="compact=last 100 days, full=20+ years (default: full)",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[2] / "data" / "sample_tsla.csv"),
        help="Output CSV file path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create config
    if args.api_key:
        config = AlphaVantageConfig(api_key=args.api_key)
    else:
        config = None  # Will use ALPHAVANTAGE_API_KEY env var
    
    try:
        client = AlphaVantageClient(config)
        ingestor = AlphaVantageIngestor(client=client, output_path=output_path)
        
        logger.info("Fetching %s data (outputsize=%s) to %s", args.symbol, args.outputsize, output_path)
        result = ingestor.run(symbol=args.symbol, outputsize=args.outputsize)
        
        logger.info("✓ Success! Saved %d rows", result["rows_written"])
        logger.info("  Date range: %s → %s", result["min_date"], result["max_date"])
        logger.info("  Output: %s", output_path)
        
    except ValueError as e:
        logger.error("Failed to fetch data: %s", e)
        logger.info("\nTo get started:")
        logger.info("1. Get free API key: https://www.alphavantage.co/support/#api-key")
        logger.info("2. Set environment variable: $env:ALPHAVANTAGE_API_KEY='YOUR_KEY'")
        logger.info("3. Or pass --api-key YOUR_KEY")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
