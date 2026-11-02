#!/usr/bin/env python3
"""Build the pinned upstream server and stage resources for the 4D component."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "aarch64-apple-darwin": ("macOS", "ai00-server"),
    "x86_64-apple-darwin": ("macOS", "ai00-server-x86_64"),
    "x86_64-pc-windows-msvc": ("Windows", "ai00-server.exe"),
}


def run(*args, cwd=None, capture=False, env=None):
    return subprocess.run(
        args, cwd=cwd, check=True, text=True, env=env,
        stdout=subprocess.PIPE if capture else None,
    ).stdout


def verify_hash(path, expected):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"{path}: expected SHA-256 {expected}, got {actual}")


def check_source(source, pin):
    actual = run("git", "rev-parse", "HEAD", cwd=source, capture=True).strip()
    if actual != pin["commit"]:
        raise ValueError(f"Expected upstream {pin['commit']}, got {actual}")
    if run("git", "status", "--porcelain", "--untracked-files=no",
           cwd=source, capture=True).strip():
        raise ValueError("Upstream tracked files are modified; use a clean checkout")
    verify_hash(source / "Cargo.lock", pin["cargo_lock_sha256"])
    verify_hash(source / "assets/www/index.zip", pin["web_ui_sha256"])
    verify_hash(source / "assets/tokenizer/rwkv_vocab_v20230424.json",
                pin["tokenizer_sha256"])
    with zipfile.ZipFile(source / "assets/www/index.zip") as archive:
        if archive.testzip() is not None:
            raise ValueError("Upstream WebUI ZIP is corrupt")


def stage(source, destination, target, pin):
    platform, name = TARGETS[target]
    executable = "ai00-server.exe" if platform == "Windows" else "ai00-server"
    files = {
        source / "target" / target / "release" / executable: f"bin/{platform}/{name}",
        source / "assets/www/index.zip": "www/index.zip",
        source / "assets/tokenizer/rwkv_vocab_v20230424.json": "tokenizer/rwkv_vocab.json",
        source / "assets/tokenizer/rwkv_vocab_v20230424.txt":
            "tokenizer/rwkv_vocab_v20230424.txt",
        source / "LICENSE": "upstream/LICENSE",
    }
    if platform == "Windows":
        files[source / "assets/ort/onnxruntime.dll"] = "ort/onnxruntime.dll"
    for src, relative in files.items():
        dest = destination / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    if platform == "macOS":
        (destination / f"bin/{platform}/{name}").chmod(0o755)
    metadata = dict(pin, target=target, artifacts={
        relative: hashlib.sha256((destination / relative).read_bytes()).hexdigest()
        for relative in files.values()
    })
    provenance = destination / "upstream" / f"{target}.json"
    provenance.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, choices=TARGETS)
    parser.add_argument("--source-dir", type=Path, default=ROOT / ".build/ai00_server")
    parser.add_argument("--output", type=Path,
                        help="Resources directory (default: dist/<target>)")
    args = parser.parse_args()
    source = args.source_dir.resolve()
    output = (args.output or ROOT / "dist" / args.target).resolve()
    pin = json.loads((ROOT / "upstream.json").read_text(encoding="utf-8"))
    if not source.exists():
        source.parent.mkdir(parents=True, exist_ok=True)
        run("git", "clone", "--config", "core.autocrlf=false", "--no-checkout",
            pin["repository"], str(source))
        run("git", "checkout", "--detach", pin["commit"], cwd=source)
    run("git", "lfs", "pull", cwd=source)
    check_source(source, pin)
    env = os.environ.copy()
    if args.target.endswith("apple-darwin"):
        env["MACOSX_DEPLOYMENT_TARGET"] = "11.0"
    run("cargo", f"+{pin['rust_toolchain']}", "build", "--locked", "--release",
        "--package", "ai00-server", "--target", args.target, cwd=source, env=env)
    executable = source / "target" / args.target / "release" / (
        "ai00-server.exe" if args.target.endswith("msvc") else "ai00-server")
    help_text = run(str(executable), "--help", cwd=source, capture=True)
    for flag in ("--config", "--ip", "--port"):
        if flag not in help_text:
            raise ValueError(f"CLI smoke test: missing {flag}")
    version = run(str(executable), "--version", cwd=source, capture=True)
    if pin["crate_version"] not in version.split():
        raise ValueError(f"Unexpected CLI version: {version}")
    stage(source, output, args.target, pin)
    print(f"Built {pin['tag']} ({pin['commit']}) for {args.target}: {output}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile, subprocess.CalledProcessError) as error:
        print(f"Source build failed: {error}", file=sys.stderr)
        sys.exit(1)
