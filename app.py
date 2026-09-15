"""
GVoices  --  Google Voices
Mantra Productions, 15.9.2026

One Flask server, one page. The thirty prebuilt Gemini voices with Google's own words for each
(gender, character), filter buttons, a sentence in, a WAV out with a player and a download
button, an archive of everything said, and a keyring manager for the Google keys that live in a
file inside this folder, picked with the file picker.

Copied file by file from MAHA_TRANSCRIBE_TERMUX_TERMINAL, the newest app with the floor
(never-back-to-zero.md): console.py (q o u r), portpick.py, localguard.py, selfupdate.py,
version.py. The engine is GOOGLE_TTS_STT's, the ring rule is Marko's of 15.9.2026 (ring.py).

Run:  python3 app.py [port]      then the page opens at http://127.0.0.1:8300
"""

import json
import os
import re
import sys
import threading
import time

from flask import Flask, Response, jsonify, request, send_from_directory

import console as term
import localguard
import portpick
import ring
import selfupdate
import speech
import version
import voices

APP_VERSION = version.APP_VERSION
DEFAULT_PORT = 8300
COMMAND = "gvoice"
REPO = "https://github.com/markoboskoauroville/GoogleVoices"

HERE = os.path.dirname(os.path.abspath(__file__))
APP_FILE = "gvoices.html"
AUDIO_DIR = os.path.join(HERE, "audio")
INDEX = os.path.join(AUDIO_DIR, "index.json")
SETTINGS = os.path.join(AUDIO_DIR, "settings.json")   # the last voice and way, kept between sessions (Marko, 15.9.2026)
DEFAULT_VOICE = "Sulafat"                              # the first start's voice: warm, female, in Google's words

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

START_TIME = time.time()
REQUEST_COUNT = 0
SAID_COUNT = 0
LIVE_PORT = DEFAULT_PORT          # the port ACTUALLY bound; localguard checks the Host header against it
_say_lock = threading.Lock()      # one sentence at a time: never two keys in flight (Marko: no parallel)
_index_lock = threading.Lock()
# THE PROGRESS (Marko, 15.9.2026: "verbose feedback what's going on with the spinner so I know it's working and the
# time estimate"): the walk of the ring as it happens, polled by the page every half second while a sentence is asked.
PROGRESS = {"busy": False, "started": None, "lines": [], "text": "", "voice": ""}


def progress_line(s):
    PROGRESS["lines"].append({"at": time.time(), "text": s})


@app.before_request
def gate():
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    return localguard.check(LIVE_PORT)


@app.after_request
def no_store(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


# ---------------------------------------------------------------- the page
@app.route("/")
def index():
    return send_from_directory(HERE, APP_FILE)


FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           '<rect width="64" height="64" rx="12" fill="#0B0D10"/>'
           '<path d="M14 32c0-10 8-18 18-18s18 8 18 18" fill="none" stroke="#F59E0B" stroke-width="6" stroke-linecap="round"/>'
           '<rect x="26" y="30" width="12" height="20" rx="6" fill="#F59E0B"/></svg>')


@app.route("/favicon.svg")
@app.route("/favicon.ico")
def favicon():
    return Response(FAVICON, mimetype="image/svg+xml")


@app.route("/api/state")
def api_state():
    return jsonify({
        "version": APP_VERSION, "port": LIVE_PORT, "command": COMMAND, "repo": REPO,
        "install": {
            "termux": "curl -fsSL https://raw.githubusercontent.com/markoboskoauroville/GoogleVoices/main/install-termux.sh | bash",
            "mac": "curl -fsSL https://raw.githubusercontent.com/markoboskoauroville/GoogleVoices/main/install-terminal.sh | bash",
        },
        "voices": voices.catalogue(), "facets": voices.facets(), "models": speech.MODELS, "speeds": speech.SPEEDS,
        "ring": ring.public(), "removed": ring.removed(), "archive": read_index(), "settings": read_settings(),
    })


# ---------------------------------------------------------------- the settings
def read_settings():
    try:
        with open(SETTINGS) as f:
            d = json.load(f)
        if not isinstance(d, dict):
            d = {}
    except (OSError, ValueError):
        d = {}
    if not voices.is_voice(d.get("voice") or ""):
        d["voice"] = DEFAULT_VOICE
    d.setdefault("style", "")
    try:
        d["speed"] = max(60, min(300, int(d.get("speed") or 150)))
    except (TypeError, ValueError):
        d["speed"] = 150
    return d


