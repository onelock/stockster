def bollinger_bands(series, period=20, std=2.0):
    ma = series.rolling(period).mean()
    sd = series.rolling(period).std()
    upper = ma + std * sd
    lower = ma - std * sd
    return ma, upper, lower
