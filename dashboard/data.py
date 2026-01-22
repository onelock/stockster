"""
Data loading and caching for dashboard
"""

import pandas as pd
import requests
from typing import Optional
import os


# API configuration
# Default to localhost for development, override with API_URL env var for production
API_URL = os.environ.get('API_URL', 'http://localhost:8000')


class StockDataLoader:
    """Handles all API communication and data loading"""
    
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
    
    def load_latest_stocks(self, limit: int = 1000) -> pd.DataFrame:
        """Load latest stock data from API"""
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
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["last_price"] = pd.to_numeric(df["last_price"], errors="coerce")
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
            df["change_pct"] = pd.to_numeric(df["change_pct"], errors="coerce")
            df["market_value"] = pd.to_numeric(df["market_value"], errors="coerce")
            return df
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to load data from API: {e}")
    
    def load_stock_history(self, stock_name: str, days: int = 30) -> pd.DataFrame:
        """Load historical data for a specific stock"""
        try:
            response = requests.get(
                f"{self.api_url}/stocks/{stock_name}?days={days}", 
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
            df = df.sort_values("timestamp")
            return df
        except requests.exceptions.RequestException:
            return pd.DataFrame()
    
    def load_stock_historical(self, stock_name: str, days: int = 30) -> pd.DataFrame:
        """Load historical comparison data for a specific stock"""
        try:
            response = requests.get(
                f"{self.api_url}/stocks/{stock_name}/historical?days={days}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data'):
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")
            return df
        except requests.exceptions.RequestException:
            return pd.DataFrame()
    
    def load_stock_metrics(self, stock_name: str, days: int = 30) -> pd.DataFrame:
        """Load financial metrics for a specific stock"""
        try:
            response = requests.get(
                f"{self.api_url}/stocks/{stock_name}/metrics?days={days}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data'):
                return pd.DataFrame()
            
            df = pd.DataFrame(data['data'])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["pe_ratio"] = pd.to_numeric(df["pe_ratio"], errors="coerce")
            df["ps_ratio"] = pd.to_numeric(df["ps_ratio"], errors="coerce")
            df["dividend_yield"] = pd.to_numeric(df["dividend_yield"], errors="coerce")
            df = df.sort_values("timestamp")
            return df
        except requests.exceptions.RequestException:
            return pd.DataFrame()
    
    def search_stocks(self, query: str) -> list:
        """Search for stocks by name"""
        try:
            response = requests.get(
                f"{self.api_url}/search?q={query}",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except requests.exceptions.RequestException:
            return []
    
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
