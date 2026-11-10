# Changelog

## 0.4.1-preview.1 — Packaged drag interaction

- Fixed packaged Windows dragging when the OS supplies a press and release without intermediate motion events.
- Added gray hover and selected-row states while keeping the compact UI.
- Preserved click-versus-drag behavior so fast dragging does not open the editor.
- Added native hover and selected-state screenshots and Windows file version metadata.

## 0.4.0-preview.1 — Snippet ordering

- Drag snippet text up or down to change its position. A thin line shows the destination, and the list scrolls near its edges.
- Save the new order on release; cancel with Escape or a drop outside the list.
- Keep exact text, duplicate rows, and unsaved edits intact when reordering. A failed save leaves the original order in place.
- Add Alt+Up/Down on focused copy buttons as a keyboard alternative.

## 0.3.0-preview.1 — Floating dock

- Chose the floating-dock layout: a narrow 260 × 398 window with circular copy buttons and a centered plus button.
- Removed the permanent headings, tagline, counters, and input field. Add and Edit share a panel that opens only when needed.
- Added editing, confirmed deletion, keyboard context-menu access, and an empty state. Changes keep the existing local file format.
- Simplified the logo to transparent charcoal copy outlines, matching the row icons.
- Added real, cursor-free screenshots made directly from the app's Windows buffer.
- Reused the existing build environment on repeat builds, avoiding replacement of an in-use Python executable.

## 0.2.0-preview.1 — Dark desktop preview

- Narrower 400 × 370 window with charcoal surfaces, neutral cards and buttons, and a dark native title bar on supported Windows versions.
- Startup near the lower-right of the pointer's monitor, within its taskbar work area.
- Refined graphite copy mark, matching button glyph, and multi-resolution Windows icon.
- Actual app screenshots, illustrated usage, private preview download, and contributor documentation.
- Exact Windows clipboard ownership, local persistence, and single-instance behavior retained.

## Initial desktop preview

- Scrollable snippet rows, one-click exact copying with feedback, multiline Add field, and atomic local JSON saving.
- Standalone Windows executable and taskbar pinning instructions.
- Clipboard contents remain available after the app closes.
