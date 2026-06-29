# Toolkit

A few small, self-contained utilities. Standard library / built-in only —
no installs, no third-party packages.

- D Das

## Files

| File | What it does |
|------|--------------|
| `keep_awake.py` | Keeps a Windows session from going idle by sending real input (an F15 key + a 1px mouse nudge) on an interval. Auto-stops after a set number of minutes. |
| `Keep-Awake.ps1` | Same idea as above, in PowerShell. Use this when Python isn't installed — PowerShell ships with Windows. |
| `slow_writer.py` | Writes Python code snippets into a text file one character at a time, with human-like pacing. A pacing / text-output demo. |
| `typing_simulator_v2.html` | A browser page that animates a code editor "typing" Python on screen. For screen recordings and demos. Holds a screen wake lock and auto-stops after a chosen duration. |
| `typing_simulator.html` | First version of the above. Superseded by V2. |

## How to run

**keep_awake.py** — edit the CONFIG block (mode, interval, `DURATION_MINUTES`), then:
```
python keep_awake.py
```
Leave the window open. Ctrl+C stops it.

**Keep-Awake.ps1** — right-click → Run with PowerShell, or:
```
powershell -ExecutionPolicy Bypass -File .\Keep-Awake.ps1
```

**slow_writer.py** — edit the CONFIG block (speed, `LOOP_FOREVER`, typos), then:
```
python slow_writer.py
```
Output lands in `generated_code.txt`. Ctrl+C stops it.

**typing_simulator_v2.html** — double-click to open in a browser. Pick speed and
"Run for" duration, click Start, then Fullscreen.

## Note on idle vs. activity

These split into two groups, and it matters which one you reach for:

- **Resets the Windows idle timer:** `keep_awake.py` and `Keep-Awake.ps1`. They
  inject real input, which is the only thing that keeps an input-idle lock from
  firing.
- **Does NOT touch the idle timer:** `slow_writer.py` and the browser pages.
  File writes and on-screen animation produce no input, so the session is still
  counted as idle while they run. The browser wake lock keeps the *monitor* lit,
  but does not reset the input timer.

None of these defeat monitoring that tracks input patterns, app usage, or
screenshots — they only address the basic idle timer and what's shown on screen.

## Requirements

- `keep_awake.py`, `slow_writer.py` — Python 3 standard library. Windows.
- `Keep-Awake.ps1` — Windows PowerShell (built in).
- `typing_simulator_v2.html` — any modern browser. Runs from file://.
