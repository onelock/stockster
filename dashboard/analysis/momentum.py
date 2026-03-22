# intraday_momentum_backtest.py
# Run as a notebook cell or script. Adjust DATA_PATH and CONFIG below.

import pandas as pd
import numpy as np
from scipy.stats import zscore
from datetime import timedelta
import math
import matplotlib.pyplot as plt

# -------------------------
# CONFIG
# -------------------------
DATA_PATH = "/home/onelock/workspace/stockster/data/archive/2026/02/18/trading_2026-02-18_164701.csv"   # expected combined DataFrame
START_DATE = "2021-01-01"
END_DATE = "2024-12-31"

# Universe filters
MIN_ADV = 2000000        # daily ADV in USD
MIN_PRICE = 5.0

# Signal params
LOOKBACKS = [5, 15, 30, 60]   # minutes
WEIGHTS = [1.0, 1.0, 1.0, 1.0]
DECISION_FREQ = 5             # minutes between decisions
TOP_N = 50                    # number of longs to open each decision
HOLD_MINUTES = 60             # time-based exit
VOLUME_MULT = 1.5             # volume spike threshold (relative to median)

# Execution / cost model
HALF_SPREAD_PCT = 0.0005      # 0.05% half-spread
COMMISSION_PER_SHARE = 0.0001 # $0.0001 per share (example)
PARTICIPATION_LIMIT = 0.05    # max fraction of minute volume we will trade
SLIPPAGE_ALPHA = 0.1          # slippage coefficient (per participation rate)
DECISION_LATENCY_SEC = 2      # seconds delay to simulate latency

# Risk sizing
TARGET_RISK_PER_TRADE = 0.001 # fraction of portfolio volatility (e.g., 0.1% of equity)
MAX_POSITION_PCT = 0.01       # max 1% of portfolio per stock

# Backtest settings
INITIAL_CAPITAL = 1_000_000
SEED = 42

np.random.seed(SEED)

# -------------------------
# HELPERS
# -------------------------
def load_data(path):
    """
    Expect combined DataFrame with columns:
    ['datetime','symbol','open','high','low','close','volume']
    datetime must be timezone-naive or consistent.
    """
    df = pd.read_csv(path)
    df = df.rename(columns={'timestamp': 'datetime', 'name': 'symbol', 'last_price': 'close'})
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime').sort_index()
    return df

def compute_adv(df):
    # approximate ADV from minute bars: sum daily dollar volume / trading days
    dv = (df['close'] * df['volume']).groupby([df.index.date, df['symbol']]).sum()
    avg = dv.groupby(level=1).mean()
    return avg.to_dict()

def minute_returns(series, k):
    # k-minute return: (P_t - P_{t-k}) / P_{t-k}
    return series.pct_change(periods=k)

