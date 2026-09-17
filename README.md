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

## Run hourly from 06:30

GitHub stores the code, but it does not keep this long-running bot process alive. Clone the repository onto a Linux VPS or other always-on server, then install and configure it there.

Create `/workspaces/delta-ema-alert/.env` with your credentials:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
CHECK_INTERVAL=3600
TIMEFRAME=1h
SYMBOLS=ETHUSDT,BTCUSDT,SOLUSDT,XRPUSDT
```

Install dependencies:

```bash
cd /workspaces/delta-ema-alert
./install.sh
```

To run without systemd, disable the installed service and add a cron job:

```bash
sudo systemctl disable --now delta-ema.service
crontab -e
```

Add this line:

```cron
30 6 * * * /usr/bin/flock -n /tmp/delta-ema.lock -c 'cd /workspaces/delta-ema-alert && /workspaces/delta-ema-alert/.venv/bin/python main.py >> /workspaces/delta-ema-alert/logs/cron.log 2>&1'
```

The process starts every day at 06:30, performs a check immediately, then checks once every hour. `flock` prevents a second copy from starting if the previous process is still running. Cron uses the server's local timezone; check it with `date`.
# delta-ema-alert