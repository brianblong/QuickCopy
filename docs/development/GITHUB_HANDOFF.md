# QuickCopy GitHub handoff

## Final floating-dock preview

The final reviewed build uses the selected floating dock: a simple charcoal 260 x 398 Windows window that starts above the lower-right taskbar area. It supports add, exact copy, edit, confirmed delete, keyboard access, local persistence, and single-instance focus/restore. The final source and executable were independently cleared with 15/15 Windows tests and no skips.

The lead visually inspected the native app and captured the four fictional-data PNGs in `docs/images`. They contain no pointer, blue glow, retouching, or personal data. The drag-ordering screenshot is also a native fictional-data capture. Remaining manual checks are taskbar pin/reopen, physical monitor/scaling comfort, and packaged-executable copy after close; the source-level clipboard-after-exit regression passed.

## Repository status

- Repository: private `https://github.com/brianblong/QuickCopy`
- Branch: `feat/quickcopy-desktop`
- Base: `main`
- Repository-local identity: `Brian Long <161542780+brianblong@users.noreply.github.com>`
- Final reviewed source commit: recorded after the drag-ordering commit below.
- Previous merged PR: [#1](https://github.com/brianblong/QuickCopy/pull/1), merged before this update.
- Draft PR: to be created against `main` for the reviewed drag-ordering update; PR #1 cannot be reopened as draft.
- Private prerelease: to be published as `v0.4.0-preview.1` at the exact drag-ordering source commit.
- Final executable: 10,647,442 bytes, SHA-256 `9C6AA2A234DD91CF244323949B878222D43364BE7BE29ABBB27A5F58E19D52F1`

The following remain outside Git: `.venv`, `.test-data`, `__pycache__`, `build`, `dist`, release checksums, personal snippets, and local session notes. The old JPEG screenshots were removed; only the final PNG screenshots are used by the README and PR.

## Final validation

- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: 15/15 passed, no skips.
- Reviewer and lead runs completed in 10.549s and 10.284s.
- Python compilation and PowerShell parsing passed.
- Final executable passed isolated local storage, exact 12px bottom-right work-area placement, duplicate launch/minimized restoration, and same-title preview collision checks.
- Source separate-process exact Unicode clipboard-after-exit regression passed.
- Windows CI passed tests, compilation, PowerShell parsing, and build.
- Drag review: 20 tests ran, 19 passed and 1 intentional single-instance skip because a live user QuickCopy process was present. No live process was closed, focused, or killed.

## Release and PR

The release must be private, prerelease, and tagged at the exact reviewed drag-ordering source commit. Upload `dist\QuickCopy.exe` and a matching `SHA256SUMS.txt`; do not commit either file. Do not merge the new draft PR.

## Manual acceptance

1. Pin the executable to the taskbar and reopen it from the pinned icon.
2. Check the dock on another physical monitor and at the user's display scaling.
3. Copy through the packaged executable, close it, and paste into another application.
