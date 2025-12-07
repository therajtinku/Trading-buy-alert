import pandas as pd

def calculate_sma(series, period):
    """
    Calculates Simple Moving Average (SMA).
    """
    return series.rolling(window=period).mean()

def detect_bullish_crossover(ma9_prev, ma20_prev, ma9_curr, ma20_curr):
    """
    Detects if MA9 crossed above MA20.
    Condition: (MA9_prev <= MA20_prev) AND (MA9_curr > MA20_curr)
    """
    if pd.isna(ma9_prev) or pd.isna(ma20_prev) or pd.isna(ma9_curr) or pd.isna(ma20_curr):
        return False
        
    return (ma9_prev <= ma20_prev) and (ma9_curr > ma20_curr)
