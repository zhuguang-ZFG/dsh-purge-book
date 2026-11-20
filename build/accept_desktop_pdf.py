"""Windows-only, opt-in SumatraPDF acceptance with an isolated settings folder."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

from PIL import Image
from pypdf import PdfReader
from pywinauto import Application
import win32gui
import win32ui

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build/tmp/live-acceptance"
EXE = Path("C:/Users/zhugu/AppData/Local/SumatraPDF/SumatraPDF.exe")
PDF = ROOT / "dist/chaizha.pdf"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "screenshots").mkdir(exist_ok=True)


def capture(hwnd, path):
    rect = win32gui.GetWindowRect(hwnd)
    width, height = rect[2] - rect[0], rect[3] - rect[1]
    dc = win32gui.GetWindowDC(hwnd)
    source = win32ui.CreateDCFromHandle(dc)
    memory = source.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(source, width, height)
    memory.SelectObject(bitmap)
    import ctypes
    assert ctypes.windll.user32.PrintWindow(hwnd, memory.GetSafeHdc(), 2)
    image = Image.frombuffer("RGB", (width, height), bitmap.GetBitmapBits(True), "raw", "BGRX", 0, 1)
    assert image.getextrema() != ((0, 0), (0, 0), (0, 0)), "Blank reader capture"
    image.save(path)
    win32gui.DeleteObject(bitmap.GetHandle())
    memory.DeleteDC()
    source.DeleteDC()
    win32gui.ReleaseDC(hwnd, dc)


def main():
    process = subprocess.Popen([str(EXE), "-appdata", str(OUT / "sumatra-profile"), "-new-window", "-page", "1", "-zoom", "fit page", str(PDF)])
    report = {"reader": "SumatraPDF 3.6.1", "sha256": sha256(PDF.read_bytes()).hexdigest(), "bookmarks": [], "screenshots": []}
    try:
        app = Application(backend="win32").connect(process=process.pid, timeout=15)
        window = app.window(class_name="SUMATRA_PDF_FRAME")
        window.wait("exists ready", timeout=15)
        time.sleep(1)
        window.move_window(x=30, y=30, width=1100, height=900)
        tree = window.child_window(class_name="SysTreeView32", found_index=0).wrapper_object()
        reader = PdfReader(PDF)

        def flatten(items):
            for item in items:
                if isinstance(item, list):
                    yield from flatten(item)
                else:
                    yield item

        destinations = list(flatten(reader.outline))
        assert tree.item_count() == len(destinations), (tree.item_count(), len(destinations))
        report.update(pages=len(reader.pages), bookmark_count=tree.item_count())

        def native_items(items):
            for item in items:
                yield item
                yield from native_items(item.children())

        items = list(native_items(tree.roots()))
        by_title = {item.text(): item for item in items}
        selections = [destinations[0]]
        for fragment in ("第 3 章", "图 3-1", "图3-1", "附录 A", "四项验收"):
            target = next((d for d in destinations if fragment in d.title), None)
            if target and target not in selections:
                selections.append(target)
        for index, target in enumerate(selections):
            item = by_title[target.title]
            # Send the native control message; no foreground mouse desktop is needed.
            assert tree.send_message(0x110B, 9, item.elem)
            tree.send_keystrokes("{ENTER}")
            time.sleep(.35)
            page = window.descendants(class_name="Edit")[0].window_text()
            wanted = reader.get_destination_page_number(target) + 1
            assert int(page) == wanted, (target.title, page, wanted)
            report["bookmarks"].append({"title": target.title, "page": int(page)})
            filename = f"sumatra-{index + 1}.png"
            capture(window.handle, OUT / "screenshots" / filename)
            report["screenshots"].append(filename)
        page_edit = window.descendants(class_name="Edit")[0]
        page_edit.set_edit_text("1")
        page_edit.send_keystrokes("{ENTER}")
        window.send_keystrokes("{ESC}{RIGHT}")
        time.sleep(.3)
        assert int(page_edit.window_text()) == 2
        window.send_keystrokes("{LEFT}")
        time.sleep(.3)
        assert int(page_edit.window_text()) == 1
        window.send_keystrokes("^f")
        search_edit = window.descendants(class_name="Edit")[1]
        search_edit.set_edit_text("persona")
        search_edit.send_keystrokes("{ENTER}")
        time.sleep(.7)
        assert int(page_edit.window_text()) > 1, "Text search did not advance"
        report["search"] = {"term": "persona", "page": int(page_edit.window_text())}
        window.send_keystrokes("{ESC}^+")
        time.sleep(.2)
        capture(window.handle, OUT / "screenshots/sumatra-search-zoom.png")
        report["pagination"] = "1 -> 2 -> 1"
        report["passed"] = True
    finally:
        (OUT / "sumatra-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        process.terminate()
        process.wait(timeout=10)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
