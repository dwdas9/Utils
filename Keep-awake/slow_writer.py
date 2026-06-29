#!/usr/bin/env python3
"""
slow_writer.py - Write Python snippets to a text file one character at a time,
with human-like pacing (variable delays, longer pauses after newlines and
punctuation, occasional "thinking" gaps).

Standard library only. No pip installs.

What this is: a text-generation + pacing demo. It writes to a file.
What this is NOT: an activity simulator. Writing to a file produces no keyboard
or mouse input, so it does not affect the OS idle timer in any way.

Author: D Das
"""

import random
import sys
import time
from datetime import datetime

# ============================ CONFIG ============================
OUTPUT_FILE   = "generated_code.txt"
SPEED         = 5        # 1 (slow, deliberate) .. 10 (fast)
ADD_TYPOS     = True     # occasionally write a wrong char, then correct it
LOOP_FOREVER  = False    # if True, keep picking new snippets until Ctrl+C
ECHO_TO_STDOUT = True    # also mirror to the console as it writes
# ===============================================================

SNIPPETS = [
    '''# count word frequency in a file
from collections import Counter

def word_counts(path):
    with open(path, encoding="utf-8") as f:
        words = f.read().lower().split()
    return Counter(words)

if __name__ == "__main__":
    for word, n in word_counts("input.txt").most_common(10):
        print(f"{n:>4}  {word}")
''',
    '''# simple retry decorator
import time
import functools

def retry(times=3, delay=1.0):
    def wrap(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    if attempt == times - 1:
                        raise
                    time.sleep(delay)
        return inner
    return wrap
''',
    '''# flatten a nested list
def flatten(items):
    result = []
    for item in items:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

print(flatten([1, [2, [3, 4], 5], [6]]))
''',
    '''# group records by key
from collections import defaultdict

def group_by(records, key):
    buckets = defaultdict(list)
    for record in records:
        buckets[record[key]].append(record)
    return dict(buckets)
''',
    '''# read csv without pandas
import csv

def load_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]
''',
]

NEIGHBORS = {"a": "s", "s": "d", "d": "f", "e": "r", "r": "t",
             "t": "y", "o": "i", "i": "o", "n": "m", "l": "k"}


def base_delay():
    mean = 0.300 - (SPEED - 1) * 0.028          # ~300ms slow -> ~48ms fast
    jitter = (random.random() - 0.35) * mean
    return max(0.018, mean + jitter)


def pause_after(ch):
    if ch == "\n":
        return 0.5 + random.random() * 1.1
    if ch in ":,)]}":
        return 0.2 + random.random() * 0.36
    if ch == ".":
        return 0.15 + random.random() * 0.22
    if ch == " ":
        r = random.random()
        if r < 0.03:
            return 3.0 + random.random() * 5.0   # long "stuck" think
        if r < 0.12:
            return 0.9 + random.random() * 2.2   # ordinary think
    return 0.0


def write_char(f, ch):
    f.write(ch)
    f.flush()
    if ECHO_TO_STDOUT:
        sys.stdout.write(ch)
        sys.stdout.flush()


def backspace(f, text_so_far):
    # remove the last char from the file by rewriting (small files, fine)
    text_so_far = text_so_far[:-1]
    f.seek(0)
    f.truncate()
    f.write(text_so_far)
    f.flush()
    if ECHO_TO_STDOUT:
        sys.stdout.write("\b \b")
        sys.stdout.flush()
    return text_so_far


def write_snippet(f, snippet):
    written = ""
    for ch in snippet:
        if ADD_TYPOS and ch.isalpha() and ch.lower() in NEIGHBORS and random.random() < 0.03:
            wrong = NEIGHBORS[ch.lower()]
            wrong = wrong if ch.islower() else wrong.upper()
            write_char(f, wrong)
            written += wrong
            time.sleep(base_delay())
            time.sleep(0.16 + random.random() * 0.26)
            written = backspace(f, written)
            time.sleep(0.11 + random.random() * 0.14)
        write_char(f, ch)
        written += ch
        time.sleep(base_delay() + pause_after(ch))
    return written


def main():
    print(f"Writing to {OUTPUT_FILE} at speed {SPEED}. Press Ctrl+C to stop.\n")
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            while True:
                snippet = random.choice(SNIPPETS)
                header = f"# --- snippet written {datetime.now():%H:%M:%S} ---\n"
                write_snippet(f, header + snippet + "\n\n")
                if not LOOP_FOREVER:
                    break
                time.sleep(1.0 + random.random() * 2.0)
    except KeyboardInterrupt:
        print("\nStopped.")
    print(f"\nDone. Output in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()