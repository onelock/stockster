import pandas as pd
from trading_engine.strategies.base import Strategy

class VWAPReversionStrategy(Strategy):

    @property
    def name(self):
        return "VWAP"

    def metadata(self):
        return {
            "description": "Identifies oversold conditions when price drops below VWAP bands with strong reversal signals. Ideal for intraday mean reversion with volume confirmation.",
            "category": "Mean Reversion",
            "risk_level": "Medium",
            "tags": ["VWAP", "Volume", "Intraday", "Bands", "Reversal"],
            "author": "Stockster Team",
            "version": "1.1.0",
            "icon": "📉"
        }

    def default_params(self):
        return {
            "vwap_dev_threshold": 0.01,
            "vwap_band_std": 1.0,
            "min_atr": 0.5,
        }

    def parameter_schema(self):
        return {
            "vwap_dev_threshold": {"type": "number", "min": 0.005, "max": 0.05},
            "vwap_band_std": {"type": "number", "min": 0.5, "max": 3},
            "min_atr": {"type": "number", "min": 0.1, "max": 5},
        }

    def generate_signals(self, df, cfg):
        params = cfg.strategy_params[self.name]

        dev = params["vwap_dev_threshold"]
        band = params["vwap_band_std"]
        min_atr = params["min_atr"]

        # compute signals using these params...

        df = df.copy()
        
        # VWAP deviation %
        dev_pct = (df["close"] - df["vwap"]) / df["vwap"]
        cond_dev = dev_pct <= -dev
        
        # VWAP bands (already computed in run_day)
        cond_band = df["close"] < df["vwap_lower"]
        
        # Candle confirmation
        cond_vol = df["volume"] > df["volume"].shift(1)
        cond_bullish = df["close"] > df["open"]
        
        # ATR filter
        cond_prev_down = df["close"].shift(1) < df["open"].shift(1)

        cond_atr = df["atr"] >= min_atr if min_atr else True

        signal =  (cond_dev & cond_band & cond_vol & cond_bullish & cond_prev_down & cond_atr)
        return signal.astype(int)




def generate_signals(self, df, cfg):
    params = cfg.strategy_params[self.name]

    dev_threshold = params["vwap_dev_threshold"]
    band_std = params["vwap_band_std"]
    min_atr = params["min_atr"]

    df = df.copy()

    # VWAP deviation %
    dev_pct = (df["close"] - df["vwap"]) / df["vwap"]
    cond_dev = dev_pct <= -dev_threshold

    # VWAP bands (already computed in run_day)
    cond_band = df["close"] < df["vwap_lower"]

    # Volume confirmation
    cond_vol = df["volume"] > df["volume"].shift(1)

    # Candle confirmation
    cond_bullish = df["close"] > df["open"]
    cond_prev_down = df["close"].shift(1) < df["open"].shift(1)

    # ATR filter
    cond_atr = df["atr"] >= min_atr if min_atr else True

    signal = cond_dev & cond_band & cond_vol & cond_bullish & cond_prev_down & cond_atr
    return signal.astype(int)
