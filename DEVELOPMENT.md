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

- **Not Streamlit.** (15.9.2026) Marko asked whether the app should be a Streamlit app on macOS and Termux. No: the
  house floor (never-back-to-zero.md) is one HTML page on a small Flask server, which is what runs on a phone; Streamlit
  is a heavy install on Termux and slow to start there, and its waveform player was a custom HTML component anyway,
  which is exactly what the deck here is. The same deck, no Streamlit round trip under it.
- **The deck is one function, Deck(host).** Built once and placed under the text box and in every archive card
  (design language 2: the same player is the same component). Pages are even divisions under ten seconds and the
  turn is instant (rule 8, nothing the eye has to follow).

- **The pace is asked, never stretched.** (15.9.2026) Gemini TTS has no rate parameter; "Speak at a slow pace, about
  110 words per minute" in the prompt is obeyed within about fifteen percent (asked 90 got 106, asked 220 got 219).
  A post-hoc time stretch would keep the exact number and add artefacts; Marko asked for the voice's own rhythm at the
  pace, so the number is a request and the measured pace is shown beside it, honestly.

- **The language is asked, not detected.** (15.9.2026) Left alone the model guesses the language from the text, and a
  Croatian sentence holding an English name can arrive with an English accent. "Speak in Croatian (hrvatski), with a
  native Croatian accent" in the preamble settles it. The language belongs to the model, not to the voice
  (gemini-speech.md), so all thirty voices offer both.
- **A tag is `<warmly>` in the text and `[warmly]` in the prompt.** (15.9.2026) Marko types the angle brackets because
  a pill inserts them at his cursor; Gemini obeys square-bracket stage directions when the preamble says what they
  are, and that note is added only when the text actually holds a tag. Tags are stripped before the words are counted,
  so the estimate is not thrown by them. Proven: three tags, 18 words, 152 words a minute measured. And the tags are
  heard, not only obeyed on paper: "<cheerfully> Good morning Marko. <whispering> And now the secret part." came back
  with its first half at −14.0 dB mean and its whispered half at −17.0 dB, three decibels quieter, in one take.

- **GEN is a cell of the deck, not a button above it.** (15.9.2026) Marko: "to generate the voice user needs to simply
  press the play button ... gen button is the first button in the play. We generate, play plays." One row of six cells
  now, gen first, and the big SAY IT is gone. gen keeps its colour and its click while the deck is idle, which is the
  Streamlit deck's own lesson written the other way round: there, play had to stay live because play was what started
  the making; here that job is gen's, so gen is the exception to the idle dimming and play is not.
- **A canvas measured while hidden has no width.** (15.9.2026) The archive's decks are built inside the gear's panel,
  which is display:none until the gear is pressed; their canvases came out zero wide. Every view change now redraws
  the decks it just revealed, on the next tick.

## THE BUGS

- (15.9.2026) "The app is not working, I don't get any voices." Driven in his Chrome: it worked; the voice arrived in
  6 s and the archive's deck played through BlackHole. What he saw was Dark Reader repainting the page: the amber
  tab grey, the CSS-border triangles as squares. `<meta name="darkreader-lock">` and SVG glyphs now; the earlier
  version had also demanded a chosen voice before SAY IT would answer, which v2 already replaced with a reason line.

- (15.9.2026, building) The pty test read the key row before the console had printed it, then looked for
  "q quit" through the colour codes. The test now waits for "restart" and strips the escapes.
- (15.9.2026, building) `pkill -f "GoogleVoices/app.py"` matched nothing, because the process's command line
  is `.venv/bin/python app.py 8300`; a second copy started and the port picker took 8301, which is what it is
  for. The test on 8399 then owned `~/.mantra/ports/gvoice` and removed it at exit: the newest copy owns the file.

## THE VERSIONS

| v | date | what |
|---|---|---|
| 1 | 15.9.2026 | born: thirty voices, the ring, the archive, both installers, the four tests, the gates |
| 12 | 15.9.2026 | the gear at the upper right holds the archive, the keys and the install lines; GEN is the first cell of the deck, SAY IT is gone |
| 11 | 15.9.2026 | the tags measured in the audio (−14.0 dB cheerful, −17.0 dB whispered) |
| 10 | 15.9.2026 | the documents for the language and the tags |
| 9 | 15.9.2026 | tags in the text: a HOW pill inserts <its words> at the cursor, the model reads them as bracketed directions |
| 8 | 15.9.2026 | LANGUAGE, English or Croatian, asked of the voice; remembered and shown |
| 7 | 15.9.2026 | the documents for the speed |
| 6 | 15.9.2026 | SPEED asked in words per minute, the pace that came back measured and shown; the estimate uses it |
| 5 | 15.9.2026 | gvoices as a second spelling; README on a Mac whose output is BlackHole |
| 4 | 15.9.2026 | the test copy opens no browser and touches no registry; a dead page names its port; gvoice opens the running copy |
| 3 | 15.9.2026 | the waveform deck of Maha Transcribe Streamlit under the text box and in every archive card; darkreader-lock; SVG glyphs; driven in Chrome and heard through BlackHole |
| 2 | 15.9.2026 | the player under the text box with the spinner, the estimate and the live walk (/api/progress); HOW as combinable pills in a fold, VOICE in a fold; SAY IT says why when it cannot; the last voice and way on the server, Sulafat the first time |

## WHAT WAS INHERITED
console.py, portpick.py, localguard.py, selfupdate.py from MAHA_TRANSCRIBE_TERMUX_TERMINAL (v5); the request,
the WAV header and the verdict words from GOOGLE_TTS_STT; the six-state classifier's money and retry rules from
KEYRING_TERMUX probes.py; the voice adjectives from Google's Gemini API docs, the genders from Google Cloud's table.
