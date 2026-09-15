#!/usr/bin/env bash

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
RC="${ZSHRC:-$HOME/.zshrc}"
SETTINGS="$DEST/settings.json"
ALIAS="alias claude='command claude --system-prompt-file \"$DEST/SYSTEM.md\"'"

command -v jq >/dev/null || { echo "faltando: jq" >&2; exit 1; }

mkdir -p "$DEST"

for name in skills output-styles SYSTEM.md; do
  rm -rf "${DEST:?}/$name"
  cp -R "$SRC/$name" "$DEST/$name"
  echo "+ $name"
done

[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
jq -s '.[0] * .[1]' "$SETTINGS" "$SRC/settings.json" > "$SETTINGS.tmp"
mv "$SETTINGS.tmp" "$SETTINGS"
echo "+ settings.json"

touch "$RC"
grep -qF "$ALIAS" "$RC" || printf '\n%s\n' "$ALIAS" >> "$RC"
echo "+ alias claude ($RC)"
