from smartapi_client import SmartApiClient
from utils import get_logger
import pandas as pd

logger = get_logger(__name__)

def test_fetch():
    client = SmartApiClient()
    if not client.login():
        print("Login failed")
        return

    # Test 1: Nifty 50, 10 days (Original failing request)
    print("\n--- Test 1: Nifty 50 (99926000), 10 days ---")
    try:
        df = client.get_5min_candles("99926000", "NSE", days=10)
        if df is not None:
            print(f"Success! Retrieved {len(df)} rows.")
            print(df.tail())
        else:
            print("Failed to retrieve data.")
    except Exception as e:
        print(f"caught error: {e}")

    # Test 2: Nifty 50, 1 day
    print("\n--- Test 2: Nifty 50 (99926000), 1 day ---")
    try:
        df = client.get_5min_candles("99926000", "NSE", days=1)
        if df is not None:
            print(f"Success! Retrieved {len(df)} rows.")
            print(df.tail())
        else:
            print("Failed to retrieve data.")
    except Exception as e:
        print(f"caught error: {e}")

    # Test 3: SBIN (3045), 1 day
    print("\n--- Test 3: SBIN (3045), 1 day ---")
    try:
        df = client.get_5min_candles("3045", "NSE", days=1)
        if df is not None:
            print(f"Success! Retrieved {len(df)} rows.")
            print(df.tail())
        else:
            print("Failed to retrieve data.")
    except Exception as e:
        print(f"caught error: {e}")

if __name__ == "__main__":
    test_fetch()
