# 🚀 Deploying to PythonAnywhere (Hacker Plan)

This guide walks you through deploying your **SmartAPI MA Crossover Alert** bot to PythonAnywhere using the **Hacker Plan ($5/month)**. 

> [!IMPORTANT]
> The **Hacker Plan** is required to run "Always-on" tasks. The free plan cannot run this bot continuously every 5 minutes reliably.

---

## 📋 Prerequisites

1.  **PythonAnywhere Account**: Upgrade to the [Hacker Plan](https://www.pythonanywhere.com/pricing/).
2.  **Angel One Details**: API Key, Client ID, PIN, TOTP Secret.
3.  **Telegram Details**: Bot Token, Chat ID.

---

## 🛠️ Step 1: Upload Files

1.  Log in to your PythonAnywhere Dashboard.
2.  Go to the **Files** tab.
3.  Create a new directory named `trading_bot`.
4.  Inside `trading_bot`, upload the following files from your local computer:
    *   `main.py`
    *   `smartapi_client.py`
    *   `indicators.py`
    *   `telegram_alerts.py`
    *   `utils.py`
    *   `config.py`
    *   `requirements.txt`
    *   (Optional) `logs` folder (empty)

> [!WARNING]
> **Do NOT upload your local `.env` file.** It contains sensitive passwords. You will create it securely on the server in the next step.

---

## 🔐 Step 2: Configure Secrets

1.  In the **Files** tab (inside `trading_bot` directory), create a **New File** named `.env`.
2.  Paste your secrets into the editor:
    ```ini
    SMARTAPI_API_KEY=your_actual_api_key_here
    SMARTAPI_CLIENT_ID=your_client_id_here
    SMARTAPI_MPIN=your_mpin_here
    SMARTAPI_TOTP_SECRET=your_totp_secret_here
    
    TELEGRAM_BOT_TOKEN=your_bot_token_here
    TELEGRAM_CHAT_ID=your_chat_id_here
    ```
3.  **Save** the file.

---

## 📦 Step 3: Install Dependencies

1.  Open a **Bash** console from the Dashboard (or from the "Consoles" tab).
2.  Run the following commands one by one:

    **Navigate to folder:**
    ```bash
    cd trading_bot
    ```

    **Create Virtual Environment:**
    ```bash
    mkvirtualenv --python=/usr/bin/python3.10 myenv
    ```
    *(The console prompt should change to `(myenv) $`)*

    **Install Libraries:**
    ```bash
    pip install -r requirements.txt
    ```

    **Verify Installation:**
    ```bash
    python -c "import pandas; import SmartApi; print('Setup Good!')"
    ```
    *(If it prints "Setup Good!", you are ready.)*

---

## ⚡ Step 4: Set Up "Always-on" Task

1.  Go to the **Tasks** tab on your Dashboard.
2.  Scroll down to the **Always-on tasks** section.
3.  In the "Command" box, enter the following (replace `yourusername` with your *actual* PythonAnywhere username):

    ```bash
    /home/yourusername/.virtualenvs/myenv/bin/python /home/yourusername/trading_bot/main.py
    ```

    > [!TIP]
    > You can find the exact path to your python executable by running `which python` inside your virtualenv console.

4.  Click **Create**.

---

## 👀 Step 5: Verify & Monitor

1.  The task state should change to **Running**.
2.  Click the **Log** icon (📄) next to the task to see the output.
    *   You should see logs like: `Initializing SmartAPI...`, `SmartAPI Login Successful`, `Scheduler started...`.
3.  **That's it!** Your bot handles 5-minute scans automatically.
    *   **Auto-Healing**: If the bot crashes or the server restarts, PythonAnywhere will automatically restart it.
    *   **Auto-Login**: The code handles daily session expiry by re-logging in automatically.

---

## ❓ Troubleshooting

*   **"ModuleNotFoundError"**: You probably forgot to install requirements or didn't use the full path to the virtualenv python in the Task command.
*   **"SmartAPI Login Failed"**: Check your `.env` file credentials.
*   **Bot stops working after 24h**: The code attempts to auto-relogin. Check the task logs to see if it failed. If it says "Re-login failed", the task will restart itself to try again cleanly.
