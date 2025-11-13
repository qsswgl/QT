"""Batch download TSLA history in chunks to avoid rate limiting."""
from __future__ import annotations

import datetime as dt
import logging
import time
from pathlib import Path

from src.data.providers import DailyBarIngestor, YFinanceClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def download_in_chunks(
    symbol: str,
    start_date: dt.date,
    end_date: dt.date,
    output_path: Path,
    chunk_months: int = 12,
    sleep_between: float = 15.0,
) -> None:
    """Download data in chunks to work around rate limiting."""
    client = YFinanceClient()
    ingestor = DailyBarIngestor(client=client, output_path=output_path)

    current = start_date
    total_chunks = 0
    
    while current < end_date:
        # Calculate chunk end (approximately chunk_months ahead)
        chunk_end = dt.date(
            current.year + (current.month + chunk_months - 1) // 12,
            (current.month + chunk_months - 1) % 12 + 1,
            1,
        )
        chunk_end = min(chunk_end, end_date)
        
        logger.info("Fetching chunk: %s to %s", current, chunk_end)
        
        try:
            result = ingestor.run(symbol=symbol, start=current, end=chunk_end)
            logger.info("✓ Downloaded %d rows, range %s → %s", result.rows_written, result.min_date, result.max_date)
            total_chunks += 1
        except Exception as e:
            logger.error("Failed to download chunk %s to %s: %s", current, chunk_end, e)
            logger.info("Waiting longer before retry...")
            time.sleep(sleep_between * 2)
            continue
        
        current = chunk_end
        
        if current < end_date:
            logger.info("Sleeping %.1f seconds before next chunk...", sleep_between)
            time.sleep(sleep_between)
    
    logger.info("Completed %d chunks. Data saved to %s", total_chunks, output_path)


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    output_path = project_root / "data" / "sample_tsla.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # TSLA IPO date: 2010-06-29
    start = dt.date(2010, 6, 29)
    end = dt.date.today()

    logger.info("Starting batch download from %s to %s", start, end)
    download_in_chunks(
        symbol="TSLA",
        start_date=start,
        end_date=end,
        output_path=output_path,
        chunk_months=12,
        sleep_between=20.0,  # Conservative delay
    )


if __name__ == "__main__":
    main()
