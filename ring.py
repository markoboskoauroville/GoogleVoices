"""
ring.py  --  the ring of Google keys, a file inside the app folder.

Marko, 15.9.2026: "You never use parallel processing. You always use only one key until it
expires. And then you put it at the bottom ... a keyring manager inside the app working with a
file inside the folder of the application which I was basically uploading through file picker.
All API keys only live on the local system. Nothing goes to GitHub."

THE FILE  keys/gvoice.keys, chmod 600, gitignored: a name line, a key line, a blank line, the
          shape his notes already have. Lines starting with # survive every rewrite.
THE ORDER The first key in the file is the one in use. A key that refuses (the daily wall, no
          credit, 401, 403) is moved to the bottom of the file and the next one takes over;
          a per-minute throttle is a wait, not a move. The order in the file IS the memory.
THE STATE keys/state.json remembers each key's last verdict and when, for the Keys tab; the
          file itself never holds a verdict, so a hand edit of the ring never breaks it.
NEVER     a key value leaves this module except to the HTTP header. The page sees a name,
          a position ("key 3 of 21"), and a verdict. Not a mask: on Gemini the first six
          characters are the same on every key (MANIFEST keyring.md).
"""

import json
import os
import re
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
KEYDIR = os.path.join(HERE, "keys")
KEYFILE = os.path.join(KEYDIR, "gvoice.keys")
STATEFILE = os.path.join(KEYDIR, "state.json")
GRAVEYARD = os.path.join(KEYDIR, "removed.keys")

# ONE regex for the whole app (apis/gemini.md: two regexes for one idea drift). AQ. is what
# Google issues now, AIza is legacy and still read.
KEY_RE = re.compile(r"(AQ\.[A-Za-z0-9_\-]{20,}|AIza[A-Za-z0-9_\-]{20,})")
MAYBE_RE = re.compile(r"^[A-Za-z0-9_\-\.]{32,}$")      # long, opaque, not a shape we know: reported, never dropped

_lock = threading.Lock()          # around every read-modify-write of the file, never around the network


def _ensure_dir():
    os.makedirs(KEYDIR, exist_ok=True)
    try:
        os.chmod(KEYDIR, 0o700)
    except OSError:
        pass


def _write(path, text):
    _ensure_dir()
    tmp = path + ".new"
    with open(tmp, "w") as f:
        f.write(text)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def parse(text):
    """(entries, unknown, comments): entries are (label, key) in file order; unknown are long
    tokens of no known shape with the line they stood on; comments are the leading # lines."""
    lines = text.splitlines()
    entries, unknown, comments = [], [], []
    seen = set()
    label = None
    for n, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            label = None
            continue
        if line.startswith("#"):
            if not entries and label is None:
                comments.append(line)
            continue
        m = KEY_RE.search(line)
        if m:
            key = m.group(1)
            if key in seen:
                label = None
                continue
            seen.add(key)
            name = label or ("key %d" % (len(entries) + 1))
            entries.append((name, key))
            label = None
            continue
        if MAYBE_RE.match(line):
            unknown.append({"line": n, "length": len(line), "starts": line[:3]})
            label = None
            continue
        label = line if not line.lower().startswith(("http://", "https://")) else label
    return entries, unknown, comments


def load():
    """(label, key) in file order. An absent file is an empty ring, not an error."""
    try:
        with open(KEYFILE) as f:
            entries, _, _ = parse(f.read())
        return entries
    except OSError:
        return []


def _comments():
    try:
        with open(KEYFILE) as f:
            _, _, comments = parse(f.read())
        return comments
    except OSError:
        return []


def _save(entries, comments=None):
    if comments is None:
        comments = _comments()
    head = "".join(c + "\n" for c in comments)
    body = "".join("%s\n%s\n\n" % (l, k) for l, k in entries)
    _write(KEYFILE, (head + "\n" if head else "") + body)


# ---------------------------------------------------------------- the state beside the ring
def _read_state():
    try:
        with open(STATEFILE) as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_state(d):
    _write(STATEFILE, json.dumps(d, indent=1))


