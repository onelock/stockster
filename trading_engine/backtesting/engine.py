from dataclasses import dataclass
import pandas as pd
from typing import List
from config import StrategyConfig
from trading_engine.strategies.base import Strategy

@dataclass
class TradeResult:
    strategy: str
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    pnl_pct: float

def backtest(df: pd.DataFrame, signals: pd.Series, cfg: StrategyConfig, strategy: Strategy) -> List[TradeResult]:
    trades = []
    in_pos = False
    entry_price = None
    entry_time = None

    for i in range(len(df) - 1):
        row = df.iloc[i]
        next_row = df.iloc[i + 1]

        if not in_pos:
            if signals.iloc[i] == 1:
                in_pos = True
                entry_price = next_row["open"]
                entry_time = next_row.name
        else:
            high = next_row["high"]
            low = next_row["low"]

            tp = entry_price * (1 + cfg.tp_pct)
            sl = entry_price * (1 - cfg.sl_pct)

            exit_price = None
            exit_time = next_row.name

            if low <= sl:
                exit_price = sl
            elif high >= tp:
                exit_price = tp

            if i == len(df) - 2 and exit_price is None:
                exit_price = next_row["close"]

            if exit_price:
                pnl = (exit_price - entry_price) / entry_price
                trades.append(TradeResult(strategy.name, entry_time, exit_time, entry_price, exit_price, pnl))
                in_pos = False

    return trades
