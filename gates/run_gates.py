#!/usr/bin/env python3
"""
gates/run_gates.py  --  the delivery gates (MANTRA_MANIFEST modules/delivery-gate.md), counts printed.

  secrets    no key shape anywhere in the tree that git would take (keys/ and audio/ are ignored)
  dead code  every .py in the root is imported by app.py or is a tool; every route has a caller in the page
  budgets    the page is one file under 64 KB; requirements has two lines
  version    version.py is a whole number, and it is higher than the one at origin/main when there is a remote
  record     gates/RECORD.md is written with the counts and the NOT TESTED block

Run before every delivery:  .venv/bin/python gates/run_gates.py
"""
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KEY_RE = re.compile(r"(AQ\.[A-Za-z0-9_\-]{20,}|AIza[A-Za-z0-9_\-]{20,}|sk-ant-[A-Za-z0-9_\-]{20,}|gsk_[A-Za-z0-9]{20,}|AC[0-9a-f]{32})")
NOT_TESTED = [
    "Termux: pkg and pip inside Termux, waitress on the phone's python, $PREFIX/bin on PATH, termux-open-url against Chrome",
    "the U key against a newer origin/main (proven only that check_remote reads version.py; no newer version existed yet)",
    "the page in a browser at 390 px: Chrome's extension was not connected on 15.9.2026, so the layout was not measured, only the routes",
    "a key that is refused for real (401 came from a made-up key, not from a revoked one)",
    "the daily wall for real (no key was driven to its ten)",
]


def files():
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True).stdout
        return [f for f in out.split("\n") if f]
    except OSError:
        return []


def main():
    counts = {}
    fails = []
    # secrets
    hits = 0
    for f in files():
        p = os.path.join(ROOT, f)
        if not os.path.isfile(p):
            continue
        try:
            txt = open(p, "rb").read().decode("utf-8", "replace")
        except OSError:
            continue
        for m in KEY_RE.finditer(txt):
            if f == "gates/run_gates.py" or f == "ring.py" or f == "tests/run_all.py":
                # the regexes and the fake keys of the tests: a fake is letters repeated
                if re.fullmatch(r"AQ\.(.)\1{20,}", m.group(1)) or re.fullmatch(r"AIza(.)\1{20,}", m.group(1)):
                    continue
                if m.group(1) in ("AQ.[A-Za-z0-9_",):
                    continue
            hits += 1
            fails.append("a key shape in %s at %d" % (f, m.start()))
    counts["secrets: key shapes in the tree"] = hits
    # dead code
    app_txt = open(os.path.join(ROOT, "app.py")).read()
    page = open(os.path.join(ROOT, "gvoices.html")).read()
    dead = 0
    for f in files():
        if f.endswith(".py") and "/" not in f and f not in ("app.py",):
            mod = f[:-3]
            if not re.search(r"^import %s\b|^from %s\b" % (mod, mod), app_txt, re.M) and not re.search(r"import %s\b" % mod, open(os.path.join(ROOT, "speech.py")).read() + open(os.path.join(ROOT, "ring.py")).read()):
                dead += 1
                fails.append("%s is imported by nothing" % f)
    routes = re.findall(r'@app\.route\("(/api/[^"<]*)', app_txt)
    unused = 0
    for r in set(routes):
        if r not in page and r.rstrip("/") not in page:
            unused += 1
            fails.append("route %s has no caller in the page" % r)
    counts["dead code: modules nobody imports"] = dead
    counts["dead code: routes nobody calls"] = unused
    # budgets
    size = os.path.getsize(os.path.join(ROOT, "gvoices.html"))
    counts["budget: page bytes"] = size
    if size > 65536:
        fails.append("the page is over 64 KB")
    req = [l for l in open(os.path.join(ROOT, "requirements.txt")).read().split("\n") if l.strip()]
    counts["budget: requirements"] = len(req)
    # version
    m = re.search(r"^APP_VERSION\s*=\s*(\d+)\s*$", open(os.path.join(ROOT, "version.py")).read(), re.M)
    if not m:
        fails.append("version.py has no whole number")
    local = int(m.group(1)) if m else 0
    counts["version: local"] = local
    try:
        remote = subprocess.run(["git", "show", "origin/main:version.py"], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout
        rm = re.search(r"^APP_VERSION\s*=\s*(\d+)\s*$", remote, re.M)
        if rm:
            counts["version: origin/main"] = int(rm.group(1))
            changed = subprocess.run(["git", "diff", "--quiet", "origin/main", "--", "."], cwd=ROOT).returncode != 0
            if changed and int(rm.group(1)) >= local:
                fails.append("the tree differs from origin/main but version.py was not bumped")
    except (OSError, subprocess.TimeoutExpired):
        pass
    # record
    lines = ["# DELIVERY RECORD, gates run %s" % time.strftime("%d.%m.%Y %H:%M"), ""]
    for k, v in counts.items():
        lines.append("- %s: %s" % (k, v))
    lines += ["", "## Failed", ""] + (["- " + f for f in fails] or ["- none"]) + ["", "## NOT TESTED", ""] + ["- " + n for n in NOT_TESTED] + [""]
    open(os.path.join(HERE, "RECORD.md"), "w").write("\n".join(lines))
    print("\n".join(lines))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
