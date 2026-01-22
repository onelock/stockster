"""
Chart creation functions for dashboard visualizations
"""

import pandas as pd
import altair as alt
from typing import Tuple


def create_price_chart(df: pd.DataFrame) -> alt.Chart:
    """Create main price line chart with tooltip"""
    return (
        alt.Chart(df)
        .mark_line(color="white", strokeWidth=2)
        .encode(
            x=alt.X("timestamp:T", title="Time", axis=alt.Axis(format="%Y-%m-%d %H:%M")),
            y=alt.Y("last_price:Q", title="Price", scale=alt.Scale(zero=False)),
            tooltip=[
                alt.Tooltip("timestamp:T", title="Time", format="%Y-%m-%d %H:%M"),
                alt.Tooltip("last_price:Q", title="Price", format=".2f"),
                alt.Tooltip("volume:Q", title="Volume", format=","),
                alt.Tooltip("rsi:Q", title="RSI", format=".2f"),
            ]
        )
    )


def create_moving_average_charts(df: pd.DataFrame) -> Tuple[alt.Chart, alt.Chart]:
    """Create SMA 20 and SMA 50 overlay charts"""
    if "sma_20" not in df.columns or "sma_50" not in df.columns:
        empty = alt.Chart(pd.DataFrame()).mark_point()
        return empty, empty
    
    sma_20 = (
        alt.Chart(df)
        .mark_line(color="blue", strokeWidth=1, opacity=0.6)
        .encode(
            x="timestamp:T",
            y="sma_20:Q",
            tooltip=[alt.Tooltip("sma_20:Q", title="SMA 20", format=".2f")]
        )
    )
    
    sma_50 = (
        alt.Chart(df)
        .mark_line(color="orange", strokeWidth=1, opacity=0.6)
        .encode(
            x="timestamp:T",
            y="sma_50:Q",
            tooltip=[alt.Tooltip("sma_50:Q", title="SMA 50", format=".2f")]
        )
    )
    
    return sma_20, sma_50


def create_volume_chart(df: pd.DataFrame) -> alt.Chart:
    """Create volume bar chart"""
    if "volume" not in df.columns:
        return alt.Chart(pd.DataFrame()).mark_point()
    
    return (
        alt.Chart(df)
        .mark_bar(opacity=0.3, color="gray")
        .encode(
            x="timestamp:T",
            y=alt.Y("volume:Q", title="Volume", axis=alt.Axis(orient="right")),
        )
    )


def create_signal_charts(df: pd.DataFrame) -> Tuple[alt.Chart, alt.Chart]:
    """Create buy and sell signal markers"""
    buy_signals = (
        alt.Chart(df[df["signal"] == 1])
        .mark_point(color="green", size=120, shape="triangle-up", filled=True)
        .encode(
            x="timestamp:T",
            y="last_price:Q",
            tooltip=[
                alt.Tooltip("timestamp:T", title="Buy Signal", format="%Y-%m-%d %H:%M"),
                alt.Tooltip("last_price:Q", title="Price", format=".2f")
            ]
        )
    )
    
    sell_signals = (
        alt.Chart(df[df["signal"] == -1])
        .mark_point(color="red", size=120, shape="triangle-down", filled=True)
        .encode(
            x="timestamp:T",
            y="last_price:Q",
            tooltip=[
                alt.Tooltip("timestamp:T", title="Sell Signal", format="%Y-%m-%d %H:%M"),
                alt.Tooltip("last_price:Q", title="Price", format=".2f")
            ]
        )
    )
    
    return buy_signals, sell_signals


def create_combined_price_chart(df: pd.DataFrame) -> alt.Chart:
    """Create layered chart with price, MAs, and signals"""
    price_chart = create_price_chart(df)
    sma_20, sma_50 = create_moving_average_charts(df)
    buy_signals, sell_signals = create_signal_charts(df)
    
    return alt.layer(
        price_chart, sma_20, sma_50, buy_signals, sell_signals
    ).properties(
        height=400
    ).interactive()


def create_comparison_chart(df: pd.DataFrame) -> alt.Chart:
    """Create multi-stock comparison chart"""
    return (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("timestamp:T", title="Time", axis=alt.Axis(format="%Y-%m-%d %H:%M")),
            y=alt.Y("last_price:Q", title="Price", scale=alt.Scale(zero=False)),
            color="name:N"
        )
    )


