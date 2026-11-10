# Contributing to QuickCopy

QuickCopy is a private Windows preview. Keep changes focused and readable. The current feature set is a small local dock for adding, viewing, copying, editing, and deleting snippets.

## Working on a change

1. Start from the current reviewed branch and describe the user-visible behavior you are changing.
2. Keep UI, clipboard, and JSON storage logic straightforward. Avoid runtime dependencies unless they solve a concrete problem.
3. Run `py -m unittest discover -s tests -v` on Windows with Tkinter. Tests use temporary storage and fictional clipboard text.
4. For UI changes, inspect the default and minimum window sizes. Use fictional snippets for screenshots.
5. Run `build.ps1`, then check launch, add/edit/delete, long multiline copy, restart persistence, scrolling, duplicate launch, and taskbar behavior.
6. Open a draft PR with actual test results, screenshots when useful, and any checks that remain manual. Leave merging to the owner.

Do not commit `.venv`, `build`, `dist`, `.test-data`, personal snippets, credentials, or screenshots containing personal data. Snippets live under `%LOCALAPPDATA%\QuickCopy`, outside the project.

## Artwork and screenshots

`assets/quickcopy.svg` is the editable charcoal copy mark. `tools/generate_icons.py` generates the matching PNG and ICO assets. `tools/capture_screenshots.py` is developer-only and captures native Windows app pixels using fictional temporary data; it is not part of the application runtime.

## Reporting a problem

Include your Windows version, display scale, monitor/taskbar arrangement, whether you used the executable or Python, and steps using fictional sample text. State what you expected and what happened. Do not attach your snippet file or personal clipboard contents.
