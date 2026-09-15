# HANDOVER, the state of GVoices

v12 · https://github.com/markoboskoauroville/GoogleVoices (public) · no artefact, the updater pulls main
The reasons are in DEVELOPMENT.md; what it cost is in LESSONS.md.

## WHAT IT IS
A Flask page, `gvoice`, port 8300: Google's thirty Gemini voices, a sentence to WAV, an archive,
and a keyring manager over `keys/gvoice.keys` in the app folder. Built 15.9.2026 from the hub.

## THE MODEL
`gemini-2.5-flash-preview-tts`, then `gemini-3.1-flash-tts-preview`, walked per key (speech.MODELS).
Never a model name in the page. Both answered on 15.9.2026 with 24 kHz mono PCM.

## THE SCREENS
ONE page: the text, then the player whose first cell is GEN (gen makes it, play plays it; gen stays live when the deck
is empty), the spinner, the estimate and the live walk of the ring above it; then LANGUAGE, SPEED, the HOW fold of
pills that write tags into the text, and the VOICE fold. THE GEAR at the upper right holds ARCHIVE, KEYS and INSTALL
(the two curl lines with COPY, and gvoice / gvoice update). The last voice, language, speed and way live in audio/settings.json; the first start is English, Sulafat, 150 words a
minute. A HOW pill inserts a tag at the cursor (<warmly>); the server turns it into a bracketed direction for Gemini.

## THE DANGEROUS PARTS, NOW
- `ring.to_bottom` rewrites the key file whole (`.new` + rename, chmod 600); the `#` header lines survive.
- `api/say` holds one lock: one sentence at a time, never two keys in flight.
- `localguard` refuses any POST or /api call without the `X-GVoices-Local` header, and any Host that is not loopback.

## THE FILES
See README.md, "The files".

## BUILDING
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, then `.venv/bin/python app.py`.
Tests: `.venv/bin/python tests/run_all.py` (35 checks; `--real` spends one request). Gates: `.venv/bin/python gates/run_gates.py`.

## WHAT HAS NEVER BEEN PROVEN
- Termux: pkg and pip inside Termux, waitress on the phone's python, $PREFIX/bin on PATH, termux-open-url against Chrome.
- The U key against a newer origin/main (no newer version existed yet).
- The page at 390 px (driven in Chrome at desktop width on 15.9.2026, heard through BlackHole; not yet at phone width).
- A key refused for real, and the daily wall for real (no key was driven to its ten).
