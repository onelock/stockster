import pandas as pd
from trading_engine.strategies.base import Strategy
from trading_engine.indicators.rsi import rsi
from trading_engine.indicators.bollinger import bollinger_bands

class MeanReversionStrategy(Strategy):

    @property
    def name(self):
        return "MeanReversion"

    def metadata(self):
        return {
            "description": "Buys when price reverts below Bollinger Bands with oversold RSI and strong volume. Targets mean reversion opportunities in volatile markets.",
            "category": "Mean Reversion",
            "risk_level": "Medium-High",
            "tags": ["RSI", "Bollinger Bands", "Volume", "ATR", "Oversold"],
            "author": "Stockster Team",
            "version": "1.2.0",
            "icon": "🔄"
        }

    def default_params(self):
        return {
            "rsi_threshold": 5,
            "bb_std": 2.0,
            "atr_multiplier": 1.0,
            "min_volume_ratio": 0.5,
        }

    def parameter_schema(self):
        return {
            "rsi_threshold": {"type": "number", "min": 1, "max": 50},
            "bb_std": {"type": "number", "min": 1, "max": 4},
            "atr_multiplier": {"type": "number", "min": 0.5, "max": 3},
            "min_volume_ratio": {"type": "number", "min": 0.1, "max": 2},
        }

    def generate_signals(self, df, cfg):
        params = cfg.strategy_params[self.name]

        rsi_threshold = params["rsi_threshold"]
        bb_std = params["bb_std"]
        atr_mult = params["atr_multiplier"]
        min_vol = params["min_volume_ratio"]

        # compute indicators and signals using these params...
        df = df.copy()
        df["rsi2"] = rsi(df["close"], cfg.rsi_period)
        
        _, _, df["bb_lower"] = bollinger_bands(
            df["close"], 
            period=cfg.bb_period, 
            std=bb_std
        )

        recent_high = df["high"].rolling(cfg.atr_period).max()
        atr = df["atr"]

        cond_rsi = df["rsi2"] < rsi_threshold
        cond_bb = df["close"] < df["bb_lower"]
        cond_atr = (recent_high - df["close"]) >= (atr * atr_mult)
        cond_vol = df["volume"] >= min_vol * df["vol_avg"]

        signal = (cond_rsi & cond_bb & cond_atr & cond_vol)
        return signal.astype(int)
