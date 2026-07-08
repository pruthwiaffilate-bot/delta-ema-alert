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
# delta-ema-alert