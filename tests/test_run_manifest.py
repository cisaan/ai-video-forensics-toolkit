"""Tests for the privacy-conscious AI run manifest utility."""
import json
import tempfile
import unittest
from pathlib import Path

from src.run_manifest import create_manifest, sha256_file, verify_manifest


class RunManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.workflow = self.root / "workflow.json"
        self.input_media = self.root / "input.png"
        self.output_media = self.root / "output.mp4"
        self.prompt_file = self.root / "private-prompt.txt"
        self.manifest_path = self.root / "manifest.json"

        self.workflow.write_text(
            '{"api_key": "synthetic-secret", "steps": []}', encoding="utf-8"
        )
        self.input_media.write_bytes(b"synthetic input")
        self.output_media.write_bytes(b"synthetic video bytes")
        self.prompt_file.write_text(
            "Synthetic prompt that must not appear in the manifest", encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def make_manifest(self):
        return create_manifest(
            self.workflow,
            self.input_media,
            self.output_media,
            model="example-model",
            model_version="1.0",
            gpu="test-gpu",
            resolution="640x360",
            fps=24,
            duration_seconds=2,
            seed=123,
            estimated_cost_gbp=0,
            prompt_file=self.prompt_file,
        )

    def test_same_file_has_stable_sha256(self):
        self.assertEqual(sha256_file(self.input_media), sha256_file(self.input_media))

    def test_unchanged_artifacts_verify_successfully(self):
        self.manifest_path.write_text(
            json.dumps(self.make_manifest()), encoding="utf-8"
        )
        results = verify_manifest(
            self.manifest_path,
            {
                "workflow": self.workflow,
                "input": self.input_media,
                "output": self.output_media,
            },
        )
        self.assertEqual([item["ok"] for item in results], [True, True, True])

    def test_one_byte_change_is_detected(self):
        self.manifest_path.write_text(
            json.dumps(self.make_manifest()), encoding="utf-8"
        )
        self.output_media.write_bytes(b"synthetic video byteS")
        results = verify_manifest(
            self.manifest_path,
            {
                "workflow": self.workflow,
                "input": self.input_media,
                "output": self.output_media,
            },
        )
        self.assertFalse(results[-1]["ok"])

    def test_manifest_contains_hash_not_prompt_or_workflow_contents(self):
        manifest = self.make_manifest()
        serialised = json.dumps(manifest)
        self.assertNotIn("Synthetic prompt", serialised)
        self.assertNotIn("synthetic-secret", serialised)
        self.assertNotIn("api_key", serialised)
        self.assertNotIn(str(self.root), serialised)
        self.assertEqual(len(manifest["prompt_sha256"]), 64)

    def test_missing_artifact_is_a_controlled_error(self):
        missing = self.root / "missing.mp4"
        with self.assertRaisesRegex(ValueError, "output file not found"):
            create_manifest(
                self.workflow,
                self.input_media,
                missing,
                model="example-model",
                model_version="1.0",
                gpu="test-gpu",
            )


if __name__ == "__main__":
    unittest.main()
