def rolling_volume_avg(df, period=20):
    return df["volume"].rolling(period).mean()
