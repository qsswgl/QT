"""Run a single iteration of the TSLA momentum strategy."""
from __future__ import annotations

import logging
from pathlib import Path

from src.data.loader import CSVPriceLoader
from src.portfolio.allocator import PositionAllocator, RiskBudget
from src.signals.momentum import MomentumSignalModel, TradeAction
from src.execution.mock_broker import MockBroker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent.parent
    data_path = project_root / "data" / "sample_tsla.csv"

    loader = CSVPriceLoader(data_path)
    bars = loader.load()

    model = MomentumSignalModel(short_window=3, long_window=6, threshold=0.3)
    raw_decisions = model.generate(bars)
    filtered_decisions = model.filter_trading_slots(raw_decisions, max_trades_per_week=2)

    allocator = PositionAllocator(symbol="TSLA", risk_budget=RiskBudget(capital=100_000))
    broker = MockBroker()

    for decision in filtered_decisions:
        plan = allocator.propose(decision)
        if not plan:
            logging.info("No trade for %s", decision.bar.date)
            continue
        report = broker.send_order(plan)
        logging.info(
            "Trade %s | action=%s qty=%s price=%.2f status=%s",
            report.order_id,
            plan.action.value,
            plan.quantity,
            plan.target_price,
            report.status,
        )

    logging.info("Run completed with %d candidate decisions, %d executed.", len(raw_decisions), len(filtered_decisions))


if __name__ == "__main__":
    main()
