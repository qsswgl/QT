import datetime as dt
import unittest

from src.data.loader import PriceBar
from src.signals.momentum import MomentumSignalModel, TradeAction


class MomentumSignalModelTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bars = [
            PriceBar(date=dt.date(2024, 10, day), open=100 + day, high=101 + day, low=99 + day, close=100 + day, volume=1_000_000)
            for day in range(1, 15)
        ]

    def test_generate_returns_same_length(self) -> None:
        model = MomentumSignalModel(short_window=3, long_window=6, threshold=0.1)
        decisions = model.generate(self.bars)
        self.assertEqual(len(decisions), len(self.bars))

    def test_filter_trading_slots_respects_cap(self) -> None:
        model = MomentumSignalModel(short_window=3, long_window=6, threshold=0.0)
        decisions = model.generate(self.bars)
        filtered = model.filter_trading_slots(decisions, max_trades_per_week=2)
        # In strictly increasing prices, expect BUY signals; ensure we get at most two per five bars.
        self.assertTrue(all(decision in decisions for decision in filtered))
        # Count non-hold decisions per five-day block
        for idx in range(0, len(decisions), 5):
            block = decisions[idx : idx + 5]
            filtered_block = [d for d in filtered if d.bar in {b.bar for b in block}]
            active_trades = [d for d in filtered_block if d.action != TradeAction.HOLD]
            self.assertLessEqual(len(active_trades), 2)


if __name__ == "__main__":
    unittest.main()
