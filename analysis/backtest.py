import pandas as pd
import numpy as np

def backtest(df, signal_col="signal"):
    df = df.copy()
    df["return"] = df["last_price"].pct_change()
    df["strategy_return"] = df[signal_col].shift(1) * df["return"]

    df["equity_curve"] = (1 + df["strategy_return"]).cumprod()

    # Metrics
    total_return = df["equity_curve"].iloc[-1] - 1
    sharpe = np.sqrt(252*26) * df["strategy_return"].mean() / df["strategy_return"].std()  # 15-min bars
    max_dd = (df["equity_curve"].cummax() - df["equity_curve"]).max()

    stats = {
        "Total Return": total_return,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd
    }

    return df, stats
