"""Real Tk/Windows clipboard checks; use temporary storage, never personal snippets."""
from pathlib import Path
import subprocess
import sys
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

from quickcopy import EXAMPLES, QuickCopy, load_snippets, save_snippets, position_window


class QuickCopyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "snippets.json"
        self.root = tk.Tk()
        self.app = QuickCopy(self.root, self.path)
        self.root.update()

    def tearDown(self):
        self.root.destroy()
        self.directory.cleanup()

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
        self.assertEqual(self.root.clipboard_get(), original)
        self.assertEqual(button.cget("text"), "Copied.")
        self.root.after(1400, self.root.quit)
        self.root.mainloop()
        self.assertEqual(button.cget("text"), "Copy")

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
        for size in ["400x370", "360x300"]:
            self.root.geometry(size)
            self.root.update()
            for widget in self.app.entry.master.winfo_children():
                self.assertTrue(widget.winfo_ismapped())
                self.assertLessEqual(widget.winfo_rooty() + widget.winfo_height(),
                                     self.root.winfo_rooty() + self.root.winfo_height())

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
import tkinter as tk
root = tk.Tk()
print(json.dumps(root.clipboard_get(), ensure_ascii=True))
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
