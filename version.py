"""
version.py  --  the single number everything else reads (modules/versioning.md).

One whole number: v1, v2, v3, never a dot. Every change is a new number. Kept in its own
file so selfupdate.py can read it without importing app.py.
v1 (15.9.2026): GVoices is born: the thirty Gemini voices, the ring of keys in the app folder, the archive.
v2 (15.9.2026): the player under the text box; a spinner, the elapsed and estimated seconds, the walk of the ring live (/api/progress); HOW as combinable pills in a fold, the voice in a fold.
v3 (15.9.2026): the waveform deck of Maha Transcribe Streamlit (peaks, amber, red playhead, clock, pages, five cells) under the text box and in every archive card.
v4 (15.9.2026): the test copy never opens a browser; a dead page names its port and says to run gvoice; gvoice opens the running copy instead of a second one.
"""

APP_VERSION = 4
