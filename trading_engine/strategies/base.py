from abc import ABC, abstractmethod
import pandas as pd
from trading_engine.config import StrategyConfig

class Strategy(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def generate_signals(self, df, cfg):
        pass

    @abstractmethod
    def default_params(self) -> dict:
        """
        Returns a dictionary of parameter_name → default_value.
        """
        pass

    @abstractmethod
    def parameter_schema(self) -> dict:
        """
        Returns a dictionary describing parameter types for UI rendering.
        Example:
        {
            "rsi_threshold": {"type": "number", "min": 0, "max": 100},
            "bb_std": {"type": "number", "min": 1, "max": 4},
        }
        """
        pass

    def metadata(self) -> dict:
        """
        Returns metadata about the strategy for marketplace display.
        Override to provide rich information.
        """
        return {
            "description": "No description available",
            "category": "Uncategorized",
            "risk_level": "Medium",
            "tags": [],
            "author": "Unknown",
            "version": "1.0.0",
            "icon": "📊"
        }

