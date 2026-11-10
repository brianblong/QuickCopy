"""QuickCopy: a small, local-only Tkinter clipboard app."""

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import sys
import time
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk


EXAMPLES = [
    "https://www.linkedin.com/in/example",
    "https://github.com/example",
    "Certification ID: EXAMPLE-12345",
]
APP_ID = "QuickCopy.Desktop.1"
ASSETS = Path(__file__).resolve().parent / "assets"
BG, SURFACE, BORDER = "#1b1e22", "#252930", "#343a43"
TEXT, MUTED = "#e7e9ed", "#9ca3ae"


def position_window(root):
    """Place the whole decorated window inside the pointer monitor's work area."""
    if sys.platform != "win32":
        return
    user = ctypes.WinDLL("user32", use_last_error=True)

    class MonitorInfo(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("monitor", wintypes.RECT),
                    ("work", wintypes.RECT), ("flags", wintypes.DWORD)]

    user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user.GetAncestor.restype = wintypes.HWND
    user.MonitorFromPoint.argtypes = [wintypes.POINT, wintypes.DWORD]
    user.MonitorFromPoint.restype = wintypes.HANDLE
    user.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MonitorInfo)]
    user.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    pointer, rect = wintypes.POINT(), wintypes.RECT()
    user.GetCursorPos(ctypes.byref(pointer))
    info = MonitorInfo(size=ctypes.sizeof(MonitorInfo))
    window = user.GetAncestor(root.winfo_id(), 2)  # GA_ROOT, includes native title bar.
    if user.GetMonitorInfoW(user.MonitorFromPoint(pointer, 2), ctypes.byref(info)) and user.GetWindowRect(window, ctypes.byref(rect)):
        x = max(info.work.left, info.work.right - (rect.right - rect.left) - 12)
        y = max(info.work.top, info.work.bottom - (rect.bottom - rect.top) - 12)
        user.SetWindowPos(window, None, x, y, 0, 0, 0x0015)  # no resize, reorder, or focus change
    # Windows 10/11 title-bar colors. Older Windows may ignore these attributes.
    dwm = ctypes.WinDLL("dwmapi")
    dwm.DwmSetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD,
                                        ctypes.c_void_p, wintypes.DWORD]
    for attribute, value in [(20, 1), (33, 2), (35, 0x00221e1b), (36, 0x00ede9e7)]:
        setting = ctypes.c_int(value)
        dwm.DwmSetWindowAttribute(window, attribute, ctypes.byref(setting), ctypes.sizeof(setting))


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
    user.FindWindowExW.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]
    user.FindWindowExW.restype = wintypes.HWND
    user.GetPropW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
    user.GetPropW.restype = wintypes.HANDLE
    user.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user.SetForegroundWindow.argtypes = [wintypes.HWND]
    for _ in range(40):
        window = None
        while True:
            window = user.FindWindowExW(None, window, None, "QuickCopy")
            if not window:
                break
            if user.GetPropW(window, APP_ID):
                user.ShowWindow(window, 9)  # SW_RESTORE
                user.SetForegroundWindow(window)
                raise SystemExit(0)
        time.sleep(0.1)
    raise SystemExit(0)


def register_window(root):
    """Mark only the real single-instance window, not tests or design previews."""
    if sys.platform != "win32":
        return
    root.update_idletasks()
    user = ctypes.WinDLL("user32", use_last_error=True)
    user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user.GetAncestor.restype = wintypes.HWND
    user.SetPropW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.HANDLE]
    user.RemovePropW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
    user.RemovePropW.restype = wintypes.HANDLE
    window = user.GetAncestor(root.winfo_id(), 2)
    if not user.SetPropW(window, APP_ID, 1):
        raise ctypes.WinError(ctypes.get_last_error())
    root.bind("<Destroy>", lambda event: user.RemovePropW(window, APP_ID)
              if event.widget == root else None, add="+")


def copy_icon(master):
    return tk.PhotoImage(master=master, file=str(ASSETS / "copy-light.png"))


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


