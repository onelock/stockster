import pandas as pd

def add_indicators(df):
    df = df.copy()
    df["sma_10"] = df["last_price"].rolling(10).mean()
    df["sma_30"] = df["last_price"].rolling(30).mean()
    df["ema_10"] = df["last_price"].ewm(span=10).mean()

    # RSI
    delta = df["last_price"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["last_price"].ewm(span=12).mean()
    ema26 = df["last_price"].ewm(span=26).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9).mean()

    # Bollinger Bands
    df["bb_mid"] = df["last_price"].rolling(20).mean()
    df["bb_std"] = df["last_price"].rolling(20).std()
    df["bb_upper"] = df["bb_mid"] + 2 * df["bb_std"]
    df["bb_lower"] = df["bb_mid"] - 2 * df["bb_std"]

    return df
