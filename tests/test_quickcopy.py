"""Real Tk/Windows clipboard checks; use temporary storage, never personal snippets."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import time
import tkinter as tk
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from quickcopy import APP_ID, EXAMPLES, QuickCopy, load_snippets, save_snippets, position_window


class QuickCopyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "snippets.json"
        self.root = tk.Tk()
        self.app = QuickCopy(self.root, self.path)
        self.root.update()

    def tearDown(self):
        self.root.update_idletasks()
        self.root.destroy()
        self.directory.cleanup()

    def clipboard_text(self):
        # Windows clipboard managers can briefly hold the exclusive clipboard lock.
        for attempt in range(15):
            try:
                return self.root.clipboard_get()
            except tk.TclError:
                if attempt == 14:
                    raise
                time.sleep(0.02)

    def test_examples_and_exact_clipboard_after_restart(self):
        self.assertEqual(self.app.items, EXAMPLES)
        original = "  https://example.com/" + "long-text-" * 1000 + "\nUnicode: café Ω 😀\n\tend  \n"
        self.app.entry.insert("1.0", original)
        self.app.add()
        self.assertEqual(self.app.items[-1], original)
        self.assertEqual(self.app.entry.get("1.0", "end-1c"), "")
        self.root.destroy()
        self.root = tk.Tk()
        self.app = QuickCopy(self.root, self.path)
        self.root.update()
        self.assertEqual(self.app.items[-1], original)
        button = self.app.rows.winfo_children()[-1].winfo_children()[1]
        button.invoke()
        self.root.update()
        self.assertEqual(self.clipboard_text(), original)
        self.assertEqual(self.app.feedback.cget("text"), "Copied.")
        self.root.after(1400, self.root.quit)
        self.root.mainloop()
        self.assertEqual(self.app.feedback.cget("text"), "")

    def test_scroll_and_blank_input(self):
        self.app.entry.insert("1.0", " \n\t")
        self.app.add()
        self.assertEqual(self.app.items, EXAMPLES)
        self.app.entry.delete("1.0", "end")
        for index in range(35):
            self.app.entry.insert("1.0", f"Snippet {index}")
            self.app.add()
        self.root.update()
        self.assertGreater(self.app.canvas.yview()[0], 0)
        self.assertAlmostEqual(self.app.canvas.yview()[1], 1, places=2)
        self.app.canvas.yview_moveto(0)
        self.assertEqual(self.app.canvas.yview()[0], 0)
        self.assertEqual(len(load_snippets(self.path)), 38)

    def test_input_and_add_visible_at_default_and_minimum_size(self):
        self.assertFalse(self.app.editor.winfo_ismapped())
        self.app.plus.invoke()
        for size in ["260x398", "240x320"]:
            self.root.geometry(size)
            self.root.update()
            for widget in self.app.entry.master.winfo_children():
                self.assertTrue(widget.winfo_ismapped())
                self.assertLessEqual(widget.winfo_rooty() + widget.winfo_height(),
                                     self.root.winfo_rooty() + self.root.winfo_height())
        self.app.entry.insert("1.0", "unsaved")
        self.app.plus.invoke()
        self.root.update()
        self.assertFalse(self.app.editor.winfo_ismapped())
        self.assertEqual(self.app.items, EXAMPLES)

    def test_edit_exact_text_persists_and_copy_uses_new_value(self):
        original = "  Updated café Ω 😀\n" + "long text " * 500 + "\n\tend  \n"
        self.app.open_editor(1)
        self.assertEqual(self.app.entry.get("1.0", "end-1c"), EXAMPLES[1])
        self.app.entry.delete("1.0", "end")
        self.app.entry.insert("1.0", original)
        self.app.save_button.invoke()
        self.assertEqual(len(self.app.items), 3)
        self.assertEqual(load_snippets(self.path)[1], original)
        self.app.rows.winfo_children()[1].winfo_children()[1].invoke()
        self.assertEqual(self.clipboard_text(), original)

    def test_delete_cancel_then_duplicate_row_and_empty_restart(self):
        save_snippets(self.path, ["same", "same", "keep"])
        self.app.items = load_snippets(self.path)
        self.app.render_rows()
        with patch("quickcopy.messagebox.askyesno", return_value=False):
            self.app.delete(1)
        self.assertEqual(self.app.items, ["same", "same", "keep"])
        with patch("quickcopy.messagebox.askyesno", return_value=True):
            self.app.delete(1)
            self.assertEqual(self.app.items, ["same", "keep"])
            self.app.rows.winfo_children()[1].winfo_children()[1].invoke()
            self.assertEqual(self.clipboard_text(), "keep")
            self.app.delete(1)
            self.app.delete(0)
        self.root.update()
        self.assertTrue(self.app.empty.winfo_ismapped())
        self.assertEqual(load_snippets(self.path), [])
        self.root.destroy()
        self.root = tk.Tk()
        self.app = QuickCopy(self.root, self.path)
        self.assertEqual(self.app.items, [])

    def test_failed_edit_and_delete_preserve_saved_data_and_input(self):
        self.app.open_editor(1)
        self.app.entry.insert("end", " changed")
        with patch("quickcopy.save_snippets", side_effect=OSError("Disk full")), patch("quickcopy.messagebox.showerror"), patch("quickcopy.messagebox.askyesno", return_value=True):
            self.app.add()
            self.app.delete(0)
        self.assertEqual(load_snippets(self.path), EXAMPLES)
        self.assertEqual(self.app.items, EXAMPLES)
        self.assertEqual(self.app.edit_index, 1)
        self.assertEqual(self.app.entry.get("1.0", "end-1c"), EXAMPLES[1] + " changed")

    def test_deleting_earlier_row_keeps_edit_target(self):
        self.app.open_editor(2)
        self.app.entry.insert("end", " changed")
        with patch("quickcopy.messagebox.askyesno", return_value=True):
            self.app.delete(0)
        self.assertEqual(self.app.edit_index, 1)
        self.app.add()
        self.assertEqual(load_snippets(self.path), [EXAMPLES[1], EXAMPLES[2] + " changed"])

    def test_keyboard_menu_edit_and_cancel(self):
        button = self.app.rows.winfo_children()[1].winfo_children()[1]
        event = SimpleNamespace(type=tk.EventType.KeyPress, widget=button, x_root=9999, y_root=9999)
        with patch.object(self.app.menu, "tk_popup") as popup:
            self.app.show_menu(1, event)
        popup.assert_called_once_with(button.winfo_rootx(), button.winfo_rooty() + button.winfo_height())
        self.app.menu.invoke(0)
        self.assertEqual(self.app.edit_index, 1)
        self.app.entry.insert("end", " not saved")
        self.assertEqual(self.app.editor_key(SimpleNamespace(keysym="Escape")), "break")
        self.assertEqual(load_snippets(self.path), EXAMPLES)

    @unittest.skipUnless(sys.platform == "win32", "Windows monitor work area")
    def test_startup_window_clears_taskbar(self):
        import ctypes
        from ctypes import wintypes
        class MonitorInfo(ctypes.Structure):
            _fields_ = [("size", wintypes.DWORD), ("monitor", wintypes.RECT),
                        ("work", wintypes.RECT), ("flags", wintypes.DWORD)]
        user = ctypes.WinDLL("user32")
        user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        user.GetAncestor.restype = wintypes.HWND
        user.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
        user.MonitorFromWindow.restype = wintypes.HANDLE
        user.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MonitorInfo)]
        user.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        position_window(self.root)
        self.root.update()
        window = user.GetAncestor(self.root.winfo_id(), 2)
        rect = wintypes.RECT()
        info = MonitorInfo(size=ctypes.sizeof(MonitorInfo))
        self.assertTrue(user.GetWindowRect(window, ctypes.byref(rect)))
        self.assertTrue(user.GetMonitorInfoW(user.MonitorFromWindow(window, 2), ctypes.byref(info)))
        self.assertEqual(rect.right, info.work.right - 12)
        self.assertEqual(rect.bottom, info.work.bottom - 12)

    @unittest.skipUnless(sys.platform == "win32", "Windows single-instance restoration")
    def test_second_launch_restores_own_window_with_same_title_preview(self):
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32")
        kernel.OpenMutexW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
        kernel.OpenMutexW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        existing = kernel.OpenMutexW(0x00100000, False, "Local\\" + APP_ID)
        if existing:
            kernel.CloseHandle(existing)
            self.skipTest("A real QuickCopy instance is already running")
        user = ctypes.WinDLL("user32")
        user.FindWindowExW.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]
        user.FindWindowExW.restype = wintypes.HWND
        user.GetPropW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
        user.GetPropW.restype = wintypes.HANDLE
        user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        user.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user.IsIconic.argtypes = [wintypes.HWND]
        user.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        environment = os.environ.copy()
        environment["LOCALAPPDATA"] = str(Path(self.directory.name) / "instance")
        command = [sys.executable, str(Path(__file__).resolve().parents[1] / "quickcopy.py")]
        # setUp's unmarked QuickCopy root deliberately has the same title.
        first = subprocess.Popen(command, env=environment, creationflags=subprocess.CREATE_NO_WINDOW)
        window = None
        try:
            deadline = time.monotonic() + 10
            while not window and time.monotonic() < deadline:
                candidate = None
                while True:
                    candidate = user.FindWindowExW(None, candidate, None, "QuickCopy")
                    if not candidate:
                        break
                    owner = wintypes.DWORD()
                    user.GetWindowThreadProcessId(candidate, ctypes.byref(owner))
                    # Windows' venv launcher may run Python in a child PID.
                    # No mutex existed before launch; only this new main marks a window.
                    if user.GetPropW(candidate, APP_ID):
                        window = candidate
                        break
                if not window:
                    time.sleep(0.05)
            self.assertIsNotNone(window, "The actual instance did not register its window")
            user.ShowWindow(window, 6)
            self.assertTrue(user.IsIconic(window))
            subprocess.run(command, env=environment, check=True, timeout=15,
                           creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertFalse(user.IsIconic(window))
            self.assertIsNone(first.poll())
        finally:
            if window:
                user.PostMessageW(window, 0x0010, 0, 0)
            try:
                first.wait(timeout=5)
            except subprocess.TimeoutExpired:
                first.terminate()
                first.wait(timeout=5)

    @unittest.skipUnless(sys.platform == "win32", "Windows clipboard ownership")
    def test_clipboard_survives_copying_process_exit(self):
        import json
        original = "  long " * 1000 + "\nUnicode: café Ω 😀\n\tend  \n"
        save_snippets(self.path, [original])
        copier = """
