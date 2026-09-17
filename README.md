# delta-ema-alert

Delta EMA Alert is a 24x7 cryptocurrency signal bot for Delta Exchange. It monitors EMA9/EMA50 crossovers on closed hourly candles and sends Telegram notifications (no auto trading).

Files
- `main.py`: entrypoint
- `config.py`: environment configuration
- `exchange.py`: CCXT client fetching OHLCV
- `strategy.py`: EMA calculation and signal evaluation
- `telegram_bot.py`: Telegram notifier and command handler
- `scheduler.py`: scheduling and orchestration
- `state.py`: persistent JSON state
- `logger.py`: logging setup
- `install.sh`: installer and systemd setup
- `systemd/delta-ema.service`: systemd unit file

See `.env.example` for configuration variables.

## Run hourly from 06:30 with cron

GitHub stores the code, but it does not keep this long-running bot process alive. Use an always-on Linux VPS or server. The following setup does not use systemd.

### 1. Connect to the server

```bash
ssh YOUR_USER@YOUR_SERVER_IP
```

### 2. Clone the GitHub repository

```bash
cd ~
git clone https://github.com/pruthwiaffilate-bot/delta-ema-alert.git
cd delta-ema-alert
```

For later code updates, run:

```bash
cd ~/delta-ema-alert
git pull origin main
```

### 3. Install Python and project dependencies

```bash
sudo apt update
sudo apt install -y git python3 python3-venv
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p logs
printf '{}\n' > state.json
```

### 4. Create the environment file

```bash
nano .env
```

Paste the following and replace the two credential values:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
CHECK_INTERVAL=3600
TIMEFRAME=1h
SYMBOLS=ETHUSDT,BTCUSDT,SOLUSDT,XRPUSDT
```

In `nano`, save with `Ctrl+O`, press Enter, then exit with `Ctrl+X`.

### 5. Check the server timezone

Cron uses the server's local timezone. The schedule below means 06:30 in this timezone.

```bash
date
timedatectl
```

### 6. Add the daily 06:30 cron job

```bash
crontab -e
```

Add this line:

```cron
30 6 * * * /usr/bin/flock -n /tmp/delta-ema.lock -c 'cd "$HOME/delta-ema-alert" && "$HOME/delta-ema-alert/.venv/bin/python" main.py >> "$HOME/delta-ema-alert/logs/cron.log" 2>&1'
```

This starts the bot at 06:30, performs a check immediately, and then checks once every hour. `flock` prevents duplicate bot processes.

### 7. Verify the cron job

```bash
crontab -l
```

To start it manually for a test:

```bash
cd ~/delta-ema-alert
flock -n /tmp/delta-ema.lock .venv/bin/python main.py
```

Stop the manual test with `Ctrl+C`. After the scheduled run, view logs with:

```bash
tail -f ~/delta-ema-alert/logs/cron.log
```
# delta-ema-alert