#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=python3.11
VENV_DIR="$PROJECT_DIR/.venv"

echo "Creating virtual environment with $PYTHON"
if ! command -v $PYTHON >/dev/null 2>&1; then
  echo "$PYTHON not found. Please install Python 3.11." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  $PYTHON -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

mkdir -p "$PROJECT_DIR/logs"

if [ ! -f "$PROJECT_DIR/state.json" ]; then
  cat > "$PROJECT_DIR/state.json" <<EOF
{}
EOF
fi

echo "Copying systemd service and enabling"
SERVICE_FILE="/etc/systemd/system/delta-ema.service"
sudo cp "$PROJECT_DIR/systemd/delta-ema.service" "$SERVICE_FILE"
sudo systemctl daemon-reload
sudo systemctl enable delta-ema.service
sudo systemctl restart delta-ema.service

echo "Install complete. Use 'sudo journalctl -u delta-ema.service -f' to follow logs."
