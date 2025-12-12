from SmartApi import SmartConnect
import pyotp
import pandas as pd
from datetime import datetime, timedelta
from config import Config
from utils import get_logger

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

    def get_5min_candles(self, symbol_token, exchange="NSE", days=5):
        """
        Fetches 5-minute candles for the last 'days'.
        """
        if not self.smart_api:
            logger.error("API not initialized. Call login() first.")
            return None

        # Calculate time range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        
        try:
            historicParam = {
                "exchange": exchange,
                "symboltoken": symbol_token,
                "interval": "FIVE_MINUTE",
                "fromdate": from_date.strftime("%Y-%m-%d %H:%M"), 
                "todate": to_date.strftime("%Y-%m-%d %H:%M")
            }
            
            data = self.smart_api.getCandleData(historicParam)
            logger.info(f"SmartAPI Response: {data}")
            
            if data and 'data' in data:
                # SmartAPI returns: [timestamp, open, high, low, close, volume]
                df = pd.DataFrame(data['data'], columns=["timestamp", "open", "high", "low", "close", "volume"])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['close'] = df['close'].astype(float)
                
                # Return all rows
                return df
            else:
                logger.warning(f"No data fetched for token {symbol_token}")
                return None

        except Exception as e:
            logger.error(f"Error fetching candles for {symbol_token}: {e}")
            return None
