# MEMORY, read first

- GVoices = `gvoice`, port 8300, repository GoogleVoices (public). Keys in `keys/gvoice.keys`, never committed.
- The ring rule is Marko's of 15.9.2026: one key, the first in the file, until it refuses; then the bottom.
- Two models per key, ten free requests per model per day; the probe never spends one.
- The page follows the AGY look; the install lines are at the top of the page on Marko's word.
- Run `tests/run_all.py` before every push, `gates/run_gates.py` before every delivery; bump `version.py` on every change.
