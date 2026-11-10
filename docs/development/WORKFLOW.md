# Plan and handoffs

## Packaged drag release — 0.4.1-preview.1

The owner reported that the earlier packaged build did not drag. The lead fixed the Windows press/release path when no intermediate `B1-Motion` event arrives, while retaining the six-pixel threshold, temporary insertion line, edge autoscroll, release-only atomic saving, and Escape/outside-drop cancellation. Hover and click selection use gray row states; fast click-then-drag does not open the editor. Copy buttons remain independent, double-click editing stays available, and Alt+Up/Down offers a keyboard alternative.

Lead and reviewer independently completed 23 Windows tests with no skips. Python compilation and PowerShell parsing passed. Packaged review independently verified gray hover, click selection, real OS drag in both directions, outside-drop cancellation, exact clipboard copying, double-click editing and Escape, and order persistence after restart using isolated fictional data. The final candidate is cleared for release.

The frozen executable is 10,651,578 bytes, SHA-256 `0BBE5398044FAE44DE96D9862F1C0CD5CFCDBE8C65BE79DB0BDCD44CE4203EE4`, with FileVersion/ProductVersion `0.4.1-preview.1`. Native PrintWindow screenshots use fictional data and contain no cursor or glow. The repository remains private, PR #2 remains a draft, and merging remains with the owner.

## Historical drag ordering update — 0.4.0-preview.1

The earlier drag-ordering review ran 20 Windows tests: 19 passed and one existing single-instance integration check was skipped because the owner's Downloads copy was running. Its v0.4.0 executable and CI details remain historical; the 0.4.1 release supersedes them.

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

On another Windows installation, run `py -m unittest discover -s tests -v` and build with `build.ps1`, or use the generated standalone executable. The redesign review and lead preview check covered the dark UI, icon treatment, and fictional-data screenshots; taskbar pinning, alternate monitor/scaling comfort, and paste from the packaged executable after exit remain manual acceptance checks. Review records distinguish completed visual checks from unperformed hardware/package checks. Leave merging to the owner.

## GitHub result

Historical v0.2 GitHub handoff: the private repository `https://github.com/brianblong/QuickCopy` was created under the authenticated `brianblong` account, and the initial draft PR and `v0.2.0-preview.1` release were published. The current branch, v0.3 release, final screenshots, and final validation are recorded in the final floating-dock handoff below.

## Dark desktop redesign

The owner requested a narrower window directly above the taskbar, a modern charcoal/gray interface inspired by Herdr, a refined dark copy mark, and a complete private GitHub presentation with screenshots and downloads.

The lead implemented a 400 × 370 window (minimum 360 × 300), dark cards/input/buttons/scrollbar, a supported Windows dark title bar, and whole-window positioning within the pointer monitor's work area. New source artwork and antialiased PNG/multi-resolution ICO assets keep the app and copy buttons visually consistent. The app still uses only the Python standard library.

The lead inspected the actual Windows preview with the computer-use skill, entered fictional sample text, clicked Add and Copy, and captured three actual app screenshots in `docs/images`. No personal snippet data was used. README now includes screenshots, usage, storage/backup, launch/pin/update/build instructions, and the published private preview download. CONTRIBUTING, CHANGELOG, issue and PR templates support the repository workflow.

Historical v0.2 lead validation: nine Windows tests passed, including decorated-window taskbar clearance and prior clipboard/persistence regressions; `git diff --check` passed; the standalone executable rebuilt with all new assets. The final v0.3 validation is recorded in the final floating-dock section.

Independent redesign review completed in `t1b`: no new blocking findings. The reviewer passed all nine tests, Python compilation and PowerShell parsing, and exercised the rebuilt executable with isolated LOCALAPPDATA. The decorated frame opened exactly 12 pixels inside the monitor's right/bottom work-area edges; local JSON creation, duplicate launch and minimized restoration passed. Taskbar pin/reopen, alternate physical monitor/scaling arrangements, and packaged UI copy-after-exit remain unperformed; the source-level process-exit clipboard test passed. See the redesign section in `REVIEW.md`.

## Selected floating dock

The owner selected concept 4 and requested the simplest UI, edit/delete, a charcoal copy-outline logo, bottom-right startup, and natural repository writing with clean screenshots. The lead implemented a 260 × 398 dock (minimum 240 × 320), circular icon-only copy buttons, a centered plus button, and a hidden Add/Edit panel. Right-click or Shift+F10 opens Edit/Delete; double-click text edits; deletion confirms before saving. The native work-area placement and exact Windows clipboard ownership are retained.

Fourteen Windows regressions passed for the lead, including exact long-text editing, deletion/cancel, duplicate-row indexing, empty restart, failed-save preservation, keyboard-menu positioning, and all prior clipboard/storage/layout checks. The lead fixed pending callback cleanup and keyboard event propagation, and verified a successful rebuild after making build.ps1 reuse an existing environment. The final reviewed-build candidate is 10,645,758 bytes with SHA-256 `7B19BA5124A9B91C21C4A56257CFBBCD645B360CA93C3253A9AAB59957EDC7A1`.

The screenshot utility creates a separate temporary snippet file with fictional data, lets native controls paint, and uses PrintWindow to save untouched app pixels without a cursor or automation overlay. The lead inspected the resulting floating-dock, add, edit, and copied states. Existing reviewer t1b cleared the final code and executable; the private v0.3.0 preview is published below. Merging remains with the owner.

The reviewer found a stale source preview sharing the application's title during a restore probe. The lead hardened the existing-instance handoff with a window marker applied only by the real main process, then added a same-title collision regression. All fifteen source tests passed for the lead; the reviewer independently passed the final packaged collision/restore test. The frozen final executable is 10,647,442 bytes, SHA-256 `9C6AA2A234DD91CF244323949B878222D43364BE7BE29ABBB27A5F58E19D52F1`. The earlier build/hash above is historical and was not published.

## Final floating-dock GitHub handoff

The final reviewed floating-dock source remains at `2ab018702e09a13d84455fa5ab3ca336042aad69`, with merged PR #1 and private v0.3 release history preserved. The current drag-ordering source commit is `24740258cfc5c2346485db8a3449d065e571b597`; draft PR [#2](https://github.com/brianblong/QuickCopy/pull/2) targets `main`, and private prerelease [`v0.4.0-preview.1`](https://github.com/brianblong/QuickCopy/releases/tag/v0.4.0-preview.1) is tagged at that exact commit with the final executable and checksum. The current executable is 10,650,235 bytes with SHA-256 `0F7051FE7EE3BC468B0117B8D3A498DF4CA877A454AFC8B482B6C8EF47ED3F84`. Local review ran 20 tests: 19 passed and one intentional live-single-instance check was skipped; fresh Windows CI run [42756379878](https://github.com/brianblong/QuickCopy/actions/runs/42756379878) ran all 20 with no skips and passed compilation, PowerShell parsing, and build. Packaged drag interaction, taskbar pinning, alternate physical monitors/scaling, and packaged UI copy-after-close remain manual checks. The repository remains private.
