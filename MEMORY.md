# MEMORY, read first

- GVoices = `gvoice`, port 8300, repository GoogleVoices (public). Keys in `keys/gvoice.keys`, never committed.
- The ring rule is Marko's of 15.9.2026: one key, the first in the file, until it refuses; then the bottom.
- Two models per key, ten free requests per model per day; the probe never spends one.
- One page: the text and its player (gen is the first cell, play the second); the gear at the upper right holds the
  archive, the keys and the install lines.
- The page follows the AGY look; the install lines are at the top of the page on Marko's word.
- Gemini has no rate, language or emotion parameter: the pace, the language and the tags are all asked in the prompt,
  never applied to the audio afterwards. A tag is <warmly> in his text and [warmly] in the prompt.
- Run `tests/run_all.py` before every push, `gates/run_gates.py` before every delivery; bump `version.py` on every change.
