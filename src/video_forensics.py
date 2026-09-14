"""Create transparent initial-review reports for a local video or test file."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

CHUNK_SIZE = 1024 * 1024
LIMITATIONS = [
    "This educational tool records technical facts; it does not establish origin or authenticity.",
    "Metadata can be absent, changed, or misleading.",
    "A SHA-256 hash identifies a particular file but does not prove it is genuine or legally admissible.",
    "The tool does not determine whether content was edited or AI-generated.",
]

def utc_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()

def file_details(path: Path) -> dict:
    stat = path.stat()
    return {"path": str(path.resolve()), "name": path.name, "suffix": path.suffix.lower(), "size_bytes": stat.st_size, "created_utc": utc_time(stat.st_ctime), "modified_utc": utc_time(stat.st_mtime), "sha256": sha256_file(path)}

def collect_ffprobe(path: Path) -> dict:
    if shutil.which("ffprobe") is None:
        return {"available": False, "reason": "ffprobe is not installed"}
    command = ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, check=False)
    except subprocess.TimeoutExpired:
        return {"available": True, "error": "ffprobe timed out after 30 seconds"}
    if result.returncode != 0:
        return {"available": True, "error": result.stderr.strip() or "ffprobe failed"}
    return {"available": True, "data": json.loads(result.stdout)}

def markdown_report(report: dict) -> str:
    facts = report["file"]
    lines = ["# Initial Review Report", "", "## File facts", "", f"- **Name:** {facts['name']}", f"- **Path:** `{facts['path']}`", f"- **Size:** {facts['size_bytes']} bytes", f"- **Modified (UTC):** {facts['modified_utc']}", f"- **SHA-256:** `{facts['sha256']}`", "", "## Limitations", ""]
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "## Metadata collection", "", "```json", json.dumps(report["ffprobe"], indent=2), "```", ""])
    return "\n".join(lines)

def main() -> None:
    parser = argparse.ArgumentParser(description="Create an initial-review evidence report for one local file.")
    parser.add_argument("file", type=Path, help="Path to the file to inspect")
    parser.add_argument("--output-dir", type=Path, default=Path("reports"), help="Directory for generated reports")
    parser.add_argument("--no-ffprobe", action="store_true", help="Skip optional ffprobe metadata collection")
    args = parser.parse_args()
    if not args.file.is_file():
        parser.error(f"file not found or not a file: {args.file}")
    ffprobe = {"available": False, "reason": "skipped by --no-ffprobe"} if args.no_ffprobe else collect_ffprobe(args.file)
    report = {"report_version": "0.1.0", "generated_utc": datetime.now(timezone.utc).isoformat(), "purpose": "Educational initial technical review of one local file.", "file": file_details(args.file), "ffprobe": ffprobe, "limitations": LIMITATIONS}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base = args.file.stem + "_report"
    json_path = args.output_dir / f"{base}.json"
    markdown_path = args.output_dir / f"{base}.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown_report(report), encoding="utf-8")
    print(f"Created: {json_path}")
    print(f"Created: {markdown_path}")

if __name__ == "__main__":
    main()
