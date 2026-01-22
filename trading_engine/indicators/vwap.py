def vwap(df):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    cum_tp_vol = (tp * df["volume"]).cumsum()
    cum_vol = df["volume"].cumsum().replace(0, None)
    return cum_tp_vol / cum_vol
