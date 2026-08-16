#!/bin/zsh
set -e
ROOT="$HOME/investment_ticker"
mkdir -p "$HOME/Library/LaunchAgents" "$ROOT/logs" "$ROOT/data"
for src in "$ROOT"/launchd/*.plist; do
  name=$(basename "$src")
  sed "s|REPLACE_USERNAME|$USER|g" "$src" > "$HOME/Library/LaunchAgents/$name"
  launchctl bootout "gui/$(id -u)" "$HOME/Library/LaunchAgents/$name" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/$name"
done
echo "launchd jobs installed."
