#!/usr/bin/env python3
"""
tests/run_all.py  --  the four tests (MANTRA_MANIFEST modules/four-tests.md), each able to fail alone.

  1 the mechanism alone   ring rotation and the verdicts with a fake poster, in a temp folder
  2 the real thing once   one sentence through a real key (only with --real: it spends one of ten)
  3 the ugly cases        a note with junk, a duplicate, an unknown token, an empty ring, 429 bodies
  4 the upgrade           version.py has one whole number, selfupdate reads it, the console answers q on a pty

Run before every push:  .venv/bin/python tests/run_all.py [--real]
Counts are printed, not adjectives.
"""
import base64
import json
import re
import os
import pty
import select
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

FAILS = []
CHECKS = [0]


def check(cond, what):
    CHECKS[0] += 1
    if not cond:
        FAILS.append(what)
        print("  FAIL  " + what)


def temp_ring():
    import ring
    d = tempfile.mkdtemp()
    ring.KEYDIR = d
    ring.KEYFILE = os.path.join(d, "gvoice.keys")
    ring.STATEFILE = os.path.join(d, "state.json")
    ring.GRAVEYARD = os.path.join(d, "removed.keys")
    return ring


def audio_body():
    return json.dumps({"candidates": [{"content": {"parts": [{"inlineData": {"data": base64.b64encode(b"\x00\x01" * 2400).decode()}}]}}]})


def test1_mechanism():
    print("1 the mechanism alone")
    ring = temp_ring()
    import speech
    ring.import_text("a\nAQ." + "a" * 40 + "\n\nb\nAQ." + "b" * 40 + "\n\nc\nAQ." + "c" * 40 + "\n")
    calls = []

    def poster(model, payload, key):
        calls.append((key[3], model))
        if key[3] == "a":                                   # spent on both models
            return 429, json.dumps({"error": {"details": [{"violations": [{"quotaId": "PerDay"}]}]}}), {}
        if key[3] == "b" and model == speech.MODELS[0]:      # busy once, then the second model answers
            return 429, '{"error":{"details":[{"retryDelay":"2s"}]}}', {}
        if key[3] == "b":
            return 200, audio_body(), {}
        return 401, "", {}
    slept = []
    r = speech.say("hi", "Kore", "", poster=poster, sleeper=slept.append)
    check(r["ok"], "a sentence came back")
    check(r["label"] == "b" and r["pos"] == 1, "the second key answered as key 1 after the first went down")
    check([l for l, _ in ring.load()] == ["b", "c", "a"], "the spent key is at the bottom of the file")
    check(slept == [2], "the busy key waited its retryDelay once")
    check(calls.count(("a", speech.MODELS[0])) == 1 and calls.count(("a", speech.MODELS[1])) == 1, "the spent key was tried on both models")
    check(len(calls) == 5, "five calls in all, one after another: a twice, b busy, b again, b's second model (%d)" % len(calls))
    check(r["wav"][:4] == b"RIFF" and abs(r["seconds"] - 0.1) < 0.001, "a WAV of 0.1 s")
    check(ring.public()[-1]["verdict"] == "spent", "the state remembers the wall")
    # a key that refuses everywhere goes to the bottom as refused
    r2 = speech.say("hi", "Kore", "", poster=lambda m, p, k: (401, "", {}), sleeper=lambda s: None)
    check(not r2["ok"] and "no key answered" in r2["error"], "a ring of refused keys says so")
    check(all(k["verdict"] == "refused" for k in ring.public()), "every key is marked refused")


def test2_real():
    print("2 the real thing once" + ("" if "--real" in sys.argv else "  (skipped: pass --real to spend one request)"))
    if "--real" not in sys.argv:
        return
    import ring
    import speech
    if not ring.load():
        check(False, "the real ring is empty (keys/gvoice.keys)")
        return
    r = speech.say("This is the real test of GVoices.", "Kore", "quickly")
    check(r["ok"], "Google answered: " + (r.get("error") or ""))
    if r["ok"]:
        check(r["seconds"] > 0.5, "audio longer than half a second (%.1f s)" % r["seconds"])
        print("  answered by %s, key %d of %d, %s, %.1f s" % (r["label"], r["pos"], r["of"], r["model"], r["seconds"]))


