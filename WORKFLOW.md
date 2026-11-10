# Plan and handoffs

## Lead plan

1. Inspect the workspace and available Python/Git tools.
2. Implement one readable Tkinter module: compact scrolling rows, exact clipboard copy, multiline Add field, atomic local JSON storage.
3. Add a Windows icon and a repeatable standalone executable build for taskbar pinning.
4. Run focused checks; send requirements, code, and results to an independent reviewer. Fix confirmed findings and repeat affected checks.
5. Pass the reviewed result to a GitHub agent for a focused branch, commits, README, and draft PR if repository access exists. Leave merging to the owner.

## Reusable review request

Review independently against the user requirements: compact Windows Tkinter app; overlapping-rectangle app/copy icons; taskbar launch/focus; scrolling rows with adjacent copy buttons; exact full-text copy with brief Copied feedback; Add immediately updates and persists locally outside Git. Check long Unicode/multiline text, whitespace, enough rows to scroll, restart persistence, save/load failures, duplicate launch, and build packaging. Return findings with severity, file/line references, reproduction steps, and expected/actual behavior. Distinguish static review from checks actually executed.

## Reusable GitHub request

Inspect the reviewed changes and recorded results. Prepare a focused feature branch and clear commit(s), keeping snippets, virtual environments, and build outputs out of Git. Verify README launch/pin instructions. If an authorized existing remote and credentials are available, push and open a draft PR; do not merge. If not available, provide branch name, commit message, and ready-to-paste PR text without creating a remote or changing credentials.

## Validation record

Executed on this Windows host with bundled Python 3.12.14:

- Python compilation passed for the app and tests.
- PowerShell parser accepted `build.ps1` without syntax errors.
- Three storage tests passed: Unicode/whitespace round trip and temporary-file replacement; invalid JSON/schema preserved; independent initial examples.
- Initial sandboxed GUI checks failed at Tcl initialization (`Can't find a usable init.tcl`), and sandboxed PyInstaller download failed with `WinError 10013`. Running outside the sandbox resolved both restrictions.
- All eight tests now pass on Windows, including real Tk layout at default/minimum size, long exact Unicode/multiline copy, Add and restart persistence, scrolling, failed save, storage cases, and a separate-process clipboard-after-exit regression.
- The windowed standalone executable was built successfully with `build.ps1 -Python <base Python executable>` and rebuilt after the clipboard fix. Output: `dist\QuickCopy.exe` (ignored by Git).

An initially spawned reviewer identified a static layout issue: packing the expanding list before the input could hide Add in the compact window. The lead switched the outer layout to grid with only the list row expanding and added a default/minimum-size visibility check. That check awaits a working Tk runtime.

The user then specified existing Herdr Copilot panes only. The spawned reviewer was stopped. Herdr was not on PATH and its folders were inaccessible inside the sandbox. Approved full-path commands outside the sandbox resolved access: `herdr-app.exe ls`, `herdr-core.exe ls --json`, and Herdr's rendered frame confirmed reviewer `t1b` (top-right) and GitHub agent `t1h` (bottom-right). The lead sent the review using `send --wait` and collected results with `read`.

The designated reviewer independently passed all seven original tests and confirmed copied text disappeared after Tk exited. The lead replaced Tk's on-demand clipboard handling with immediate Windows `CF_UNICODETEXT` ownership via a temporary native window, added a separate-process regression, passed all eight tests, rebuilt the executable, and requested independent re-review in the same pane. The reviewer confirmed the fix, independently passed all eight tests, and exercised rebuilt executable launch with isolated LOCALAPPDATA, local JSON creation, single-instance enforcement, and minimized-window restoration. No actionable ctypes issue remained. See `REVIEW.md` for final findings and checks. The lead then handed the reviewed result to existing GitHub session `t1h`.

On another Windows installation, run `py -m unittest discover -s tests -v` and build with `build.ps1`, or use the generated standalone executable. User taskbar pinning, visual comfort at the user's display scale, and paste into the user's chosen destination app remain manual acceptance checks. Review records distinguish executable checks from unperformed manual checks. Leave merging to the owner.

## GitHub result

The bottom-right existing Copilot (`t1h`) read the reviewed changes and prepared `GITHUB_HANDOFF.md` with validation, intended branch `feat/quickcopy-desktop`, and exact draft PR title/body. It found no Git author identity, no repository/remote, and no authenticated GitHub host, so no commits, push, or draft PR were created. The lead added the suggested commit messages to the handoff. No credentials or remote repository were created. Both designated Copilot sessions were kept open. To finish, configure the owner's actual Git identity and intended repository, follow the handoff's base/feature-branch steps, and open the PR as draft; merging remains with the owner.
