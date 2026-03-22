"""
Stock list display component
"""
import streamlit as st
import pandas as pd
from dashboard.analysis.volatility import calculate_volatility, get_volatility_summary, rank_stocks_by_volatility
from dashboard.volatility_charts import create_volatility_ranking_chart

from dashboard.api.routes import get_recent_stock_info

class HomePage:
    def __init__(self):
        self.df = pd.DataFrame()
        self.initialize()
        
    def initialize(self):
        """Initialize the home page by loading data"""
        self.load_data()
        self.render()
        
        
    def render(self):
        """Render latest stock prices section"""
        st.subheader("📈 Latest Stock Prices")
        
        # Display top stocks by volume
        n = 7
        cols = st.columns(n)
        
        top_stocks = self.df.nlargest(n, 'change_pct')
        for i, (idx, stock) in enumerate(top_stocks.iterrows()):
            col = cols[i]
            with col:
                st.metric(
                    label=stock['name'],
                    value=f"${stock['last_price']:.2f}",
                    delta=f"{stock['change_pct']:.2f}%"
                )
                
        st.pills(label="Select Exchange", options=[_ for _ in self.df['list'].unique()] , key="exchange_filter")
        
        exchange_filter = st.session_state.get("exchange_filter", "All")
        
        if exchange_filter :
            self.df = self.df[self.df['list'] == exchange_filter]
        
        
        # self.df: pd.DataFrame = self.df.astype({'highest': float, 'lowest': float})

        # Full stock list
        event = st.dataframe(
            self.df,
            column_config={
            'name': 'Name',
            'last_price': 'Last Price',
            'change_pct': '+/- %',
            'change_abs': '+/-',
            'highest': 'High',
            'lowest': 'Low',
            'volume': 'Volume',
            'market_value': 'Market Value',
            'list': 'List',
            'timestamp': st.column_config.TimeColumn(label="Timestamp")
        },
            on_select="rerun",
            selection_mode="single-row",
            width='stretch',
        )
       
        # 
        if event.selection.rows:
            selected_index = event.selection.rows[0]
            selected_stock = self.df.iloc[selected_index]
            st.session_state["selected_ticker"] = selected_stock['name']
            st.session_state["page"] = "Stock details"
            st.rerun()


    def load_data(self):
        """Load latest stock data from dev API"""
        try:
            self.df = get_recent_stock_info(limit=100)
        except ConnectionError as e:
            st.error(str(e))
            self.df = pd.DataFrame()
