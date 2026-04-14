"""Calculate and rank stock volatility"""
import pandas as pd
import numpy as np


def calculate_volatility(stock_df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Calculate volatility metrics for stock data
    
    Args:
        stock_df: DataFrame with 'last_price' column
        window: Period for volatility calculation (default 20)
    
    Returns:
        DataFrame with added volatility columns
    """
    df = stock_df.copy()
    
    df['returns'] = df['last_price'].pct_change()
    df = df.dropna()
    
    # Calculate rolling volatility (standard deviation of returns)
    df['volatility'] = df['returns'].rolling(window=window).std()
    
    # Average daily volatility - simple mean of absolute returns
    df['avg_daily_volatility'] = df['returns'].abs().rolling(window=window).mean()
    
    # Annualized volatility (assuming 252 trading days per year)
    df['volatility_annualized'] = df['volatility'] * np.sqrt(252)
    
    # Calculate historical volatility (realized volatility)
    df['hist_volatility'] = df['returns'].rolling(window=window).std() * 100
    
    # Average True Range (ATR) - measure of price movement
    if 'highest' in df.columns and 'lowest' in df.columns:
        df['true_range'] = df.apply(
            lambda row: max(
                row['highest'] - row['lowest'],
                abs(row['highest'] - row['last_price']),
                abs(row['lowest'] - row['last_price'])
            ), axis=1
        )
        df['atr'] = df['true_range'].rolling(window=window).mean()
        df['atr_pct'] = (df['atr'] / df['last_price']) * 100
    
    return df


def calculate_average_daily_volatility(df: pd.DataFrame, window: int = 20) -> float:
    """
    Calculate average daily volatility for a stock
    
    Args:
        df: DataFrame with 'last_price' column
        window: Period for calculation (default 20)
    
    Returns:
        Average daily volatility as a percentage
    """
    if df.empty or len(df) < 2:
        return 0.0
    
    # Calculate daily returns
    returns = df['last_price'].pct_change().dropna()
    
    if len(returns) < window:
        # Use all available data if less than window
        avg_volatility = returns.abs().mean()
    else:
        # Use the most recent window period
        avg_volatility = returns.tail(window).abs().mean()
    
    return float(avg_volatility * 100)  # Convert to percentage


def rank_stocks_by_volatility(stocks_data: dict, window: int = 20) -> pd.DataFrame:
    """
    Rank multiple stocks by their volatility
    
    Args:
        stocks_data: Dict of {stock_name: DataFrame}
        window: Period for volatility calculation
    
    Returns:
        DataFrame with stocks ranked by volatility
    """
    volatility_rankings = []
    
    for stock_name, df in stocks_data.items():
        if df.empty or len(df) < window:
            continue
        
        # Calculate volatility
        df_vol = calculate_volatility(df, window)
        
        # Get latest volatility metrics
        latest = df_vol.dropna(subset=['volatility']).iloc[-1] if not df_vol.empty else None
        
        if latest is not None:
            volatility_rankings.append({
                'name': stock_name,
                'volatility': latest.get('volatility', np.nan),
                'avg_daily_volatility': latest.get('avg_daily_volatility', np.nan),
                'volatility_annualized': latest.get('volatility_annualized', np.nan),
                'hist_volatility': latest.get('hist_volatility', np.nan),
                'atr_pct': latest.get('atr_pct', np.nan) if 'atr_pct' in df_vol.columns else np.nan,
                'last_price': latest.get('last_price', np.nan),
                'returns': latest.get('returns', np.nan)
            })
    
    # Create ranking DataFrame
    ranking_df = pd.DataFrame(volatility_rankings)
    
    if not ranking_df.empty:
        # Sort by volatility (descending)
        ranking_df = ranking_df.sort_values('volatility', ascending=False)
        ranking_df['rank'] = range(1, len(ranking_df) + 1)
        
        # Add risk classification
        ranking_df['risk_level'] = pd.cut(
            ranking_df['volatility_annualized'],
            bins=[0, 0.15, 0.30, 0.50, 1.0],
            labels=['Low', 'Medium', 'High', 'Very High']
        )
    
    return ranking_df


def get_volatility_summary(df: pd.DataFrame, window: int = 20) -> dict:
    """
    Get summary statistics for stock volatility
    
    Args:
        df: DataFrame with price data
        window: Period for calculation
    
    Returns:
        Dictionary with volatility statistics
    """
    df_vol = calculate_volatility(df, window)
    df_clean = df_vol.dropna(subset=['volatility'])
    
    if df_clean.empty:
        return {}
    
    latest = df_clean.iloc[-1]
    
    return {
        'current_volatility': latest['volatility'],
        'avg_daily_volatility': latest.get('avg_daily_volatility', np.nan),
        'avg_daily_volatility_pct': latest.get('avg_daily_volatility', 0) * 100,
        'annualized_volatility': latest['volatility_annualized'],
        'avg_volatility': df_clean['volatility'].mean(),
        'max_volatility': df_clean['volatility'].max(),
        'min_volatility': df_clean['volatility'].min(),
        'volatility_trend': 'increasing' if df_clean['volatility'].iloc[-5:].mean() > df_clean['volatility'].iloc[-20:-5].mean() else 'decreasing' 
    }
