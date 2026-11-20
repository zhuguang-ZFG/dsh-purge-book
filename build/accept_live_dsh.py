"""Opt-in acceptance of an already installed DSH in a disposable workspace.

Uses a loopback Messages fixture, never a model account. Apply/revert target one
explicit package tree; the plugin's multi-installation HTTP Apply is not used.
"""
import argparse
from collections import Counter
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import http.cookiejar
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request

BOOK = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("root", type=Path)
args = parser.parse_args()
root = args.root.resolve()
assert root.is_relative_to(BOOK / "build/tmp/live-acceptance")
entry = root / "node_modules/@deepseek-ai/dsh/lib/bin.js"
home = root / "home"
temp = root / "temp"
temp.mkdir(exist_ok=True)
env = os.environ.copy()
env.update(DSH_HOME=str(home), DSH_SURFACE="web", DSH_BASE=str(root / "node_modules/@deepseek-ai"),
           APPDATA=str(home / "appdata"), LOCALAPPDATA=str(home / "localappdata"),
           TMP=str(temp), TEMP=str(temp))
# An account-free fixture must not inherit user model credentials.
for key in list(env):
    if key.endswith("API_KEY") or key.endswith("AUTH_TOKEN"):
        env.pop(key)
node = ["node", "--permission", "--allow-fs-read=*", "--allow-fs-write=" + str(root),
        "--allow-addons", "--expose-internals"]
report = {"scope": "Windows DSH rc.3, isolated package copy; local deterministic transport, no model efficacy claim",
          "native_addons": "enabled; Node filesystem permissions are not an OS sandbox", "stages": {}}


def run(label, arguments, timeout=45):
    result = subprocess.run(node + arguments, cwd=root, env=env, input="", capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=timeout)
    (root / (label + ".stdout.txt")).write_text(result.stdout, encoding="utf-8")
    (root / (label + ".stderr.txt")).write_text(result.stderr, encoding="utf-8")
    assert result.returncode == 0, (label, result.returncode, result.stderr[-1600:])
    return result.stdout


