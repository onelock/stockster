from typing import List

import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime, timedelta

from dashboard.analysis.volatility import calculate_average_daily_volatility, calculate_volatility, get_volatility_summary
from dashboard.api.routes import get_stock_details, get_stock_metrics
from dashboard.volatility_charts import create_volatility_ranking_chart

class StockDetailPage:
    def __init__(self):
        self.stock_data_frame = pd.DataFrame()
        self.stock_metrics_frame = pd.DataFrame()
        self.ticker = st.session_state.get("selected_ticker", None)
        self.initialize()
        
    def initialize(self):
        """Initialize the stock detail page by loading data"""
        self.load_data()
        self.render()

    def load_data(self):
        """Load latest stock data from dev API"""
        try:
            self.stock_data_frame = get_stock_details(ticker=self.ticker)
            self.stock_metrics_frame = get_stock_metrics(ticker=self.ticker)
        except ConnectionError as e:
            st.error(str(e))
            self.stock_data_frame = pd.DataFrame()
            self.stock_metrics_frame = pd.DataFrame()
            
    def Div(self, change_pct, unit, color, border_radius, background_color):
        div = f""" 
                <div style='
                    font-size: 1.2em; color: {color};
                    font-weight: 500; border: 0px solid {color};
                    display: inline-block; justify-content: center; align-items: center;
                    padding: 4px 12px; 
                    place-content: space-between;
                    border-radius: {border_radius}; background-color: {background_color};
                '>
                        {"▲" if change_pct >= 0 else "▼"} {change_pct:.2f} {unit}
                </div> """
        return div
    
    def render(self):
        
        ticker = st.session_state.get("selected_ticker", None)
        
        colors = ["#5CE488", "#FF6E6E"]
        
        df = self.stock_data_frame.copy()
        if df.empty:
            st.info("No data available for this ticker.")
            return
        df = df.dropna()
        cols1 = st.columns([3, 1])
        with cols1[0]:
            with st.container(horizontal=True, gap="medium", border=True):
                
                col1, col2 = st.columns([1, 2])   
                
                # Display stock name, price, change, volume, market value
                with col1:
                    latest = df[df["timestamp"] == df["timestamp"].max()]
                    last_price = latest['last_price'].iloc[-1]
                    change_pct = latest['change_pct'].iloc[-1]
                    change_abs = latest['change_abs'].iloc[-1]
                    
                    highest = latest['last_price'].max()
                    lowest = latest['last_price'].min()
                    
                
                    color = colors[0] if change_pct >= 0 else colors[1]
                    border_radius = "8em"
                    background_color = "#3dd56d33" if change_pct >= 0 else "#FF6E6E33"
                    
                    # date of last update
                    last_update = pd.to_datetime(latest['timestamp'].iloc[-1])
                    st.caption(f"Last update: {last_update.strftime('%d %B %H:%M')}")
                    
                    st.markdown(f"""
                                <div>
                                    <h3 style='padding: 0;'>{ticker}</h3>
                                    <h1 style='padding: 0;'>{last_price:.2f} 
                                        <span style='font-size:0.70em;'>SEK</span>
                                    </h1>
                                    {self.Div(change_abs, "SEK", color, border_radius, background_color)}
                                    {self.Div(change_pct, "%", color, border_radius, background_color)}
                                </div>
                                """, unsafe_allow_html=True)
                    cols = st.columns(2)
                    
                    with cols[0]:
                        st.metric(
                            label="High",
                            value=f"{highest:.2f}",
                        )
                        st.metric(
                            label="Lowest",
                            value=f"{lowest:.2f}",
                        )
                    with cols[1]:
                        volume = format(latest['volume'].iloc[-1], ",.0f").replace(",", " ")
                        market_value = format(latest['market_value'].iloc[-1], ",.0f").replace(",", " ")    
                        st.metric(
                            label="Volume",
                            value=f"{volume}",
                        )
                        st.metric(
                            label="Market Value",
                            value=f"{market_value}",
                        )
                
                # Display stock chart
                with col2:
                    current_date = df['timestamp'].max()
                    current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)  
                    
                    df_chart_data = df.loc[:, ["timestamp", "last_price"]]
                    df_chart_data = df_chart_data.sort_values("timestamp")
                    df_chart_data = df_chart_data.set_index("timestamp")
                    
                    
                    
                    filter = {
                        "1 dag":[ (current_date - pd.Timedelta(days=0)), '%H:%M'],
                        "1 vecka":[ current_date - pd.Timedelta(weeks=1), '%d %b'],
                        "1 mån":[ current_date - pd.Timedelta(days=30), '%d %b'],
                        "3 mån":[ current_date - pd.Timedelta(days=90), '%d %b'],
                        "i år":[ current_date.replace(month=1, day=1), '%d %b'],
                        "1 år":[ current_date - pd.Timedelta(days=365), '%y %b'],
                        "3 år":[ current_date - pd.Timedelta(days=365*3), '%y %b'],
                        "5 år":[ current_date - pd.Timedelta(days=365*5), '%b %Y'],
                        "Max":[ current_date - pd.Timedelta(days=365*5), '%Y'],
                    }
                    
                    time_period_filter = st.session_state.get("time_period_filter", "1 dag")
                    
                    if not time_period_filter:
                        time_period_filter = "1 dag"
                    
                    time_interval = filter[time_period_filter][1]
                    
                    if time_period_filter in filter:
                        df_chart_data = df_chart_data[df_chart_data.index >= filter[time_period_filter][0]]
                        time_interval = filter[time_period_filter][1]
                    # else:
                    
                    st.write(f"Price Chart{filter[time_period_filter][0]} interval")
                    df_chart_data = df_chart_data.reset_index()
                    df_chart_data["timestamp"] = pd.to_datetime(df_chart_data["timestamp"])
                    df_chart_data = df_chart_data.sort_values("timestamp").reset_index(drop=True)

                    df_chart_data["trade_index"] = df_chart_data.index
                    tick_map = {
                        "1 dag": 10,
                        "1 vecka": 8,
                        "1 mån": 10,
                        "3 mån": 12,
                        "i år": 12,
                        "1 år": 12,
                        "3 år": 10,
                        "5 år": 8
                    }

                    ticks = tick_map.get(time_period_filter, 10)
                    
                    y_min = df_chart_data['last_price'].min()
                    y_max = df_chart_data['last_price'].max()
                    s = df_chart_data['last_price'].iloc[0]
                    t = df_chart_data['last_price'].iloc[-1]
                    
                    chart_color =  colors[1] if s > t else colors[0]
                    chart = alt.Chart(df_chart_data.reset_index()).mark_area(
                            color=alt.Gradient(
                                gradient='linear',
                                stops=[
                                    alt.GradientStop(color="#ffffff00", offset=0),
                                    alt.GradientStop(color=chart_color, offset=1), 
                                    ],
                                x1=1, x2=1, y1=1, y2=0
                                ), 
                            
                        ).encode(
                            x=alt.X(
                                'timestamp:T',
                                title='Time',
                                axis=alt.Axis(
                                    labelAngle=0,
                                    tickCount=ticks,
                                    format=time_interval,
                                    grid=True,
                                    tickExtra=True,
                                    domain=False
                                    )
                                ),
                            y=alt.Y(
                                'last_price:Q',
                                title='Price (SEK)',
                                axis=alt.Axis(
                                    labelAngle=0,
                                    tickCount=6,
                                    domain=False,
                                    ),
                                scale=alt.Scale(domainMin=y_min*.995)
                                ),
                            ).interactive()
                    
                    st.altair_chart(chart)
                    
                    options = ["1 dag", "1 vecka", "1 mån", "3 mån", "i år" , "1 år", "3 år", "5 år", "Max"]
                    
                    st.pills(
                        label="Time Period",options=options, key="time_period_filter",default=options[0], label_visibility="hidden"
                        )
                        
                    st.caption("add change rate for time periods")

        # Display points for breaking even and profit/loss thresholds
        with cols1[1]:
            with st.container(horizontal=True, gap="medium", border=True):
                st.write("Transaction Cost")
                st.write("Profit/Loss")
                
        # Display key performance indicators
        with st.expander("Key Performance Indicators", expanded=True):
            df_metrics = self.stock_metrics_frame.copy()
            if df_metrics.empty:
                st.info("No metrics data available for this ticker.")
                return
            
            # df_metrics = df_metrics.dropna()
            df_metrics = df_metrics[df_metrics["timestamp"] == df_metrics["timestamp"].max()]
            
            p_e_ratio = df_metrics['pe_ratio'].iloc[-1]
            dividend_yield = df_metrics['dividend_yield'].iloc[-1]
            price_to_sales = df_metrics['ps_ratio'].iloc[-1]
            earnings_per_share = df_metrics['earning_per_share'].iloc[-1]
            market_list = df_metrics['list'].iloc[-1]
            equity_ratio = df_metrics['equity_per_share'].iloc[-1]
            dividend_per_share = df_metrics['dividend_yield'].iloc[-1]
            
            cols = st.columns(3)
            
            with cols[0]:
                
                st.metric(
                    label="Ticker",
                    value=ticker
                )
                st.metric(
                    label="Price to Sales",
                    value=f"{price_to_sales}",
                    help="Price to Sales (P/S) ratio is a valuation metric that compares a company's stock price to its revenues. It is calculated by dividing the market capitalization by the total sales or revenue over the past 12 months."
                )
                st.metric(
                    label="Earnings per share",
                    value=f"{earnings_per_share}",
                    help="Earnings per share (EPS) is the portion of a company's profit allocated to each outstanding share of common stock."
                )
            with cols[1]:
                
                st.metric(
                    label="Market List",
                    value=market_list,
                    help="The stock exchange or market where the stock is listed, such as NYSE, NASDAQ, or OMX."
                )
                st.metric(
                    label="P/E Ratio",
                    value=f"{p_e_ratio}",
                    help="Price to Earnings (P/E) ratio is a valuation metric that compares a company's stock price to its earnings per share (EPS). It is calculated by dividing the market price per share by the earnings per share."
                )
                st.metric(
                    label="Dividend Yield",
                    value=f"{dividend_yield}",
                    help="Dividend Yield is a financial ratio that shows how much a company pays out in dividends each year relative to its stock price."
                )
            with cols[2]:
                st.metric(
                    label="Equity Ratio",
                    value=f"{equity_ratio}",
                    help="Equity Ratio is a financial metric that indicates the proportion of a company's total assets that are financed by shareholders' equity."
                )
                st.metric(
                    label="Dividend per share",
                    value=f"{dividend_per_share}",
                    help="Dividend per share (DPS) is the total dividends declared by a company for every outstanding share of stock."
                )
            

        # average_daily_volatility = calculate_average_daily_volatility(df,252)
        
        # volatility_chart = create_volatility_ranking_chart(df)
        # st.write(average_daily_volatility)  
        summary = get_volatility_summary(df)
        st.dataframe(data=summary)