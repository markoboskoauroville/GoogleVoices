#!/data/data/com.termux/files/usr/bin/bash
# Install GVoices (Google Voices) in Termux.
# Run with:  curl -fsSL https://raw.githubusercontent.com/markoboskoauroville/GoogleVoices/main/install-termux.sh | bash
# No token: the repository is public and holds no key. Your keys stay in GoogleVoices/keys/ on this phone.
set -euo pipefail

REPO_URL="https://github.com/markoboskoauroville/GoogleVoices.git"
INSTALL_DIR="$HOME/GoogleVoices"

missing=""
for need in python git; do
  if command -v "$need" >/dev/null; then printf '  %-8s ok    %s\n' "$need" "$("$need" --version 2>&1 | head -1)"
  else printf '  %-8s missing, installing\n' "$need"; missing="$missing $need"; fi
done
if [[ -n "$missing" ]]; then pkg update -y; pkg install -y $missing; fi

if [[ -d "$INSTALL_DIR/.git" ]]; then
  echo "already cloned, pulling latest..."
  git -C "$INSTALL_DIR" pull -q --ff-only
else
  echo "cloning into $INSTALL_DIR..."
  git clone -q "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
echo "installing flask and waitress (no venv on Termux, termux-app.md)..."
pip install --quiet -r requirements.txt
chmod +x "$INSTALL_DIR/gvoice" "$INSTALL_DIR/gvoice-update"

# the command in $PREFIX/bin AND ~/.local/bin, a wrapper written by rename (termux-app.md)
for BIN_DIR in "$PREFIX/bin" "$HOME/.local/bin"; do
  mkdir -p "$BIN_DIR"
  rm -f "$BIN_DIR/gvoice.new"
  printf '#!/data/data/com.termux/files/usr/bin/bash\nexec bash "%s/gvoice" "$@"\n' "$INSTALL_DIR" > "$BIN_DIR/gvoice.new"
  chmod +x "$BIN_DIR/gvoice.new"
  mv -f "$BIN_DIR/gvoice.new" "$BIN_DIR/gvoice"
done

echo ""
echo "done. anywhere in Termux:"
echo "  gvoice            start it: the page opens in Chrome; q quits, u updates, o opens the page again"
echo "  gvoice update     pull the latest version without starting"
echo "  your Google keys: on the page, KEYS tab, choose the file with your keys; they stay in $INSTALL_DIR/keys/"
echo ""
echo "for the page to open by itself, install the Termux:API app from F-Droid and run:  pkg install termux-api"