import sys
from pathlib import Path
import tkinter as tk
from quickcopy import QuickCopy
root = tk.Tk()
app = QuickCopy(root, Path(sys.argv[1]))
root.update()
app.rows.winfo_children()[0].winfo_children()[1].invoke()
root.destroy()
"""
        reader = """
import json
import time
import tkinter as tk
root = tk.Tk()
for attempt in range(15):
    try:
        value = root.clipboard_get()
        break
    except tk.TclError:
        if attempt == 14:
            raise
        time.sleep(0.02)
print(json.dumps(value, ensure_ascii=True))
root.destroy()
"""
        subprocess.run([sys.executable, "-c", copier, str(self.path)], check=True,
                       capture_output=True, text=True)
        result = subprocess.run([sys.executable, "-c", reader], check=True,
                                capture_output=True, text=True)
        self.assertEqual(json.loads(result.stdout), original)

    def test_failed_save_keeps_input_and_list(self):
        self.app.entry.insert("1.0", "keep this")
        with patch("quickcopy.save_snippets", side_effect=OSError("Disk full")), patch("quickcopy.messagebox.showerror") as dialog:
            self.app.add()
        dialog.assert_called_once()
        self.assertEqual(self.app.items, EXAMPLES)
        self.assertEqual(self.app.entry.get("1.0", "end-1c"), "keep this")

class StorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "snippets.json"

    def tearDown(self):
        self.directory.cleanup()

    def test_invalid_file_is_not_replaced(self):
        for invalid in ["broken JSON", '{"wrong": "shape"}', '[1]']:
            self.path.write_text(invalid, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_snippets(self.path)
            self.assertEqual(self.path.read_text(encoding="utf-8"), invalid)

    def test_atomic_unicode_save(self):
        items = ["\r\n whitespace \t", "😀"]
        save_snippets(self.path, items)
        self.assertEqual(load_snippets(self.path), items)
        self.assertFalse(self.path.with_suffix(".tmp").exists())

    def test_missing_file_uses_independent_examples(self):
        items = load_snippets(self.path)
        items.append("new")
        self.assertEqual(load_snippets(self.path), EXAMPLES)


if __name__ == "__main__":
    unittest.main()
