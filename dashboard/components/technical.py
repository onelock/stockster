"""
Technical indicators component
"""
import streamlit as st
import pandas as pd
from dashboard.charts import (
    create_rsi_chart,
    create_macd_chart,
    create_bollinger_bands_chart
)


def render_technical_indicators(df: pd.DataFrame):
    """Render technical indicators in tabs"""
    tab1, tab2, tab3 = st.tabs(["RSI", "MACD", "Bollinger Bands"])
    
    with tab1:
        st.altair_chart(create_rsi_chart(df), use_container_width=True)
    
    with tab2:
        st.altair_chart(create_macd_chart(df), use_container_width=True)
    
    with tab3:
        st.altair_chart(create_bollinger_bands_chart(df), use_container_width=True)
