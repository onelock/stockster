
import requests
from .config import API_URL
import pandas as pd
import streamlit as st


def make_api_request(endpoint: str, params: dict = None) -> dict:
    """Helper function to perform GET requests to the API and return a dictionary"""
    try:
        response = requests.get(f"{API_URL}{endpoint}", params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("data", {})
        
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"API request failed: {e}")

def get_stocks(url: str, params: dict = None) -> pd.DataFrame:
    """Helper function to perform GET requests to the API"""
    try:
        data = make_api_request(f"{url}")

        df = pd.DataFrame(data)
        
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["last_price"] = pd.to_numeric(df["last_price"], errors="coerce")
        df["lowest"] = pd.to_numeric(df["lowest"], errors="coerce")
        df["highest"] = pd.to_numeric(df["highest"], errors="coerce")
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
        df["change_abs"] = pd.to_numeric(df["change_abs"], errors="coerce")
        df["change_pct"] = pd.to_numeric(df["change_pct"], errors="coerce")
        df["market_value"] = pd.to_numeric(df["market_value"], errors="coerce")
        
        df = df.loc[:, ~df.columns.isin([ "id", "created_at", "updated_at", 'href'])]
        return df
        
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"API request failed: {e}")

def get_recent_stock_info(limit: int = 1000) -> pd.DataFrame:
    """Load latest stock data from API"""
    data = get_stocks(f"/stocks/latest?limit={limit}")
    return data


@st.cache_data
def get_stock_details(ticker: str) -> pd.DataFrame:
    """Load detailed stock data for a specific ticker from API"""
    data = get_stocks(f"/stocks/{ticker}")
    return data

@st.cache_data
def get_stock_metrics(ticker: str) -> pd.DataFrame:
    """Load stock metrics for a specific ticker from API"""
    data = make_api_request(f"/stocks/{ticker}/metrics")
    df = pd.DataFrame(data)
    df = df.loc[:, ~df.columns.isin([ "id", "created_at", "updated_at", 'href'])]
    
    return df

