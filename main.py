import time
import schedule
import pandas as pd
from smartapi_client import SmartApiClient
from indicators import calculate_sma, detect_bullish_crossover, detect_bearish_crossover
from telegram_alerts import send_telegram_message
from utils import get_logger, format_ist_time
from config import Config

logger = get_logger(__name__)

# Configuration
# NOTE: You need to map symbols to their SmartAPI tokens.
# Example tokens (Need to be updated with actual tokens from Angel One instrument list)
SYMBOLS_MAP = {
    "NSE:NIFTY": {"token": "99926000", "exchange": "NSE"}
}

# State to track alerts to avoid duplicates
# Format: { "SYMBOL": "LAST_ALERT_TIME_OR_STATUS" }
last_alert_status = {}

from datetime import datetime, time as dtime

def is_market_open():
    """
    Checks if current IST time is between 09:15 and 15:30.
    """
    now = datetime.now()
    current_time = now.time()
    start_time = dtime(9, 15)
    end_time = dtime(15, 30)
    
    # Simple check for now. Ideally should check for weekends/holidays too.
    return start_time <= current_time <= end_time

def job(client):
    if not is_market_open():
        logger.info("Market is closed. Skipping scan.")
        return

    logger.info("Starting scheduled scan for Confirmed Crossovers...")
    
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
            
            # 2. Filter out Forming Candle
            # We want to ensure we only process COMPLETED candles.
            # A 5-min candle at 09:15 completes at 09:20.
            # If current time is 09:18, the 09:15 candle is forming -> Drop it.
            # If current time is 09:21, the 09:15 candle is confirmed -> Keep it.
            
            from datetime import timedelta
            current_time = datetime.now()
            
            # Check the last candle
            last_candle = df.iloc[-1]
            last_candle_time = last_candle['timestamp']
            
            # Theoretically, close time is timestamp + 5 mins
            candle_close_time = last_candle_time + timedelta(minutes=5)
            
            if current_time < candle_close_time:
                logger.info(f"Dropping forming candle at {last_candle_time} (Current: {current_time.strftime('%H:%M:%S')})")
                df = df.iloc[:-1] # Remove the last row
            
            if len(df) < 20: 
                logger.warning("Insufficient data after filtering forming candle.")
                continue

            # 3. Compute Indicators on Confirmed Data
            df['MA9'] = calculate_sma(df['close'], 9)
            df['MA20'] = calculate_sma(df['close'], 20)
            
            # 4. Scan for Crossover
            # We only need to check the very last confirmed candle interaction with the one before it.
            # Because we run this every 5 minutes, we just need to catch the latest event.
            # To be safe against missed runs, we can scan the last 3 candles.
            
            scan_depth = 3
            start_idx = max(1, len(df) - scan_depth)
            
            logger.info(f"Scanning last {len(df) - start_idx} confirmed candles...")

            for i in range(start_idx, len(df)):
                curr_candle = df.iloc[i]
                prev_candle = df.iloc[i-1]
                
                ma9_curr = curr_candle['MA9']
                ma20_curr = curr_candle['MA20']
                ma9_prev = prev_candle['MA9']
                ma20_prev = prev_candle['MA20']
                
                close_price = curr_candle['close']
                timestamp = curr_candle['timestamp']
                
                # Detect Crossover
                is_bullish = detect_bullish_crossover(ma9_prev, ma20_prev, ma9_curr, ma20_curr)
                is_bearish = detect_bearish_crossover(ma9_prev, ma20_prev, ma9_curr, ma20_curr)
                
                if is_bullish or is_bearish:
                    last_alert_time = last_alert_status.get(symbol_name)
                    
                    if last_alert_time != timestamp:
                        if is_bullish:
                            emoji = "🚀"
                            signal = "**BULLISH CROSSOVER CONFIRMED**"
                            desc = "Signal: MA9 crossed ABOVE MA20"
                        else:
                            emoji = "🔴"
                            signal = "**BEARISH CROSSOVER CONFIRMED**"
                            desc = "Signal: MA9 crossed BELOW MA20"
                            
                        message = (
                            f"{emoji} {signal}\n\n"
                            f"Symbol: {symbol_name}\n"
                            f"{desc}\n"
                            f"Price: {close_price}\n"
                            f"Time: {timestamp} (Candle Close)\n"
                        )
                        
                        send_telegram_message(message)
                        logger.info(f"Alert sent for {symbol_name} at {timestamp}")
                        
                        last_alert_status[symbol_name] = timestamp
                    else:
                        logger.info(f"Duplicate alert suppressed for {symbol_name} at {timestamp}")
            
        except RuntimeError as re:
            logger.error(f"RuntimeError processing {symbol_name}: {re}")
            # Check for session issues
            if "Session" in str(re) or "Authorization" in str(re):
                logger.warning("Session appears invalid. Attempting re-login...")
                if client.login():
                    logger.info("Re-login successful. Continuing...")
                else:
                    logger.critical("Re-login failed. Exiting script to force restart.")
                    import sys
                    sys.exit(1)
            else:
                # Other runtime errors (e.g. rate limit), just log and continue
                logger.error(f"API Error (Non-Session): {re}")
                
        except Exception as e:
            logger.error(f"Error processing {symbol_name}: {e}")

    logger.info("Scan completed.")

