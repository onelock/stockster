from dataclasses import dataclass, field

@dataclass
class StrategyConfig:
    symbol: str
    date: str
    tp_pct: float = 0.005
    sl_pct: float = 0.003
    strategy_params: dict = field(default_factory=dict)
    # rsi_period: int = 2
    # bb_period: int = 20
    # bb_std: float = 2.0
    # atr_period: int = 14
    # vwap_band_std: float = 1.0
    # vwap_dev_threshold: float = 0.01
    # min_volume_ratio: float = 0.5
    # min_atr: float | None = None
# 