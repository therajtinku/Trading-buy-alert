import pandas as pd
from indicators import calculate_sma, detect_bullish_crossover, detect_bearish_crossover

def test_logic():
    print("--- Testing Crossover Logic ---")
    
    # 1. Simulate data where crossover happens on the LAST candle (Forming)
    # We want to ensure we DO NOT alert if we consider it forming.
    
    data_forming = {
        'timestamp': pd.to_datetime([
            '2023-10-27 09:15:00',
            '2023-10-27 09:20:00',
            '2023-10-27 09:25:00', # Crossover starts here?
            '2023-10-27 09:30:00',
            '2023-10-27 09:35:00'  # Current forming candle
        ]),
        'close': [100, 101, 102, 105, 110] # Price rising
    }
    df = pd.DataFrame(data_forming)
    
    # Calculate Indicators
    df['MA9'] = calculate_sma(df['close'], 3) # Short period for test
    df['MA20'] = calculate_sma(df['close'], 5) # Short period for test
    
    print("\nData Frame with Indicators:")
    print(df)
    
    # Simulate the logic in main.py loop
    # We pretend we are at 09:37, so 09:35 is the LAST candle and it is FORMING (not closed).
    
    print("\n--- Simulation: Current Time 09:37 (Candle 09:35 is Forming) ---")
    
    # Current simplistic logic (iterates to end)
    for i in range(2, len(df)):
        curr = df.iloc[i]
        prev = df.iloc[i-1]
        
        is_bullish = detect_bullish_crossover(prev['MA9'], prev['MA20'], curr['MA9'], curr['MA20'])
        
        if is_bullish:
            print(f"ALERT DETECTED at {curr['timestamp']} (Close: {curr['close']})")
        else:
            print(f"No Alert at {curr['timestamp']}")

if __name__ == "__main__":
    test_logic()