def test3_ugly():
    print("3 the ugly cases")
    ring = temp_ring()
    import speech
    r = ring.import_text("random note\nhttps://example.com\n\n" + "x" * 40 + "\n\nfather\nAQ." + "f" * 40 + "\n\nfather\nAQ." + "f" * 40 + "\n\ntwin\nAQ." + "f" * 40 + "\n\nlegacy\nAIza" + "z" * 35 + "\n")
    check(r["added"] == 2, "two keys from a messy note (%d)" % r["added"])
    check(len(r["unknown"]) == 1 and r["unknown"][0]["length"] == 40, "one unknown long token reported, not dropped")
    r = ring.import_text("father\nAQ." + "g" * 40 + "\n")
    check([l for l, _ in ring.load()][-1] == "father 2", "a second key wanting a taken name is numbered")
    check(ring.import_text("")["added"] == 0, "an empty note adds nothing")
    check(ring.import_text("nothing here\n")["added"] == 0, "a note without keys adds nothing")
    empty = temp_ring()
    r = speech.say("hi", "Kore", "", poster=lambda m, p, k: (200, audio_body(), {}))
    check(not r["ok"] and "empty" in r["error"], "an empty ring says so before asking Google")
    v, why = speech.verdict(429, json.dumps({"error": {"message": "quota exceeded", "details": [{"violations": [{"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier", "quotaValue": "10"}]}]}}), {})
    check(v == "spent", "a PerDay quotaId is the wall (%s)" % v)
    v, _ = speech.verdict(429, '{"error":{"message":"Resource has been exhausted","details":[{"@type":"RetryInfo","retryDelay":"31s"}]}}', {})
    check(v == "busy", "a retryDelay is busy, not money (%s)" % v)
    check(speech.retry_after('{"retryDelay":"31s"}', {}) == 31, "retryDelay read as 31")
    check(speech.retry_after("", {"Retry-After": "7"}) == 7, "Retry-After read as 7")
    v, _ = speech.verdict(429, "insufficient credit, prepayment required", {})
    check(v == "spent", "money words without a hint are no credit")
    check(speech.verdict(404, "", {})[0] == "model", "404 is the model, not the key")
    check(speech.verdict(503, "", {})[0] == "outage", "503 is Google's day")
    check(speech.verdict(-1, "no network", {})[0] == "outage", "no network is not the key")
    check(speech.pcm_of('{"candidates":[]}') == b"", "an answer without audio is empty, not a crash")
    check(speech.prompt_of("hello", "slowly.") == "slowly: hello" and speech.prompt_of("hello", "") == "hello", "the style goes before the text as prose")
    import voices
    check(len(voices.catalogue()) == 30 and not voices.is_voice("Nobody"), "thirty voices, and an unknown name is refused")


def test4_upgrade():
    print("4 the upgrade")
    txt = open(os.path.join(ROOT, "version.py")).read()
    m = re.search(r"^APP_VERSION\s*=\s*(\d+)\s*$", txt, re.M)
    check(bool(m), "version.py holds one whole number")
    import version
    check(m and int(m.group(1)) == version.APP_VERSION, "and it is the number the app imports")
    import selfupdate
    check(callable(selfupdate.check_remote) and callable(selfupdate.perform_update), "selfupdate has the two halves")
    # the console on a pty: the banner, the key row, then q ends it
    env = dict(os.environ, GVOICE_TEST="1")
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(ROOT)
        os.execv(sys.executable, [sys.executable, "app.py", "8399"])
    out = b""
    deadline = time.time() + 15
    while time.time() < deadline:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            out += chunk
            if "\u0950".encode() in out:          # the rule line comes after the key row: the console is in cbreak now
                break
    check(b"GVoices" in out, "the banner names the app")
    plain = re.sub(rb"\x1b\[[0-9;]*m", b"", out)
    check(b"q quit" in plain and b"o open page" in plain and b"u check for update" in plain and b"r restart" in plain, "the key row is q o u r")
    check(b"\xe2\x94\x82" not in out, "no box is drawn")
    time.sleep(2.0)
    os.write(fd, b"q")
    end = time.time() + 8
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            out += chunk
        try:
            wpid, status = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            wpid = pid
        if wpid:
            break
    ended = False
    for _ in range(20):
        try:
            wpid, _st = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            wpid = pid
        if wpid:
            ended = True
            break
        time.sleep(0.5)
    if not ended:
        os.kill(pid, 9)
        try:
            os.waitpid(pid, 0)
        except ChildProcessError:
            pass
    check(ended, "q ends the process within ten seconds (after q: %r)" % re.sub(rb"\x1b\[[0-9;]*m", b"", out)[-120:])
    check(b"stopped" in out.lower() or b"quit" in out.lower(), "and it says so")
    check(not os.path.exists(os.path.expanduser("~/.mantra/ports/gvoice")) or open(os.path.expanduser("~/.mantra/ports/gvoice")).read().strip() != "8399", "the registry forgot 8399 at exit")


if __name__ == "__main__":
    for t in (test1_mechanism, test2_real, test3_ugly, test4_upgrade):
        try:
            t()
        except Exception as e:
            FAILS.append("%s crashed: %r" % (t.__name__, e))
            print("  CRASH " + repr(e))
    print("\n%d checks, %d failed" % (CHECKS[0], len(FAILS)))
    for f in FAILS:
        print("  " + f)
    sys.exit(1 if FAILS else 0)
