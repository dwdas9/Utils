#!/usr/bin/env python3
"""
Author: D Das
"""

import ctypes
from ctypes import wintypes
import subprocess
import time
from datetime import datetime

# ============================ CONFIG ============================
MODE             = "innocuous"   # "innocuous" or "notepad"
INTERVAL_SECONDS = 60            # seconds between activity bursts
DURATION_MINUTES = 90            # auto-stop after this many minutes (0 = run forever)
NOTEPAD_TEXT     = "Staying active... {0}\n"   # {0} -> timestamp
# ===============================================================

user32 = ctypes.WinDLL("user32", use_last_error=True)

# --- constants ---
INPUT_KEYBOARD    = 1
KEYEVENTF_KEYUP   = 0x0002
KEYEVENTF_UNICODE = 0x0004
MOUSEEVENTF_MOVE  = 0x0001
VK_F15            = 0x7E   # no real keyboard has F15, so pressing it is invisible
VK_RETURN         = 0x0D
SW_MINIMIZE       = 6
SW_MAXIMIZE       = 3

# --- SendInput structures ---
PUL = ctypes.POINTER(ctypes.c_ulong)

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", PUL)]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", PUL)]

class _INPUTunion(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTunion)]

# --- restypes/argtypes (critical on 64-bit: HWND is pointer-sized) ---
user32.GetForegroundWindow.restype  = wintypes.HWND
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype  = wintypes.BOOL
user32.ShowWindow.argtypes          = [wintypes.HWND, ctypes.c_int]
user32.ShowWindow.restype           = wintypes.BOOL
user32.SendInput.argtypes           = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype            = wintypes.UINT


def _send(inputs):
    n = len(inputs)
    arr = (INPUT * n)(*inputs)
    user32.SendInput(n, arr, ctypes.sizeof(INPUT))


def _key_unicode(ch):
    code = ord(ch)
    down = INPUT(INPUT_KEYBOARD, _INPUTunion(ki=KEYBDINPUT(0, code, KEYEVENTF_UNICODE, 0, None)))
    up   = INPUT(INPUT_KEYBOARD, _INPUTunion(ki=KEYBDINPUT(0, code, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, None)))
    return [down, up]


def _key_vk(vk):
    down = INPUT(INPUT_KEYBOARD, _INPUTunion(ki=KEYBDINPUT(vk, 0, 0, 0, None)))
    up   = INPUT(INPUT_KEYBOARD, _INPUTunion(ki=KEYBDINPUT(vk, 0, KEYEVENTF_KEYUP, 0, None)))
    return [down, up]


def type_string(text):
    inputs = []
    for ch in text:
        if ch == "\n":
            inputs += _key_vk(VK_RETURN)
        else:
            inputs += _key_unicode(ch)
    if inputs:
        _send(inputs)


def send_innocuous():
    # F15 press + release (counts as input, has no visible effect anywhere)
    user32.keybd_event(VK_F15, 0, 0, 0)
    user32.keybd_event(VK_F15, 0, KEYEVENTF_KEYUP, 0)
    # nudge mouse 1px right, then back
    user32.mouse_event(MOUSEEVENTF_MOVE, 1, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_MOVE, -1, 0, 0, 0)


def send_notepad_activity(hwnd):
    if not hwnd:
        return
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    type_string(NOTEPAD_TEXT.format(stamp))
    time.sleep(0.3)
    user32.ShowWindow(hwnd, SW_MINIMIZE)
    time.sleep(0.5)
    user32.ShowWindow(hwnd, SW_MAXIMIZE)


def main():
    hwnd = None
    if MODE == "notepad":
        subprocess.Popen(["notepad.exe"])
        time.sleep(1.0)
        # the window we just launched is the current foreground window;
        # grab its handle (works regardless of Win10/Win11 title differences)
        hwnd = user32.GetForegroundWindow()

    end_time = None
    if DURATION_MINUTES > 0:
        end_time = time.monotonic() + DURATION_MINUTES * 60

    stop_note = f"for {DURATION_MINUTES} min" if end_time else "until stopped"
    print(f"Keep-awake running in '{MODE}' mode. Interval: {INTERVAL_SECONDS}s, {stop_note}. "
          f"Press Ctrl+C to stop.")
    try:
        while True:
            if end_time is not None and time.monotonic() >= end_time:
                print("Duration reached. Stopping.")
                break
            if MODE == "notepad":
                send_notepad_activity(hwnd)
            else:
                send_innocuous()
            if end_time is not None:
                left = int(end_time - time.monotonic())
                print(f"[{datetime.now():%H:%M:%S}] activity sent  ({left // 60}m {left % 60}s left)")
            else:
                print(f"[{datetime.now():%H:%M:%S}] activity sent")
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()