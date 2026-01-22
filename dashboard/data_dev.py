"""
Data loading for development dashboard using Alpaca data
"""

import pandas as pd
import requests
from typing import Optional
import os


# API configuration - Development API runs on port 8001
API_URL = os.environ.get('DEV_API_URL', 'http://localhost:8000')


class StockDataLoader:
    """Handles all API communication and data loading for Alpaca development data"""
    
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
    
    def load_latest_stocks(self, limit: int = 100) -> pd.DataFrame:
        """Load latest Alpaca stock data from development API"""
        try:
            response = requests.get(
                f"{self.api_url}/stocks/latest?limit={limit}", 
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('stocks'):
                return pd.DataFrame()
            
            df = pd.DataFrame(data['stocks'])
            print(f'\ntesting columun names: {df.columns}\n')
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["last_price"] = pd.to_numeric(df["last_price"], errors="coerce")
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
            df["change_pct"] = pd.to_numeric(df["change_pct"], errors="coerce")
            df["change_abs"] = pd.to_numeric(df["change_abs"], errors="coerce")
            df["open_price"] = pd.to_numeric(df["open_price"], errors="coerce")
            df["vwap"] = pd.to_numeric(df["vwap"], errors="coerce")
            df["highest"] = pd.to_numeric(df["highest"], errors="coerce")
            df["lowest"] = pd.to_numeric(df["lowest"], errors="coerce")
            return df
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to load data from dev API: {e}")
    
    def load_stock_history(self, stock_symbol: str, days: int = 30) -> pd.DataFrame:
        """Load historical Alpaca data for a specific stock"""
        try:
            response = requests.get(
                f"{self.api_url}/stocks/{stock_symbol}?days={days}", 
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data'):
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["last_price"] = pd.to_numeric(df["last_price"], errors="coerce")
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
            df["change_pct"] = pd.to_numeric(df["change_pct"], errors="coerce")
            df["change_abs"] = pd.to_numeric(df["change_abs"], errors="coerce")
            df["open_price"] = pd.to_numeric(df["open_price"], errors="coerce")
            df["vwap"] = pd.to_numeric(df["vwap"], errors="coerce")
            df["highest"] = pd.to_numeric(df["highest"], errors="coerce")
            df["lowest"] = pd.to_numeric(df["lowest"], errors="coerce")
            df = df.sort_values("timestamp")
            return df
        except requests.exceptions.RequestException:
            return pd.DataFrame()
    
    def get_stats(self) -> dict:
        """Get database statistics"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            return {}
    
    def health_check(self) -> dict:
        """Check API health"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "unhealthy", "error": str(e)}