"""
Development Dashboard for Alpaca US Stock Data
Uses data_dev.py to connect to main.dev.py API
"""

import streamlit as st
import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dashboard.data_dev import StockDataLoader
from dashboard.components.sidebar import (
    render_health_check,
    render_controls,
    render_interval_selector,
    render_strategy_registry,
    render_footer
)
from dashboard.components.marketplace import render_strategy_marketplace
from dashboard.components.stock_list import render_latest_stocks
from dashboard.components.comparison import render_comparison
from dashboard.components.analysis import (
    render_stock_metrics,
    render_price_chart,
    render_raw_data,
    prepare_chart_data
)
from dashboard.components.technical import render_technical_indicators
from dashboard.components.data_utils import resample_data


# ============================================================================
# Configuration & Data Loading
# ============================================================================

st.set_page_config(
    page_title="Stockster Dev Dashboard",
    page_icon="📊",
    layout="wide"
)



data_loader = StockDataLoader()

@st.cache_data(ttl=60)
def load_data():
    """Load latest stock data from dev API"""
    try:
        return data_loader.load_latest_stocks(limit=100)
    except ConnectionError as e:
        st.error(str(e))
        return pd.DataFrame()

@st.cache_data(ttl=60)
def load_stock_history(stock_name, days=7):
    """Load historical data for a specific stock"""
    return data_loader.load_stock_history(stock_name, days)


# ============================================================================
# Main Dashboard
# ============================================================================

st.title("📊 Stockster Development Dashboard (Alpaca Data)")

# Add navigation tabs
tab_main, tab_marketplace = st.tabs(["📈 Trading Dashboard", "🏪 Strategy Marketplace"])

with tab_marketplace:
    strategy_params_mp = render_strategy_marketplace()

with tab_main:
    # ============================================================================
    # Sidebar
    # ============================================================================

    # with st.sidebar:
        # render_health_check(data_loader)

    # Load data
    df = load_data()

    if df.empty:
        st.warning("No data available. Please check dev API connection at http://localhost:8000")
        st.info("Start dev API with: `python3 api/main.dev.py`")
        st.stop()

    # Sidebar controls
    stocks = sorted(df["name"].unique())
    selected, days, compare_mode = render_controls(stocks)
    selected_interval_label, selected_interval = render_interval_selector()
    enabled_strategies, strategy_params = render_strategy_registry()
    render_footer()

    # Display timestamp
    latest_time = df['timestamp'].max()
    st.caption(f"Latest data: {latest_time}")

    # ============================================================================
    # Latest Stock Prices
    # ============================================================================

    render_latest_stocks(df)


    # ============================================================================
    # Multi-Stock Comparison
    # ============================================================================

    # if compare_mode:
    #     render_comparison(stocks, days, load_stock_history)


    # ============================================================================
    # Single Stock Analysis
    # ============================================================================

    st.subheader(f"🔍 Detailed Analysis — {selected}")

    # Load historical data
    # df_stock = load_stock_history(selected, days=days)

    # if df_stock.empty:
    #     st.warning(f"No historical data for {selected}")
    #     st.stop()

    # Display metrics
    # render_stock_metrics(df_stock.iloc[-1])

    # Resample data based on selected interval
    # df_resampled = resample_data(df_stock, selected_interval)

    # if df_resampled.empty:
    #     st.warning("Not enough data for the selected interval")
    #     st.stop()

    # Add technical indicators and signals
    # df_chart = prepare_chart_data(df_resampled)

    # ============================================================================
    # Price Chart with Signals
    # ============================================================================

    # render_price_chart(df_chart, selected_interval_label)

    # ============================================================================
    # Technical Indicators
    # ============================================================================

    # render_technical_indicators(df_chart)

    # ============================================================================
    # Raw Data
    # ============================================================================

    # render_raw_data(df_chart, df_stock, selected_interval_label)
