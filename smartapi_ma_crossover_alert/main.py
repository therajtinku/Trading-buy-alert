import time
import schedule
import pandas as pd
from smartapi_client import SmartApiClient
from indicators import calculate_sma, detect_bullish_crossover
from telegram_alerts import send_telegram_message
from utils import get_logger, format_ist_time
from config import Config

logger = get_logger(__name__)

# Configuration
# NOTE: You need to map symbols to their SmartAPI tokens.
# Example tokens (Need to be updated with actual tokens from Angel One instrument list)
# For this example, we assume a dictionary mapping.
SYMBOLS_MAP = {
    "NSE:RELIANCE": {"token": "2885", "exchange": "NSE"},
    "NSE:TCS": {"token": "11536", "exchange": "NSE"},
    "NSE:INFY": {"token": "1594", "exchange": "NSE"}
}

# State to track alerts to avoid duplicates
# Format: { "SYMBOL": "LAST_ALERT_TIME_OR_STATUS" }
last_alert_status = {}

def job(client):
    logger.info("Starting scheduled scan...")
    
    for symbol_name, details in SYMBOLS_MAP.items():
        try:
            token = details["token"]
            exchange = details["exchange"]
            
            logger.info(f"Processing {symbol_name}...")
            
            # 1. Fetch Data
            df = client.get_5min_candles(token, exchange)
            
            if df is None or len(df) < 20:
                logger.warning(f"Insufficient data for {symbol_name}")
                continue
            
            # 2. Compute Indicators
            df['MA9'] = calculate_sma(df['close'], 9)
            df['MA20'] = calculate_sma(df['close'], 20)
            
            # Get last two completed candles (ignoring the currently forming one if needed, 
            # but usually API returns completed or we take the last two rows)
            # Assuming the last row is the most recent completed candle:
            curr_candle = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            ma9_curr = curr_candle['MA9']
            ma20_curr = curr_candle['MA20']
            ma9_prev = prev_candle['MA9']
            ma20_prev = prev_candle['MA20']
            
            close_price = curr_candle['close']
            timestamp = curr_candle['timestamp']
            
            # 3. Detect Crossover
            is_bullish = detect_bullish_crossover(ma9_prev, ma20_prev, ma9_curr, ma20_curr)
            
            # 4. Alert Logic
            if is_bullish:
                # Check if we already alerted for this specific event (or recent time)
                # We use the candle timestamp to ensure uniqueness per candle
                last_alert_time = last_alert_status.get(symbol_name)
                
                if last_alert_time != timestamp:
                    message = (
                        f"🚀 **BULLISH CROSSOVER DETECTED**\n\n"
                        f"Symbol: {symbol_name}\n"
                        f"Signal: MA9 crossed ABOVE MA20 — BUY SIGNAL\n"
                        f"Price: {close_price}\n"
                        f"Time: {timestamp} (IST)"
                    )
                    
                    send_telegram_message(message)
                    logger.info(f"Alert sent for {symbol_name}")
                    
                    # Update status
                    last_alert_status[symbol_name] = timestamp
                else:
                    logger.info(f"Duplicate alert suppressed for {symbol_name} at {timestamp}")
            else:
                logger.info(f"No crossover for {symbol_name}. MA9: {ma9_curr:.2f}, MA20: {ma20_curr:.2f}")
                
        except Exception as e:
            logger.error(f"Error processing {symbol_name}: {e}")

    logger.info("Scan completed.")

def main():
    logger.info("Initializing SmartAPI MA Crossover Alert System...")
    
    # Validate Config
    try:
        Config.validate()
    except ValueError as e:
        logger.error(e)
        return

    # Initialize API Client
    client = SmartApiClient()
    if not client.login():
        logger.error("Failed to login. Exiting.")
        return

    # Schedule Job
    # Run every 5 minutes
    schedule.every(5).minutes.do(job, client)
    
    # Run once immediately on startup
    job(client)
    
    logger.info("Scheduler started. Waiting for next run...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
