"""Portfolio allocation helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from src.signals.momentum import SignalDecision, TradeAction


@dataclass(frozen=True)
class RiskBudget:
    capital: float
    max_allocation_pct: float = 0.2
    risk_per_trade_pct: float = 0.01


@dataclass(frozen=True)
class PositionPlan:
    symbol: str
    quantity: int
    action: TradeAction
    rationale: str
    target_price: float


class PositionAllocator:
    def __init__(self, symbol: str, risk_budget: RiskBudget) -> None:
        self.symbol = symbol
        self.risk_budget = risk_budget

    def propose(self, decision: SignalDecision, price: Optional[float] = None) -> Optional[PositionPlan]:
        if decision.action == TradeAction.HOLD:
            return None

        reference_price = price or decision.bar.close
        if reference_price <= 0:
            raise ValueError("reference price must be positive")

        max_position_value = self.risk_budget.capital * self.risk_budget.max_allocation_pct
        risk_per_trade_value = self.risk_budget.capital * self.risk_budget.risk_per_trade_pct
        # Simplified sizing: ensure notional stays within max allocation and risk per trade.
        raw_quantity = int(min(max_position_value, risk_per_trade_value * 4) // reference_price)
        quantity = max(raw_quantity, 1)  # ensure at least one share

        return PositionPlan(
            symbol=self.symbol,
            quantity=quantity,
            action=decision.action,
            rationale=decision.reason,
            target_price=reference_price,
        )
