# QuickCopy GitHub handoff

## Final floating-dock preview

The current reviewed build adds simple drag-to-reorder to the selected charcoal floating dock. It supports add, exact copy, edit, confirmed delete, keyboard access, local persistence, and single-instance focus/restore. Local review ran 20 tests with 19 passed and 1 intentional skip; fresh Windows CI ran all 20 with no skips.

The lead visually inspected the native app and captured the four fictional-data PNGs in `docs/images`. They contain no pointer, blue glow, retouching, or personal data. The drag-ordering screenshot is also a native fictional-data capture. Remaining manual checks are taskbar pin/reopen, physical monitor/scaling comfort, and packaged-executable copy after close; the source-level clipboard-after-exit regression passed.

## Repository status

- Repository: private `https://github.com/brianblong/QuickCopy`
- Branch: `feat/quickcopy-desktop`
- Base: `main`
- Repository-local identity: `Brian Long <161542780+brianblong@users.noreply.github.com>`
- Final reviewed source commit: `24740258cfc5c2346485db8a3449d065e571b597` (`feat: add drag ordering for saved snippets`)
- Previous merged PR: [#1](https://github.com/brianblong/QuickCopy/pull/1), merged before this update.
- Draft PR: [#2](https://github.com/brianblong/QuickCopy/pull/2), targeting `main`; PR #1 cannot be reopened as draft.
- Private prerelease: [`v0.4.0-preview.1`](https://github.com/brianblong/QuickCopy/releases/tag/v0.4.0-preview.1), tagged at the exact drag-ordering source commit.
- Final executable: 10,650,235 bytes, SHA-256 `0F7051FE7EE3BC468B0117B8D3A498DF4CA877A454AFC8B482B6C8EF47ED3F84`

The following remain outside Git: `.venv`, `.test-data`, `__pycache__`, `build`, `dist`, release checksums, personal snippets, and local session notes. The old JPEG screenshots were removed; only the final PNG screenshots are used by the README and PR.

## Final validation

- Historical v0.3 baseline: `.venv\Scripts\python.exe -m unittest discover -s tests -v` passed 15/15 with no skips.
- Reviewer and lead runs completed in 10.549s and 10.284s.
- Python compilation and PowerShell parsing passed.
- Final executable passed isolated local storage, exact 12px bottom-right work-area placement, duplicate launch/minimized restoration, and same-title preview collision checks.
- Source separate-process exact Unicode clipboard-after-exit regression passed.
- Windows CI passed tests, compilation, PowerShell parsing, and build.
- Drag review: 20 tests ran, 19 passed and 1 intentional single-instance skip because a live user QuickCopy process was present. No live process was closed, focused, or killed.
- Fresh Windows CI run [42756379878](https://github.com/brianblong/QuickCopy/actions/runs/42756379878) passed all 20 tests with no skips, plus compilation, PowerShell parsing, and the build.
- Final drag executable: 10,650,235 bytes, SHA-256 `0F7051FE7EE3BC468B0117B8D3A498DF4CA877A454AFC8B482B6C8EF47ED3F84`.

## Release and PR

The release is private, prerelease, and tagged at the exact reviewed drag-ordering source commit. Its assets are [`QuickCopy.exe`](https://github.com/brianblong/QuickCopy/releases/download/v0.4.0-preview.1/QuickCopy.exe) and [`SHA256SUMS.txt`](https://github.com/brianblong/QuickCopy/releases/download/v0.4.0-preview.1/SHA256SUMS.txt); the executable hash is `0F7051FE7EE3BC468B0117B8D3A498DF4CA877A454AFC8B482B6C8EF47ED3F84`. Do not merge the new draft PR.

## Manual acceptance

1. Pin the executable to the taskbar and reopen it from the pinned icon.
2. Check the dock on another physical monitor and at the user's display scaling.
3. Copy through the packaged executable, close it, and paste into another application.
