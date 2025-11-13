"""Mock broker adapter for dry-run execution."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from src.portfolio.allocator import PositionPlan


@dataclass(frozen=True)
class ExecutionReport:
    order_id: str
    status: str
    filled_quantity: int
    avg_price: float
    message: str


class MockBroker:
    def __init__(self) -> None:
        self._logger = logging.getLogger("mock-broker")

    def send_order(self, plan: PositionPlan) -> ExecutionReport:
        order_id = f"MOCK-{plan.symbol}-{plan.action}-{plan.quantity}"
        self._logger.info(
            "Submitting mock order",
            extra={
                "symbol": plan.symbol,
                "action": plan.action.value,
                "quantity": plan.quantity,
                "target_price": plan.target_price,
                "rationale": plan.rationale,
            },
        )
        return ExecutionReport(
            order_id=order_id,
            status="FILLED",
            filled_quantity=plan.quantity,
            avg_price=plan.target_price,
            message="Simulated fill",
        )

    def cancel_order(self, order_id: str) -> ExecutionReport:
        self._logger.warning("Cancelling mock order", extra={"order_id": order_id})
        return ExecutionReport(
            order_id=order_id,
            status="CANCELLED",
            filled_quantity=0,
            avg_price=0.0,
            message="Cancelled in simulation",
        )
