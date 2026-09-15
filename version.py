"""
version.py  --  the single number everything else reads (modules/versioning.md).

One whole number: v1, v2, v3, never a dot. Every change is a new number. Kept in its own
file so selfupdate.py can read it without importing app.py.
v1 (15.9.2026): GVoices is born: the thirty Gemini voices, the ring of keys in the app folder, the archive.
v2 (15.9.2026): the player under the text box; a spinner, the elapsed and estimated seconds, the walk of the ring live (/api/progress); HOW as combinable pills in a fold, the voice in a fold.
v3 (15.9.2026): the waveform deck of Maha Transcribe Streamlit (peaks, amber, red playhead, clock, pages, five cells) under the text box and in every archive card.
v4 (15.9.2026): the test copy never opens a browser; a dead page names its port and says to run gvoice; gvoice opens the running copy instead of a second one.
v5 (15.9.2026): gvoices as a second spelling of the command; README on a Mac whose output is BlackHole.
v6 (15.9.2026): SPEED before generating, asked of the voice in words per minute, the pace that came back measured and shown.
v7 (15.9.2026): the documents for the speed.
v8 (15.9.2026): LANGUAGE, English or Croatian, asked of the voice in the prompt, remembered and shown.
v9 (15.9.2026): tags in the text: a HOW pill inserts <its words> at the cursor; the model reads them as directions.
v10 (15.9.2026): the documents for the language and the tags.
v11 (15.9.2026): the tags measured in the audio.
v12 (15.9.2026): the gear at the upper right holds the archive, the keys and the install lines; GEN is the first cell of the deck and SAY IT is gone.
"""

APP_VERSION = 12
