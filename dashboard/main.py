"""
Development Dashboard for Alpaca US Stock Data
Uses data_dev.py to connect to main.dev.py API
"""

import streamlit as st
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# from dashboard.api import StockDataLoader

from dashboard.components.navbar import Navbar
from dashboard.components.home import HomePage
from dashboard.components.stock_detail import StockDetailPage
from dashboard.components.marketplace import render_strategy_marketplace


# ============================================================================
# Configuration & Data Loading
# ============================================================================

st.set_page_config(page_title="Stockster Dev Dashboard", page_icon="📊", layout="wide")


# data_loader = StockDataLoader()


# ============================================================================
# Main Dashboard
# ============================================================================

# st.title("Dashboard")
Navbar()

# Add navigation tabs


# with tab_main:
    # ============================================================================
    # Sidebar
    # ============================================================================

# with st.sidebar:
    # render_health_check(data_loader)

    # Load data
    # df = load_data()

    # if df.empty:
    #     # st.warning("No data available. Please check dev API connection at http://localhost:8000/api/v1")
    #     st.info("Start dev API with: `python3 api/main.dev.py`")
    #     st.stop()

    # Sidebar controls
    # stocks = sorted(df["name"].unique())
    # selected, days, compare_mode = render_controls(stocks)
    # selected_interval_label, selected_interval = render_interval_selector()
    # enabled_strategies, strategy_params = render_strategy_registry()
    # render_footer()

    # Display timestamp
    # latest_time = df['timestamp'].max()
    # st.caption(f"Latest data: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
pg = st.session_state.get("page")

if pg == "home":
    tab_main, tab_marketplace = st.tabs(["📈 Trading Dashboard", "🏪 Strategy Marketplace"])

    with tab_marketplace:
        strategy_params_mp = render_strategy_marketplace()
        
    with tab_main:
        HomePage()
elif pg == "Stock details":
    StockDetailPage()


    