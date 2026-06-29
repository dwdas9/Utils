# slow_writer

A small standard-library Python script that writes Python code snippets into a
text file one character at a time, with human-like pacing.

— D Das

## What it does

- Picks from a set of short Python snippets.
- Writes the chosen snippet to `generated_code.txt` character by character.
- Paces the writing like a person: variable per-character delays, longer pauses
  after newlines and punctuation, and occasional longer "thinking" gaps.
- Optionally simulates the odd typo and corrects it.
- Optionally mirrors the output to the console as it writes.

It is a text-generation and pacing demo. Nothing more.

## What it does NOT do

This is the important part, and the reason it's worth understanding:

- It does **not** generate keyboard or mouse input.
- It therefore has **no effect on the Windows idle timer** (`GetLastInputInfo`).
- A session that is otherwise idle will **still be treated as idle** and will
  still lock/sleep on schedule while this runs.

Why: on Windows, "is the user active?" is measured from injected input events,
not from disk activity. File writes and input are separate signals. This script
exercises the first and leaves the second untouched — which is the system
behavior it's meant to illustrate.

If the goal is to reset the idle timer, that requires injecting real input
(e.g. via the Win32 `keybd_event` / `SendInput` APIs), which is a different
mechanism entirely and is not what this script does.

## Configuration

Edit the `CONFIG` block at the top of `slow_writer.py`:

- `OUTPUT_FILE`    — file to write to (default `generated_code.txt`).
- `SPEED`          — 1 (slow, deliberate) to 10 (fast).
- `ADD_TYPOS`      — write an occasional wrong char, then correct it.
- `LOOP_FOREVER`   — keep picking new snippets until Ctrl+C.
- `ECHO_TO_STDOUT` — also mirror to the console as it writes.

## Run

```
python slow_writer.py
```

Stop any time with Ctrl+C. Output lands in `generated_code.txt`.

## Requirements

Python 3 standard library only. No third-party packages, no installs.