def create_rsi_chart(df: pd.DataFrame) -> alt.Chart:
    """Create RSI chart with reference lines"""
    rsi_chart = (
        alt.Chart(df)
        .mark_line(color="purple", strokeWidth=2)
        .encode(
            x=alt.X("timestamp:T", title="Time", axis=alt.Axis(format="%Y-%m-%d %H:%M")),
            y=alt.Y("rsi:Q", title="RSI", scale=alt.Scale(domain=[0, 100])),
            tooltip=[
                alt.Tooltip("timestamp:T", format="%Y-%m-%d %H:%M"),
                alt.Tooltip("rsi:Q", format=".2f")
            ]
        )
    ).properties(height=150)
    
    # Reference lines
    oversold = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(
        color='green', strokeDash=[5, 5]
    ).encode(y='y:Q')
    
    overbought = alt.Chart(pd.DataFrame({'y': [70]})).mark_rule(
        color='red', strokeDash=[5, 5]
    ).encode(y='y:Q')
    
    midline = alt.Chart(pd.DataFrame({'y': [50]})).mark_rule(
        color='gray', strokeDash=[2, 2], opacity=0.5
    ).encode(y='y:Q')
    
    return (rsi_chart + oversold + overbought + midline).interactive()


def create_macd_chart(df: pd.DataFrame) -> alt.Chart:
    """Create MACD chart with signal line and histogram"""
    # MACD line
    macd_line = (
        alt.Chart(df)
        .mark_line(color="blue", strokeWidth=2)
        .encode(
            x=alt.X("timestamp:T", title="Time"),
            y=alt.Y("macd:Q", title="MACD"),
            tooltip=[
                alt.Tooltip("timestamp:T", format="%Y-%m-%d %H:%M"),
                alt.Tooltip("macd:Q", format=".3f")
            ]
        )
    ).properties(height=150)
    
    # Signal line
    if "macd_signal" in df.columns:
        signal_line = (
            alt.Chart(df)
            .mark_line(color="orange", strokeWidth=2)
            .encode(
                x="timestamp:T",
                y="macd_signal:Q",
                tooltip=[alt.Tooltip("macd_signal:Q", format=".3f")]
            )
        )
    else:
        signal_line = alt.Chart(pd.DataFrame()).mark_point()
    
    # Histogram
    if "macd_hist" in df.columns:
        macd_hist = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x="timestamp:T",
                y="macd_hist:Q",
                color=alt.condition(
                    alt.datum.macd_hist > 0,
                    alt.value("green"),
                    alt.value("red")
                ),
                tooltip=[alt.Tooltip("macd_hist:Q", format=".3f")]
            )
        )
    else:
        macd_hist = alt.Chart(pd.DataFrame()).mark_point()
    
    # Zero line
    zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
        color='gray', strokeDash=[2, 2]
    ).encode(y='y:Q')
    
    return (macd_hist + macd_line + signal_line + zero_line).interactive()


def create_bollinger_bands_chart(df: pd.DataFrame) -> alt.Chart:
    """Create Bollinger Bands chart"""
    
    # Calculate the y-axis domain to fit all data
    y_min = min(df['last_price'].min(), df['bb_lower'].min()) if 'bb_lower' in df.columns else df['last_price'].min()
    y_max = max(df['last_price'].max(), df['bb_upper'].max()) if 'bb_upper' in df.columns else df['last_price'].max()
    
    # Add padding (5% on each side)
    padding = (y_max - y_min) * 0.05
    y_domain = [y_min - padding, y_max + padding]

    price = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x="timestamp:T", 
            y=alt.Y("last_price:Q", scale=alt.Scale(domain=y_domain), title="Price")
        )
    )
    
    sma = (
        alt.Chart(df)
        .mark_line(color="orange", strokeDash=[3, 3])
        .encode(
            x="timestamp:T", 
            y=alt.Y("bb_mid:Q", scale=alt.Scale(domain=y_domain))
        )
    )
    
    upper = (
        alt.Chart(df)
        .mark_line(color="green", strokeDash=[3, 3])
        .encode(
            x="timestamp:T", 
            y=alt.Y("bb_upper:Q", scale=alt.Scale(domain=y_domain))
        )
    )
    
    lower = (
        alt.Chart(df)
        .mark_line(color="red", strokeDash=[3, 3])
        .encode(
            x="timestamp:T", 
            y=alt.Y("bb_lower:Q", scale=alt.Scale(domain=y_domain))
        )
    )
    
    return (price + sma + upper + lower).properties(
        height=400,
        title="Bollinger Bands"
    ).interactive()


def create_equity_curve_chart(df: pd.DataFrame) -> alt.Chart:
    """Create backtest equity curve chart"""
    return (
        alt.Chart(df)
        .mark_line(color="yellow")
        .encode(
            x="timestamp:T",
            y="equity_curve:Q",
            tooltip=[
                alt.Tooltip("timestamp:T", format="%Y-%m-%d %H:%M"),
                alt.Tooltip("equity_curve:Q", format=",.2f")
            ]
        )
    ).interactive()
