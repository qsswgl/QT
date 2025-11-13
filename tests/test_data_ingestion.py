import datetime as dt
import tempfile
from pathlib import Path
from typing import List

import pandas as pd
import unittest

from src.data.providers import DailyBarIngestor


class StubClient:
    def __init__(self, frames: List[pd.DataFrame]) -> None:
        self._frames = frames

    def fetch_daily_history(self, *args, **kwargs) -> pd.DataFrame:
        if not self._frames:
            raise AssertionError("No more frames available")
        return self._frames.pop(0)


class DailyBarIngestorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name) / "tsla.csv"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_run_writes_ordered_csv(self) -> None:
        frame = pd.DataFrame(
            {
                "date": [dt.date(2024, 10, 20), dt.date(2024, 10, 21)],
                "open": [250.0, 251.0],
                "high": [255.0, 256.0],
                "low": [249.0, 250.0],
                "close": [254.0, 255.5],
                "volume": [1000000, 1100000],
            }
        )
        ingestor = DailyBarIngestor(client=StubClient([frame]), output_path=self.output_path)
        result = ingestor.run(symbol="TSLA")

        saved = pd.read_csv(self.output_path)
        self.assertEqual(len(saved), 2)
        self.assertListEqual(saved["date"].tolist(), ["2024-10-20", "2024-10-21"])
        self.assertEqual(result.rows_written, 2)
        self.assertEqual(result.min_date, dt.date(2024, 10, 20))
        self.assertEqual(result.max_date, dt.date(2024, 10, 21))

    def test_run_deduplicates_existing_data(self) -> None:
        initial = pd.DataFrame(
            {
                "date": ["2024-10-19", "2024-10-20"],
                "open": [248.0, 249.0],
                "high": [249.5, 250.5],
                "low": [247.5, 248.5],
                "close": [249.0, 249.5],
                "volume": [900000, 950000],
            }
        )
        initial.to_csv(self.output_path, index=False)

        new_frame = pd.DataFrame(
            {
                "date": [dt.date(2024, 10, 20), dt.date(2024, 10, 21)],
                "open": [249.0, 252.0],
                "high": [250.0, 254.0],
                "low": [248.0, 251.0],
                "close": [249.8, 253.5],
                "volume": [960000, 1200000],
            }
        )
        ingestor = DailyBarIngestor(client=StubClient([new_frame]), output_path=self.output_path)
        result = ingestor.run(symbol="TSLA")

        saved = pd.read_csv(self.output_path)
        self.assertEqual(len(saved), 3)
        self.assertListEqual(saved["date"].tolist(), ["2024-10-19", "2024-10-20", "2024-10-21"])
        # Latest values for overlapping date should be retained (compare close price)
        row = saved[saved["date"] == "2024-10-20"].iloc[0]
        self.assertEqual(row["close"], 249.8)
        self.assertEqual(result.rows_written, 3)
        self.assertEqual(result.min_date, dt.date(2024, 10, 19))
        self.assertEqual(result.max_date, dt.date(2024, 10, 21))


if __name__ == "__main__":
    unittest.main()
