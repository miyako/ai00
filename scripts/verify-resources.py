#!/usr/bin/env python3
"""Reject incomplete or stale server resources before component packaging."""

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "aarch64-apple-darwin": "bin/macOS/ai00-server",
    "x86_64-apple-darwin": "bin/macOS/ai00-server-x86_64",
    "x86_64-pc-windows-msvc": "bin/Windows/ai00-server.exe",
}


def verify(resources, pin):
    for target, executable in TARGETS.items():
        metadata = json.loads(
            (resources / "upstream" / f"{target}.json").read_text(encoding="utf-8"))
        for key, value in pin.items():
            if metadata.get(key) != value:
                raise ValueError(f"{target}: upstream pin mismatch for {key}")
        if metadata.get("target") != target or executable not in metadata["artifacts"]:
            raise ValueError(f"{target}: missing executable provenance")
        required = {executable, "www/index.zip", "tokenizer/rwkv_vocab.json",
                    "tokenizer/rwkv_vocab_v20230424.txt", "upstream/LICENSE"}
        if target.endswith("msvc"):
            required.add("ort/onnxruntime.dll")
        if not required.issubset(metadata["artifacts"]):
            raise ValueError(f"{target}: incomplete runtime asset provenance")
        for relative, expected in metadata["artifacts"].items():
            path = resources / relative
            if not path.resolve().is_relative_to(resources.resolve()):
                raise ValueError(f"{target}: invalid artifact path {relative}")
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError(f"{target}: artifact checksum mismatch for {relative}")
    # GitHub artifact downloads do not preserve Unix executable permissions.
    for relative in TARGETS.values():
        if not relative.endswith(".exe"):
            path = resources / relative
            path.chmod(path.stat().st_mode | 0o111)
    print("All three source-built server targets and runtime assets verified")


if __name__ == "__main__":
    try:
        verify(ROOT / "Ai00/Resources",
               json.loads((ROOT / "upstream.json").read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError) as error:
        print(f"Cannot package component: {error}", file=sys.stderr)
        sys.exit(1)