def profile(name, bundles, patch="[]\n"):
    folder = home / "profiles" / name
    folder.mkdir(parents=True, exist_ok=True)
    manifest = {"name": "dsh-profile-" + name, "private": True, "type": "module",
                "dependencies": {"dsh-purge-safe": "file:../../../node_modules/dsh-purge-safe"},
                "dsh": {"profile": {"bundles": bundles}}}
    (folder / "package.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (folder / "cordis.patch.yml").write_text(patch, encoding="utf-8")


def web_status(label):
    logpath = root / (label + ".private.log")
    with logpath.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(node + [str(entry), "web", "--host", "127.0.0.1", "--port", "19341", "--no-open"],
                                   env=env, cwd=root, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(40):
                assert process.poll() is None, "Web host exited; see private log"
                match = re.search(r"http://127\.0\.0\.1:19341/\?token=\S+", logpath.read_text(encoding="utf-8"))
                if match:
                    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
                    opener.open(match[0], timeout=5).close()
                    response = opener.open("http://127.0.0.1:19341/dsh-purge-safe/status", timeout=15)
                    state = json.load(response)
                    assert state["ok"] and state["ready"] and state["patches_pending"] == 0, state
                    (root / (label + ".json")).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
                    return {k: state[k] for k in ("ok", "ready", "surface", "patches_applied", "patches_pending", "patches_ready")}
                time.sleep(.5)
            raise AssertionError("Web startup timeout")
        finally:
            process.terminate()
            process.wait(timeout=10)


source = json.loads((BOOK / "examples/label-task/input.json").read_text(encoding="utf-8"))
expected = [{"id": row["id"], "tag": row["tag"].strip().lower()} for row in source]
answer = json.dumps(expected, ensure_ascii=False)
task = "Normalize tags by trimming and lowercasing. Preserve every id and order; return only a JSON array.\n" + json.dumps(source)
requests = []


class Fixture(BaseHTTPRequestHandler):
    def log_message(self, *unused):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        requests.append({"path": self.path, "body": body})
        message = {"id": "book-fixture-1", "type": "message", "role": "assistant", "content": [],
                   "model": body.get("model", "deepseek-flash"), "stop_reason": None, "stop_sequence": None,
                   "usage": {"input_tokens": 10, "output_tokens": 0}}
        events = [("message_start", {"message": message}),
                  ("content_block_start", {"index": 0, "content_block": {"type": "text", "text": ""}}),
                  ("content_block_delta", {"index": 0, "delta": {"type": "text_delta", "text": answer}}),
                  ("content_block_stop", {"index": 0}),
                  ("message_delta", {"delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 50}}),
                  ("message_stop", {})]
        data = "".join("event: " + kind + "\ndata: " + json.dumps({"type": kind, **value}) + "\n\n" for kind, value in events).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    version = run("live-version", [str(entry), "--version"]).strip()
    assert version == "0.2.2-rc.3", version
    report["version"] = version
    contract = str(BOOK / "build/live_dsh_contract.mjs")
    apply = json.loads(run("live-apply", [contract, str(root), "dsh-purge-safe", "apply"]))
    report["stages"]["apply"] = dict(Counter(row["status"] for row in apply["result"]))
    assert len(apply["result"]) == 59 and all(row["status"] in ("applied", "already") for row in apply["result"])
    profile("web", ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-web-app", "dsh-purge-safe"])
    for label in ("live-web-first", "live-web-restart"):
        report["stages"][label] = web_status(label)
        print(label, "ready", flush=True)
    # The headless bundle retains workspace-write while patched base defaults
    # can infer never approval. Explicitly choose a preset for this fixture.
    # Its HTTP-only bridge has no webServer in a headless profile.
    profile("headless", ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-headless", "dsh-purge-safe"],
            "- id: permission\n  config:\n    defaultPreset: workspace-write\n"
            "- id: dsh-purge-safe-redteam-ui\n  disabled: true\n")
    report["headless_profile_overrides"] = {"permission.defaultPreset": "workspace-write", "HTTP-only redteam UI": "disabled"}
    previous = root / "live-task.stderr.txt"
    preserved = root / "live-task-default.stderr.txt"
    if previous.exists() and not preserved.exists() and "match no preset" in previous.read_text(encoding="utf-8"):
        preserved.write_bytes(previous.read_bytes())
    fixture = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    threading.Thread(target=fixture.serve_forever, daemon=True).start()
    env.update(DEEPSEEK_API_KEY="book-local-fixture", DEEPSEEK_BASE_URL=f"http://127.0.0.1:{fixture.server_port}")
    try:
        output = run("live-task", [str(entry), "headless", task], timeout=90)
    finally:
        fixture.shutdown()
        fixture.server_close()
    assert "entries did not activate" not in (root / "live-task.stderr.txt").read_text(encoding="utf-8"), "Inactive headless plugin; inspect stderr"
    (root / "live-model-requests.json").write_text(json.dumps(requests, ensure_ascii=False, indent=2), encoding="utf-8")
    assert requests, "No actual provider request reached the fixture"
    wire = json.dumps(requests[0]["body"], ensure_ascii=False)
    marker = (home / "prompt-inject.md").read_text(encoding="utf-8").strip()
    assert marker and marker in wire, "Custom injection absent from actual provider input"
    def strings(value):
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            return [s for v in value.values() for s in strings(v)]
        if isinstance(value, list):
            return [s for v in value for s in strings(v)]
        return []
    assert any(task in text for text in strings(requests[0]["body"])), "User task was changed"
    start, end = output.find("["), output.rfind("]")
    actual = json.loads(output[start:end + 1])
    assert actual == expected, "Durable task result did not preserve all records"
    report["stages"]["task"] = {"transport": "loopback Messages SSE fixture", "requests": len(requests),
                                    "injection_in_provider_input": True, "records_equal": len(expected)}
    profile("web", ["@deepseek-ai/dsh-base", "@deepseek-ai/dsh-web-app"])
    result = json.loads(run("live-revert", [contract, str(root), "dsh-purge-safe", "revert"]))
    before = json.loads((root / "before-files.json").read_text(encoding="utf-8"))
    differences = [name for name, digest in before.items() if sha256((root / name).read_bytes()).hexdigest() != digest]
    report["stages"]["restore"] = {"files_compared": len(before), "different": differences, "result": result["result"]}
    assert not differences, differences
    config = run("live-restored-config", [str(entry), "web", "--dump-config"])
    assert "@deepseek-ai/dsh-web-app" in config and "dsh-purge-safe" not in config
    report["passed"] = True


try:
    main()
except Exception as error:
    report["passed"] = False
    report["error"] = str(error)
    raise
finally:
    (root / "live-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("PASS: installed rc.3, 59 patch rows, plugin load/restart, actual local transport input, 12 records, restoration")
