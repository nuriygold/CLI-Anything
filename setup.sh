#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "Setting up CLI-Anything..."

if ! command -v python3.12 >/dev/null 2>&1; then
  echo "python3.12 is missing. Installing with Homebrew..."
  brew install python@3.12
fi

python3.12 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e litellm/agent-harness
python -m pip install -e pm2/agent-harness

echo "Checking PM2 binary..."
if ! command -v pm2 >/dev/null 2>&1; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm is missing. Install Node.js first, then rerun ./setup.sh"
    exit 1
  fi
  echo "Installing PM2 globally..."
  npm install -g pm2
fi


python - <<'PY'
import cli_anything.pm2
print("PM2 adapter import: OK")
PY

echo ""
echo "Setup complete."
echo "Use:"
echo "  cd ~/CLI-Anything"
echo "  source .venv/bin/activate"
echo "  cli"
