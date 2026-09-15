# LESSONS, what it cost to learn

1. **A key spent on one model is not spent.** (15.9.2026) The free tier's ten a day is per model. The first
   draft sent a key to the bottom after the first wall; the test caught it: the key must be asked on the
   second model first, and only then moved.
2. **zsh does not split an unquoted variable.** `H='-H X: 1'; curl $H …` sends one argument, "-H X: 1", and the
   guard refuses; every route looked broken for one line of shell. Write the header out.
3. **The port picker is not a bug report.** A second copy on 8301 meant the first was still alive, not that
   the picker was wrong. `pkill -f` needs the real command line, `app.py 8300`.
4. **The pty test must strip the colours** before it looks for "q quit"; and it must wait for the LAST word
   of the row, not the first, or it reads a half-printed banner.
5. **"It is not working" must be watched in his browser, not curled.** (15.9.2026) Every route answered curl; the
   page in his Chrome was repainted by Dark Reader, amber to grey and triangles to squares. A `<meta
   name="darkreader-lock">` stops it, and glyphs drawn as inline SVG cannot be repainted. Check
   `document.documentElement.attributes` for data-darkreader-* before doubting the CSS.
6. **Hear it through BlackHole.** The Mac's output is BlackHole 2ch; `ffmpeg -f avfoundation -i ":BlackHole 2ch"`
   records what the browser plays, and volumedetect and silencedetect turn it into numbers: silence until the press,
   −21.8 dB peak while the voice spoke, silence after. That is the test of the sound, not of the file.

