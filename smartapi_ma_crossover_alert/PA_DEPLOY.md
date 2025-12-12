# Deploying SmartAPI MA Crossover Alert on PythonAnywhere

This guide explains how to deploy your trading bot on [PythonAnywhere](https://www.pythonanywhere.com/).

## Prerequisites

1.  **PythonAnywhere Account**:
    *   **Paid Account (Recommended)**: Required for "Always-on tasks" (continuous monitoring) and to access external APIs if they are not whitelisted.
    *   **Free Account**: Limited to "Scheduled Tasks" (daily/hourly). Not suitable for 5-minute alerts unless you manually run the script in a console (which will eventually time out).

2.  **Angel One SmartAPI Account**: Ensure you have your API Key, Client ID, Password, and TOTP Secret.

## Step 1: Upload Code

1.  Log in to PythonAnywhere.
2.  Go to the **Files** tab.
3.  Create a new directory (e.g., `trading_bot`).
4.  Upload the following files to this directory:
    *   `main.py`
    *   `smartapi_client.py`
    *   `indicators.py`
    *   `telegram_alerts.py`
    *   `utils.py`
    *   `config.py`
    *   `requirements.txt`
    *   `requirements.txt`
    *   **Do NOT upload your local `.env` if it has real keys.** Create a new one on the server securely.

## Step 2: Set Up Virtual Environment

1.  Open a **Bash** console from the Dashboard.
2.  Navigate to your project directory:
    ```bash
    cd trading_bot
    ```
3.  Create a virtual environment:
    ```bash
    mkvirtualenv --python=/usr/bin/python3.10 myenv
    ```
    *(Note: `mkvirtualenv` is a helper on PythonAnywhere. You can also use `python3 -m venv venv`)*
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Step 3: Configure Environment Variables

Ensure your `.env` file is in the same directory as `main.py` and contains:

```ini
SMARTAPI_API_KEY=your_api_key
SMARTAPI_CLIENT_ID=your_client_id
SMARTAPI_PASSWORD=your_password
SMARTAPI_TOTP_SECRET=your_totp_secret
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Step 4: Run the Bot

### Option A: Always-on Task (Paid Account) - **Recommended**

1.  Go to the **Tasks** tab.
2.  Scroll to **Always-on tasks**.
3.  Enter the command to run your script. Make sure to use the python from your virtual environment.
    *   If you used `mkvirtualenv`:
        ```bash
        /home/yourusername/.virtualenvs/myenv/bin/python /home/yourusername/trading_bot/main.py
        ```
    *   Replace `yourusername` with your actual PythonAnywhere username.
4.  Click **Create**.
5.  The task will start and restart automatically if it crashes. Check the log file (icon next to the task) or `app.log` in the file browser for output.

### Option B: Scheduled Task (Free/Paid)

*Note: Free accounts only support Daily tasks. Paid accounts support Hourly.*

1.  Go to the **Tasks** tab.
2.  Under **Scheduled tasks**, set the time (e.g., Daily at 09:00 UTC).
3.  Enter the command with the `--once` flag to run a single scan and exit:
    ```bash
    /home/yourusername/.virtualenvs/myenv/bin/python /home/yourusername/trading_bot/main.py --once
    ```
4.  Click **Create**.

### Option C: Manual Console (Testing)

1.  Open a **Bash** console.
2.  Activate virtualenv: `workon myenv`
3.  Run: `python main.py`
4.  **Warning**: This will stop if you close the browser tab or if the server restarts.

## Troubleshooting

*   **Log Files**: Check `app.log` in your project directory for errors.
*   **Path Issues**: The code has been updated to use absolute paths, so it should find `.env` and `app.log` correctly regardless of how it's run.
*   **SmartAPI Connection**: If you get connection errors on a Free account, it means Angel One API is not whitelisted. You must upgrade to a paid account.
