# AI Video Forensics Toolkit

> A Python toolkit for responsible initial review of digital video files: metadata inspection, timestamp recording, SHA-256 hashing, and readable evidence reporting.

## Why this project exists

Video files are often shared without enough context to assess their origin or handling. This project explores how a repeatable, transparent workflow can record basic technical facts about a file before deeper specialist analysis.

It is being built as an MSc AI / cybersecurity portfolio project with an emphasis on careful claims, reproducibility, and clear reporting.

## Scope

The toolkit is intended to:

- calculate a SHA-256 file hash to identify the exact file reviewed;
- record file-system timestamps and size;
- extract available container and stream metadata;
- produce a human-readable report that can be retained with a review record.

## Important limitations

This is an educational, initial-review tool. Metadata can be missing, altered, or inconsistent. A hash identifies a specific file but does not establish who created it or whether its content is authentic. The toolkit does **not** claim to prove that a video is genuine, edited, AI-generated, or suitable as legal evidence.

## Planned workflow

1. Select a locally available video file.
2. Record its path, size, timestamps, and SHA-256 hash.
3. Extract available metadata using a documented method.
4. Generate a clear report with findings and limitations.
5. Retain only safe, non-sensitive sample files for testing.

## Roadmap

- [x] Define scope, ethical boundaries, and evidence-reporting approach.
- [ ] Create a Python command-line tool for file hashing and timestamp capture.
- [ ] Add metadata extraction using FFmpeg/ffprobe where installed.
- [ ] Generate JSON and Markdown reports.
- [ ] Add safe synthetic sample data and tests.
- [ ] Document design decisions and evaluation results.

## Project structure

```text
src/        Python source code
tests/      Automated checks
sample_data/ Safe, non-sensitive test material
docs/       Design notes and weekly progress
```

## Week 1 objective

Establish the repository, build a small file-inspection command, and document the data-handling boundaries. The first deliverable will be a reproducible report for a user-provided sample file.

## Technology direction

Python standard library for hashing and file details; FFmpeg/ffprobe for optional metadata extraction; JSON and Markdown for portable reports.

## License

Released under the [MIT License](LICENSE).
