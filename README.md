# GVoices, Google Voices

One page, one server: Google's thirty prebuilt Gemini voices with Google's own words for each, a
sentence in, a WAV out with a player and a download button, an archive of everything said, and a
keyring manager for the Google keys that live in a file inside this folder. Marko, 15.9.2026: "We are
making Google Voices application. Call it gvoice and make it a global command in the terminal."

The terminal command is `gvoice`. The page is http://127.0.0.1:8300 (the next free port if that one is
taken). Two versions from one repository: Termux on Android and the terminal on macOS or Linux.

## How to install

No token: this repository is public and holds no key. Your keys stay in `GoogleVoices/keys/` on the
machine that runs it, never on GitHub.

Termux (Android):

    curl -fsSL https://raw.githubusercontent.com/markoboskoauroville/GoogleVoices/main/install-termux.sh | bash

macOS or Linux terminal:

    curl -fsSL https://raw.githubusercontent.com/markoboskoauroville/GoogleVoices/main/install-terminal.sh | bash

Then `gvoice` (or `gvoices`, both work). The page opens in the browser (Chrome on the phone). In the terminal: **q** quit,
**o** open the page again, **u** check for an update (shows installed and available, `y` pulls and
restarts on the same port), **r** restart. `gvoice update` pulls without starting. Both install lines
also stand at the top of the page, each with a COPY button.

## The page

- **SAY**: the text, and right under it the player with the feedback: a spinner while Google works, the
  seconds so far against an estimate (the length of the speech times what the last sentences measured),
  the walk of the ring as it happens (which key, which model, waiting, to the bottom, answered), then
  the deck, and what it cost. The deck is the waveform player of Maha Transcribe Streamlit, built once and
  placed under the text box and in every archive card: a black scope with the peaks, the spoken part in
  amber, a red playhead, the clock on the right, pages of ten seconds turned at once, and five cells,
  play, stop, back and next (five seconds), save (the WAV). Two folds under the player, each with its choice on its
  header so they can stay closed: Above the folds, **SPEED**: one of seven paces, very slow (90) to very fast (220 words per
  minute), asked of the voice in the prompt, since Gemini has no rate knob; the audio is never stretched
  afterwards, and the pace that came back is measured (words / seconds) and shown beside the asked one
  (measured 15.9.2026: asked 90, got 106; asked 220, got 219). **HOW**, pills that combine (mood, pace, volume, tone, "as", sounds)
  into a prose direction before the text, editable in your own words; **VOICE**, the filter rows and the
  thirty voices. SAY IT always answers: an empty text, no voice, an empty ring, a refused key each say
  why in the feedback line. The last voice and way are kept in `audio/settings.json` between sessions;
  the first start speaks with Sulafat.
- **ARCHIVE**: everything said, newest first, each with its own deck (save is the download), SAY AGAIN
  (puts the text, the way and the voice back on the SAY tab) and DELETE. The files are
  `audio/<date>_<voice>_<words>.wav`, the list `audio/index.json`. The same text in the same voice
  with the same way is never asked twice: the archive answers, nothing is spent.
- **KEYS**: CHOOSE A KEYS FILE… opens the system file picker; the file is read for keys by shape
  (a name on one line, the key on the next, the shape of Marko's notes), and every new key is
  appended to `keys/gvoice.keys` (chmod 600). Or paste a note. TEST asks Google's models list with
  one key (valid or refused; nothing is spent), TEST ALL does that one key after another. TO THE
  BOTTOM moves a key by hand. DELETE moves it to `keys/removed.keys`, PUT BACK brings it back.
  The page shows a name, a position ("key 3 of 21") and a verdict, never a key or a mask.

## The voices, and the filters

Thirty voices. Two facts per voice are Google's and nothing else is invented:

- **GENDER** (female, male) from Google Cloud's Gemini-TTS and Chirp 3 HD voice table.
- **CHARACTER**, the one adjective of the Gemini API's voice table: Bright, Upbeat, Informative,
  Firm, Excitable, Youthful, Breezy, Easy-going, Breathy, Clear, Smooth, Gravelly, Soft, Even,
  Mature, Forward, Friendly, Casual, Gentle, Lively, Knowledgeable, Warm.
- **FAMILY** is ours, labelled so on the page: those twenty-two words on seven shelves, bright
  (Bright, Upbeat, Lively, Excitable), warm (Warm, Friendly, Gentle, Soft), firm (Firm, Forward,
  Mature, Even), clear (Clear, Informative, Knowledgeable), relaxed (Easy-going, Casual, Breezy),
  textured (Breathy, Gravelly, Smooth), young (Youthful).

Ticks within a row are OR, rows are AND; a voice outside the filter is dimmed, not removed. The
language is the text's own: the model speaks what it is given (Croatian was proven on 15.9.2026).

## The ring of keys

Marko: "You never use parallel processing. You always use only one key until it expires. And then
you put it at the bottom." So: the first key in `keys/gvoice.keys` is the one in use. For each
sentence it is asked with `gemini-2.5-flash-preview-tts`, then `gemini-3.1-flash-tts-preview` (the
free tier gives every key ten requests per model per day). A per-minute limit is a wait (the
retryDelay Google names, 30 s at most) and one more try. The daily wall on both models, no credit,
or a 401/403 sends the key to the bottom of the file and the next one takes over; the order in the
file is the memory, and `keys/state.json` remembers each key's last verdict for the KEYS tab. One
sentence at a time, never two keys in flight.

## The files

    app.py            the Flask routes: /api/state, /api/say, /audio/<file>, /api/archive/<id>, /api/keys/…
    gvoices.html      the page, one file, the AGY look (dark, amber, sand, mono)
    speech.py         one sentence to Google through the ring, the verdicts, PCM to WAV
    ring.py           the key file, import by shape, to the bottom, delete and put back, the state
    voices.py         the thirty voices with Google's gender and character, and our families
    console.py        q o u r, plain lines, waitress (copied from MAHA_TRANSCRIBE_TERMUX_TERMINAL)
    portpick.py       a port that never fails to open; ~/.mantra/ports/gvoice
    localguard.py     127.0.0.1 only: Host, Origin, and the page's own header
    selfupdate.py     the U key: fetch, compare version.py, pull --ff-only
    version.py        one whole number
    gvoice            the launcher (venv on a Mac, Termux's python on the phone; `gvoice update`)
    gvoice-update     pull and refresh, then exit
    install-terminal.sh, install-termux.sh
    tests/run_all.py  the four tests (--real spends one request)
    gates/run_gates.py, gates/RECORD.md

Keys and audio are gitignored. `TAKEOVER.md` brings it back on a fresh machine, `LESSONS.md` is
what it cost to learn, `HANDOVER.md` the state now, `DEVELOPMENT.md` the reasons.

## Heard, not only served

On 15.9.2026 the page was driven in Marko's own Chrome: a sentence typed, SAY IT pressed, the spinner and
the walk watched, the voice arrived in 6 s; then the archive's deck was played while ffmpeg recorded the
Mac's BlackHole output: silence until the press, then the voice at −21.8 dB peak with the sentence's own
pauses. The muted colours he saw were Dark Reader recolouring the page; the page now carries
`<meta name="darkreader-lock">`, and the deck's glyphs are inline SVG, which no extension repaints.

## No sound?

The page plays through the Mac's current sound output. On 15.9.2026 that output was BlackHole 2ch, a virtual
cable that is silent unless something records it; every page was mute, not only this one. Sound Settings, or
`SwitchAudioSource -s "MacBook Pro Speakers"`, puts it back on speakers. `afplay audio/<file>.wav` plays a
said file outside the browser and settles whether the page or the output is the question.
