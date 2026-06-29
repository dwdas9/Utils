<#
.SYNOPSIS
    Keeps Windows from registering as idle by periodically generating real
    input events. No installs, no third-party modules - pure PowerShell.

.DESCRIPTION
    Real input events reset the OS idle timer (GetLastInputInfo), which is what
    the screensaver, lock screen, sleep, and "Away" presence indicators read.

    Two modes:
      'Innocuous' (recommended) - sends an F15 keypress + a 1px mouse nudge each
                  interval. Resets the idle timer WITHOUT stealing focus, so it
                  doesn't interfere with whatever you're actually doing.
      'Notepad'   - opens Notepad, types a timestamped line, then minimizes and
                  maximizes the window. Visible demonstration of the behavior you
                  described. Note: this steals focus each cycle.

    Stop at any time with Ctrl+C.

.NOTES
    F15 is used because no physical keyboard has that key, so pressing it has no
    visible effect anywhere while still counting as input.
#>

# ============================ CONFIG ============================
$Mode            = 'Innocuous'   # 'Innocuous' or 'Notepad'
$IntervalSeconds = 60            # seconds to wait between activity bursts
$NotepadText     = "Staying active... {0}"   # {0} -> timestamp (Notepad mode)
# ===============================================================

Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win32 {
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, UIntPtr dwExtraInfo);
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    public const byte VK_F15            = 0x7E;
    public const uint KEYEVENTF_KEYUP   = 0x0002;
    public const uint MOUSEEVENTF_MOVE  = 0x0001;
    public const int  SW_MINIMIZE       = 6;
    public const int  SW_MAXIMIZE       = 3;
    public const int  SW_RESTORE        = 9;
}
"@

function Send-Innocuous {
    # Press + release F15 (a key no real keyboard has, so zero side effects)
    [Win32]::keybd_event([Win32]::VK_F15, 0, 0, [UIntPtr]::Zero)
    [Win32]::keybd_event([Win32]::VK_F15, 0, [Win32]::KEYEVENTF_KEYUP, [UIntPtr]::Zero)
    # Nudge the mouse 1px right, then back
    [Win32]::mouse_event([Win32]::MOUSEEVENTF_MOVE,  1, 0, 0, [UIntPtr]::Zero)
    [Win32]::mouse_event([Win32]::MOUSEEVENTF_MOVE, -1, 0, 0, [UIntPtr]::Zero)
}

function Send-NotepadActivity {
    param([System.Diagnostics.Process]$Proc)

    $Proc.Refresh()
    $hwnd = $Proc.MainWindowHandle
    if ($hwnd -eq [IntPtr]::Zero) { return }

    # Bring Notepad forward and type
    [void][Win32]::SetForegroundWindow($hwnd)
    Start-Sleep -Milliseconds 300
    $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    [System.Windows.Forms.SendKeys]::SendWait((($NotepadText -f $stamp) + "{ENTER}"))
    Start-Sleep -Milliseconds 300

    # Minimize, then maximize
    [void][Win32]::ShowWindow($hwnd, [Win32]::SW_MINIMIZE)
    Start-Sleep -Milliseconds 500
    [void][Win32]::ShowWindow($hwnd, [Win32]::SW_MAXIMIZE)
}

# ============================ MAIN =============================
Add-Type -AssemblyName System.Windows.Forms

$proc = $null
if ($Mode -eq 'Notepad') {
    $proc = Start-Process notepad -PassThru
    Start-Sleep -Seconds 1
}

Write-Host "Keep-awake running in '$Mode' mode. Interval: $IntervalSeconds s. Press Ctrl+C to stop." -ForegroundColor Green

try {
    while ($true) {
        switch ($Mode) {
            'Innocuous' { Send-Innocuous }
            'Notepad'   { Send-NotepadActivity -Proc $proc }
        }
        Write-Host ("[{0}] activity sent" -f (Get-Date -Format "HH:mm:ss"))
        Start-Sleep -Seconds $IntervalSeconds
    }
}
finally {
    Write-Host "Stopped." -ForegroundColor Yellow
}
