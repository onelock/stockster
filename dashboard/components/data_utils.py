"""
Data utility functions for dashboard
"""
import pandas as pd


def resample_data(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """Resample data to specified interval"""
    if df.empty or interval == '1min':
        return df
    
    df_copy = df.copy()
    df_copy = df_copy.set_index('timestamp')
    
    # Resample OHLCV data
    resampled = df_copy.resample(interval).agg({
        'last_price': 'last',
        'open_price': 'first',
        'highest': 'max',
        'lowest': 'min',
        'volume': 'sum',
        'vwap': 'mean',
        'name': 'first'
    }).dropna()
    
    resampled = resampled.reset_index()
    return resampled
