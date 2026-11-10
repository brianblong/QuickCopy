# Contributing to QuickCopy

QuickCopy is a private preview. Keep changes small enough that someone learning Python can read and explain them. The current scope is adding, viewing, and copying local snippets.

## Working on a change

1. Start from the current reviewed branch and create a focused branch. Describe the user-visible problem and expected behavior.
2. Keep UI, clipboard, and saving logic straightforward. Avoid runtime dependencies unless they solve a concrete problem.
3. Run `py -m unittest discover -s tests -v` on Windows with Tkinter. The tests use temporary storage and overwrite the clipboard with test text.
4. For UI changes, inspect the actual window at its default and minimum sizes. Use fictional snippets for screenshots.
5. Run `build.ps1`, then check the executable: launch, copy long multiline text, close/paste, Add/reopen, scroll, minimize/relaunch, and taskbar pin/reopen.
6. Open a draft PR with the behavior change, screenshots if relevant, actual test results, and anything still unverified. Request independent review. Leave merging to the owner.

Do not commit `.venv`, `build`, `dist`, `.test-data`, personal snippets, credentials, or screenshots of personal data. Snippets live under `%LOCALAPPDATA%\QuickCopy`, outside the project.

## Artwork

`assets/quickcopy.svg` is the editable copy mark. `tools/generate_icons.py` generates matching antialiased PNG and multi-size ICO assets. With Pillow installed in a development environment, run `python tools/generate_icons.py`. Pillow is not required to run QuickCopy or build using the checked-in assets.

## Reporting a problem

Include your Windows version, display scale, monitor/taskbar arrangement, whether you used the executable or Python, and steps using fictional sample text. State what you expected and what happened. Omit your actual snippet file and personal clipboard contents.
