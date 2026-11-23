"""Create and verify privacy-conscious manifests for AI video-generation runs.

This command-line tool links a generation workflow, its input image, and its
output video using SHA-256 hashes. It also records selected run details, such as
the model, GPU, resolution, and seed, so a run can be reviewed later.

Typical use:
    Record a run with the record subcommand, supplying workflow, input, output,
    manifest, model, model-version, and GPU values.
    Later, use the verify subcommand with that manifest and the same three files.

Privacy boundary:
    The manifest contains file basenames and hashes, not file contents or
    absolute paths. If a prompt file is supplied, only its SHA-256 digest is
    recorded; the prompt text is not copied into the manifest. A prompt hash can
    still be guessable for short or predictable prompts.

Limits:
    A matching hash shows that file bytes match the digest in the manifest. It
    does not prove who created the file, where it came from, or that it is
    authentic. The manifest is not signed and is not a complete chain-of-custody
    record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

CHUNK_SIZE = 1024 * 1024  # Read large video files in 1 MiB pieces.
ARTIFACT_LABELS = ("workflow", "input", "output")


def sha256_file(path: Path) -> str:
    """Calculate a file's SHA-256 digest without loading the whole file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_file(path: Path, label: str) -> None:
    """Stop with a clear error unless path points to a regular file."""
    if not path.is_file():
        raise ValueError(f"{label} file not found or not a regular file: {path}")


def create_manifest(
    workflow: Path,
    input_media: Path,
    output_media: Path,
    *,
    model: str,
    model_version: str,
    gpu: str,
    resolution: str | None = None,
    fps: float | None = None,
    duration_seconds: float | None = None,
    seed: int | None = None,
    estimated_cost_gbp: float | None = None,
    prompt_file: Path | None = None,
) -> dict:
    """Build a JSON-ready run record from files and operator-supplied metadata.

    Hashes the workflow, input and output files. Optional prompt text is hashed
    separately; it is never copied into the returned manifest. Only each file's
    basename is recorded, so local directory paths are not disclosed.
    """
    paths = {"workflow": workflow, "input": input_media, "output": output_media}
    for label, path in paths.items():
        _require_file(path, label)
    if prompt_file is not None:
        _require_file(prompt_file, "prompt")

    # These values help describe the run but are supplied by the operator.
    metadata = {
        "model": model,
        "model_version": model_version,
        "gpu": gpu,
        "resolution": resolution,
        "fps": fps,
        "duration_seconds": duration_seconds,
        "seed": seed,
        "estimated_cost_gbp": estimated_cost_gbp,
    }

    # Store labels, basenames and digests—not workflow or media file contents.
    artifacts = {
        label: {"name": path.name, "sha256": sha256_file(path)}
        for label, path in paths.items()
    }
    # Keep the prompt private by recording only its digest, when provided.
    prompt_digest = sha256_file(prompt_file) if prompt_file is not None else None

    return {
        "schema_version": "1.0",
        "recorded_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "metadata": metadata,
        "prompt_sha256": prompt_digest,
        "artifacts": artifacts,
    }


def verify_manifest(manifest_path: Path, artifact_paths: Mapping[str, Path]) -> list[dict]:
    """Re-hash supplied files and compare them with the manifest's saved digests.

    Returns one result per required artefact. Each result has an ok value:
    True means the digest matches; False means the file has changed. Missing
    files or malformed manifest entries raise a controlled error for the CLI.
    """
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    recorded = manifest.get("artifacts")
    if not isinstance(recorded, dict):
        raise ValueError("manifest is missing a valid 'artifacts' object")

    results = []
    for label in ARTIFACT_LABELS:
        entry = recorded.get(label)
        path = artifact_paths.get(label)
        if not isinstance(entry, dict) or not isinstance(entry.get("sha256"), str):
            raise ValueError(f"manifest is missing a valid SHA-256 for {label}")
        if path is None:
            raise ValueError(f"no file supplied for {label}")
        _require_file(path, label)
        actual = sha256_file(path)
        expected = entry["sha256"]
        results.append({
            "label": label,
            "expected": expected,
            "actual": actual,
            "ok": actual == expected,
        })
    return results


def _positive_float(value: str) -> float:
    """Parse a command-line number that must be greater than zero."""
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return number


def _non_negative_float(value: str) -> float:
    """Parse a command-line amount that may be zero but not negative."""
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("value must be zero or greater")
    return number


def build_parser() -> argparse.ArgumentParser:
    """Define the record and verify commands, their options, and help text."""
    parser = argparse.ArgumentParser(
        description="Record or verify hashes for an AI video-generation run."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # The record command creates a new manifest from one generation run.
    record = subparsers.add_parser("record", help="write a run manifest")
    record.add_argument("--workflow", type=Path, required=True)
    record.add_argument("--input", dest="input_media", type=Path, required=True)
    record.add_argument("--output", dest="output_media", type=Path, required=True)
    record.add_argument("--manifest", type=Path, required=True, help="output JSON manifest")
    record.add_argument("--model", required=True)
    record.add_argument("--model-version", required=True)
    record.add_argument("--gpu", required=True)
    record.add_argument("--resolution")
    record.add_argument("--fps", type=_positive_float)
    record.add_argument("--duration-seconds", type=_positive_float)
    record.add_argument("--seed", type=int)
    record.add_argument("--estimated-cost-gbp", type=_non_negative_float)
    record.add_argument(
        "--prompt-file",
        type=Path,
        help="optional local prompt file; only its SHA-256 digest is recorded",
    )

    # The verify command compares fresh hashes with those saved in a manifest.
    verify = subparsers.add_parser("verify", help="verify files against a manifest")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--workflow", type=Path, required=True)
    verify.add_argument("--input", dest="input_media", type=Path, required=True)
    verify.add_argument("--output", dest="output_media", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the selected command and return its process exit status.

    Returns 0 when recording succeeds or all files verify, 1 when one or more
    hashes differ, and 2 for a missing file or invalid manifest. Argument
    parsing provides its own usage and validation messages.
    """
    args = build_parser().parse_args(argv)
    try:
        if args.command == "record":
            manifest = create_manifest(
                args.workflow,
                args.input_media,
                args.output_media,
                model=args.model,
                model_version=args.model_version,
                gpu=args.gpu,
                resolution=args.resolution,
                fps=args.fps,
                duration_seconds=args.duration_seconds,
                seed=args.seed,
                estimated_cost_gbp=args.estimated_cost_gbp,
                prompt_file=args.prompt_file,
            )
            args.manifest.parent.mkdir(parents=True, exist_ok=True)
            args.manifest.write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
            print(f"Manifest written: {args.manifest}")
            return 0

        # Match each CLI path to the label used when the manifest was recorded.
        supplied = {
            "workflow": args.workflow,
            "input": args.input_media,
            "output": args.output_media,
        }
        results = verify_manifest(args.manifest, supplied)
        for item in results:
            status = "PASS" if item["ok"] else "FAIL"
            print(f"{status} {item['label']}: {item['actual']}")
        # A changed file produces a non-zero status, useful for scripts and CI.
        return 0 if all(item["ok"] for item in results) else 1
    except (OSError, ValueError, json.JSONDecodeError) as error:
        # Give the user a concise diagnostic without exposing file contents.
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
