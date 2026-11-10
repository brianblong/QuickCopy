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
- **Documentation/privacy (historical redesign review):** At that stage, `README.md` identified Windows 10/11, local `%LOCALAPPDATA%` storage, fictional screenshot data, private preview access, build instructions, and planned `v0.2.0-preview.1` links. The current README and release are documented in the final floating-dock handoff.

### Unperformed manual checks

- Taskbar pinning and reopening from the pinned icon.
- Physical multi-monitor arrangements, negative-coordinate monitor placement, and alternate display scaling.
- Visual comfort/icon appearance outside the supplied screenshots.
- Packaged-executable copy through the UI followed by clipboard read after executable exit; the source-level separate-process regression passed.

### Handoff status

The redesign is clear of new functional findings based on the executed checks. Keep the repository private and the PR draft as requested; taskbar, multi-monitor/scaling, and release-link verification remain manual or GitHub-agent checks.

## Build-script follow-up — 2026-11-09

- `build.ps1:5-8` now creates `.venv` only when `.venv\Scripts\python.exe` is absent, avoiding the repeated-build failure caused by trying to replace an interpreter currently in use by tests or another build.
- PowerShell parser check for the revised script: **passed**.
- The script still installs requirements and invokes PyInstaller through the project-local interpreter; the lead's concurrent rebuild was not duplicated by this review.

## Final floating-dock build review — 2026-11-09

### Initial finding and correction

#### Initially reported high: duplicate launch did not restore a minimized window

- **Location:** `quickcopy.py:85-109`, especially `ShowWindow(window, 9)` at line 107; the promised behavior is also documented at `README.md:19`.
- **Reproduction:**
  1. Confirm no QuickCopy process is running.
  2. Launch the final `dist\QuickCopy.exe` (`10,645,758` bytes, timestamp `2026-11-09 20:49:17`) with a temporary `LOCALAPPDATA`.
  3. Minimize its window through Win32 `ShowWindow(hwnd, SW_MINIMIZE)`.
  4. Launch the same executable again.
  5. Wait six seconds and inspect the single remaining QuickCopy window with `IsIconic`.
- **Expected:** The second launch restores and foregrounds the existing window.
- **Initial actual:** The second process exited and only one QuickCopy process/window remained, but the window appeared iconic. An external `ShowWindow(hwnd, SW_RESTORE)` control restored it.
- **Root cause:** The initial repro environment contained a reviewer-created orphan `python.exe` process (PID 37036) with a `TkTopLevel` window titled `QuickCopy`, while no process named QuickCopy was running. `claim_instance` uses `FindWindowW(None, "QuickCopy")`, so it could target that stale title window instead of the packaged app window. The process was from the failed keyboard interaction probe and was stopped by its specific PID.
- **Clean retest:** `.test-data\reviewer-restore-repro.ps1` now aborts if either a QuickCopy process or any existing `QuickCopy`-title window is present, records every matching handle/class/title/PID, and cleans only processes it launches. With no stale title window, the final executable's duplicate launch left one visible QuickCopy window with `Iconic=False`; the repro output reports `duplicate launch restore PASSED`.
- **Conclusion:** **No application finding remains.** The initial failure was test contamination, not a confirmed product regression.

### Historical final-build checks (before marker fix)

- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: **passed, 14 tests**.
- `.venv\Scripts\python.exe -m py_compile quickcopy.py tests\test_quickcopy.py`: **passed**.
- PowerShell parser check for `build.ps1`: **passed**.
- Final executable timestamp/size matched the lead report.
- Final executable isolated storage and bottom-right work-area placement: **passed** (`276x437` decorated frame, 12-pixel right/bottom margin).
- Final executable duplicate launch process collapse and minimized-window restoration: **passed** in the clean repro.
- Clean duplicate-launch evidence: `.test-data\reviewer-restore-repro.ps1` and `.test-data\reviewer-restore-repro-output.txt`; final result was **PASSED**, with one visible QuickCopy window and `final iconic=False`.

### Remaining unperformed checks

- Taskbar pinning and reopening from the pinned icon.
- Physical multi-monitor arrangements, negative-coordinate placement, and display-scaling comfort.
- Visual screenshot/icon review outside the supplied assets.
- Packaged-executable UI copy followed by clipboard read after executable exit; the source-level 14-test clipboard regression passed.

### Clearance

The apparent minimized-restore failure is cleared as reviewer test contamination. The final executable passes the clean duplicate-launch restore check. Keep taskbar pinning, multi-monitor/scaling, visual, and packaged-executable clipboard UI checks listed as unperformed manual checks.

