"""Offline teaching fixture. No DSH, plugin or model calls are made."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def validate(source, actual):
    expected = [{"id": row["id"], "tag": row["tag"].strip().lower()} for row in source]
    ids = [row.get("id") for row in actual]
    wanted = [row["id"] for row in expected]
    return {
        "missing": [key for key in wanted if key not in ids],
        "unexpected": [key for key in ids if key not in wanted],
        "duplicate": sorted({key for key in ids if ids.count(key) > 1}),
        "order_matches": ids == wanted,
        "content_matches": actual == expected,
        "passed": actual == expected,
    }


def save(name, data):
    path = ROOT / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
    return sha256(path.read_bytes()).hexdigest()


def main():
    source = [{"id": f"A{i:02d}", "tag": " Note " if i % 2 else " GUIDE "}
              for i in range(1, 13)]
    expected = [{"id": row["id"], "tag": row["tag"].strip().lower()} for row in source]
    bad = expected[:-1]
    rejected, accepted = validate(source, bad), validate(source, expected)
    assert rejected["missing"] == ["A12"] and not rejected["passed"]
    assert accepted["passed"]
    # Exercise distinct failures, so row count alone cannot pass this fixture.
    assert not validate(source, expected[::-1])["passed"]
    assert not validate(source, expected[:-1] + [expected[0]])["passed"]
    assert not validate(source, [dict(row, tag="wrong") for row in expected])["passed"]
    digests = {name: save(name, rows) for name, rows in (
        ("input.json", source), ("output-incomplete.json", bad), ("output.json", expected))}
    save("verification.json", {
        "scope": "虚构资料的本地教学校验；不代表真实 DSH 运行结果",
        "sha256": digests, "incomplete": rejected, "corrected": accepted,
        "host_install_apply": "未测", "process_loading": "未测", "model_input": "未测",
    })
    print("故意缺项：拒绝，缺少 A12；完整输出：通过（12 条逐条相等）。")
    print("顺序、重复 id 和标签错误均能检出；真实宿主仍未测。")


if __name__ == "__main__":
    main()
