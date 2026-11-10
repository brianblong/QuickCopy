"""QuickCopy: a small, local-only Tkinter clipboard app."""

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import sys
import time
import tkinter as tk
from tkinter import messagebox, ttk


EXAMPLES = [
    "https://www.linkedin.com/in/example",
    "https://github.com/example",
    "Certification ID: EXAMPLE-12345",
]
APP_ID = "QuickCopy.Desktop.1"


def data_path():
    return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "QuickCopy" / "snippets.json"


def load_snippets(path):
    if not path.exists():
        return EXAMPLES.copy()
    items = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(items, list) or any(not isinstance(item, str) for item in items):
        raise ValueError("Expected a JSON list of text snippets.")
    return items


def save_snippets(path, items):
    """Replace atomically so an interrupted write cannot truncate the saved file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        json.dump(items, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def claim_instance():
    """Keep a Windows mutex open; a second launch restores the existing window."""
    if sys.platform != "win32":
        return None
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    handle = kernel.CreateMutexW(None, False, "Local\\" + APP_ID)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    if ctypes.get_last_error() != 183:  # ERROR_ALREADY_EXISTS
        return handle
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle(handle)
    user = ctypes.WinDLL("user32", use_last_error=True)
    user.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    user.FindWindowW.restype = wintypes.HWND
    user.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user.SetForegroundWindow.argtypes = [wintypes.HWND]
    for _ in range(40):
        window = user.FindWindowW(None, "QuickCopy")
        if window:
            user.ShowWindow(window, 9)  # SW_RESTORE
            user.SetForegroundWindow(window)
            break
        time.sleep(0.1)
    raise SystemExit(0)


def copy_icon(master):
    """The same two outline rectangles used by assets/quickcopy.ico."""
    icon = tk.PhotoImage(master=master, width=24, height=24)
    for left, top, right, bottom in [(9, 3, 21, 16), (3, 8, 15, 21)]:
        for x, y, width, height in [
            (left, top, right - left, 2), (left, bottom - 2, right - left, 2),
            (left, top, 2, bottom - top), (right - 2, top, 2, bottom - top),
        ]:
            icon.put("#245c9c", to=(x, y, x + width, y + height))
    return icon


def write_clipboard(root, text):
    if sys.platform != "win32":
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        return
    # Tk renders clipboard text on demand. Give Windows the actual bytes now,
    # so they remain available even after our window and process have closed.
    user = ctypes.WinDLL("user32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel.GlobalAlloc.restype = wintypes.HGLOBAL
    kernel.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel.GlobalLock.restype = ctypes.c_void_p
    kernel.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel.GlobalFree.argtypes = [wintypes.HGLOBAL]
    user.OpenClipboard.argtypes = [wintypes.HWND]
    user.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user.SetClipboardData.restype = wintypes.HANDLE
    user.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR,
                                   wintypes.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, wintypes.HWND, wintypes.HMENU,
                                   wintypes.HINSTANCE, ctypes.c_void_p]
    user.CreateWindowExW.restype = wintypes.HWND
    user.DestroyWindow.argtypes = [wintypes.HWND]
    # A hidden native owner avoids Tk clearing its own clipboard on shutdown.
    owner = user.CreateWindowExW(0, "STATIC", "", 0, 0, 0, 0, 0, None, None, None, None)
    if not owner:
        raise ctypes.WinError(ctypes.get_last_error())
    encoded = text.encode("utf-16-le") + b"\x00\x00"
    handle = kernel.GlobalAlloc(0x0002, len(encoded))  # GMEM_MOVEABLE
    if not handle:
        user.DestroyWindow(owner)
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        pointer = kernel.GlobalLock(handle)
        if not pointer:
            raise ctypes.WinError(ctypes.get_last_error())
        ctypes.memmove(pointer, encoded, len(encoded))
        kernel.GlobalUnlock(handle)
        for attempt in range(10):
            if user.OpenClipboard(owner):
                break
            if attempt == 9:
                raise ctypes.WinError(ctypes.get_last_error())
            time.sleep(0.01)
        try:
            if not user.EmptyClipboard() or not user.SetClipboardData(13, handle):  # CF_UNICODETEXT
                raise ctypes.WinError(ctypes.get_last_error())
            handle = None  # Windows now owns and eventually frees this memory.
        finally:
            user.CloseClipboard()
    finally:
        if handle:
            kernel.GlobalFree(handle)
        user.DestroyWindow(owner)


class QuickCopy:
    def __init__(self, root, path=None):
        self.root = root
        self.path = path if path is not None else data_path()
        self.items = load_snippets(self.path)
        if not self.path.exists():
            save_snippets(self.path, self.items)
        root.title("QuickCopy")
        root.geometry("460x310")
        root.minsize(360, 240)
        self.icon = copy_icon(root)
        root.iconphoto(True, self.icon)
        icon_path = Path(__file__).resolve().parent / "assets" / "quickcopy.ico"
        if sys.platform == "win32" and icon_path.exists():
            root.iconbitmap(str(icon_path))

        outer = ttk.Frame(root, padding=10)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(1, weight=1)
        ttk.Label(outer, text="Saved snippets", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        area = ttk.Frame(outer)
        area.grid(row=1, column=0, sticky="nsew", pady=(6, 8))
        self.canvas = tk.Canvas(area, highlightthickness=0, takefocus=True)
        scrollbar = ttk.Scrollbar(area, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.rows = ttk.Frame(self.canvas)
        self.row_window = self.canvas.create_window((0, 0), window=self.rows, anchor="nw")
        self.rows.bind("<Configure>", self.update_scroll)
        self.canvas.bind("<Configure>", self.resize_rows)
        root.bind_all("<MouseWheel>", self.mousewheel)
        self.canvas.bind("<Next>", lambda event: self.canvas.yview_scroll(1, "pages"))
        self.canvas.bind("<Prior>", lambda event: self.canvas.yview_scroll(-1, "pages"))

        entry_area = ttk.Frame(outer)
        entry_area.grid(row=2, column=0, sticky="ew")
        self.entry = tk.Text(entry_area, height=2, width=25, wrap="word", font=("Segoe UI", 10), undo=True)
        self.entry.pack(side="left", fill="x", expand=True)
        ttk.Button(entry_area, text="Add", command=self.add).pack(side="right", padx=(8, 0))
        ttk.Label(outer, text="Paste text above. Add saves it on this PC.").grid(row=3, column=0, sticky="w", pady=(5, 0))
        for item in self.items:
            self.add_row(item)

    def update_scroll(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_rows(self, event):
        self.canvas.itemconfigure(self.row_window, width=event.width)
        for row in self.rows.winfo_children():
            row.winfo_children()[0].configure(wraplength=max(100, event.width - 100))

    def mousewheel(self, event):
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        while widget is not None:
            if widget == self.canvas:
                self.canvas.yview_scroll(-int(event.delta / 120), "units")
                return "break"
            widget = widget.master

    def add_row(self, text):
        row = ttk.Frame(self.rows, padding=(0, 5))
        row.pack(fill="x")
        preview = text.replace("\r", " ").replace("\n", " ")
        if len(preview) > 160:
            preview = preview[:157] + "..."
        ttk.Label(row, text=preview, wraplength=max(100, self.canvas.winfo_width() - 100)).pack(
            side="left", fill="x", expand=True)
        button = ttk.Button(row, image=self.icon, text="Copy", compound="left", width=8)
        button.configure(command=lambda: self.copy(text, button))
        button.pack(side="right", padx=(6, 0))
        button.bind("<FocusIn>", lambda event: self.reveal(row))

    def reveal(self, row):
        self.root.update_idletasks()
        top = self.canvas.canvasy(0)
        if row.winfo_y() < top or row.winfo_y() + row.winfo_height() > top + self.canvas.winfo_height():
            self.canvas.yview_moveto(row.winfo_y() / max(1, self.rows.winfo_height()))

    def copy(self, text, button):
        try:
            write_clipboard(self.root, text)
        except (OSError, tk.TclError) as error:
            messagebox.showerror("Could not copy", str(error), parent=self.root)
            return
        button.configure(text="Copied.")
        # Each click owns its reset, so repeated clicks keep feedback visible.
        if hasattr(button, "reset_job"):
            self.root.after_cancel(button.reset_job)
        button.reset_job = self.root.after(1200, lambda: button.configure(text="Copy"))

    def add(self):
        text = self.entry.get("1.0", "end-1c")  # Exclude only Tk's extra trailing newline.
        if not text.strip():
            return
        try:
            save_snippets(self.path, self.items + [text])
        except OSError as error:
            messagebox.showerror("Could not save", str(error), parent=self.root)
            return
        self.items.append(text)
        self.add_row(text)
        self.entry.delete("1.0", "end")
        self.root.update_idletasks()
        self.canvas.yview_moveto(1)


def main():
    instance_handle = claim_instance()  # Keep the mutex alive for the process lifetime.
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    root.withdraw()
    try:
        QuickCopy(root)
    except (OSError, ValueError) as error:
        messagebox.showerror("QuickCopy could not open saved snippets",
                             f"{data_path()}\n\n{error}\n\nYour saved file has not been replaced.", parent=root)
        root.destroy()
        return
    root.deiconify()
    root.mainloop()


if __name__ == "__main__":
    main()