def run_historical_test(client):
    logger.info("Starting historical crossover test...")
    # Fetch 10 days of data for NIFTY 50 (Token 99926000)
    token = "99926000" 
    exchange = "NSE"
    symbol_name = "NSE:NIFTY"
    
    df = client.get_5min_candles(token, exchange, days=10)
    
    if df is None or len(df) < 20:
        logger.error("Insufficient historical data.")
        return

    # Compute Indicators
    df['MA9'] = calculate_sma(df['close'], 9)
    df['MA20'] = calculate_sma(df['close'], 20)
    
    # Iterate backwards to find LAST crossover
    found = False
    for i in range(len(df) - 2, 20, -1):
        curr = df.iloc[i]
        prev = df.iloc[i-1]
        
        is_bullish = detect_bullish_crossover(
            prev['MA9'], prev['MA20'],
            curr['MA9'], curr['MA20']
        )
        is_bearish = detect_bearish_crossover(
            prev['MA9'], prev['MA20'],
            curr['MA9'], curr['MA20']
        )
        
        if is_bullish or is_bearish:
            timestamp = curr['timestamp']
            close_price = curr['close']
            
            type_str = "BULLISH" if is_bullish else "BEARISH"
            desc_str = "MA9 crossed ABOVE MA20" if is_bullish else "MA9 crossed BELOW MA20"
            
            logger.info(f"Found historical {type_str} crossover at {timestamp}")
            
            message = (
                f"🧪 **[TEST/HISTORICAL] {type_str} CROSSOVER FOUND**\n\n"
                f"Symbol: {symbol_name}\n"
                f"Time: {timestamp} (IST)\n"
                f"Price: {close_price}\n"
                f"{desc_str}\n\n"
                f"This is a test of the alert system based on past data."
            )
            
            send_telegram_message(message)
            found = True
            break
            
    if not found:
        logger.info("No crossover found in the last 10 days.")

def main():
    logger.info("Initializing SmartAPI MA Crossover Alert System...")
    
    # Validate Config
    try:
        Config.validate()
    except ValueError as e:
        logger.error(e)
        return

    # Parse Arguments
    import argparse
    parser = argparse.ArgumentParser(description="SmartAPI MA Crossover Alert")
    parser.add_argument("--once", action="store_true", help="Run the scan once and exit (for cron jobs)")
    parser.add_argument("--test-history", action="store_true", help="Test alert system using historical data")
    args = parser.parse_args()

    # Initialize API Client
    client = SmartApiClient()
    if not client.login():
        logger.error("Failed to login. Exiting.")
        return

    if args.once:
        job(client)
        logger.info("Single run completed. Exiting.")
        return

    if args.test_history:
        run_historical_test(client)
        return

    # Schedule Job
    schedule.every(5).minutes.do(job, client)
    
    logger.info("Scheduler started. Waiting for next run...")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
