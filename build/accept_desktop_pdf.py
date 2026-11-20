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
        toolbar = window.child_window(class_name="ToolbarWindow32").wrapper_object()
        fit_page = next(toolbar.get_button(i).idCommand for i in range(toolbar.button_count())
                        if toolbar.get_button(i).text.startswith("单页视图"))
        window.send_message(0x111, fit_page, toolbar.handle)
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
            item.click()
            time.sleep(.35)
            page = window.descendants(class_name="Edit")[0].window_text()
            wanted = reader.get_destination_page_number(target) + 1
            assert int(page) == wanted, (target.title, page, wanted)
            report["bookmarks"].append({"title": target.title, "page": int(page)})
            filename = f"sumatra-{index + 1}.png"
            capture(window.handle, OUT / "screenshots" / filename)
            report["screenshots"].append(filename)
        page_edit = window.descendants(class_name="Edit")[0]
        toolbar = window.child_window(class_name="ToolbarWindow32").wrapper_object()
        commands = {toolbar.get_button(i).text: toolbar.get_button(i).idCommand for i in range(toolbar.button_count())}
        def command(label):
            code = next(code for text, code in commands.items() if text.startswith(label))
            window.send_message(0x111, code, toolbar.handle)
        by_title[destinations[0].title].click()
        command("下一页")
        time.sleep(.3)
        assert int(page_edit.window_text()) == 2
        command("上一页")
        time.sleep(.3)
        assert int(page_edit.window_text()) == 1
        command("放大")
        time.sleep(.2)
        capture(window.handle, OUT / "screenshots/sumatra-zoom.png")
        report["pagination"] = "1 -> 2 -> 1"
        process.terminate()
        process.wait(timeout=10)
        # The documented reader launch option runs its own actual text search.
        process = subprocess.Popen([str(EXE), "-appdata", str(OUT / "sumatra-profile"), "-new-window", "-search", "persona", str(PDF)])
        time.sleep(3)
        window = Application(backend="win32").connect(process=process.pid).window(class_name="SUMATRA_PDF_FRAME")
        edits = window.descendants(class_name="Edit")
        assert edits[1].window_text() == "persona" and int(edits[0].window_text()) > 1
        report["search"] = {"term": "persona", "page": int(edits[0].window_text())}
        capture(window.handle, OUT / "screenshots/sumatra-search.png")
        report["passed"] = True
    finally:
        (OUT / "sumatra-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        process.terminate()
        process.wait(timeout=10)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
