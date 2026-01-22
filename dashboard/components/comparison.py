"""
Multi-stock comparison component
"""
import streamlit as st
import pandas as pd
from dashboard.charts import create_comparison_chart


def render_comparison(stocks, days, load_stock_history_fn):
    """Render multi-stock comparison section"""
    st.subheader("📊 Multi-Stock Comparison")
    selected_stocks = st.sidebar.multiselect("Select stocks", stocks, default=stocks[:3])
    
    if selected_stocks:
        comparison_data = []
        for stock_name in selected_stocks:
            stock_hist = load_stock_history_fn(stock_name, days=days)
            if not stock_hist.empty:
                comparison_data.append(stock_hist)
        
        if comparison_data:
            df_multi = pd.concat(comparison_data, ignore_index=True)
            st.altair_chart(create_comparison_chart(df_multi), use_container_width=True)
        else:
            st.warning("No historical data available for selected stocks")
