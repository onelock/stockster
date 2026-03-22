"""Volatility visualization for dashboard"""
import altair as alt
import pandas as pd
from dashboard.analysis.volatility import calculate_volatility


def create_volatility_ranking_chart(df: pd.DataFrame, top_n: int = 5) -> alt.Chart:
    """
    Create horizontal bar chart showing volatility rankings
    
    Args:
        df: DataFrame with columns: name, avg_daily_volatility_pct, risk_level
        top_n: Number of top volatile stocks to show
    
    Returns:
        Altair chart
    """
    # Take top N
    df_top = df
    
    # Use avg_daily_volatility_pct directly
    if 'avg_daily_volatility_pct' not in df_top.columns:
        df_top['volatility_pct'] = df_top['avg_daily_volatility'] * 100
    else:
        df_top['volatility_pct'] = df_top['avg_daily_volatility_pct']
    
    # Color scale based on risk level
    color_scale = alt.Scale(
        domain=['Low', 'Medium', 'High', 'Very High'],
        range=['#4CAF50', '#FFC107', '#FF9800', '#F44336']
    )
    
    # Calculate dynamic height based on number of stocks (minimum 25px per stock)
    chart_height = max(400, len(df_top) * 25)
    
    chart = alt.Chart(df_top).mark_bar().encode(
        y=alt.Y('name:N', 
                sort='-x', 
                title='Stock',
                axis=alt.Axis(labelLimit=200, labelOverlap=False)),
        x=alt.X('volatility_pct:Q', title='Average Daily Volatility (%)'),
        color=alt.Color('risk_level:N', scale=color_scale, title='Risk Level'),
        tooltip=[
            alt.Tooltip('name:N', title='Stock'),
            alt.Tooltip('volatility_pct:Q', title='Daily Volatility (%)', format='.2f'),
            alt.Tooltip('risk_level:N', title='Risk Level'),
            alt.Tooltip('rank:Q', title='Rank')
        ]
    ).properties(
        height=chart_height,
        title='Stock Volatility Rankings - Average Daily Movement (Higher = More Volatile)'
    )
    
    return chart.interactive()


def create_volatility_timeseries_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Create time series chart showing volatility over time
    
    Args:
        df: DataFrame with columns: timestamp, avg_daily_volatility, last_price
    
    Returns:
        Layered Altair chart
    """
    # Convert to percentage
    df = df.copy()
    if 'avg_daily_volatility' in df.columns:
        df['volatility_pct'] = df['avg_daily_volatility'] * 100
    else:
        df['volatility_pct'] = df['volatility_annualized'] * 100
    
    # Price chart
    price_chart = alt.Chart(df).mark_line(color='steelblue').encode(
        x=alt.X('timestamp:T', title='Date'),
        y=alt.Y('last_price:Q', title='Price', scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip('timestamp:T', format='%Y-%m-%d'),
            alt.Tooltip('last_price:Q', title='Price', format='.2f')
        ]
    )
    
    # Volatility chart
    volatility_chart = alt.Chart(df).mark_line(color='orange', strokeDash=[5, 5]).encode(
        x=alt.X('timestamp:T', title='Date'),
        y=alt.Y('volatility_pct:Q', title='Daily Volatility (%)', axis=alt.Axis(orient='right')),
        tooltip=[
            alt.Tooltip('timestamp:T', format='%Y-%m-%d'),
            alt.Tooltip('volatility_pct:Q', title='Daily Volatility (%)', format='.2f')
        ]
    )
    
    return alt.layer(
        price_chart,
        volatility_chart
    ).resolve_scale(
        y='independent'
    ).properties(
        height=300,
        title='Price and Average Daily Volatility Over Time'
    ).interactive()


def create_volatility_distribution_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Create histogram showing distribution of volatility across stocks
    
    Args:
        df: DataFrame with avg_daily_volatility_pct column
    
    Returns:
        Altair chart
    """
    df = df.copy()
    if 'avg_daily_volatility_pct' in df.columns:
        df['volatility_pct'] = df['avg_daily_volatility_pct']
    else:
        df['volatility_pct'] = df['avg_daily_volatility'] * 100
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('volatility_pct:Q', bin=alt.Bin(maxbins=30), title='Average Daily Volatility (%)'),
        y=alt.Y('count()', title='Number of Stocks'),
        tooltip=[
            alt.Tooltip('count()', title='Count'),
            alt.Tooltip('volatility_pct:Q', bin=True, title='Daily Volatility (%)')
        ]
    ).properties(
        height=250,
        title='Distribution of Daily Volatility Across Stocks'
    )
    
    return chart.interactive()


def create_risk_level_pie_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Create pie chart showing distribution of risk levels
    
    Args:
        df: DataFrame with risk_level column
    
    Returns:
        Altair chart
    """
    # Count by risk level
    risk_counts = df['risk_level'].value_counts().reset_index()
    risk_counts.columns = ['risk_level', 'count']
    
    # Color scale
    color_scale = alt.Scale(
        domain=['Low', 'Medium', 'High', 'Very High'],
        range=['#4CAF50', '#FFC107', '#FF9800', '#F44336']
    )
    
    chart = alt.Chart(risk_counts).mark_arc().encode(
        theta=alt.Theta('count:Q'),
        color=alt.Color('risk_level:N', scale=color_scale, title='Risk Level'),
        tooltip=[
            alt.Tooltip('risk_level:N', title='Risk Level'),
            alt.Tooltip('count:Q', title='Count')
        ]
    ).properties(
        height=250,
        title='Stock Distribution by Risk Level'
    )
    
    return chart