class RoundButton(tk.Canvas):
    """A small, keyboard-focusable icon button with no permanent caption."""
    def __init__(self, parent, command, image=None, symbol="", size=34, light=False):
        super().__init__(parent, width=size, height=size, background=BG,
                         highlightthickness=0, takefocus=True, cursor="hand2")
        self.command, self.image, self.symbol = command, image, symbol
        self.size, self.light, self.hover = size, light, False
        prefix = "plus" if light else "button"
        self.disks = [tk.PhotoImage(master=self, file=str(ASSETS / f"{prefix}{suffix}.png"))
                      for suffix in ("", "-hover")]
        self.bind("<Button-1>", lambda event: self.invoke())
        self.bind("<Return>", self.press_key)
        self.bind("<space>", self.press_key)
        self.bind("<Enter>", lambda event: self.set_hover(True))
        self.bind("<Leave>", lambda event: self.set_hover(False))
        self.bind("<FocusIn>", lambda event: self.draw())
        self.bind("<FocusOut>", lambda event: self.draw())
        self.draw()

    def invoke(self):
        return self.command()

    def press_key(self, event):
        self.invoke()
        return "break"

    def set_hover(self, hovered):
        self.hover = hovered
        self.draw()

    def draw(self):
        self.delete("all")
        self.create_image(self.size / 2, self.size / 2, image=self.disks[int(self.hover)])
        if self.focus_get() == self:
            self.create_oval(2, 2, self.size - 2, self.size - 2, outline="#a8b5c8")
        if self.image is not None:
            self.create_image(self.size / 2, self.size / 2, image=self.image)
        else:
            self.create_text(self.size / 2, self.size / 2 - 1, text=self.symbol,
                             fill="#242930" if self.light else TEXT, font=("Segoe UI", 19))


