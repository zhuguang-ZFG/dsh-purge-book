#!/usr/bin/env python3
"""把 Markdown 中的 Mermaid 代码块预渲染为 SVG，生成 pandoc 可直接消费的副本。

源文件保持 Mermaid 可编辑；只有 build/tmp 下的副本把图块替换为图片引用。
"""
import argparse
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
BLOCK = re.compile(r"^```mermaid\s*\n(.*?)^```\s*$", re.M | re.S)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="Markdown 输入（显式白名单）")
    parser.add_argument("--out", required=True, help="替换后的 Markdown 输出目录")
    parser.add_argument("--figures", required=True, help="SVG 与 .mmd 输出目录")
    args = parser.parse_args()

    out = Path(args.out)
    figures = Path(args.figures)
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["PUPPETEER_EXECUTABLE_PATH"] = env.get("CHROME_PATH", env.get("PUPPETEER_EXECUTABLE_PATH", ""))
    total = 0

    for name in args.files:
        source = Path(name)
        counter = 0

        def render(match):
            nonlocal counter, total
            counter += 1
            total += 1
            stem = f"{source.stem}-{counter}"
            mmd = figures / f"{stem}.mmd"
            svg = figures / f"{stem}.svg"
            mmd.write_text(match.group(1), encoding="utf-8")
            result = subprocess.run(
                ["bun", "x", "mmdc", "-i", str(mmd), "-o", str(svg), "-b", "transparent"],
                cwd=BUILD,
                env=env,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"mmdc 渲染失败 {stem} (exit {result.returncode}):\n"
                    f"{result.stderr}\n{result.stdout}"
                )
            if not svg.exists() or svg.stat().st_size == 0:
                raise RuntimeError(f"SVG 未生成: {svg}")
            # pandoc 通过 --resource-path 指向 figures 目录，引用写成文件名即可
            return f"![图示 {stem}]({svg.name})"

        result = BLOCK.sub(render, source.read_text(encoding="utf-8"))
        (out / source.name).write_text(result, encoding="utf-8")
        print(f"{source.name}: {counter} 图")

    print(f"共渲染 {total} 张图")


if __name__ == "__main__":
    main()
