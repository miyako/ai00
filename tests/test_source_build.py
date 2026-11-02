import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = load_script("build-server")
verify = load_script("verify-resources")
components = load_script("restore-components")


class SourceBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.resources = self.root / "resources"
        self.pin = json.loads((ROOT / "upstream.json").read_text())
        for relative in (
            "Cargo.lock", "LICENSE", "assets/tokenizer/rwkv_vocab_v20230424.json",
            "assets/tokenizer/rwkv_vocab_v20230424.txt", "assets/ort/onnxruntime.dll",
        ):
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(relative.encode())
        web = self.source / "assets/www/index.zip"
        web.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(web, "w") as archive:
            archive.writestr("index.html", "test UI")
        for relative, key in (
            ("Cargo.lock", "cargo_lock_sha256"),
            ("assets/www/index.zip", "web_ui_sha256"),
            ("assets/tokenizer/rwkv_vocab_v20230424.json", "tokenizer_sha256"),
        ):
            self.pin[key] = hashlib.sha256((self.source / relative).read_bytes()).hexdigest()

    def stage_all(self):
        for target in build.TARGETS:
            name = "ai00-server.exe" if target.endswith("msvc") else "ai00-server"
            executable = self.source / "target" / target / "release" / name
            executable.parent.mkdir(parents=True, exist_ok=True)
            executable.write_bytes(target.encode())
            build.stage(self.source, self.resources, target, self.pin)

    def test_all_targets_stage_and_verify(self):
        self.stage_all()
        verify.verify(self.resources, self.pin)
        self.assertTrue((self.resources / "ort/onnxruntime.dll").is_file())
        self.assertEqual((self.resources / "tokenizer/rwkv_vocab.json").read_bytes(),
                         (self.source / "assets/tokenizer/rwkv_vocab_v20230424.json").read_bytes())

    def test_missing_target_rejected(self):
        self.stage_all()
        (self.resources / "bin/macOS/ai00-server-x86_64").unlink()
        with self.assertRaises(FileNotFoundError):
            verify.verify(self.resources, self.pin)

    def test_stale_binary_rejected(self):
        self.stage_all()
        (self.resources / "bin/Windows/ai00-server.exe").write_bytes(b"old binary")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            verify.verify(self.resources, self.pin)

    def test_wrong_pin_rejected(self):
        self.stage_all()
        with self.assertRaisesRegex(ValueError, "pin mismatch"):
            verify.verify(self.resources, dict(self.pin, commit="wrong"))

    def test_incomplete_runtime_provenance_rejected(self):
        self.stage_all()
        path = self.resources / "upstream/x86_64-pc-windows-msvc.json"
        metadata = json.loads(path.read_text())
        del metadata["artifacts"]["ort/onnxruntime.dll"]
        path.write_text(json.dumps(metadata))
        with self.assertRaisesRegex(ValueError, "incomplete runtime"):
            verify.verify(self.resources, self.pin)

    @unittest.skipIf(os.name == "nt", "Unix executable permissions")
    def test_executable_permissions_restored_after_artifact_download(self):
        self.stage_all()
        path = self.resources / "bin/macOS/ai00-server"
        path.chmod(0o644)
        verify.verify(self.resources, self.pin)
        self.assertTrue(path.stat().st_mode & 0o111)

    def test_wrong_source_and_dirty_source_rejected(self):
        with patch.object(build, "run", return_value="wrong\n"):
            with self.assertRaisesRegex(ValueError, "Expected upstream"):
                build.check_source(self.source, self.pin)
        with patch.object(build, "run", side_effect=[self.pin["commit"], " M Cargo.toml"]):
            with self.assertRaisesRegex(ValueError, "modified"):
                build.check_source(self.source, self.pin)

    def test_clean_source_and_asset_hashes(self):
        with patch.object(build, "run", side_effect=[self.pin["commit"], ""]):
            build.check_source(self.source, self.pin)
        (self.source / "assets/www/index.zip").write_bytes(b"version https://git-lfs.github.com/spec/v1")
        with patch.object(build, "run", side_effect=[self.pin["commit"], ""]):
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                build.check_source(self.source, self.pin)

    def test_checkout_forces_lf_even_with_global_crlf_policy(self):
        repository = self.root / "fixture"
        repository.mkdir()
        build.run("git", "init", "--quiet", str(repository))
        (repository / ".gitattributes").write_bytes(b"* text=auto\n")
        (repository / "Cargo.lock").write_bytes(b"first\nsecond\n")
        build.run("git", "-c", "core.autocrlf=false", "add", ".", cwd=repository)
        build.run("git", "-c", "user.name=Build Test", "-c", "user.email=build@example.invalid",
                  "-c", "commit.gpgsign=false", "commit", "--quiet", "--no-verify",
                  "-m", "fixture", cwd=repository)
        commit = build.run("git", "rev-parse", "HEAD", cwd=repository, capture=True).strip()
        checkout = self.root / "checkout"
        global_config = self.root / "gitconfig"
        global_config.write_text("[core]\n\teol = crlf\n", encoding="utf-8")
        with patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(global_config),
                                   "GIT_CONFIG_NOSYSTEM": "1"}):
            build.checkout_source(checkout, {"repository": str(repository), "commit": commit})
        self.assertEqual((checkout / "Cargo.lock").read_bytes(), b"first\nsecond\n")

    def test_packaging_paths_both_consume_source_artifacts(self):
        workflow = (ROOT / ".github/workflows/publish.yml").read_text()
        self.assertEqual(workflow.count("needs: server"), 2)
        self.assertEqual(workflow.count("pattern: server-*"), 2)
        self.assertEqual(workflow.count("run: python3 scripts/verify-resources.py"), 2)
        self.assertEqual(workflow.count("run: python3 scripts/restore-components.py"), 2)
        self.assertEqual(workflow.count('test -s "$PRODUCT_PATH/Ai00.4DZ"'), 2)
        self.assertEqual(workflow.count('--resources "$PRODUCT_PATH/Resources"'), 2)

    def test_pages_uses_readme(self):
        self.assertIn("{% include_relative README.md %}", (ROOT / "guide.md").read_text())
        self.assertIn("'/guide.html'", (ROOT / "index.md").read_text())

    def test_publish_versions_clean_checkout_before_staging_resources(self):
        workflow = (ROOT / ".github/workflows/publish.yml").read_text()
        for job in ("publish", "publish-locally"):
            with self.subTest(job=job):
                steps = workflow.split(f"\n  {job}:\n", 1)[1].split("\n  publish-locally:\n", 1)[0]
                checkout = steps.index("uses: actions/checkout@v4")
                version = steps.index("uses: miyako/4D/.github/actions/package-set-version@v1")
                staging = steps.index("uses: actions/download-artifact@v4")
                restore = steps.index("run: python3 scripts/restore-components.py")
                build_step = steps.index("uses: miyako/4D/.github/actions/build-component@v1")
                self.assertLess(checkout, version)
                self.assertLess(version, staging)
                self.assertLess(staging, restore)
                self.assertLess(restore, build_step)

    def test_invalid_component_namespace_rejected(self):
        project = self.root / "project"
        manifest = project / "Project/Sources/dependencies.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"dependencies": {
            "../escape": {"github": "miyako/event", "version": "latest"}
        }}))
        with self.assertRaisesRegex(ValueError, "Invalid component namespace"):
            components.restore(project)

    def test_missing_compiled_dependency_rejected(self):
        project = self.root / "project"
        manifest = project / "Project/Sources/dependencies.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"dependencies": {
            "event": {"github": "miyako/event", "version": "latest"}
        }}))
        with patch.object(components.subprocess, "check_output", return_value="20.0.19\n"), \
                patch.object(components.subprocess, "run"):
            with self.assertRaisesRegex(ValueError, "missing compiled"):
                components.restore(project)


if __name__ == "__main__":
    unittest.main()
