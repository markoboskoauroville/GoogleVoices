"""
speech.py  --  one sentence to Google, one WAV back, through the ring.

The API is the Gemini API's generateContent with responseModalities AUDIO (apis/gemini.md,
modules/gemini-speech.md): the answer is raw 24 kHz mono 16-bit PCM, base64, no header; the WAV
header is written here. The free tier gives every key ten requests per model per day
(gemini-speech.md), so two models are walked per key before the key is called tired.

THE VERDICTS (GOOGLE_TTS_STT, KEYRING_TERMUX probes.py): 200 working; 401/403 refused; 429 with
a retry hint is busy (a wait, and the hint is checked FIRST because a spent free tier and two
requests in one second both say RESOURCE_EXHAUSTED); 429 with a daily quotaId or money words is
spent for today; 404 is the model, not the key; 5xx is Google's day, not the key.

THE RULE (Marko, 15.9.2026): one key at a time, the first in the file, until it refuses; then it
goes to the bottom and the next takes over. A busy key waits its retryDelay once (30 s at most)
and is asked again; only a refusal or a wall moves it.
"""

import base64
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.request
import wave

import ring
import version

BASE = "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent"
MODELS = ["gemini-2.5-flash-preview-tts", "gemini-3.1-flash-tts-preview"]   # walked in this order, per key
USER_AGENT = "GVoices/%d (+https://github.com/markoboskoauroville/GoogleVoices)" % version.APP_VERSION
RATE = 24000
MAX_WAIT = 30

RETRY_HINT = re.compile(r"retrydelay|retry-after|retryinfo|quotafailure|per minute|perminute|try again in", re.I)
MONEY = re.compile(r"credit|balance|depleted|insufficient|billing|payment|prepayment|e0300|zero_credits", re.I)


def post(model, payload, key, timeout=300):
    req = urllib.request.Request(BASE % model, data=json.dumps(payload).encode(),
                                 headers={"x-goog-api-key": key, "Content-Type": "application/json",
                                          "User-Agent": USER_AGENT})
    try:
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read().decode(), dict(r.headers)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
        except Exception:
            body = ""
        return e.code, body, dict(e.headers or {})
    except Exception as e:                       # no network, refused, timeout
        return -1, str(e), {}


def retry_after(body, headers):
    """Seconds to wait, from Retry-After, RetryInfo's retryDelay, or 'try again in Ns'."""
    for h in ("Retry-After", "retry-after"):
        if headers.get(h):
            try:
                return max(1, min(3600, int(float(headers[h]))))
            except ValueError:
                pass
    m = re.search(r'"retryDelay"\s*:\s*"(\d+)', body) or re.search(r"try again in (\d+)", body, re.I)
    if m:
        return max(1, min(3600, int(m.group(1))))
    return None


def is_daily(body):
    """A PerDay quotaId writes a key off until midnight Pacific; PerMinute costs a wait."""
    try:
        d = json.loads(body)
        for det in d.get("error", {}).get("details", []):
            for v in det.get("violations", []) or []:
                if "PerDay" in (v.get("quotaId") or ""):
                    return True
    except ValueError:
        pass
    return bool(re.search(r"PerDay", body))


def verdict(code, body, headers):
    """One of working, refused, busy, spent, model, outage, unclear; and a sentence."""
    if code == 200:
        return "working", "answered"
    if code in (401, 403):
        return "refused", "refused (%d): wrong, revoked, or restricted" % code
    if code == 429:
        if is_daily(body):
            return "spent", "the daily wall: ten requests a day on the free tier, back at 09:00 Zagreb"
        if MONEY.search(body) and not RETRY_HINT.search(body):
            return "spent", "no credit on this account"
        wait = retry_after(body, headers)
        return "busy", "per-minute limit, %s" % ("wait %ds" % wait if wait else "wait a moment")
    if code == 404:
        return "model", "404: the model is gone, not the key"
    if code == 400:
        return "unclear", "400: the request was refused, not the key"
    if code >= 500 or code == -1:
        return "outage", "%s: Google's side, not the key" % (code if code > 0 else "no network")
    return "unclear", "%d" % code


def payload(text, voice):
    return {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}


def pcm_of(body):
    d = json.loads(body)
    for c in d.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            if "inlineData" in p:
                return base64.b64decode(p["inlineData"]["data"])
    return b""


def wav_bytes(pcm):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm)
    return buf.getvalue()


def seconds_of(pcm):
    return len(pcm) / 2.0 / RATE


