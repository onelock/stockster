"""
Single stock analysis component
"""
import streamlit as st
import pandas as pd
from analysis.indicators import add_indicators
from analysis.signals import add_signals
from dashboard.charts import create_combined_price_chart


def render_stock_metrics(latest: pd.Series):
    """Render stock metrics row"""
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Last Price", f"${latest['last_price']:.2f}", f"{latest.get('change_pct', 0):.2f}%")
    col2.metric("Volume", f"{latest['volume']:,.0f}")
    col3.metric("VWAP", f"${latest['vwap']:.2f}")
    col4.metric("High/Low", f"${latest['highest']:.2f} / ${latest['lowest']:.2f}")


def render_price_chart(df: pd.DataFrame, interval_label: str):
    """Render price chart with signals"""
    st.subheader(f"💹 Price & Signals — {interval_label}")
    st.caption(f"Showing {len(df)} {interval_label.lower()} candles")
    st.altair_chart(create_combined_price_chart(df), use_container_width=True)


def render_raw_data(df_resampled: pd.DataFrame, df_original: pd.DataFrame, interval_label: str):
    """Render raw data expander"""
    with st.expander("📋 Raw Data"):
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"Resampled Data ({interval_label})")
            st.dataframe(df_resampled.tail(50), use_container_width=True)
        with col2:
            st.caption("Original 1-Minute Data")
            st.dataframe(df_original.tail(50), use_container_width=True)


def prepare_chart_data(df: pd.DataFrame):
    """Add indicators and signals to dataframe"""
    df = add_indicators(df)
    df = add_signals(df)
    return df
