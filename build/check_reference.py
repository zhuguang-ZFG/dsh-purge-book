#!/usr/bin/env python3
"""核对本书固定源码与离线教学示例；不调用宿主安装、Apply 或网络。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--baseline", type=Path, default=ROOT / "build/baseline.json")
    parser.add_argument("--peer", type=Path, help="另一份已固定并核对的参考树，用于跨包假对象实验")
    args = parser.parse_args()
    reference = args.reference.resolve()
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    failures = []
    checks = []

    def check(ok, name):
        print(("PASS " if ok else "FAIL ") + name)
        (checks if ok else failures).append(name)

    head = subprocess.run(
        ["git", "-C", str(reference), "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    check(head.returncode == 0 and head.stdout.strip() == baseline["commit"], "参考提交与基线一致")
    for name, expected in baseline["files"].items():
        source = reference / name
        data = source.read_bytes().replace(b"\r\n", b"\n") if source.is_file() else b""
        check(bool(data) and hashlib.sha256(data).hexdigest() == expected, f"文件摘要 {name}")
    if failures:
        return 1

    package = json.loads((reference / "package.json").read_text(encoding="utf-8"))
    check(package["name"] == baseline["package"] and package["version"] == baseline["version"], "包名与版本")
    check(package["dshTarget"] == baseline["host_target"], "目标宿主版本")
    core = (reference / "lib/core.js").read_text(encoding="utf-8")
    counts = {}
    for name, expected in baseline["patch_arrays"].items():
        match = re.search(r"(?:export )?const " + name + r" = \[", core)
        end = core.index("\n];", match.end())
        counts[name] = len(re.findall(r"^    id: \d+,", core[match.end():end], re.M))
        check(counts[name] == expected, f"数组 {name} = {expected}")

    cli = (reference / baseline.get("cli_file", "bin/dsh-purge-safe.js")).read_text(encoding="utf-8")
    modes = re.search(r"const mode = args\.find\(\(a\) => \[(.*?)\]\.includes", cli)
    check(bool(modes) and re.findall(r'"(--[^\"]+)"', modes.group(1)) == baseline["cli_modes"], "CLI 动作集合")
    check(not (reference / "AGENTS.md").exists() and "check:docs" not in package.get("scripts", {}), "不借用旧版 AGENTS/check:docs 合同")
    schema = (reference / "lib/redteam/schema.js").read_text(encoding="utf-8")
    tool_source = (reference / "lib/redteam/tools.js").read_text(encoding="utf-8")
    for table in ["http_evidence", "data_proof", "agent_report"]:
        check(bool(re.search(r"CREATE TABLE IF NOT EXISTS " + table + r"\s*\(", schema)), f"事实表 {table}")
    check("CREATE TABLE IF NOT EXISTS agent_task" not in schema, "agent_task 仍按设计方案标注")
    check("name: 'redteam_agent_task'" not in tool_source and "redteam_evidence_upgrade" not in tool_source, "不提供旧版或提案中的工具")

    (ROOT / "build/tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="reference-fixture-", dir=ROOT / "build/tmp") as fixture:
        env = os.environ.copy()
        env.update({"DSH_HOME": fixture, "DSH_BASE": str(Path(fixture) / "missing-host"), "DSH_SURFACE": "web"})
        # Environment variables select fixtures; they do not isolate host discovery.
        # Grant reads only. No fs.write or child-process permission is passed.
        result = subprocess.run(
            ["node", "--permission", "--allow-fs-read=*",
             str(ROOT / "build/reference_contract.mjs"), str(reference), baseline["package"]],
            capture_output=True, text=True, encoding="utf-8", env=env, check=False,
            timeout=60,
        )
    check(result.returncode == 0, "离线组件示例")
    experiments = {}
    if result.returncode == 0:
        experiments = json.loads(result.stdout)
        for name in experiments["checks"]:
            check(True, name)
        check(experiments["patches"] == baseline["patches"], "导出补丁 id/name 与基线逐项一致")
    else:
        print(result.stderr)
    if args.peer:
        peer = args.peer.resolve()
        peer_baseline = json.loads((ROOT / ("build/baseline-pi.json" if baseline["package"] == "dsh-purge-safe"
                                            else "build/baseline.json")).read_text(encoding="utf-8"))
        peer_head = subprocess.run(["git", "-C", str(peer), "rev-parse", "HEAD"], capture_output=True,
                                   text=True, encoding="utf-8", check=False)
        valid_peer = peer_head.returncode == 0 and peer_head.stdout.strip() == peer_baseline["commit"]
        for name, digest in peer_baseline["files"].items():
            file = peer / name
            valid_peer = valid_peer and file.is_file() and hashlib.sha256(
                file.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == digest
        check(valid_peer, "跨包参考树提交与文件摘要一致")
        if valid_peer:
            mappings = [("dsh-purge-safe", "pi-purge"), ("DSH-PURGE-SAFE", "PI-PURGE"),
                        ("DSH_PURGE", "PI_PURGE"), ("dshPurge", "piPurge"),
                        ("dshpurge", "pipurge"), ("dshpg", "pipg")]

            def renamed(value):
                for old, new in mappings:
                    value = value.replace(old, new)
                return value

            old_root, new_root = (reference, peer) if baseline["package"] == "dsh-purge-safe" else (peer, reference)
            tracked = subprocess.check_output(["git", "-C", str(old_root), "ls-files", "-z"]).decode("utf-8").rstrip("\0").split("\0")
            comparison = {"identical": 0, "rename_only": 0, "other": 0}
            for name in tracked:
                old = (old_root / name).read_bytes().replace(b"\r\n", b"\n")
                target = new_root / renamed(name)
                new = target.read_bytes().replace(b"\r\n", b"\n") if target.is_file() else b""
                if old == new:
                    comparison["identical"] += 1
                else:
                    try:
                        same = renamed(old.decode("utf-8-sig")) == new.decode("utf-8-sig")
                    except UnicodeDecodeError:
                        same = False
                    comparison["rename_only" if same else "other"] += 1
            check(comparison == {"identical": 92, "rename_only": 52, "other": 9},
                  "两仓跟踪文件：92 原样、52 名称映射、9 另有变化")
            mixed = subprocess.run(["node", "--permission", "--allow-fs-read=*",
                                    str(ROOT / "build/migration_contract.mjs"), str(reference), str(peer)],
                                   capture_output=True, text=True, encoding="utf-8", env=env,
                                   timeout=60, check=False)
            check(mixed.returncode == 0, "跨包假对象实验")
            if mixed.returncode == 0:
                for name in json.loads(mixed.stdout)["checks"]:
                    check(True, name)
            else:
                print(mixed.stderr)
    report = {
        "commit": baseline["commit"], "checks": checks, "failures": failures,
        "experiments": experiments.get("checks", []),
        "scope": "source-and-offline-components; no live DSH install, Apply, restart or model evaluation",
    }
    report_path = ROOT / ("build/tmp/reference-pi-check.json" if baseline["package"] == "pi-purge"
                          else "build/tmp/reference-check.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(checks)} 项通过，{len(failures)} 项失败；报告 {report_path}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
