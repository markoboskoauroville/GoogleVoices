"""
voices.py  --  the thirty prebuilt Gemini voices and what Google says about them.

Two facts per voice come from Google, nothing else is invented (GOOGLE_TTS_STT's rule, "a blank
is a fact, a guess is not"):
  - the GENDER, from Google Cloud's Chirp 3 HD / Gemini-TTS voice table
    (https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd), read 15.9.2026;
  - the CHARACTER, the one adjective of the Gemini API's voice table
    (https://ai.google.dev/gemini-api/docs/speech-generation), read 15.9.2026.
The FAMILY is ours: Google's twenty-two adjectives sorted into seven shelves, so that a filter
button means something ("warm" and "gentle" and "soft" are one shelf). The page says so.
"""

# name, gender (Google Cloud), character (Google AI)
VOICES = [
    ("Zephyr",        "female", "Bright"),
    ("Puck",          "male",   "Upbeat"),
    ("Charon",        "male",   "Informative"),
    ("Kore",          "female", "Firm"),
    ("Fenrir",        "male",   "Excitable"),
    ("Leda",          "female", "Youthful"),
    ("Orus",          "male",   "Firm"),
    ("Aoede",         "female", "Breezy"),
    ("Callirrhoe",    "female", "Easy-going"),
    ("Autonoe",       "female", "Bright"),
    ("Enceladus",     "male",   "Breathy"),
    ("Iapetus",       "male",   "Clear"),
    ("Umbriel",       "male",   "Easy-going"),
    ("Algieba",       "male",   "Smooth"),
    ("Despina",       "female", "Smooth"),
    ("Erinome",       "female", "Clear"),
    ("Algenib",       "male",   "Gravelly"),
    ("Rasalgethi",    "male",   "Informative"),
    ("Laomedeia",     "female", "Upbeat"),
    ("Achernar",      "female", "Soft"),
    ("Alnilam",       "male",   "Firm"),
    ("Schedar",       "male",   "Even"),
    ("Gacrux",        "female", "Mature"),
    ("Pulcherrima",   "female", "Forward"),
    ("Achird",        "male",   "Friendly"),
    ("Zubenelgenubi", "male",   "Casual"),
    ("Vindemiatrix",  "female", "Gentle"),
    ("Sadachbia",     "male",   "Lively"),
    ("Sadaltager",    "male",   "Knowledgeable"),
    ("Sulafat",       "female", "Warm"),
]

# our shelves for Google's adjectives (the page labels them "grouped here, not by Google")
FAMILIES = [
    ("bright",   ["Bright", "Upbeat", "Lively", "Excitable"]),
    ("warm",     ["Warm", "Friendly", "Gentle", "Soft"]),
    ("firm",     ["Firm", "Forward", "Mature", "Even"]),
    ("clear",    ["Clear", "Informative", "Knowledgeable"]),
    ("relaxed",  ["Easy-going", "Casual", "Breezy"]),
    ("textured", ["Breathy", "Gravelly", "Smooth"]),
    ("young",    ["Youthful"]),
]

_FAMILY_OF = {adj: fam for fam, adjs in FAMILIES for adj in adjs}


def catalogue():
    """Every voice as a dict: name, gender, character, family."""
    out = []
    for name, gender, character in VOICES:
        out.append({"name": name, "gender": gender, "character": character,
                    "family": _FAMILY_OF.get(character, "other")})
    return out


NAMES = [v[0] for v in VOICES]


def is_voice(name):
    return name in NAMES


def facets():
    """What the filter rows offer: genders, characters (Google's words), families (ours)."""
    return {
        "gender": ["female", "male"],
        "character": sorted({v[2] for v in VOICES}),
        "family": [f for f, _ in FAMILIES],
    }
