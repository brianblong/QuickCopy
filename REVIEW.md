# QuickCopy independent review

## Result

**Original blocking finding resolved.** The source and rebuilt executable now use eager native Windows `CF_UNICODETEXT` ownership, so copied snippets are no longer dependent on Tk staying alive after QuickCopy exits.

## Findings

### High: clipboard data is unavailable after the app closes

- **Location:** `quickcopy.py:177-180`
- **Reproduction:**
  1. Start QuickCopy with `.venv\Scripts\python.exe`, using a temporary snippets path.
  2. Invoke one of the existing row Copy buttons and confirm its feedback changes to `Copied.`.
  3. Destroy the Tk root.
  4. Read the Windows clipboard with `Get-Clipboard -Raw`.
  5. The same behavior is reproducible with a direct Tk `clipboard_clear`/`clipboard_append` call using multiline Unicode text.
- **Expected:** The exact copied text remains available after QuickCopy closes.
- **Actual:** `Get-Clipboard -Raw` returned an empty value after the QuickCopy process exited. This was reproduced from the app's own Copy button, not only from a mocked test harness.
- **Suggested fix:** Set Windows `CF_UNICODETEXT` clipboard data through the Win32 clipboard API, transferring ownership to the system with `SetClipboardData`, or otherwise use a clipboard-preservation mechanism that does not depend on the Tk process remaining alive. Add a regression test that copies, closes the app, and reads the clipboard from a separate process.

### Resolution and retest

- `quickcopy.py:75-133` now allocates movable global memory, writes UTF-16LE text including its terminator, calls `SetClipboardData(CF_UNICODETEXT, handle)`, and leaves successful ownership with Windows. A hidden native `STATIC` window is used only as the clipboard owner while the data is installed.
- `tests/test_quickcopy.py:62-91` now launches a separate copier process and a separate Tk reader after the copier exits.
- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: **passed, 8 tests**, including the new process-exit regression with long Unicode/multiline text.
- Static ctypes review found correct pointer/handle declarations for `GlobalAlloc`, `GlobalLock`, `CreateWindowExW`, and `SetClipboardData`; successful handles are not freed after Windows takes ownership, while failed allocations are freed.

## Executed checks

- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: **passed, 7 tests**.
  - This included real Tk layout, scrolling, exact long Unicode/multiline copy while the app remained open, restart persistence, invalid-file handling, and failed-save behavior.
- `.venv\Scripts\python.exe -m py_compile quickcopy.py tests\test_quickcopy.py`: **passed**.
- PowerShell parser check for `build.ps1`: **passed**.
- Direct Windows clipboard-after-exit check: **failed** as described above. The separate-process reader was PowerShell's `Get-Clipboard -Raw`; the observed output was `QuickCopy clipboard-after-exit reproduced: empty`.
- The requested `py -m unittest discover -s tests -v` command could not run because this host has no `py` launcher; the equivalent project Python command passed.

## Static observations

- The outer `grid` layout reserves rows for the list, multiline input, Add button, and helper text. The new visibility test passed at both `460x310` and `360x240`.
- `save_snippets` uses a temporary file and replacement, and the storage tests confirm Unicode/whitespace round trips and preservation of malformed files.
- The mutex and foreground-window behavior is Windows-specific and was not independently exercised.

## Blocked checks

- Standalone executable build: the rebuilt `dist\QuickCopy.exe` was present at `2026-11-09 19:16:38` and was tested without invoking the build.
- Executable launch with temporary `LOCALAPPDATA`, isolated JSON creation, single-instance enforcement, and minimized-window restoration on second launch: **passed**. The second launch left one visible, non-minimized QuickCopy window.
- Executable-level copy-after-exit was not independently exercised through UI automation; the source-level separate-process regression passed.
- Taskbar pinning/reopen from a pinned icon and visual icon/display-scaling checks were not performed.

## Handoff status

The original clipboard blocker is resolved and affected tests plus executable launch/focus checks pass. Keep taskbar pinning and visual checks marked unperformed in the handoff.

## Redesign review — 2026-11-09

### Result

**No new release-blocking findings.** The redesign behavior reviewed here is consistent with the requested compact charcoal UI, bottom-right placement, retained clipboard/storage behavior, and single-instance focus behavior.

### Executed checks

- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: **passed, 9 tests**.
  - This covers exact long Unicode/multiline copy, clipboard survival after process exit, Add/restart persistence, scrolling, default/minimum input visibility at `400x370` and `360x300`, failed saves, malformed storage, and startup placement against the current monitor work area.
- `.venv\Scripts\python.exe -m py_compile quickcopy.py tests\test_quickcopy.py`: **passed**.
- PowerShell parser check for `build.ps1`: **passed**.
- Rebuilt `dist\QuickCopy.exe` was present with size `10,650,166` bytes and timestamp `2026-11-09 19:59:37`.
- Executable smoke test with a temporary `LOCALAPPDATA`: **passed**.
  - The executable created isolated `QuickCopy\snippets.json`.
  - The actual decorated frame was `416x409` and its right/bottom edges were exactly 12 pixels above/right of the current monitor work area.
  - Minimizing the first instance, then launching the executable again, left one visible, restored, non-minimized window.
  - Test processes and temporary data were cleaned up by their specific process IDs/path.

### Static observations

- **Placement and ctypes:** `quickcopy.py:16-47` uses `MonitorFromPoint(..., MONITOR_DEFAULTTONEAREST)`, `GetMonitorInfoW`, the whole decorated frame from `GetWindowRect`, and `SetWindowPos` with `SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE`. The `max(work.left, right - width - 12)` and corresponding Y calculation correctly keep the window inside work areas with negative monitor coordinates; a physical multi-monitor arrangement was not available for execution.
- **Startup sequencing:** `quickcopy.py:264` schedules placement with `after_idle`, after Tk has created and measured the native frame. The executable smoke test confirmed the resulting decorated-frame placement.
- **Clipboard ownership:** `quickcopy.py:111-133` retains the previously reviewed native `CF_UNICODETEXT` ownership path. The nine-test run reconfirmed the separate-process clipboard regression.
- **Layout and interaction:** `quickcopy.py:161-264` keeps the list as the expanding grid row and reserves the new-snippet label, field/Add row, and helper text. The focused scrollbar and buttons remain adjacent to previews; the test suite confirms scrolling, focus reveal, and input visibility.
- **Assets/package:** `assets/copy-light.png`, `assets/quickcopy.png`, `assets/quickcopy.ico`, and `assets/quickcopy.svg` are present. `build.ps1:9` adds the complete `assets` directory to the one-file package, while the ICO remains the executable icon.
- **Documentation/privacy:** `README.md` identifies Windows 10/11, local `%LOCALAPPDATA%` storage, fictional screenshot data, private preview access, build instructions, and the planned `v0.2.0-preview.1` links. The release URL and private-repository permissions were not independently verified through GitHub in this review.

### Unperformed manual checks

- Taskbar pinning and reopening from the pinned icon.
- Physical multi-monitor arrangements, negative-coordinate monitor placement, and alternate display scaling.
- Visual comfort/icon appearance outside the supplied screenshots.
- Packaged-executable copy through the UI followed by clipboard read after executable exit; the source-level separate-process regression passed.

### Handoff status

The redesign is clear of new functional findings based on the executed checks. Keep the repository private and the PR draft as requested; taskbar, multi-monitor/scaling, and release-link verification remain manual or GitHub-agent checks.
