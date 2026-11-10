# QuickCopy GitHub handoff

## Final 0.4.1 packaged drag preview

The final reviewed build adds reliable Windows packaged dragging to the charcoal floating dock. Hovering a snippet shows a gray highlight; clicking selects it; holding and dragging its text reorders it. A thin insertion line marks the destination, edge holding scrolls the list, and release saves the order. Escape and outside drops cancel. Fast click-then-drag does not open the editor. Add, exact copy, edit, confirmed delete, keyboard access, local persistence, and single-instance focus/restore remain supported.

The final review independently completed 23 Windows tests with no skips. Packaged review verified hover, selection, real OS dragging in both directions, outside-drop cancellation, exact clipboard copying, double-click editing with Escape cancellation, and persistence after restart using isolated fictional data. Python compilation and PowerShell parsing passed. The candidate is cleared for release.

Screenshots were regenerated through native PrintWindow capture with fictional data. The seven PNGs contain no cursor, blue glow, retouching, or personal data: `floating-dock.png`, `add-snippet.png`, `edit-snippet.png`, `copied.png`, `reorder-snippets.png`, `hover-snippet.png`, and `selected-snippet.png`.

## Repository status

- Repository: private `https://github.com/brianblong/QuickCopy`
- Branch: `feat/quickcopy-desktop`
- Base: `main`
- Draft PR: [#2](https://github.com/brianblong/QuickCopy/pull/2), targeting `main`
- Previous merged PR: [#1](https://github.com/brianblong/QuickCopy/pull/1)
- Final candidate: 10,651,578 bytes, SHA-256 `0BBE5398044FAE44DE96D9862F1C0CD5CFCDBE8C65BE79DB0BDCD44CE4203EE4`
- FileVersion/ProductVersion: `0.4.1-preview.1`

`.venv`, `.test-data`, caches, `build`, `dist`, release checksums, personal snippets, and local session notes remain outside Git. Installed copies were verified and updated without reading or changing personal snippets; their local backup records remain ignored.

## Final validation

- Full Windows suite: **23 tests passed, no skips**.
- `py_compile` passed for `quickcopy.py`, `tests\test_quickcopy.py`, and `tools\capture_screenshots.py`.
- PowerShell parsing passed for `build.ps1`.
- Packaged real-input checks passed for hover, selection, both reorder directions, outside cancellation, exact clipboard output, double-click edit, Escape, close/restart persistence, and final hash/version.
- The frozen executable was not rebuilt during this handoff.
- Taskbar pin/reopen and alternate physical monitor/scaling comfort remain manual checks.

## Historical v0.4.0 handoff

The earlier v0.4.0-preview.1 drag release used executable hash `0F7051FE7EE3BC468B0117B8D3A498DF4CA877A454AFC8B482B6C8EF47ED3F84` and 20-test local/CI reporting. It is superseded by this 0.4.1 candidate and should not be used for current download links.

## Published release

Private prerelease [`v0.4.1-preview.1`](https://github.com/brianblong/QuickCopy/releases/tag/v0.4.1-preview.1) is published at final commit `317fe3cfd0ee83b5acab1038a81c9998f3985301`. Its assets are [`QuickCopy.exe`](https://github.com/brianblong/QuickCopy/releases/download/v0.4.1-preview.1/QuickCopy.exe) and [`SHA256SUMS.txt`](https://github.com/brianblong/QuickCopy/releases/download/v0.4.1-preview.1/SHA256SUMS.txt). The downloaded executable independently matched 10,651,578 bytes, SHA-256 `0BBE5398044FAE44DE96D9862F1C0CD5CFCDBE8C65BE79DB0BDCD44CE4203EE4`, and FileVersion/ProductVersion `0.4.1-preview.1`. Windows CI run [42769369353](https://github.com/brianblong/QuickCopy/actions/runs/42769369353) passed all checks for this final documentation commit. Do not merge PR #2 or change repository visibility.
