# TAKEOVER, bringing GVoices back on a fresh machine

1. macOS or Linux: `curl -fsSL https://raw.githubusercontent.com/markoboskoauroville/GoogleVoices/main/install-terminal.sh | bash`
   (clones to `~/GoogleVoices`, builds `.venv`, writes `~/.local/bin/gvoice`). Termux: the `install-termux.sh` line.
   On Marko's Mac the working copy is `~/Developer/GoogleVoices` and `~/.local/bin/gvoice` execs its `gvoice`.
2. `gvoice`. The page opens. KEYS tab, CHOOSE A KEYS FILE…, pick the note with the Google keys (on the Mac it is
   `~/Downloads/API/VOICES_gemini-free-tier-api.txt`, a name on one line and the key on the next). The keys are
   appended to `keys/gvoice.keys`; nothing else on the machine is touched.
3. SAY tab: a sentence, a voice, SAY IT. The first key in the file answers.
4. Checks: `.venv/bin/python tests/run_all.py` (35 checks green on 15.9.2026), `.venv/bin/python gates/run_gates.py`.
5. Ports: 8300, the next fifteen, then any (`~/.mantra/ports/gvoice` holds the live one). The row is in
   MANTRA_MANIFEST `modules/ports.md` §2.
