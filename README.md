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

## Run with GitHub Actions

GitHub Actions can run one check per scheduled workflow run. This repository includes [`.github/workflows/hourly-alert.yml`](.github/workflows/hourly-alert.yml), which runs at minute 30 from 06:30 through 23:30 **UTC** and can also be started manually.

### 1. Add repository secrets

In GitHub, open the repository and go to **Settings > Secrets and variables > Actions > New repository secret**. Add:

- `TELEGRAM_TOKEN`: your Telegram bot token
- `CHAT_ID`: your Telegram chat ID

Do not put these values directly in the workflow or commit them to the repository.

### 2. Adjust the schedule if needed

GitHub Actions cron uses UTC. To run at 06:30 in another timezone, convert that time to UTC and edit the cron expression in [`.github/workflows/hourly-alert.yml`](.github/workflows/hourly-alert.yml). Scheduled workflows can occasionally start a few minutes late.

### 3. Run it manually

Open the repository's **Actions** tab, select **Hourly EMA alert**, choose **Run workflow**, and confirm. The workflow performs one check and exits.

The workflow commits `state.json` after each run so the bot remembers the last candle and signal. The workflow requires repository **Contents: write** permission, which is configured in the workflow file. GitHub Actions is not a continuously running process; this one-check workflow is the correct mode for scheduled runs.

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