## Marker-fix verification — 2026-11-09

- The final rebuilt executable was `dist\QuickCopy.exe`, size `10,647,442` bytes, timestamp `2026-11-09 20:56:11`.
- `quickcopy.py:85-123` now marks only the real application HWND with `SetPropW(APP_ID, 1)`, searches same-title windows with `FindWindowExW`, and restores only a window carrying that marker. `register_window` removes the marker on root destruction.
- Independent same-title collision smoke test: **passed**. A separate unmarked Tk preview window titled `QuickCopy` remained open while the packaged executable launched, was minimized, and launched a second time. The marked application window restored (`Iconic=False`), while the unmarked preview was ignored.
- The final smoke test observed exactly one marked visible application window plus the separate unmarked preview, then closed the application and preview; no QuickCopy processes remained afterward.
- The updated source integration test accounts for PyInstaller/venv launcher child-PID differences by identifying the marked HWND rather than comparing it to `Popen.pid`. This targeted collision/restore check independently passed.

## Final frozen clearance — 2026-11-09

- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: **passed, 15/15 tests, 10.549 seconds, no skips**.
- The suite includes the marked-window same-title preview collision regression, exact clipboard survival after process exit, edit/delete persistence and failure cases, keyboard menu/editor behavior, empty-list restart, scrolling, compact layout, and work-area placement.
- Final frozen executable: `dist\QuickCopy.exe`, `10,647,442` bytes, SHA-256 `9C6AA2A234DD91CF244323949B878222D43364BE7BE29ABBB27A5F58E19D52F1`.
- The independent packaged collision smoke test passed with an unmarked Tk preview open; the marked application window restored after minimize and duplicate launch, and cleanup left no QuickCopy processes.
- **Final review status: cleared for the GitHub handoff**, subject to the already documented manual checks for taskbar pinning, physical multi-monitor/scaling behavior, visual comfort, and packaged-executable UI clipboard verification.

## Drag-to-reorder review — 2026-11-09

### Result

**No new functional findings.** The drag implementation preserves the requested simple interaction: labels initiate drag after a 6-pixel threshold, copy buttons remain copy-only, release is the only persistence point, and keyboard Alt+Up/Down provides a fallback.

### Executed checks

- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: **20 tests ran: 19 passed and 1 intentional skip** in 12.251 seconds.
  - Passed coverage includes real press/motion/release reorder and restart persistence, click/cancel/outside-drop no-save behavior, held-edge autoscroll, duplicate reorder with pending edit and row actions, failed-save preservation, keyboard boundaries, edit/delete interactions, and clipboard/storage regressions.
  - `test_second_launch_restores_own_window_with_same_title_preview` was skipped because a real QuickCopy instance was already running. It was not closed, focused, or killed.
- `.venv\Scripts\python.exe -m py_compile quickcopy.py tests\test_quickcopy.py`: **passed**.
- PowerShell parser check for `build.ps1`: **passed**.
- Current rebuilt executable: `dist\QuickCopy.exe`, size `10,650,235` bytes, timestamp `2026-11-09 22:26:41`.

### Static review

- **Reorder math:** `quickcopy.py:380-417` computes the insertion position from row midpoints and adjusts for removal of the source row. Moving to the first, last, adjacent, and same position has the expected off-by-one behavior.
- **Duplicate/edit identity:** `quickcopy.py:417-431` moves by original index order, not text value, then maps `edit_index` through that order. This preserves duplicate rows and an unsaved editor target across moves.
- **Interaction boundaries:** `quickcopy.py:330-379` starts only from labels, ignores sub-threshold clicks, keeps double-click edit binding, shows the insertion line only during active drag, and cancels on Escape, outside release, render, menu, editor open, or root destruction.
- **Persistence/failure behavior:** `move()` calls `persist()` only after an active in-bounds release. A failed atomic save returns before changing UI order or editor state; no-op and keyboard-boundary moves do not write.
- **Autoscroll/callbacks:** `drag_tick()` uses an 80ms timer, scrolls within 24 pixels of the canvas edges, recomputes the target after scrolling, and cleanup cancels the outstanding timer.

### Unperformed or blocked checks

- Packaged-executable drag interaction was not run because an existing live QuickCopy instance was present; focusing or terminating it would violate the review constraints.
- Taskbar pinning, physical multi-monitor/scaling behavior, and visual comfort remain manual checks.

### Clearance

The drag-to-reorder change is **cleared for the GitHub handoff** based on the 20-test suite, static review, and source-level interaction coverage. Keep the intentional single-instance skip and packaged smoke limitation explicit in the handoff.
