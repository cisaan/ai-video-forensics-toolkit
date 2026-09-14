# AI Video Forensics Toolkit

> A Python toolkit for responsible initial review of digital video files: metadata inspection, timestamp recording, SHA-256 hashing, and readable evidence reports.

## Why this project exists

Video files are often shared without enough context to assess their origin or handling. This project records transparent technical facts about a file before deeper specialist analysis. It is an MSc AI / cybersecurity portfolio project focused on careful claims, reproducibility, and clear reporting.

## What the first version does

- Calculates a SHA-256 hash to identify the exact file reviewed.
- Records path, file name, size, and file-system timestamps.
- Uses ffprobe, when installed, to collect container and stream metadata.
- Writes both JSON and Markdown reports.

## Important limitations

This is an educational initial-review tool. Metadata can be missing, altered, or inconsistent. A hash identifies a specific file but does not establish origin or authenticity. The toolkit does **not** prove that a video is genuine, edited, AI-generated, or suitable as legal evidence.

## Run it

Requirements: Python 3.10 or newer. ffprobe is optional; it is supplied with FFmpeg.

    git clone https://github.com/cisaan/ai-video-forensics-toolkit.git
    cd ai-video-forensics-toolkit
    python src/video_forensics.py /path/to/video.mp4 --output-dir reports

The command creates:

    reports/<video_name>_report.json
    reports/<video_name>_report.md

To run without ffprobe metadata collection:

    python src/video_forensics.py /path/to/video.mp4 --no-ffprobe

## Planned workflow

1. Select a locally available video file.
2. Record its path, size, timestamps, and SHA-256 hash.
3. Extract available metadata using a documented method.
4. Generate a clear report with findings and limitations.
5. Retain only safe, non-sensitive sample files for testing.

## Roadmap

- [x] Define scope, ethical boundaries, and evidence-reporting approach.
- [x] Create a Python command-line tool for file hashing and timestamp capture.
- [x] Add optional ffprobe metadata collection.
- [x] Generate JSON and Markdown reports.
- [ ] Add safe synthetic sample data and automated tests.
- [ ] Document design decisions and evaluation results.

## Project structure

    src/         Python source code
    tests/       Automated checks
    sample_data/ Safe, non-sensitive test material
    docs/        Design notes and weekly progress

## License

Released under the [MIT License](LICENSE).