# -------------------------
# CORE BACKTEST
# -------------------------
def run_backtest(df, config):
    # Unpack config
    lookbacks = config['LOOKBACKS']
    weights = np.array(config['WEIGHTS'])
    decision_freq = config['DECISION_FREQ']
    top_n = config['TOP_N']
    hold_minutes = config['HOLD_MINUTES']
    volume_mult = config['VOLUME_MULT']
    half_spread = config['HALF_SPREAD_PCT']
    commission = config['COMMISSION_PER_SHARE']
    part_limit = config['PARTICIPATION_LIMIT']
    slippage_alpha = config['SLIPPAGE_ALPHA']
    latency_sec = config['DECISION_LATENCY_SEC']
    target_risk = config['TARGET_RISK_PER_TRADE']
    max_pos_pct = config['MAX_POSITION_PCT']
    initial_cap = config['INITIAL_CAPITAL']

    # Prepare outputs
    trades = []
    equity = initial_cap
    positions = {}  # symbol -> dict(entry_time, size, entry_price, stop, expiry)
    pnl_series = []

    # Precompute per-symbol daily ADV and median minute volume
    adv = compute_adv(df)
    median_min_vol = df.groupby('symbol')['volume'].median().to_dict()

    # Build minute-level cross-section pivot for fast ops
    # We'll iterate by minute timestamp
    all_times = sorted(df.index.unique())
    # Decision times: every DECISION_FREQ minutes starting at market open each day
    # For simplicity, assume data contains only market hours and minute alignment

    for t in all_times:
        # Skip if outside date range
        if t < pd.to_datetime(config['START_DATE']) or t > pd.to_datetime(config['END_DATE']):
            continue

        # Update open positions: check stops, profit targets, expiry
        # Use latest close price at time t
        row_t = df.loc[t]
        # row_t is multi-indexed by symbol; ensure we can get price per symbol
        # For speed, convert to dict
        close_prices = row_t['close'].to_dict()
        minute_volumes = row_t['volume'].to_dict()

        # Update positions PnL and check exits
        to_close = []
        for sym, pos in list(positions.items()):
            if sym not in close_prices:
                continue
            price = close_prices[sym]
            # mark-to-market PnL
            pos_pnl = (price - pos['entry_price']) * pos['size']
            # stop loss check
            if 'stop' in pos and ((pos['size'] > 0 and price <= pos['stop']) or (pos['size'] < 0 and price >= pos['stop'])):
                # exit at stop price (simulate spread/slippage)
                exit_price = pos['stop']
                trades.append({
                    'symbol': sym, 'entry_time': pos['entry_time'], 'exit_time': t,
                    'entry_price': pos['entry_price'], 'exit_price': exit_price,
                    'size': pos['size']
                })
                equity += (exit_price - pos['entry_price']) * pos['size']
                to_close.append(sym)
                continue
            # time expiry
            if t >= pos['expiry']:
                exit_price = price
                trades.append({
                    'symbol': sym, 'entry_time': pos['entry_time'], 'exit_time': t,
                    'entry_price': pos['entry_price'], 'exit_price': exit_price,
                    'size': pos['size']
                })
                equity += (exit_price - pos['entry_price']) * pos['size']
                to_close.append(sym)
        for sym in to_close:
            positions.pop(sym, None)

        # Record equity snapshot
        pnl_series.append({'time': t, 'equity': equity})

        # Decision step: only every DECISION_FREQ minutes
        if (t.minute % decision_freq) != 0:
            continue

        # Build cross-section returns for each lookback
        cs = df.loc[:t]  # all data up to t
        # For each symbol compute returns for lookbacks
        symbols = cs['symbol'].unique()
        ret_matrix = {}
        for k in lookbacks:
            # compute k-minute returns using last k minutes
            # get price series per symbol
            last_prices = cs.groupby('symbol')['close'].apply(lambda s: s.iloc[-(k+1):] if len(s) >= (k+1) else None)
            # compute returns only for symbols with enough history
            ret_k = {}
            for sym, series in last_prices.items():
                if series is None or len(series) < (k+1):
                    continue
                ret_k[sym] = (series.iloc[-1] - series.iloc[0]) / series.iloc[0]
            ret_matrix[k] = ret_k

        # Build z-scores per lookback across cross-section
        z_scores = {k: {} for k in lookbacks}
        for k in lookbacks:
            vals = np.array(list(ret_matrix[k].values()))
            if len(vals) < 5:
                continue
            mu = vals.mean()
            sigma = vals.std(ddof=0) if vals.std(ddof=0) > 0 else 1.0
            for i, sym in enumerate(ret_matrix[k].keys()):
                z_scores[k][sym] = (ret_matrix[k][sym] - mu) / sigma

        # Compute IMS for each symbol
        ims = {}
        for sym in symbols:
            zvec = []
            for j, k in enumerate(lookbacks):
                z = z_scores.get(k, {}).get(sym, None)
                if z is None:
                    z = 0.0
                zvec.append(z * weights[j])
            ims[sym] = np.sum(zvec)

        # Rank and select top N
        sorted_syms = sorted(ims.items(), key=lambda x: x[1], reverse=True)
        candidates = [s for s,score in sorted_syms[:top_n]]

        # Apply liquidity and volume filters
        selected = []
        for sym in candidates:
            # ADV filter
            if adv.get(sym, 0) < config['MIN_ADV']:
                continue
            # price filter
            price = close_prices.get(sym, None)
            if price is None or price < config['MIN_PRICE']:
                continue
            # volume spike
            med_vol = median_min_vol.get(sym, 1)
            cur_vol = minute_volumes.get(sym, 0)
            if cur_vol < volume_mult * med_vol:
                continue
            selected.append(sym)

        # For each selected symbol, compute position size and simulate entry
        for sym in selected:
            if sym in positions:
                continue  # skip if already have position
            price = close_prices[sym]
            # volatility estimate: use 20-minute realized vol (std of returns)
            hist = df[df['symbol'] == sym].loc[:t]['close']
            if len(hist) < 21:
                continue
            returns_20 = hist.pct_change().dropna().iloc[-20:]
            vol = returns_20.std() * math.sqrt(252*6.5*60)  # annualized approx (not critical)
            if vol == 0 or np.isnan(vol):
                continue
            # position notional based on target risk
            # approximate dollar volatility per $1 notional = vol
            # desired notional = target_risk * equity / vol
            desired_notional = target_risk * equity / vol
            max_notional = max_pos_pct * equity
            notional = min(desired_notional, max_notional)
            size = math.floor(notional / price)  # shares
            if size <= 0:
                continue

            # Participation check: do not exceed PARTICIPATION_LIMIT of minute volume
            cur_min_vol = minute_volumes.get(sym, 1)
            max_shares = int(part_limit * cur_min_vol)
            size = min(size, max_shares)
            if size <= 0:
                continue

            # Simulate fill price: mid + half_spread + slippage
            # participation rate
            part_rate = size / max(1, cur_min_vol)
            slippage = slippage_alpha * part_rate * price
            entry_price = price * (1 + half_spread + slippage)  # long
            # record position
            positions[sym] = {
                'entry_time': t + pd.Timedelta(seconds=latency_sec),
                'entry_price': entry_price,
                'size': size,
                'stop': entry_price * (1 - 0.015),  # example 1.5% stop
                'expiry': t + pd.Timedelta(minutes=hold_minutes)
            }
            # deduct cash for entry (simplified)
            equity -= entry_price * size
            # record trade entry (exit_price None for now)
            trades.append({
                'symbol': sym, 'entry_time': positions[sym]['entry_time'],
                'exit_time': None, 'entry_price': entry_price, 'exit_price': None,
                'size': size
            })

    # Finalize: close remaining positions at last available price
    last_time = all_times[-1]
    last_prices = df.loc[last_time]['close'].to_dict()
    for sym, pos in positions.items():
        price = last_prices.get(sym, pos['entry_price'])
        exit_price = price * (1 - half_spread)  # assume exit at mid - half spread
        trades.append({
            'symbol': sym, 'entry_time': pos['entry_time'], 'exit_time': last_time,
            'entry_price': pos['entry_price'], 'exit_price': exit_price, 'size': pos['size']
        })
        equity += exit_price * pos['size']

    trades_df = pd.DataFrame(trades)
    pnl_df = pd.DataFrame(pnl_series).set_index('time')
    return trades_df, pnl_df

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    config = {
        'LOOKBACKS': LOOKBACKS,
        'WEIGHTS': WEIGHTS,
        'DECISION_FREQ': DECISION_FREQ,
        'TOP_N': TOP_N,
        'HOLD_MINUTES': HOLD_MINUTES,
        'VOLUME_MULT': VOLUME_MULT,
        'HALF_SPREAD_PCT': HALF_SPREAD_PCT,
        'COMMISSION_PER_SHARE': COMMISSION_PER_SHARE,
        'PARTICIPATION_LIMIT': PARTICIPATION_LIMIT,
        'SLIPPAGE_ALPHA': SLIPPAGE_ALPHA,
        'DECISION_LATENCY_SEC': DECISION_LATENCY_SEC,
        'TARGET_RISK_PER_TRADE': TARGET_RISK_PER_TRADE,
        'MAX_POSITION_PCT': MAX_POSITION_PCT,
        'INITIAL_CAPITAL': INITIAL_CAPITAL,
        'MIN_ADV': MIN_ADV,
        'MIN_PRICE': MIN_PRICE,
        'START_DATE': START_DATE,
        'END_DATE': END_DATE
    }

    print("Loading data...")
    df = load_data(DATA_PATH)
    print("Running backtest...")
    trades, pnl = run_backtest(df, config)
    print("Trades:", len(trades))
    print(trades.head())
    pnl['equity'].plot(title="Equity Curve")
    plt.show()
