import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import os
import sys

# Add parent directory to path so we can import analysis module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from analysis.indicators import add_indicators
from analysis.signals import add_signals
from analysis.backtest import backtest
# from analysis.alerts import check_alerts


# Get path relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(script_dir, "..", "db", "stocks_db.db")

@st.cache_data(ttl=60)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM stocks_trading", conn)
    conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["last_price"] = pd.to_numeric(df["last_price"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    return df

st.title("📈 DI.se Trading Dashboard")

df = load_data()

# Sidebar
stocks = sorted(df["name"].unique())
selected = st.sidebar.selectbox("Select stock", stocks)
df_stock = df[df["name"] == selected].sort_values("timestamp")
compare_mode = st.sidebar.checkbox("Compare multiple stocks")


if compare_mode:
    selected_stocks = st.sidebar.multiselect("Select stocks", stocks, default=[stocks[0]])

    df_multi = df[df["name"].isin(selected_stocks)]
    df_multi = df_multi.sort_values("timestamp")

    chart = (
        alt.Chart(df_multi)
        .mark_line()
        .encode(
            x=alt.X("timestamp:T", title="Time", axis=alt.Axis(format="%Y-%m-%d %H:%M")),
            y=alt.Y("last_price:Q", title="Price", scale=alt.Scale(zero=False)),
            color="name:N"
        )
    )

    st.subheader("Multi‑Stock Comparison")
    st.altair_chart(chart, use_container_width=True)


# Add indicators + signals
df_stock = add_indicators(df_stock)
df_stock = add_signals(df_stock)

# Price chart with signals
st.subheader(f"Price & Signals — {selected}")

# Main price line with tooltip
price_chart = (
    alt.Chart(df_stock)
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

# Moving averages overlay
if "sma_20" in df_stock.columns and "sma_50" in df_stock.columns:
    sma_20 = (
        alt.Chart(df_stock)
        .mark_line(color="blue", strokeWidth=1, opacity=0.6)
        .encode(
            x="timestamp:T",
            y="sma_20:Q",
            tooltip=[alt.Tooltip("sma_20:Q", title="SMA 20", format=".2f")]
        )
    )
    
    sma_50 = (
        alt.Chart(df_stock)
        .mark_line(color="orange", strokeWidth=1, opacity=0.6)
        .encode(
            x="timestamp:T",
            y="sma_50:Q",
            tooltip=[alt.Tooltip("sma_50:Q", title="SMA 50", format=".2f")]
        )
    )
else:
    sma_20 = alt.Chart(pd.DataFrame()).mark_point()
    sma_50 = alt.Chart(pd.DataFrame()).mark_point()

# Volume bars in background (scaled to fit price chart)
if "volume" in df_stock.columns:
    volume_chart = (
        alt.Chart(df_stock)
        .mark_bar(opacity=0.3, color="gray")
        .encode(
            x="timestamp:T",
            y=alt.Y("volume:Q", title="Volume", axis=alt.Axis(orient="right")),
        )
    )
else:
    volume_chart = alt.Chart(pd.DataFrame()).mark_point()

# Buy/sell signals
buy_signals = (
    alt.Chart(df_stock[df_stock["signal"] == 1])
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
    alt.Chart(df_stock[df_stock["signal"] == -1])
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

# Combine all layers
combined_chart = alt.layer(
    price_chart, sma_20, sma_50, buy_signals, sell_signals
).properties(
    height=400
).interactive()

st.altair_chart(combined_chart, use_container_width=True)

# Back-testing
st.subheader("Backtest Results")

bt_df, stats = backtest(df_stock)

st.write(stats)

bt_chart = (
    alt.Chart(bt_df)
    .mark_line(color="yellow")
    .encode(x="timestamp:T", y="equity_curve:Q")
)

st.altair_chart(bt_chart, use_container_width=True)


# RSI
st.subheader("RSI (Relative Strength Index)")
rsi_chart = (
    alt.Chart(df_stock)
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

# Add overbought/oversold reference lines
oversold_line = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(color='green', strokeDash=[5, 5]).encode(y='y:Q')
overbought_line = alt.Chart(pd.DataFrame({'y': [70]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='y:Q')
midline = alt.Chart(pd.DataFrame({'y': [50]})).mark_rule(color='gray', strokeDash=[2, 2], opacity=0.5).encode(y='y:Q')

st.altair_chart((rsi_chart + oversold_line + overbought_line + midline).interactive(), use_container_width=True)

# MACD
st.subheader("MACD (Moving Average Convergence Divergence)")
macd_line = (
    alt.Chart(df_stock)
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

# MACD signal line
if "macd_signal" in df_stock.columns:
    signal_line = (
        alt.Chart(df_stock)
        .mark_line(color="orange", strokeWidth=2)
        .encode(
            x="timestamp:T",
            y="macd_signal:Q",
            tooltip=[alt.Tooltip("macd_signal:Q", format=".3f")]
        )
    )
else:
    signal_line = alt.Chart(pd.DataFrame()).mark_point()

# MACD histogram
if "macd_hist" in df_stock.columns:
    macd_hist = (
        alt.Chart(df_stock)
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

zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='gray', strokeDash=[2, 2]).encode(y='y:Q')

st.altair_chart((macd_hist + macd_line + signal_line + zero_line).interactive(), use_container_width=True)
signal_chart = (
    alt.Chart(df_stock)
    .mark_line(color="orange")
    .encode(x="timestamp:T", y="macd_signal:Q")
)
st.altair_chart(macd_hist + signal_chart, use_container_width=True)

# Bollinger Bands
st.subheader("Bollinger Bands")
bb_chart = (
    alt.Chart(df_stock)
    .mark_line()
    .encode(x="timestamp:T", y="last_price:Q")
)
upper = (
    alt.Chart(df_stock)
    .mark_line(color="gray")
    .encode(x="timestamp:T", y="bb_upper:Q")
)
lower = (
    alt.Chart(df_stock)
    .mark_line(color="gray")
    .encode(x="timestamp:T", y="bb_lower:Q")
)
st.altair_chart(bb_chart + upper + lower, use_container_width=True)

# Raw data
st.subheader("Raw data")
st.dataframe(df_stock.tail(50))