# THE PACE (Marko, 15.9.2026: "I need the speed of generation ... how fast the voice is talking so it's generating
# exactly that pace without artifacts of stretching"): Gemini has no rate parameter; the pace is asked for in the
# prompt as words per minute, and the audio is never stretched afterwards. What came back is measured (words / seconds)
# and shown beside what was asked.
SPEEDS = [(90, "very slow"), (110, "slow"), (130, "unhurried"), (150, "natural"), (170, "brisk"), (190, "fast"), (220, "very fast")]


def pace_words(speed):
    try:
        speed = int(speed)
    except (TypeError, ValueError):
        return ""
    name = min(SPEEDS, key=lambda p: abs(p[0] - speed))[1]
    return "Speak at a %s pace, about %d words per minute, evenly, with natural pauses" % (name, speed)


def prompt_of(text, style, speed=None):
    """The direction is prose before the text (Gemini has no style field): 'Speak at ... . Say it slowly: ...'."""
    style = (style or "").strip().rstrip(":.")
    text = (text or "").strip()
    head = ". ".join([x for x in (pace_words(speed), style) if x])
    return ("%s: %s" % (head, text)) if head else text


def fingerprint(text, voice, style, speed=None):
    return hashlib.sha256(("%s|%s|%s|%s" % (voice, style or "", speed or "", text)).encode()).hexdigest()[:16]


def words_of(text):
    return len([w for w in (text or "").split() if w.strip()])


def say(text, voice, style="", poster=post, sleeper=time.sleep, log=None, speed=None):
    """Walk the ring, one key at a time, and return a dict:
       ok, wav (bytes), seconds, model, label, pos, of, log (the sentences of the walk).
    poster and sleeper are injectable for the tests (four-tests.md, test 1: the mechanism alone)."""
    lines = []
    def tell(s):
        lines.append(s)
        if log:
            log(s)
    body_text = prompt_of(text, style, speed)
    if not ring.load():
        return {"ok": False, "error": "the ring is empty: pick your keys file on the KEYS tab", "log": lines}
    for label, key, pos, of in ring.walk():
        tired = None                               # the verdict that sends this key to the bottom
        for model in MODELS:
            tell("key %d of %d (%s): sending to %s" % (pos, of, label, model))
            code, body, headers = poster(model, payload(body_text, voice), key)
            v, why = verdict(code, body, headers)
            if v == "busy":
                wait = retry_after(body, headers) or 10
                if wait <= MAX_WAIT:
                    tell("key %d of %d, %s: %s; waiting %d s, then asking again" % (pos, of, model, why, wait))
                    sleeper(wait)
                    code, body, headers = poster(model, payload(body_text, voice), key)
                    v, why = verdict(code, body, headers)
            tell("key %d of %d (%s), %s: %s" % (pos, of, label, model, why))
            if v == "working":
                pcm = pcm_of(body)
                if not pcm:
                    tell("answered without audio, trying the next model")
                    continue
                ring.note(key, "working", "%s answered" % model)
                return {"ok": True, "wav": wav_bytes(pcm), "seconds": seconds_of(pcm), "model": model,
                        "label": label, "pos": pos, "of": of, "log": lines}
            if v == "refused":
                tired = (v, why)
                break                              # a wrong key is wrong on every model
            if v == "spent":
                tired = (v, why)
                continue                           # the wall is per model: the other model may still have its ten
            # model, outage, unclear, busy: not the key; the next model
        if tired:
            ring.note(key, tired[0], tired[1])
            ring.to_bottom(key)
            tell("key %s goes to the bottom" % label)
    return {"ok": False, "error": "no key answered: " + (lines[-1] if lines else "the ring is empty"), "log": lines}


def probe(key, poster=post):
    """Test one key cheaply: the models list proves validity; nothing is spent."""
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=1",
                                 headers={"x-goog-api-key": key, "User-Agent": USER_AGENT})
    try:
        r = urllib.request.urlopen(req, timeout=30)
        code, body, headers = r.status, r.read().decode(), dict(r.headers)
    except urllib.error.HTTPError as e:
        code, body, headers = e.code, (e.read().decode() if e.fp else ""), dict(e.headers or {})
    except Exception as e:
        code, body, headers = -1, str(e), {}
    v, why = verdict(code, body, headers)
    if v == "working":
        why = "valid (the models list answers; a spent free tier answers too)"
        v = "valid"
    ring.note(key, v, why)
    return v, why
