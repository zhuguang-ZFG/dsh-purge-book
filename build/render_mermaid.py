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
CAPTIONS = {
    ('01', 1): '流程 1-A：一次工具调用的往返',
    ('01', 2): '流程 1-B：五处改动的生效时机',
    ('02', 1): '流程 2-A：匹配、应用与恢复',
    ('03', 1): '流程 3-A：正文选择与前缀折叠',
    ('03', 2): '流程 3-B：尾段与动态上下文',
    ('04', 1): '流程 4-A：任务未完成时怎样继续排查',
    ('05', 1): '流程 5-A：派活、回报与处理确认',
    ('06', 1): '流程 6-A：安装到恢复的验收顺序',
    ('07', 1): '流程 7-A：版本更新后的复核',
}


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
    # CI 上 Chromium 受 AppArmor 限制无法建沙箱；仅 CI 传 --no-sandbox
    mmdc_extra = []
    if env.get("CI"):
        puppeteer_config = figures / "puppeteer.json"
        puppeteer_config.write_text('{"args": ["--no-sandbox"]}', encoding="utf-8")
        mmdc_extra = ["-p", str(puppeteer_config)]
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
                ["bun", "x", "mmdc", "-i", str(mmd), "-o", str(svg),
                 "-c", str(BUILD / "mermaid.json"), "-b", "transparent", *mmdc_extra],
                cwd=BUILD,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"mmdc 渲染失败 {stem} (exit {result.returncode}):\n"
                    f"{result.stderr}\n{result.stdout}"
                )
            if not svg.exists() or svg.stat().st_size == 0:
                raise RuntimeError(f"SVG 未生成: {svg}")
            # pandoc 通过 --resource-path 指向 figures 目录，引用写成文件名即可
            # 保持独立段落，否则下一段文字会使 Pandoc 把图降为普通行内图片。
            caption = CAPTIONS[(source.name[:2], counter)]
            return f"\n\n![{caption}]({svg.name})\n\n"

        result = BLOCK.sub(render, source.read_text(encoding="utf-8"))
        # 插图源文件在仓库根目录；复制到 figures 后按文件名引用，源文件仍可被 GitHub 预览
        result = re.sub(r"\]\(illustrations/", "](", result)
        (out / source.name).write_text(result, encoding="utf-8")
        print(f"{source.name}: {counter} 图")

    print(f"共渲染 {total} 张图")


if __name__ == "__main__":
    main()
