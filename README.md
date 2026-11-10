# QuickCopy

A small Windows Tkinter app for adding, viewing, and copying saved text. No runtime packages or accounts are needed when running from Python.

## Run from source

Install Python 3.12 or newer with Tcl/Tk and the Windows Python launcher. In this folder:

```powershell
py quickcopy.py
```

The first run supplies three fictional examples. Paste into the field and click **Add**. The field supports multiple lines. Empty or whitespace-only input is ignored. Each row previews up to 160 characters, with line breaks shown as spaces; **Copy** copies the entire original, including whitespace and Unicode. The button briefly says **Copied**. Scroll with the wheel over the list or drag the scrollbar. Tab reaches copy buttons and brings their rows into view.

## Build, launch, and pin on Windows

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\build.ps1
```

If Python is installed without `py`, pass `-Python 'C:\path\to\python.exe'` to the script. The build installs pinned PyInstaller into a project-local `.venv` and produces `dist\QuickCopy.exe`. It requires internet access the first time. The build has no console window and includes the overlapping-rectangle icon.

1. Copy `dist\QuickCopy.exe` to a permanent location, such as a QuickCopy folder under Documents. It is a standalone file; no Python installation is required on the target PC.
2. Double-click that file. Right-click its running taskbar icon and choose **Pin to taskbar** (on some Windows versions, right-click the app name again).
3. Close the window, then click the pinned icon to reopen it. While running, clicking the icon focuses/restores it. Launching the executable again also restores the existing window rather than opening another copy.

Keep the executable at the same path after pinning. Rebuilding `dist` does not update a separately copied executable. The window starts at 460 × 310 pixels, can be resized, and is aware of Windows display scaling. Check comfort on your monitor; the one-sixteenth-screen size is an approximate target.

## Local storage

Snippets live in `%LOCALAPPDATA%\QuickCopy\snippets.json`, outside the repository and build output. They are plain text, not encrypted. Closing the app or replacing the executable keeps them. A malformed file produces an error instead of overwriting it; back it up and repair the JSON or rename it to start over. Save failures leave your input available for retry. No edit/delete feature is included in this version.

## Read the code

Start with `quickcopy.py`: `QuickCopy` creates the window and rows; `copy` calls `write_clipboard`, which gives Windows ownership of the text so it stays available after the app closes; `add` saves and then inserts a row. `load_snippets` and `save_snippets` handle JSON and atomic replacement. `claim_instance` uses a Windows mutex to detect another launch and restore its window. The same rectangle design appears in `copy_icon` and `assets/quickcopy.ico`.

Run checks with `py -m unittest discover -s tests -v`. These create real Tk windows and temporarily replace the clipboard with test text. They use temporary snippet files, not your saved list. See `WORKFLOW.md` for the build/review/GitHub handoffs and validation record.
