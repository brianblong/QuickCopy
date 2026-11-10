"""Capture real, cursor-free Windows previews with fictional data (requires Pillow).

Run with a Windows Python that has Tkinter and Pillow installed. Personal snippets
are never opened. PrintWindow reads the app's pixels directly, without a pointer
or an automation overlay, and the saved PNGs are not retouched.
"""
import ctypes
from ctypes import wintypes
from pathlib import Path
import sys
import tempfile
import tkinter as tk
from types import SimpleNamespace

from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from quickcopy import QuickCopy, position_window, save_snippets


def capture(root, target):
    user = ctypes.WinDLL("user32", use_last_error=True)
    gdi = ctypes.WinDLL("gdi32", use_last_error=True)
    user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user.GetAncestor.restype = wintypes.HWND
    user.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user.GetWindowDC.argtypes = [wintypes.HWND]
    user.GetWindowDC.restype = wintypes.HDC
    user.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
    user.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, wintypes.UINT]
    gdi.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi.CreateCompatibleDC.restype = wintypes.HDC
    gdi.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
    gdi.CreateCompatibleBitmap.restype = wintypes.HBITMAP
    gdi.SelectObject.argtypes = [wintypes.HDC, wintypes.HANDLE]
    gdi.SelectObject.restype = wintypes.HANDLE
    gdi.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT,
                             wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p, wintypes.UINT]
    gdi.DeleteObject.argtypes = [wintypes.HANDLE]
    gdi.DeleteDC.argtypes = [wintypes.HDC]
    window = user.GetAncestor(root.winfo_id(), 2)
    rect = wintypes.RECT()
    if not user.GetWindowRect(window, ctypes.byref(rect)):
        raise ctypes.WinError(ctypes.get_last_error())
    width, height = rect.right - rect.left, rect.bottom - rect.top
    window_dc = user.GetWindowDC(window)
    dc = gdi.CreateCompatibleDC(window_dc)
    bitmap = gdi.CreateCompatibleBitmap(window_dc, width, height)
    if not window_dc or not dc or not bitmap:
        if bitmap:
            gdi.DeleteObject(bitmap)
        if dc:
            gdi.DeleteDC(dc)
        if window_dc:
            user.ReleaseDC(window, window_dc)
        raise ctypes.WinError(ctypes.get_last_error())
    old = gdi.SelectObject(dc, bitmap)
    try:
        if not user.PrintWindow(window, dc, 2):
            raise RuntimeError("Windows could not capture the preview window")
        gdi.SelectObject(dc, old)
        # BITMAPINFOHEADER: a negative height requests top-down, 32-bit BGR pixels.
        header = ctypes.create_string_buffer(40)
        import struct
        struct.pack_into("<IiiHHIIiiII", header, 0, 40, width, -height, 1, 32,
                         0, width * height * 4, 0, 0, 0, 0)
        pixels = ctypes.create_string_buffer(width * height * 4)
        if gdi.GetDIBits(dc, bitmap, 0, height, pixels, header, 0) != height:
            raise RuntimeError("Windows could not read the preview pixels")
        picture = Image.frombytes("RGB", (width, height), pixels.raw, "raw", "BGRX")
        # Exclude only Windows' invisible resize margins; keep the real title bar.
        visible = wintypes.RECT()
        dwm = ctypes.WinDLL("dwmapi")
        dwm.DwmGetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD,
                                            ctypes.c_void_p, wintypes.DWORD]
        if dwm.DwmGetWindowAttribute(window, 9, ctypes.byref(visible), ctypes.sizeof(visible)) == 0:
            picture = picture.crop((visible.left - rect.left, visible.top - rect.top,
                                    visible.right - rect.left, visible.bottom - rect.top))
        picture.save(target)
    finally:
        gdi.SelectObject(dc, old)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(dc)
        user.ReleaseDC(window, window_dc)


def main():
    ctypes.windll.user32.SetProcessDPIAware()
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("QuickCopy.Screenshots")
    output = PROJECT / "docs" / "images"
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "snippets.json"
        save_snippets(path, ["https://github.com/example", "alex@example.com",
                             "INV-2026-1042", "https://example.com/portfolio",
                             "Certification ID: EXAMPLE-12345"])
        root = tk.Tk()
        app = QuickCopy(root, path)
        def settle():
            root.after(250, root.quit)
            root.mainloop()
            root.update_idletasks()
        root.update()
        position_window(root)
        settle()
        capture(root, output / "floating-dock.png")
        app.open_editor()
        app.entry.insert("1.0", "https://www.linkedin.com/in/example")
        settle()
        capture(root, output / "add-snippet.png")
        app.close_editor()
        app.open_editor(2)
        settle()
        capture(root, output / "edit-snippet.png")
        app.close_editor()
        app.copy(1)
        settle()
        capture(root, output / "copied.png")
        app.reset_copy_feedback()
        first = app.rows.winfo_children()[0].winfo_children()[0]
        third = app.rows.winfo_children()[2]
        x = first.winfo_rootx() + 10
        app.begin_drag(0, SimpleNamespace(x_root=x, y_root=first.winfo_rooty() + 5))
        app.drag_motion(SimpleNamespace(x_root=x, y_root=third.winfo_rooty() + third.winfo_height() - 3))
        settle()
        capture(root, output / "reorder-snippets.png")
        app.cancel_drag()
        root.destroy()
    print("Captured five real Windows views with fictional snippets and no cursor.")


if __name__ == "__main__":
    main()
