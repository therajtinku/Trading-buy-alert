# SmartAPI MA Crossover Alert

This project monitors stock prices using Angel One's SmartAPI and sends Telegram alerts when a bullish Moving Average (MA) crossover occurs on 5-minute candles.

## Features
- **SmartAPI Integration**: Authenticates securely using TOTP.
- **Technical Analysis**: Calculates SMA 9 and SMA 20.
- **Alert System**: Detects Bullish Crossover (MA9 > MA20) and sends Telegram notifications.
- **Scheduler**: Runs automatically every 5 minutes during market hours.
- **Duplicate Prevention**: Ensures alerts are sent only once per crossover event.

## Prerequisites
- Python 3.8+
- Angel One SmartAPI Account
- Telegram Bot Token & Chat ID

## Installation

1. **Clone the repository** (or navigate to the folder):
   ```bash
   cd smartapi_ma_crossover_alert
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   - Rename `.env.example` to `.env`.
   - Edit `.env` and fill in your details:
     ```ini
     SMARTAPI_API_KEY=your_api_key
     SMARTAPI_CLIENT_ID=your_client_id
     SMARTAPI_PASSWORD=your_password
     SMARTAPI_TOTP_SECRET=your_totp_secret
     TELEGRAM_BOT_TOKEN=your_bot_token
     TELEGRAM_CHAT_ID=your_chat_id
     ```

## Usage

Run the main script:
```bash
python main.py
```

The script will:
1. Log in to SmartAPI.
2. Fetch historical data for configured symbols.
3. Check for crossovers.
4. Send alerts if conditions are met.
5. Repeat every 5 minutes.

## Configuration
- **Symbols**: Update the `SYMBOLS_MAP` in `main.py` with the stock tokens you want to monitor. You can find tokens in the Angel One instrument list.

## Logic
- **Bullish Crossover**:
  - Previous Candle: MA9 <= MA20
  - Current Candle: MA9 > MA20
- **Timeframe**: 5 Minutes

## Disclaimer
This software is for educational purposes only. Do not use it for live trading without proper testing and risk management.