class QuickCopy:
    def __init__(self, root, path=None):
        self.root = root
        self.path = path if path is not None else data_path()
        self.items = load_snippets(self.path)
        if not self.path.exists():
            save_snippets(self.path, self.items)
        self.edit_index = None
        self.copy_job = None
        self.position_job = None
        self.drag = None
        self.drag_job = None
        self.selected_index = None
        self.hover_index = None
        root.bind("<Destroy>", self.cleanup, add="+")
        root.title("QuickCopy")
        root.geometry("260x398")
        root.minsize(240, 320)
        root.configure(background=BG)
        root.option_add("*Font", ("Segoe UI", 10))
        self.text_font = tkfont.Font(root=root, family="Segoe UI", size=10)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TButton", background="#303640", foreground=TEXT,
                        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER,
                        padding=(10, 6), relief="flat")
        style.map("TButton", background=[("active", "#414852")])
        style.configure("Vertical.TScrollbar", background="#454c57", troughcolor=BG,
                        bordercolor=BG, lightcolor=BG, darkcolor=BG, borderwidth=0, width=5)
        style.map("Vertical.TScrollbar", background=[("active", "#626c7a"), ("!active", "#454c57")])
        style.layout("Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {
            "sticky": "ns", "children": [("Vertical.Scrollbar.thumb", {"sticky": "nsew"})]})])
        self.icon = copy_icon(root)
        self.check_icon = tk.PhotoImage(master=root, file=str(ASSETS / "check-light.png"))
        self.logo = tk.PhotoImage(master=root, file=str(ASSETS / "quickcopy.png")).subsample(8)
        root.iconphoto(True, self.logo)
        if sys.platform == "win32":
            root.iconbitmap(str(ASSETS / "quickcopy.ico"))

        outer = ttk.Frame(root, padding=(12, 5, 10, 8))
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)
        area = ttk.Frame(outer)
        area.grid(row=0, column=0, sticky="nsew")
        self.canvas = tk.Canvas(area, background=BG, highlightthickness=0, takefocus=True)
        self.scrollbar = ttk.Scrollbar(area, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_changed)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.rows = ttk.Frame(self.canvas)
        self.row_window = self.canvas.create_window((0, 0), window=self.rows, anchor="nw")
        self.rows.bind("<Configure>", self.update_scroll)
        self.canvas.bind("<Configure>", self.resize_rows)
        root.bind_all("<MouseWheel>", self.mousewheel)
        self.canvas.bind("<Next>", lambda event: self.canvas.yview_scroll(1, "pages"))
        self.canvas.bind("<Prior>", lambda event: self.canvas.yview_scroll(-1, "pages"))
        self.canvas.bind("<Button-1>", self.clear_selection)
        self.empty = tk.Label(self.canvas, text="Add your first snippet", background=BG, foreground=MUTED)
        self.drop_line = tk.Frame(self.canvas, background="#a8b5c8", height=2)
        root.bind("<Escape>", self.cancel_drag, add="+")

        self.editor = ttk.Frame(outer, padding=(0, 8, 0, 3))
        self.editor.columnconfigure(0, weight=1)
        self.editor_title = ttk.Label(self.editor, text="Add snippet")
        self.editor_title.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.entry = tk.Text(self.editor, height=4, width=20, wrap="word", undo=True,
                             background=SURFACE, foreground=TEXT, insertbackground=TEXT,
                             selectbackground="#465165", selectforeground="#ffffff", relief="flat",
                             highlightthickness=1, highlightbackground=BORDER,
                             highlightcolor="#8993a3", padx=7, pady=7)
        self.entry.grid(row=1, column=0, sticky="ew")
        self.save_button = ttk.Button(self.editor, text="Save", command=self.add)
        self.save_button.grid(row=2, column=0, sticky="e", pady=(5, 0))
        self.entry.bind("<Control-Return>", self.editor_key)
        self.entry.bind("<Escape>", self.editor_key)

        footer = ttk.Frame(outer, height=52)
        footer.grid(row=2, column=0, sticky="ew")
        footer.pack_propagate(False)
        self.plus = RoundButton(footer, command=self.toggle_editor, symbol="+", size=40, light=True)
        self.plus.place(relx=0.5, rely=0.5, anchor="center")
        self.feedback = tk.Label(footer, text="", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        self.feedback.place(x=1, rely=0.5, anchor="w")
        self.menu = tk.Menu(root, tearoff=False, background=SURFACE, foreground=TEXT,
                            activebackground="#414852", activeforeground=TEXT, borderwidth=0)
        self.render_rows()
        self.position_job = root.after_idle(self.place)

    def place(self):
        self.position_job = None
        position_window(self.root)

    def cleanup(self, event):
        if event.widget == self.root:
            for job in (self.copy_job, self.position_job, self.drag_job):
                if job is not None:
                    self.root.after_cancel(job)

    def update_scroll(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def scroll_changed(self, first, last):
        self.scrollbar.set(first, last)
        if float(first) <= 0 and float(last) >= 1:
            self.scrollbar.pack_forget()
        elif not self.scrollbar.winfo_manager():
            self.scrollbar.pack(side="right", fill="y", before=self.canvas)

    def preview(self, text, width):
        text = " ".join(text.splitlines())[:160]
        if self.text_font.measure(text) <= width:
            return text
        while text and self.text_font.measure(text + "…") > width:
            text = text[:-1]
        return text + "…"

    def resize_rows(self, event):
        self.canvas.itemconfigure(self.row_window, width=event.width)
        for index, row in enumerate(self.rows.winfo_children()):
            row.winfo_children()[0].configure(text=self.preview(self.items[index], max(60, event.width - 66)))

    def mousewheel(self, event):
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        while widget is not None:
            if widget == self.canvas:
                self.canvas.yview_scroll(-int(event.delta / 120), "units")
                return "break"
            widget = widget.master

    def reset_copy_feedback(self):
        if self.copy_job is not None:
            self.root.after_cancel(self.copy_job)
            self.copy_job = None
        self.feedback.configure(text="")
        for row in self.rows.winfo_children():
            button = row.winfo_children()[1]
            button.image = self.icon
            button.draw()

    def render_rows(self):
        self.cancel_drag()
        self.hover_index = None
        self.reset_copy_feedback()
        for row in self.rows.winfo_children():
            row.destroy()
        if self.items:
            self.empty.place_forget()
        else:
            self.empty.place(relx=0.5, rely=0.4, anchor="center")
        for index, text in enumerate(self.items):
            row = ttk.Frame(self.rows, padding=(2, 8, 3, 8))
            row.pack(fill="x")
            row.columnconfigure(0, weight=1)
            label = tk.Label(row, text=self.preview(text, max(60, self.canvas.winfo_width() - 66)),
                             width=1, anchor="w", background=BG, foreground=TEXT, cursor="hand2",
                             padx=7, pady=5, highlightthickness=1, highlightbackground=BG)
            label.grid(row=0, column=0, sticky="nsew")
            button = RoundButton(row, command=lambda i=index: self.copy(i), image=self.icon)
            button.grid(row=0, column=1, padx=(6, 0))
            button.bind("<FocusIn>", lambda event, r=row: self.reveal(r), add="+")
            button.bind("<Alt-Up>", lambda event, i=index: self.move_key(i, -1))
            button.bind("<Alt-Down>", lambda event, i=index: self.move_key(i, 1))
            label.bind("<Button-1>", lambda event, i=index: self.begin_drag(i, event))
            label.bind("<Enter>", lambda event, i=index: self.hover_row(i))
            label.bind("<Leave>", lambda event: self.hover_row(None))
            label.bind("<B1-Motion>", self.drag_motion)
            label.bind("<ButtonRelease-1>", self.end_drag)
            label.bind("<Double-Button-1>", lambda event, i=index: self.begin_drag(i, event, edit_on_click=True))
            for widget in (row, label, button):
                widget.bind("<Button-3>", lambda event, i=index: self.show_menu(i, event))
                widget.bind("<Shift-F10>", lambda event, i=index: self.show_menu(i, event))
                widget.bind("<Menu>", lambda event, i=index: self.show_menu(i, event))
        self.paint_rows()

    def paint_rows(self):
        for index, row in enumerate(self.rows.winfo_children()):
            active = self.drag is not None and self.drag["active"] and self.drag["source"] == index
            if active:
                background, border = "#465565", "#a8b5c8"
            elif self.selected_index == index:
                background, border = "#3b4552", "#77879c"
            elif self.hover_index == index:
                background, border = "#30363e", "#454d59"
            else:
                background, border = BG, BG
            row.winfo_children()[0].configure(background=background, foreground=TEXT,
                highlightbackground=border, highlightcolor=border, cursor="fleur" if active else "hand2")

    def hover_row(self, index):
        self.hover_index = index
        self.paint_rows()

    def clear_selection(self, event=None):
        self.cancel_drag()
        self.selected_index = None
        self.paint_rows()

    def begin_drag(self, index, event, edit_on_click=False):
        self.cancel_drag()
        self.selected_index = index
        label = self.rows.winfo_children()[index].winfo_children()[0]
        label.grab_set()  # Keep receiving real motion/release outside the small text box.
        self.canvas.focus_set()
        self.drag = {"source": index, "target": index, "start": (event.x_root, event.y_root),
                     "pointer": (event.x_root, event.y_root), "active": False,
                     "widget": label, "edit_on_click": edit_on_click}
        self.paint_rows()

    def drag_motion(self, event):
        if self.drag is None:
            return
        self.drag["pointer"] = (event.x_root, event.y_root)
        if not self.drag["active"]:
            x, y = self.drag["start"]
            if max(abs(event.x_root - x), abs(event.y_root - y)) < 6:
                return  # A click or double-click should not reorder anything.
            self.drag["active"] = True
            self.canvas.focus_set()
            self.paint_rows()
        if self.drag_job is None:
            self.drag_tick()

    def drag_tick(self, scroll=True):
        self.drag_job = None
        if self.drag is None or not self.drag["active"]:
            return
        _, pointer_y = self.drag["pointer"]
        y = pointer_y - self.canvas.winfo_rooty()
        height = self.canvas.winfo_height()
        if scroll and y < 24:
            self.canvas.yview_scroll(-1, "units")
        elif scroll and y > height - 24:
            self.canvas.yview_scroll(1, "units")
        content_y = self.canvas.canvasy(y)
        rows = self.rows.winfo_children()
        before = next((i for i, row in enumerate(rows)
                       if content_y < row.winfo_y() + row.winfo_height() / 2), len(rows))
        self.drag["target"] = before - (before > self.drag["source"])
        line_y = rows[before].winfo_y() if before < len(rows) else self.rows.winfo_height()
        self.drop_line.place(x=2, y=max(1, min(height - 2, line_y - self.canvas.canvasy(0))),
                             width=max(1, self.canvas.winfo_width() - 4), height=2)
        self.drop_line.lift()
        self.drag_job = self.root.after(80, self.drag_tick)

    def cancel_drag(self, event=None):
        if self.drag_job is not None:
            self.root.after_cancel(self.drag_job)
            self.drag_job = None
        if self.drag is not None:
            label = self.drag["widget"]
            if label.winfo_exists() and self.root.grab_current() == label:
                label.grab_release()
        self.drag = None
        self.drop_line.place_forget()
        self.paint_rows()

    def end_drag(self, event):
        if self.drag is None:
            return
        # Some Windows input paths coalesce all held-button motion. A distant
        # release still counts as a drag, using the same six-pixel threshold.
        if not self.drag["active"]:
            self.drag_motion(event)
        drag = self.drag
        # Use the release location even if Windows coalesced the last motion event.
        if drag["active"]:
            drag["pointer"] = (event.x_root, event.y_root)
            if self.drag_job is not None:
                self.root.after_cancel(self.drag_job)
            self.drag_tick(scroll=False)
        x = event.x_root - self.canvas.winfo_rootx()
        y = event.y_root - self.canvas.winfo_rooty()
        inside = 0 <= x < self.canvas.winfo_width() and 0 <= y < self.canvas.winfo_height()
        self.cancel_drag()
        if drag["active"] and inside:
            self.move(drag["source"], drag["target"])
        elif not drag["active"] and inside and drag["edit_on_click"]:
            self.open_editor(drag["source"])

    def move(self, source, target):
        if source == target or not (0 <= source < len(self.items) and 0 <= target < len(self.items)):
            return False
        order = list(range(len(self.items)))
        order.insert(target, order.pop(source))
        items = [self.items[index] for index in order]
        view = self.canvas.yview()[0]
        if not self.persist(items):
            return False
        if self.edit_index is not None:
            self.edit_index = order.index(self.edit_index)
        self.selected_index = target
        self.paint_rows()
        self.root.update_idletasks()
        self.canvas.yview_moveto(view)
        self.reveal(self.rows.winfo_children()[target])
        return True

    def move_key(self, index, direction):
        if self.move(index, index + direction):
            self.rows.winfo_children()[index + direction].winfo_children()[1].focus_set()
        return "break"

    def reveal(self, row):
        self.root.update_idletasks()
        top = self.canvas.canvasy(0)
        if row.winfo_y() < top or row.winfo_y() + row.winfo_height() > top + self.canvas.winfo_height():
            self.canvas.yview_moveto(row.winfo_y() / max(1, self.rows.winfo_height()))

    def show_menu(self, index, event):
        self.cancel_drag()
        self.menu.delete(0, "end")
        self.menu.add_command(label="Edit", command=lambda: self.open_editor(index))
        self.menu.add_command(label="Delete", command=lambda: self.delete(index))
        keyboard = event.type == tk.EventType.KeyPress
        x = event.widget.winfo_rootx() if keyboard else event.x_root
        y = event.widget.winfo_rooty() + event.widget.winfo_height() if keyboard else event.y_root
        try:
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    def copy(self, index):
        try:
            write_clipboard(self.root, self.items[index])
        except (OSError, tk.TclError) as error:
            messagebox.showerror("Could not copy", str(error), parent=self.root)
            return
        self.reset_copy_feedback()
        button = self.rows.winfo_children()[index].winfo_children()[1]
        button.image = self.check_icon
        button.draw()
        self.feedback.configure(text="Copied.")
        self.copy_job = self.root.after(1200, self.finish_copy)

    def finish_copy(self):
        self.copy_job = None
        self.reset_copy_feedback()

    def toggle_editor(self):
        if self.editor.winfo_ismapped():
            self.close_editor()
        else:
            self.open_editor()

    def editor_key(self, event):
        if event.keysym == "Escape":
            self.close_editor()
        else:
            self.add()
        return "break"

    def open_editor(self, index=None):
        self.cancel_drag()
        self.selected_index = index
        self.paint_rows()
        self.edit_index = index
        self.entry.delete("1.0", "end")
        self.entry.edit_reset()
        if index is not None:
            self.entry.insert("1.0", self.items[index])
        self.editor_title.configure(text="Edit snippet" if index is not None else "Add snippet")
        self.editor.grid(row=1, column=0, sticky="ew")
        self.plus.symbol = "×"
        self.plus.draw()
        self.entry.focus_set()

    def close_editor(self):
        self.editor.grid_remove()
        self.entry.delete("1.0", "end")
        self.edit_index = None
        self.plus.symbol = "+"
        self.plus.draw()
        self.plus.focus_set()

    def persist(self, items):
        try:
            save_snippets(self.path, items)
        except OSError as error:
            messagebox.showerror("Could not save", str(error), parent=self.root)
            return False
        self.items = items
        self.selected_index = None
        self.render_rows()
        return True

    def add(self):
        text = self.entry.get("1.0", "end-1c")  # Exclude only Tk's extra trailing newline.
        if not text.strip():
            return
        index = self.edit_index
        items = self.items.copy()
        if index is None:
            items.append(text)
        else:
            items[index] = text
        if not self.persist(items):
            return
        self.close_editor()
        self.root.update_idletasks()
        if index is None:
            self.canvas.yview_moveto(1)
        else:
            self.reveal(self.rows.winfo_children()[index])

    def delete(self, index):
        if not messagebox.askyesno("Delete snippet?", "Remove this saved snippet?",
                                   parent=self.root, icon="warning"):
            return
        items = self.items.copy()
        del items[index]
        if not self.persist(items):
            return
        if self.edit_index == index:
            self.close_editor()
        elif self.edit_index is not None and self.edit_index > index:
            self.edit_index -= 1


def main():
    instance_handle = claim_instance()  # Keep the mutex alive for the process lifetime.
    if sys.platform == "win32":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        ctypes.windll.user32.SetProcessDPIAware()
    root = tk.Tk()
    root.withdraw()
    try:
        QuickCopy(root)
        root.deiconify()
        register_window(root)
    except (OSError, ValueError) as error:
        messagebox.showerror("QuickCopy could not open saved snippets",
                             f"{data_path()}\n\n{error}\n\nYour saved file has not been replaced.", parent=root)
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
