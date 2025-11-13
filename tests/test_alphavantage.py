"""Tests for Alpha Vantage data provider."""
from __future__ import annotations

import datetime as dt
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd

from src.data.alphavantage import AlphaVantageClient, AlphaVantageConfig, AlphaVantageIngestor


class MockResponse:
    def __init__(self, json_data: dict, status_code: int = 200) -> None:
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self) -> dict:
        return self.json_data
    
    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class AlphaVantageClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = AlphaVantageConfig(api_key="test_key", rate_limit_delay=0.1)
    
    @patch("src.data.alphavantage.requests.get")
    def test_fetch_daily_history_success(self, mock_get: Mock) -> None:
        mock_response = MockResponse({
            "Time Series (Daily)": {
                "2024-10-25": {
                    "1. open": "250.00",
                    "2. high": "255.00",
                    "3. low": "248.00",
                    "4. close": "253.50",
                    "5. volume": "1000000",
                },
                "2024-10-24": {
                    "1. open": "248.00",
                    "2. high": "252.00",
                    "3. low": "247.00",
                    "4. close": "250.00",
                    "5. volume": "950000",
                },
            }
        })
        mock_get.return_value = mock_response
        
        client = AlphaVantageClient(self.config)
        df = client.fetch_daily_history("TSLA", outputsize="compact")
        
        self.assertEqual(len(df), 2)
        self.assertListEqual(df["date"].tolist(), [dt.date(2024, 10, 24), dt.date(2024, 10, 25)])
        self.assertEqual(df.iloc[0]["close"], 250.00)
        self.assertEqual(df.iloc[1]["volume"], 1000000)
    
    @patch("src.data.alphavantage.requests.get")
    def test_fetch_handles_api_error(self, mock_get: Mock) -> None:
        mock_response = MockResponse({"Error Message": "Invalid API key"})
        mock_get.return_value = mock_response
        
        client = AlphaVantageClient(self.config)
        with self.assertRaises(ValueError) as ctx:
            client.fetch_daily_history("TSLA")
        
        self.assertIn("Invalid API key", str(ctx.exception))
    
    def test_config_from_env_var(self) -> None:
        with patch.dict("os.environ", {"ALPHAVANTAGE_API_KEY": "env_key"}):
            client = AlphaVantageClient()
            self.assertEqual(client._config.api_key, "env_key")
    
    def test_missing_api_key_raises(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                AlphaVantageClient()
            self.assertIn("API key required", str(ctx.exception))


class AlphaVantageIngestorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = Path(self.temp_dir.name) / "test_tsla.csv"
    
    def tearDown(self) -> None:
        self.temp_dir.cleanup()
    
    def test_run_writes_new_file(self) -> None:
        mock_client = Mock()
        mock_client.fetch_daily_history.return_value = pd.DataFrame({
            "date": [dt.date(2024, 10, 24), dt.date(2024, 10, 25)],
            "open": [248.0, 250.0],
            "high": [252.0, 255.0],
            "low": [247.0, 248.0],
            "close": [250.0, 253.5],
            "volume": [950000, 1000000],
        })
        
        ingestor = AlphaVantageIngestor(client=mock_client, output_path=self.output_path)
        result = ingestor.run("TSLA", outputsize="full")
        
        self.assertEqual(result["rows_written"], 2)
        self.assertEqual(result["min_date"], "2024-10-24")
        self.assertEqual(result["max_date"], "2024-10-25")
        
        saved = pd.read_csv(self.output_path)
        self.assertEqual(len(saved), 2)
    
    def test_run_merges_with_existing(self) -> None:
        # Create existing file
        existing = pd.DataFrame({
            "date": ["2024-10-23"],
            "open": [245.0],
            "high": [248.0],
            "low": [244.0],
            "close": [247.0],
            "volume": [900000],
        })
        existing.to_csv(self.output_path, index=False)
        
        mock_client = Mock()
        mock_client.fetch_daily_history.return_value = pd.DataFrame({
            "date": [dt.date(2024, 10, 24)],
            "open": [248.0],
            "high": [252.0],
            "low": [247.0],
            "close": [250.0],
            "volume": [950000],
        })
        
        ingestor = AlphaVantageIngestor(client=mock_client, output_path=self.output_path)
        result = ingestor.run("TSLA")
        
        self.assertEqual(result["rows_written"], 2)
        saved = pd.read_csv(self.output_path)
        self.assertEqual(len(saved), 2)
        self.assertListEqual(saved["date"].tolist(), ["2024-10-23", "2024-10-24"])


if __name__ == "__main__":
    unittest.main()
