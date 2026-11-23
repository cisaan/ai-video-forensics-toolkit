# AI Video Forensics Toolkit

> A Python toolkit for responsible initial review of digital video files: metadata inspection, timestamp recording, SHA-256 hashing, and readable evidence reports.

## Why this project exists

Video files are often shared without enough context to assess their origin or handling. This project records transparent technical facts about a file before deeper specialist analysis. It is an MSc AI / cybersecurity portfolio project focused on careful claims, reproducibility, and clear reporting.

## What the toolkit does

- Calculates a SHA-256 hash to identify the exact file reviewed.
- Records path, file name, size, and file-system timestamps.
- Uses ffprobe, when installed, to collect container and stream metadata.
- Writes JSON and Markdown reports.
- Creates privacy-conscious run manifests for AI video-generation workflows.
- Verifies workflow, input and output files against their recorded hashes.

## Initial video review

Requirements: Python 3.10 or newer. ffprobe is optional; it is supplied with FFmpeg.

    python src/video_forensics.py /path/to/video.mp4 --output-dir reports

The command creates JSON and Markdown reports under `reports/`. To skip ffprobe:

    python src/video_forensics.py /path/to/video.mp4 --no-ffprobe

## AI generation run manifests

The run-manifest utility records UTC time, model/GPU metadata, optional generation settings, and SHA-256 hashes for the workflow, input image and generated output. It stores file basenames rather than local paths, and stores only a prompt-file digest—not the prompt text or media contents.

Create a manifest:

    python src/run_manifest.py record \
      --workflow workflows/example.json \
      --input assets/start-frame.png \
      --output outputs/generated.mp4 \
      --manifest reports/run-manifest.json \
      --model "Example model" \
      --model-version "1.0" \
      --gpu "Example GPU" \
      --resolution "640x360" \
      --fps 24 \
      --duration-seconds 4 \
      --seed 12345 \
      --prompt-file private-prompt.txt

Verify the same files later:

    python src/run_manifest.py verify \
      --manifest reports/run-manifest.json \
      --workflow workflows/example.json \
      --input assets/start-frame.png \
      --output outputs/generated.mp4

Verification returns exit code 0 when all hashes match, 1 when a file differs, and 2 for an invalid manifest or missing file. Add `--estimated-cost-gbp` when you have a reasonable estimate. Cost and run metadata are operator-supplied, not independently measured.

See [the run-manifest threat model](docs/run-manifest-threat-model.md) for privacy guidance and limitations. Do not commit prompts, credentials, private inputs, generated videos, model weights or cloud URLs. A hash match supports integrity checking; it does not prove file origin, authorship, authenticity or legal admissibility. A prompt hash may still be guessable if the prompt is short or predictable.

## Tests

The project uses Python's standard library; no external package installation is needed.

    python -m unittest discover -s tests -v

The suite includes unit tests and command-line end-to-end checks using disposable synthetic files. It checks manifest creation, successful verification, changed-file detection, prompt/secret privacy and controlled handling of missing files. GitHub Actions runs the suite on pushes and pull requests; no GPU or cloud generation is needed for these checks.

## Roadmap

- [x] Define scope, ethical boundaries, and evidence-reporting approach.
- [x] Create a Python command-line tool for file hashing and timestamp capture.
- [x] Add optional ffprobe metadata collection.
- [x] Generate JSON and Markdown reports.
- [x] Add safe synthetic test data and automated tests.
- [x] Add AI generation run manifests with integrity verification.
- [x] Document design decisions and security limitations.

## Project structure

    src/         Python command-line tools
    tests/       Automated checks using synthetic files
    sample_data/ Safe, non-sensitive test material
    docs/        Design and threat-model notes
    .github/     Continuous integration workflow

## Limitations

This is an educational initial-review and integrity-checking toolkit. Metadata can be missing, altered or inconsistent. A hash identifies particular bytes but does not establish origin or authenticity. The tools do not determine whether content was edited or AI-generated, and they do not establish legal admissibility or a complete chain of custody.

## License

Released under the [MIT License](LICENSE).
