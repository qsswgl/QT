"""Simple momentum-based signal model for TSLA."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Sequence

from src.data.loader import PriceBar


class TradeAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class SignalDecision:
    bar: PriceBar
    action: TradeAction
    score: float
    reason: str


class MomentumSignalModel:
    """Generates trade decisions based on moving-average momentum.

    The model compares short-term and long-term averages of closing prices to determine
    trend direction and strength. It throttles signals to roughly match the desired
    twice-per-week trading cadence by requiring a minimum score gap before acting.
    """

    def __init__(self, short_window: int = 3, long_window: int = 6, threshold: float = 0.5) -> None:
        if short_window <= 0 or long_window <= 0:
            raise ValueError("window lengths must be positive")
        if short_window >= long_window:
            raise ValueError("short_window must be smaller than long_window")
        self.short_window = short_window
        self.long_window = long_window
        self.threshold = threshold

    def generate(self, bars: Sequence[PriceBar]) -> List[SignalDecision]:
        closes = [bar.close for bar in bars]
        decisions: List[SignalDecision] = []

        for idx, bar in enumerate(bars):
            if idx + 1 < self.long_window:
                decisions.append(SignalDecision(bar=bar, action=TradeAction.HOLD, score=0.0, reason="warmup"))
                continue
            short_avg = _moving_average(closes[: idx + 1], self.short_window)
            long_avg = _moving_average(closes[: idx + 1], self.long_window)
            momentum = (short_avg - long_avg) / long_avg if long_avg else 0.0

            if momentum > self.threshold:
                action = TradeAction.BUY
                score = momentum
                reason = f"short_avg({short_avg:.2f}) > long_avg({long_avg:.2f})"
            elif momentum < -self.threshold:
                action = TradeAction.SELL
                score = momentum
                reason = f"short_avg({short_avg:.2f}) < long_avg({long_avg:.2f})"
            else:
                action = TradeAction.HOLD
                score = momentum
                reason = "momentum within threshold"

            decisions.append(SignalDecision(bar=bar, action=action, score=score, reason=reason))

        return decisions

    def filter_trading_slots(self, decisions: Iterable[SignalDecision], max_trades_per_week: int = 2) -> List[SignalDecision]:
        """Reduce signal frequency to target at most max_trades_per_week decisions.

        Uses a simple batching approach by selecting top-N absolute scores per 5-bar window.
        """
        batch: List[SignalDecision] = []
        reduced: List[SignalDecision] = []
        bars_per_week = 5  # trading days

        for decision in decisions:
            batch.append(decision)
            if len(batch) == bars_per_week:
                reduced.extend(_select_top_n(batch, max_trades_per_week))
                batch.clear()

        if batch:
            reduced.extend(_select_top_n(batch, max_trades_per_week))

        return sorted(reduced, key=lambda d: d.bar.date)


def _moving_average(series: Sequence[float], window: int) -> float:
    if len(series) < window:
        return sum(series) / len(series)
    window_slice = series[-window:]
    return sum(window_slice) / window


def _select_top_n(decisions: Sequence[SignalDecision], n: int) -> List[SignalDecision]:
    sorted_decisions = sorted(decisions, key=lambda d: abs(d.score), reverse=True)
    selected = [d for d in sorted_decisions if d.action != TradeAction.HOLD][:n]
    if not selected:
        # ensure at least one hold decision for traceability
        return [sorted_decisions[0]] if sorted_decisions else []
    return selected
