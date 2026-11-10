# QuickCopy GitHub handoff

## Release status

The final independent review is complete. The original clipboard-after-exit bug was fixed and re-tested. The app and rebuilt executable are reviewed for the recorded checks below; taskbar pinning and visual/display checks remain unperformed and must not be represented as passed.

## Repository status

- Intended branch: `feat/quickcopy-desktop`
- Suggested app commit message: `feat: add local QuickCopy desktop snippet app`
- Suggested base commit message: `chore: initialize QuickCopy repository ignores`
- Base: a new local repository should have a `main` base before the feature branch.
- Current blocker: this folder is still not a Git repository, no Git author name/email is configured, and no existing QuickCopy destination repository was found.
- GitHub access: authenticated as `brianblong` via `gh`, with `repo` scope.
- Remote: none configured. No remote repository was created and no credentials were changed.
- Commit SHAs: none created because of the missing Git identity.
- Existing repository search: no repository matching `QuickCopy`, `quick-copy`, or `quickcopy` was found under `brianblong`; unrelated repositories were not selected.

The following must remain outside commits: `.venv`, `.test-data`, `__pycache__`, `build`, `dist`, generated snippets, and personal snippet data. The existing `.gitignore` excludes these paths and generated files.

## Final validation and review

Passed:

- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: 8 tests passed.
- `.venv\Scripts\python.exe -m py_compile quickcopy.py tests\test_quickcopy.py`: passed.
- PowerShell parser check for `build.ps1`: passed.
- Rebuilt `dist\QuickCopy.exe` launch with isolated `LOCALAPPDATA`: passed.
- Executable local JSON creation: passed.
- Single-instance enforcement and minimized-window restoration: passed.
- Independent reviewer confirmed the native Windows clipboard ownership fix and all 8 tests.

Not performed or not independently exercised:

- Taskbar pinning and reopening from a pinned icon.
- Visual/icon/display-scaling comfort checks.
- Executable-level UI automation for copy-after-exit; the source-level separate-process regression passed.
- The `py` launcher command was unavailable on this host; the bundled project Python command above passed.

## Manual verification

1. Run the app or copy `dist\QuickCopy.exe` to a permanent location.
2. Add a long multiline Unicode snippet containing leading/trailing whitespace; restart and confirm exact persistence.
3. Add enough snippets to require scrolling; scroll with the wheel and scrollbar.
4. Click a row's adjacent copy button, confirm brief `Copied.` feedback, close QuickCopy, and paste into another app.
5. Pin the permanent executable from its running taskbar icon, close it, reopen it from the pinned icon, and confirm a second launch focuses/restores one existing window.
6. Check the icon and layout at the user's display scaling.

## Ready-to-paste draft PR

**Title:** `Add QuickCopy Windows snippet app`

**Description:**

Adds a compact Windows Tkinter QuickCopy desktop app with:

- Compact scrolling saved snippets with adjacent matching copy icons.
- Copy buttons that preserve the original text, including multiline Unicode and whitespace, and briefly show `Copied.`.
- A multiline Add field that immediately updates the list and saves snippets atomically as JSON under `%LOCALAPPDATA%\QuickCopy\snippets.json`.
- Single-instance launch behavior that focuses/restores the existing window.
- A standalone windowed executable build with the overlapping-rectangle app icon.
- README instructions for launching, building, and pinning the executable to the Windows taskbar.

Validation:

- 8 project tests passed independently and for the lead, including storage, scrolling/layout, exact long-text copy, restart persistence, failed-save handling, and a separate-process clipboard-after-exit regression.
- The rebuilt executable passed isolated local-data launch, JSON creation, single-instance enforcement, and minimized-window restoration checks.
- Taskbar pinning/reopen and visual/display checks remain manual acceptance checks and were not performed.

## Landing steps

After the owner provides or creates the intended existing GitHub repository and configures a real Git author identity (including email), initialize the repository if needed, commit `.gitignore` on `main`, create `feat/quickcopy-desktop`, and commit the reviewed source, tests, icon/build setup, README, review/workflow records, and this handoff. Then push the feature branch with the existing authenticated account and open a **draft** PR with the title and description above. Do not merge.
