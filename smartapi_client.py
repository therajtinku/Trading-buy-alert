from SmartApi import SmartConnect
import pyotp
import pandas as pd
from datetime import datetime, timedelta
from config import Config
from utils import get_logger
import time

logger = get_logger(__name__)

class SmartApiClient:
    def __init__(self):
        self.api_key = Config.SMARTAPI_API_KEY
        self.client_id = Config.SMARTAPI_CLIENT_ID
        self.mpin = Config.SMARTAPI_MPIN
        self.totp_secret = Config.SMARTAPI_TOTP_SECRET
        self.smart_api = None
        self.session = None

    def login(self):
        """
        Authenticates with Angel One SmartAPI using TOTP.
        """
        try:
            self.smart_api = SmartConnect(api_key=self.api_key)
            totp = pyotp.TOTP(self.totp_secret).now()
            data = self.smart_api.generateSession(self.client_id, self.mpin, totp)
            
            if data['status']:
                self.session = data['data']
                logger.info("SmartAPI Login Successful")
                return True
            else:
                logger.error(f"SmartAPI Login Failed: {data['message']}")
                return False
        except Exception as e:
            logger.error(f"Error during SmartAPI login: {e}")
            return False

    def get_5min_candles(self, symbol_token, exchange="NSE", days=5, max_retries=3):
        """
        Fetches 5-minute candles for the last 'days'.
        Implements retry logic with exponential backoff for transient errors.
        """
        if not self.smart_api:
            logger.error("API not initialized. Call login() first.")
            return None

        # Calculate time range (timezone-naive for consistency)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        historicParam = {
            "exchange": exchange,
            "symboltoken": symbol_token,
            "interval": "FIVE_MINUTE",
            "fromdate": from_date.strftime("%Y-%m-%d %H:%M"), 
            "todate": to_date.strftime("%Y-%m-%d %H:%M")
        }
        
        for attempt in range(max_retries):
            try:
                data = self.smart_api.getCandleData(historicParam)
                logger.info(f"SmartAPI Response: {data}")
                
                if data and 'status' in data and data['status'] is True and 'data' in data:
                    # SmartAPI returns: [timestamp, open, high, low, close, volume]
                    df = pd.DataFrame(data['data'], columns=["timestamp", "open", "high", "low", "close", "volume"])
                    # Convert to datetime and ensure timezone-naive
                    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
                    df['close'] = df['close'].astype(float)
                    
                    # Return all rows
                    return df
                elif data and 'status' in data and data['status'] is False:
                    # API Error
                    error_msg = data.get('message', 'Unknown API Error')
                    error_code = data.get('errorcode', '')
                    
                    # Check if it's a transient error (AB1004)
                    if error_code == 'AB1004' and attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"Transient error {error_code} for {symbol_token}. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                    
                    logger.error(f"SmartAPI Error for {symbol_token}: {error_msg}")
                    raise RuntimeError(f"SmartAPI Error: {error_msg}")
                else:
                    logger.warning(f"No data fetched for token {symbol_token} (Response: {data})")
                    return None

            except RuntimeError:
                # Re-raise RuntimeError (already logged)
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Error fetching candles for {symbol_token}: {e}. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Error fetching candles for {symbol_token}: {e}")
                    raise e
        
        # If all retries exhausted
        logger.error(f"Failed to fetch candles for {symbol_token} after {max_retries} attempts")
        return None
