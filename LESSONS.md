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
