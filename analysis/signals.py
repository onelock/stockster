def add_signals(df):
    df = df.copy()
    df["signal"] = 0

    # SMA crossover
    df.loc[df["sma_10"] > df["sma_30"], "signal"] = 1
    df.loc[df["sma_10"] < df["sma_30"], "signal"] = -1

    return df
