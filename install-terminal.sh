#!/usr/bin/env bash
# Install GVoices (Google Voices) in a macOS or Linux terminal (not Termux).
# Run with:  curl -fsSL https://raw.githubusercontent.com/markoboskoauroville/GoogleVoices/main/install-terminal.sh | bash
# No token: the repository is public and holds no key. Your keys stay in GoogleVoices/keys/ on this machine.
set -euo pipefail

REPO_URL="https://github.com/markoboskoauroville/GoogleVoices.git"
INSTALL_DIR="${GVOICE_HOME:-$HOME/GoogleVoices}"
BIN_DIR="$HOME/.local/bin"

ok=1
for need in python3 git; do
  if command -v "$need" >/dev/null; then printf '  %-8s ok    %s\n' "$need" "$("$need" --version 2>&1 | head -1)"
  else printf '  %-8s MISSING, install it first\n' "$need"; ok=0; fi
done
python3 -c 'import venv' >/dev/null 2>&1 || { echo "  python3's venv module is missing, install it first"; ok=0; }
[[ $ok == 1 ]] || exit 1

if [[ -d "$INSTALL_DIR/.git" ]]; then
  echo "already cloned, pulling latest..."
  git -C "$INSTALL_DIR" pull -q --ff-only
else
  echo "cloning into $INSTALL_DIR..."
  git clone -q "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
echo "building the virtual environment..."
rm -rf .venv
python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt
chmod +x "$INSTALL_DIR/gvoice" "$INSTALL_DIR/gvoice-update"

# the command: a wrapper written by rename, never a truncation (termux-app.md)
mkdir -p "$BIN_DIR"
rm -f "$BIN_DIR/gvoice.new"
printf '#!/usr/bin/env bash\nexec bash "%s/gvoice" "$@"\n' "$INSTALL_DIR" > "$BIN_DIR/gvoice.new"
chmod +x "$BIN_DIR/gvoice.new"
mv -f "$BIN_DIR/gvoice.new" "$BIN_DIR/gvoice"
cp -f "$BIN_DIR/gvoice" "$BIN_DIR/gvoices.new" && mv -f "$BIN_DIR/gvoices.new" "$BIN_DIR/gvoices"   # both spellings (Marko typed gvoices, 15.9.2026)

echo ""
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo "$BIN_DIR is not on your PATH yet, add this to your shell profile:"
  echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
echo "done."
echo "  gvoice            start it: the page opens in the browser; q quits, u updates, o opens the page again"
echo "  gvoice update     pull the latest version without starting"
echo "  your Google keys: on the page, KEYS tab, choose the file with your keys; they stay in $INSTALL_DIR/keys/"
