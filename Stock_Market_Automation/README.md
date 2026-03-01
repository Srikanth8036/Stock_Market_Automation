# Stock Market Automation Bot 📈

This is a fully automated trading bot designed for the Indian Stock Market (NIFTY, BANKNIFTY) using Angel One's SmartAPI.

Even if you don't know Python, you can run this bot by following the steps below.

---

## ✅ Prerequisites

1.  **Angel One Account**: You need an active trading account.
2.  **SmartAPI Access**: Go to [smartapi.angelbroking.com](https://smartapi.angelbroking.com/), sign up, and create an app to get:
    *   `API Key`
    *   `Client ID` (Your Angel One User ID)
    *   `Password` (Your Angel One Login PIN/Password)
    *   `TOTP Secret` (Enable TOTP in Angel One app security settings and copy the key)
3.  **Telegram Bot**:
    *   Open Telegram and search for `@BotFather`.
    *   Send `/newbot` and follow instructions to get the `BOT TOKEN`.
    *   Search for `@userinfobot` to get your `CHAT ID`.

---

## 🚀 Setup Guide (Step-by-Step)

### 1. Configure Your Credentials
1.  In this folder, you will find a file named `.env.example`.
2.  **Rename** it to just `.env` (remove the `.example` part).
3.  Open `.env` with Notepad or any text editor.
4.  Fill in your details like this:

    ```ini
    SMART_API_KEY=YourApiKeyFromSmartApiWebsite
    SMART_CLIENT_ID=A123456
    SMART_PASSWORD=1234
    SMART_TOTP_SECRET=JBSWY3DPEHPK3PXP
    TELEGRAM_BOT_TOKEN=123456789:ABCDefGhIjkLmNoPqRsTuVwXyZ
    TELEGRAM_CHAT_ID=987654321
    ```
5.  Save the file.

### 2. Install & Run
1.  Double-click the **`run.bat`** file in this folder.
2.  It will automatically install everything and start the bot.
3.  Two windows will open:
    *   **Backend Console**: Shows logs like "Market analysis started..." or "Order Placed".
    *   **Frontend Dashboard**: Opens in your browser to show live trades and profit.

---

## ❓ How It Works (The Flow)

You don't need to do anything manually once it's running.

1.  **Start Time**: You can start the bot (run `run.bat`) anytime before market opens (e.g., 9:00 AM).
2.  **Automatic Scheduling**: The bot has an internal clock (Scheduler). It waits until **9:15 AM** automatically.
3.  **Market Hours (9:15 AM - 3:30 PM)**:
    *   Every **1 minute**, the bot wakes up.
    *   It connects to Angel One and checks the current price of NIFTY/BANKNIFTY.
    *   It checks your strategy (e.g., "Is price near support?").
4.  **Trade Execution**:
    *   If a **Buy Signal** appears, it automatically places an order on your Angel One account.
    *   It sends a **Telegram Message** to your phone: "🚀 ENTERED CALL OPTION".
5.  **Exit**:
    *   It monitors the trade every minute.
    *   If **Target** or **Stop Loss** is hit, it sells the position automatically.
    *   It sends a **Telegram Message**: "🛑 CLOSED TRADE. PROFIT: 500".
6.  **End of Day**:
    *   The bot stops trading automatically at 3:30 PM.
    *   You can close the black console windows to stop it completely.

---

## 🛠 Technical Details (For Developers)

### Why do we need a Database?
Even though we use a Real API, we use a local database (`trading.db`) to:
1.  **Track Strategy Performance**: Broker APIs don't tell you *why* you took a trade (e.g., "VWAP Strategy"). We record that locally.
2.  **Calculate Custom P&L**: We want to see our bot's specific win rate, distinct from your manual trades.
3.  **State Management**: If the internet disconnects or the bot restarts, the database remembers "I am currently in a trade" so it can resume managing it.

### File Structure
*   `backend/config.py`: Loads your `.env` credentials.
*   `backend/scheduler.py`: The timer that runs the `analyze_market` function every minute.
*   `backend/strategy.py`: The brain. Decides when to buy/sell and calls the API.
*   `backend/smart_api.py`: The connector. Talks to Angel One servers.

### Switching to Real Money
Currently, the code in `backend/strategy.py` has the "Real Order" line commented out for safety.
To enable real trading:
1.  Open `backend/strategy.py`.
2.  Search for `# client.place_order`.
3.  Uncomment those lines in `execute_trade` and `manage_trade` functions.

---

**⚠️ Disclaimer**: Stock market trading involves risk. Use this bot at your own risk. Always test with paper trading (mock mode) first.
