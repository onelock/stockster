"""
Stock list display component
"""
import streamlit as st
import pandas as pd


def render_latest_stocks(df: pd.DataFrame):
    """Render latest stock prices section"""
    st.subheader("📈 Latest Stock Prices")
    
    # Display top stocks by volume
    col1, col2, col3 = st.columns(3)
    
    top_stocks = df.nlargest(3, 'volume')
    for i, (idx, stock) in enumerate(top_stocks.iterrows()):
        col = [col1, col2, col3][i]
        with col:
            st.metric(
                label=stock['name'],
                value=f"${stock['last_price']:.2f}",
                delta=f"{stock['change_pct']:.2f}%"
            )
    
    # Full stock list
    st.dataframe(
        df[['name', 'last_price', 'change_pct', 'volume', 'vwap']].style.format({
            'last_price': '${:.2f}',
            'change_pct': '{:.2f}%',
            'volume': '{:,.0f}',
            'vwap': '${:.2f}'
        }),
        use_container_width=True
    )
