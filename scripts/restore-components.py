#!/usr/bin/env python3
"""Restore the project's declared 4D components for the existing compiler action."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def restore(project):
    dependencies = json.loads(
        (project / "Project/Sources/dependencies.json").read_text(encoding="utf-8")
    )["dependencies"]
    components = project / "Components"
    components.mkdir(parents=True, exist_ok=True)
    resolved = {}
    with tempfile.TemporaryDirectory(prefix="ai00-components-") as directory:
        cache = Path(directory)
        for name, dependency in dependencies.items():
            if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
                raise ValueError(f"Invalid component namespace: {name}")
            repository = dependency["github"]
            version = dependency["version"]
            query = ["gh", "release", "view"]
            if version != "latest":
                query.append(version)
            query += ["--repo", repository, "--json", "tagName", "--jq", ".tagName"]
            tag = subprocess.check_output(query, text=True).strip()
            subprocess.run(
                ["gh", "release", "download", tag, "--repo", repository,
                 "--pattern", f"{name}.zip", "--dir", str(cache)], check=True)
            archive = cache / f"{name}.zip"
            subprocess.run(["ditto", "-x", "-k", str(archive), str(components)], check=True)
            bundle = components / f"{name}.4dbase"
            if not bundle.is_dir() or not (
                list(bundle.glob("*.4DZ")) or list(bundle.glob("*.4DC"))
            ):
                raise ValueError(f"{repository}@{tag}: missing compiled {name}.4dbase")
            resolved[name] = {
                "repository": repository, "tag": tag,
                "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
            }
            print(f"Restored {repository}@{tag}")
    provenance = project / "Resources/upstream/components.json"
    provenance.parent.mkdir(parents=True, exist_ok=True)
    provenance.write_text(json.dumps(resolved, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=ROOT / "Ai00")
    args = parser.parse_args()
    try:
        restore(args.project_dir.resolve())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Cannot restore 4D components: {error}", file=sys.stderr)
        sys.exit(1)