def note(key, verdict, detail=""):
    """Remember what a key last answered. Keyed by the key's sha-ish tail, never the key."""
    with _lock:
        d = _read_state()
        d[_fp(key)] = {"verdict": verdict, "detail": detail[:200], "at": int(time.time())}
        _write_state(d)


def _fp(key):
    import hashlib
    return hashlib.sha256(key.encode()).hexdigest()[:12]


# ---------------------------------------------------------------- what the page sees
def public():
    """The ring for the page: position, name, last verdict. No key, no mask."""
    entries = load()
    st = _read_state()
    out = []
    for i, (label, key) in enumerate(entries, 1):
        s = st.get(_fp(key), {})
        out.append({"pos": i, "of": len(entries), "label": label,
                    "verdict": s.get("verdict", "untested"), "detail": s.get("detail", ""), "at": s.get("at")})
    return out


# ---------------------------------------------------------------- the rule: one key, then the bottom
def first():
    """The key in use: the first in the file. None on an empty ring."""
    entries = load()
    return entries[0] if entries else None


def to_bottom(key):
    """The key that refused goes to the bottom of the file; the next one is first now."""
    with _lock:
        entries = load()
        keep = [(l, k) for l, k in entries if k != key]
        gone = [(l, k) for l, k in entries if k == key]
        if not gone:
            return False
        _save(keep + gone)
        return True


def walk():
    """Yield (label, key, pos, of) in the order of use. Reads the file each step, so a
    to_bottom() in between is honoured, and a key is yielded once."""
    seen = set()
    while True:
        entries = load()
        nxt = None
        for i, (l, k) in enumerate(entries, 1):
            if k not in seen:
                nxt = (l, k, i, len(entries))
                break
        if nxt is None:
            return
        seen.add(nxt[1])
        yield nxt


# ---------------------------------------------------------------- import, delete, put back
def import_text(text, source="picked file"):
    """Add every key of a known shape from a note; keep the name beside it; never drop a long
    unknown token silently. Returns counts and the unknown tokens' positions."""
    entries, unknown, _ = parse(text)
    with _lock:
        have = load()
        known = {k for _, k in have}
        names = {l for l, _ in have}
        added = []
        for label, key in entries:
            if key in known:
                continue
            name, n = label, 2
            while name in names:
                name = "%s %d" % (label, n)
                n += 1
            names.add(name)
            known.add(key)
            added.append((name, key))
        if added:
            _save(have + added)
    return {"added": len(added), "skipped": len(entries) - len(added), "unknown": unknown,
            "total": len(have) + len(added), "source": source}


def remove(labels, reason="removed"):
    """Delete by name. Nothing is destroyed: the entry goes to keys/removed.keys with the date."""
    with _lock:
        entries = load()
        keep = [(l, k) for l, k in entries if l not in labels]
        gone = [(l, k) for l, k in entries if l in labels]
        if gone:
            _save(keep)
            _ensure_dir()
            with open(GRAVEYARD, "a") as f:
                for l, k in gone:
                    f.write("# %s, %s\n%s\n%s\n\n" % (reason, time.strftime("%d.%m.%Y %H:%M"), l, k))
            os.chmod(GRAVEYARD, 0o600)
    return {"removed": len(gone), "total": len(keep)}


def removed():
    """The names in the graveyard, newest last."""
    try:
        with open(GRAVEYARD) as f:
            entries, _, _ = parse(f.read())
    except OSError:
        return []
    return [l for l, _ in entries]


def restore(labels):
    """Put back by name: fed through import so a key cannot be doubled."""
    try:
        with open(GRAVEYARD) as f:
            text = f.read()
    except OSError:
        return {"added": 0}
    entries, _, _ = parse(text)
    want = "".join("%s\n%s\n\n" % (l, k) for l, k in entries if l in labels)
    r = import_text(want, source="put back")
    keep = "".join("%s\n%s\n\n" % (l, k) for l, k in entries if l not in labels)
    with _lock:
        _write(GRAVEYARD, keep)
    return r