def write_settings(d):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    tmp = SETTINGS + ".new"
    with open(tmp, "w") as f:
        json.dump(d, f, indent=1)
    os.replace(tmp, SETTINGS)


@app.route("/api/settings", methods=["POST"])
def api_settings():
    d = request.get_json(silent=True) or {}
    cur = read_settings()
    if voices.is_voice(d.get("voice") or ""):
        cur["voice"] = d["voice"]
    if "style" in d:
        cur["style"] = str(d["style"])[:400]
    if "speed" in d:
        try:
            cur["speed"] = max(60, min(300, int(d["speed"])))
        except (TypeError, ValueError):
            pass
    write_settings(cur)
    return jsonify({"ok": True, "settings": cur})


# ---------------------------------------------------------------- the archive
def read_index():
    try:
        with open(INDEX) as f:
            d = json.load(f)
        return d if isinstance(d, list) else []
    except (OSError, ValueError):
        return []


def write_index(items):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    tmp = INDEX + ".new"
    with open(tmp, "w") as f:
        json.dump(items, f, indent=1)
    os.replace(tmp, INDEX)


def slug(text):
    s = re.sub(r"[^A-Za-z0-9]+", "-", text.strip()).strip("-").lower()
    return (s[:40] or "said")


@app.route("/api/say", methods=["POST"])
def api_say():
    global SAID_COUNT
    d = request.get_json(silent=True) or {}
    text = (d.get("text") or "").strip()
    voice = d.get("voice") or ""
    style = (d.get("style") or "").strip()
    speed = d.get("speed") or read_settings().get("speed") or 150
    try:
        speed = max(60, min(300, int(speed)))
    except (TypeError, ValueError):
        speed = 150
    if not text:
        return jsonify({"ok": False, "error": "nothing to say: the text box is empty"}), 400
    if not voices.is_voice(voice):
        return jsonify({"ok": False, "error": "no voice chosen: open VOICE and pick one" if not voice else "unknown voice %r" % voice}), 400
    if not ring.load():
        return jsonify({"ok": False, "error": "the ring is empty: on the KEYS tab choose the file with your Google keys"}), 400
    fp = speech.fingerprint(text, voice, style, speed)
    for it in read_index():                       # the same sentence in the same voice is not spent twice
        if it.get("fp") == fp and os.path.exists(os.path.join(AUDIO_DIR, it["file"])):
            return jsonify({"ok": True, "item": it, "cached": True, "log": ["cached: said before, nothing spent"]})
    with _say_lock:
        PROGRESS.update({"busy": True, "started": time.time(), "lines": [], "text": text, "voice": voice})
        progress_line("asking Google with the first key of the ring, %s" % voice)
        try:
            r = speech.say(text, voice, style, log=progress_line, speed=speed)
        finally:
            progress_line("Google answered" if r.get("ok") else "no answer")
            PROGRESS["busy"] = False
    took = round(time.time() - PROGRESS["started"], 1)
    if not r["ok"]:
        return jsonify({"ok": False, "error": r["error"], "log": r["log"], "ring": ring.public()}), 502
    os.makedirs(AUDIO_DIR, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    fname = "%s_%s_%s.wav" % (stamp, voice, slug(text))
    with open(os.path.join(AUDIO_DIR, fname), "wb") as f:
        f.write(r["wav"])
    item = {"id": stamp + "-" + fp[:6], "file": fname, "text": text, "style": style, "voice": voice,
            "model": r["model"], "key": "%s, key %d of %d" % (r["label"], r["pos"], r["of"]),
            "seconds": round(r["seconds"], 1), "bytes": len(r["wav"]), "at": int(time.time()), "fp": fp, "took": took,
            "speed": speed, "words": speech.words_of(text),
            "wpm": round(speech.words_of(text) * 60.0 / r["seconds"]) if r["seconds"] > 0 else None}
    with _index_lock:
        items = read_index()
        items.insert(0, item)
        write_index(items)
    SAID_COUNT += 1
    return jsonify({"ok": True, "item": item, "cached": False, "log": r["log"], "ring": ring.public()})


@app.route("/api/progress")
def api_progress():
    """What is happening right now: busy, seconds so far, the lines of the walk."""
    return jsonify({"busy": PROGRESS["busy"], "elapsed": (time.time() - PROGRESS["started"]) if PROGRESS["started"] else 0,
                    "lines": [l["text"] for l in PROGRESS["lines"]], "text": PROGRESS["text"], "voice": PROGRESS["voice"]})


@app.route("/audio/<path:name>")
def audio(name):
    resp = send_from_directory(AUDIO_DIR, name, mimetype="audio/wav", conditional=True)
    if request.args.get("download"):
        resp.headers["Content-Disposition"] = 'attachment; filename="%s"' % os.path.basename(name)
    return resp


@app.route("/api/archive/<item_id>", methods=["DELETE"])
def api_archive_delete(item_id):
    with _index_lock:
        items = read_index()
        keep = [it for it in items if it.get("id") != item_id]
        gone = [it for it in items if it.get("id") == item_id]
        for it in gone:
            try:
                os.remove(os.path.join(AUDIO_DIR, it["file"]))
            except OSError:
                pass
        write_index(keep)
    return jsonify({"ok": True, "archive": keep})


# ---------------------------------------------------------------- the keys
@app.route("/api/keys")
def api_keys():
    return jsonify({"ring": ring.public(), "removed": ring.removed()})


@app.route("/api/keys/import", methods=["POST"])
def api_keys_import():
    """The file picker's upload (multipart, field keyfile), or a pasted note ({text})."""
    f = request.files.get("keyfile")
    if f is not None:
        raw = f.read()
        if b"\x00" in raw:
            return jsonify({"ok": False, "error": "that is not a text file"}), 400
        r = ring.import_text(raw.decode("utf-8", "replace"), source=f.filename or "picked file")
    else:
        d = request.get_json(silent=True) or {}
        r = ring.import_text(d.get("text") or "", source="pasted")
    r["ok"] = True
    r["ring"] = ring.public()
    return jsonify(r)


@app.route("/api/keys/test", methods=["POST"])
def api_keys_test():
    """Test the named keys, or all, one after another (never in parallel). Nothing is spent:
    the probe is the models list."""
    d = request.get_json(silent=True) or {}
    want = set(d.get("labels") or [])
    out = []
    for label, key in ring.load():
        if want and label not in want:
            continue
        v, why = speech.probe(key)
        out.append({"label": label, "verdict": v, "detail": why})
    return jsonify({"ok": True, "tested": out, "ring": ring.public()})


@app.route("/api/keys/delete", methods=["POST"])
def api_keys_delete():
    d = request.get_json(silent=True) or {}
    r = ring.remove(d.get("labels") or [], reason=d.get("reason") or "removed on the page")
    r.update({"ok": True, "ring": ring.public(), "removed_names": ring.removed()})
    return jsonify(r)


@app.route("/api/keys/restore", methods=["POST"])
def api_keys_restore():
    d = request.get_json(silent=True) or {}
    r = ring.restore(d.get("labels") or [])
    r.update({"ok": True, "ring": ring.public(), "removed_names": ring.removed()})
    return jsonify(r)


@app.route("/api/keys/bottom", methods=["POST"])
def api_keys_bottom():
    """Send a key to the bottom by hand (the page's button)."""
    d = request.get_json(silent=True) or {}
    for label, key in ring.load():
        if label == d.get("label"):
            ring.to_bottom(key)
    return jsonify({"ok": True, "ring": ring.public()})


def console_snapshot():
    return {"version": APP_VERSION, "uptime": time.time() - START_TIME, "requests": REQUEST_COUNT,
            "said": SAID_COUNT, "keys": len(ring.load()), "archive": len(read_index())}


if __name__ == "__main__":
    if not os.path.exists(os.path.join(HERE, APP_FILE)):
        print("error: %s not found next to app.py in %s" % (APP_FILE, HERE))
        sys.exit(1)
    requested = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            requested = int(sys.argv[1])
        except ValueError:
            print("ignoring invalid port argument %r, using %d" % (sys.argv[1], DEFAULT_PORT))
    LIVE_PORT, port_note = portpick.pick("127.0.0.1", requested)       # never "could not start" (ports.md)
    if not os.environ.get("GVOICE_TEST"):                              # the test copy neither announces nor forgets
        portpick.announce(COMMAND, LIVE_PORT)                          # ~/.mantra/ports/gvoice
    action = term.run(app, "127.0.0.1", LIVE_PORT, snapshot=console_snapshot, note=port_note,
                      on_check_update=selfupdate.check_remote, on_perform_update=selfupdate.perform_update)
    if action == "restart":
        os.execv(sys.executable, [sys.executable] + sys.argv)
