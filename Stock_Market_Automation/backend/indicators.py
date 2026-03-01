def calculate_heikin_ashi(candles):
    """
    Converts standard candles to Heikin-Ashi candles.
    Input format: [timestamp, open, high, low, close, volume]
    Output format: [timestamp, ha_open, ha_high, ha_low, ha_close, volume]
    """
    ha_candles = []
    if not candles:
        return []

    for i, c in enumerate(candles):
        # Ensure candle has enough data
        if len(c) < 6:
            continue
            
        timestamp, open_, high, low, close, vol = c[0], c[1], c[2], c[3], c[4], c[5]
        
        ha_close = (open_ + high + low + close) / 4
        
        if i == 0:
            ha_open = (open_ + close) / 2
        else:
            prev_ha = ha_candles[-1]
            ha_open = (prev_ha[1] + prev_ha[4]) / 2  # (prev_open + prev_close) / 2
            
        ha_high = max(high, ha_open, ha_close)
        ha_low = min(low, ha_open, ha_close)
        
        ha_candles.append([timestamp, ha_open, ha_high, ha_low, ha_close, vol])
        
    return ha_candles

def calculate_vwap(candles):
    """Calculates VWAP from a list of candles."""
    total_pv = 0
    total_vol = 0
    
    for c in candles:
        if len(c) < 6:
            continue
        typical_price = (c[2] + c[3] + c[4]) / 3  # (High + Low + Close) / 3
        volume = c[5]
        
        total_pv += typical_price * volume
        total_vol += volume
        
    if total_vol > 0:
        return round(total_pv / total_vol, 2)
    return None

def calculate_fib_levels(high, low):
    """Calculates Fibonacci retracement levels."""
    diff = high - low
    return {
        "fib236": round(high - diff * 0.236, 2),
        "fib382": round(high - diff * 0.382, 2),
        "fib50":  round(high - diff * 0.5, 2),
        "fib618": round(high - diff * 0.618, 2),
        "fib786": round(high - diff * 0.786, 2)
    }
