# Hayagriva Desktop Agent

This is the local companion that lets the Hayagriva web app interact with the **user's own PC**.

## What it supports

- Open a safe allow-listed desktop app
- Open an HTTP/HTTPS URL
- Type text
- Press a key
- Send a keyboard shortcut
- Take a desktop screenshot

The server binds to **127.0.0.1 only**. A random token is printed at startup and required by every request.

## Windows setup

1. Install Python 3.10+.
2. Open PowerShell in this folder.
3. Run:

```powershell
py -m pip install -r requirements.txt
py desktop-agent.py
```

4. Copy the printed token.
5. Open Hayagriva → **Desktop Agent**.
6. Keep the terminal running.

## Example voice commands

After owner voice verification and the Desktop Agent is connected:

- "Open Chrome"
- "Open https://youtube.com"
- "Open Notepad"
- "Type Hello Hayagriva"
- "Press Enter"
- "Shortcut Ctrl+L"
- "Show my screen"

Every desktop action still goes through Hayagriva's confirmation/owner-action gate.

> The web app cannot directly control arbitrary Windows applications by itself. This local companion is the bridge that makes that possible.
