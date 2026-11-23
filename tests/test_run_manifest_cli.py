"""End-to-end CLI tests using disposable synthetic files only."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY_ROOT / "src" / "run_manifest.py"


class RunManifestCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workflow = self.root / "workflow.json"
        self.input_media = self.root / "input.png"
        self.output_media = self.root / "output.mp4"
        self.prompt_file = self.root / "prompt.txt"
        self.manifest = self.root / "run-manifest.json"

        self.workflow.write_text(
            '{"api_key": "test-only-secret", "steps": []}', encoding="utf-8"
        )
        self.input_media.write_bytes(b"synthetic input bytes")
        self.output_media.write_bytes(b"synthetic output bytes")
        self.prompt_file.write_text(
            "private synthetic prompt", encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, arguments)],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def record(self):
        return self.run_cli(
            "record",
            "--workflow", self.workflow,
            "--input", self.input_media,
            "--output", self.output_media,
            "--manifest", self.manifest,
            "--model", "synthetic-model",
            "--model-version", "test-version",
            "--gpu", "synthetic-gpu",
            "--prompt-file", self.prompt_file,
        )

    def verify(self):
        return self.run_cli(
            "verify",
            "--manifest", self.manifest,
            "--workflow", self.workflow,
            "--input", self.input_media,
            "--output", self.output_media,
        )

    def test_cli_records_private_data_as_hashes_and_verifies_unchanged_files(self):
        recorded = self.record()
        self.assertEqual(recorded.returncode, 0, recorded.stderr)
        manifest_text = self.manifest.read_text(encoding="utf-8")
        manifest = json.loads(manifest_text)
        self.assertNotIn("private synthetic prompt", manifest_text)
        self.assertNotIn("test-only-secret", manifest_text)
        self.assertEqual(len(manifest["prompt_sha256"]), 64)

        verified = self.verify()
        self.assertEqual(verified.returncode, 0, verified.stderr)
        self.assertIn("PASS workflow:", verified.stdout)
        self.assertIn("PASS input:", verified.stdout)
        self.assertIn("PASS output:", verified.stdout)

    def test_cli_returns_failure_after_output_is_changed(self):
        recorded = self.record()
        self.assertEqual(recorded.returncode, 0, recorded.stderr)
        self.output_media.write_bytes(b"one byte changed!")
        verified = self.verify()
        self.assertEqual(verified.returncode, 1)
        self.assertIn("FAIL output:", verified.stdout)

    def test_cli_returns_controlled_error_for_missing_file(self):
        self.output_media.unlink()
        recorded = self.record()
        self.assertEqual(recorded.returncode, 2)
        self.assertIn("output file not found", recorded.stderr)


if __name__ == "__main__":
    unittest.main()
