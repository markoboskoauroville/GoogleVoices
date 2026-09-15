# DEVELOPMENT, the reasons

## THE DECISIONS

- **The engine is GOOGLE_TTS_STT's, the rule is Marko's.** (15.9.2026) The manifest's rotation sorts keys by
  budget remaining. Marko asked for one key until it expires, then the bottom of the file. The file order is the
  memory; a wall on one model does not move the key until the other model has refused too, because the free
  tier's ten a day is per model. Rejected: a ledger of spend per key (GOOGLE_TTS_STT): it counts what other tools
  spend on the same key wrong, and Marko wanted the file itself to say the order.
- **A per-minute 429 is a wait, not a move.** Google names the retryDelay; up to 30 s is waited once. A move
  on every throttle would walk the whole ring in a minute of talking.
- **The keys live in the app folder.** Marko: "working with a file inside the folder of the application which I
  was basically uploading through file picker. All API keys only live on the local system." `keys/` is gitignored;
  the gates scan the tree for key shapes before a delivery.
- **The probe is the models list, not a TTS call.** Ten a day is too few to spend on a test. The models list
  says valid or refused; it cannot say spent, and the page says so.
- **Families are ours and say so.** Google gives one adjective and a gender. The seven shelves are a grouping of
  Google's words, labelled "grouped here, not by Google"; nothing about age or accent is invented.
- **The cache is the archive.** The same text, way and voice answers from `audio/index.json`; a preview that
  quietly spends a request looks free and is not.
- **Waitress, not the dev server**, on both paths of the console (the tty one and the no-tty one); Flask's own
  server only when waitress is missing, and it says so.

- **The feedback is polled, not pushed.** (15.9.2026) The walk of the ring is written to PROGRESS as it happens and
  the page asks /api/progress every half second while a sentence is out; simpler than a stream on waitress, and the
  console's one thread per request stays free. The estimate is the speech length (words / 2.6) times the median of
  took / seconds over the last eight sentences in the archive, 1.8 before anything is measured, plus two seconds.
- **The voice and the way are the server's memory**, audio/settings.json, so a new browser or the phone's Chrome
  finds them; localStorage only mirrors. The first start is Sulafat (warm), a choice, not Google's.

## THE BUGS

- (15.9.2026, building) The pty test read the key row before the console had printed it, then looked for
  "q quit" through the colour codes. The test now waits for "restart" and strips the escapes.
- (15.9.2026, building) `pkill -f "GoogleVoices/app.py"` matched nothing, because the process's command line
  is `.venv/bin/python app.py 8300`; a second copy started and the port picker took 8301, which is what it is
  for. The test on 8399 then owned `~/.mantra/ports/gvoice` and removed it at exit: the newest copy owns the file.

## THE VERSIONS

| v | date | what |
|---|---|---|
| 1 | 15.9.2026 | born: thirty voices, the ring, the archive, both installers, the four tests, the gates |
| 2 | 15.9.2026 | the player under the text box with the spinner, the estimate and the live walk (/api/progress); HOW as combinable pills in a fold, VOICE in a fold; SAY IT says why when it cannot; the last voice and way on the server, Sulafat the first time |

## WHAT WAS INHERITED
console.py, portpick.py, localguard.py, selfupdate.py from MAHA_TRANSCRIBE_TERMUX_TERMINAL (v5); the request,
the WAV header and the verdict words from GOOGLE_TTS_STT; the six-state classifier's money and retry rules from
KEYRING_TERMUX probes.py; the voice adjectives from Google's Gemini API docs, the genders from Google Cloud's table.
