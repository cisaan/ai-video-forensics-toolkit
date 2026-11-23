# Run manifest: scope and threat model

## Purpose

The run manifest links a video-generation workflow, source image and generated
video to SHA-256 digests and selected run metadata. It supports later integrity
checking and reproducibility review; it is not a chain-of-custody system.

## Assets and risks

| Asset or risk | Treatment |
| --- | --- |
| Workflow or media replaced after a run | Record hashes and compare them during verification. |
| Prompt or credential disclosure | Store only the prompt digest; do not embed workflow or media contents. |
| Local path disclosure | Store basenames only, not absolute paths. |
| Manifest altered or replaced | Keep the manifest in a controlled location and retain a separately protected copy or repository history. This prototype does not sign manifests. |
| Misleading metadata | Treat model, GPU, timing and cost fields as operator-supplied claims, not independently verified facts. |

## Handling guidance

- Use synthetic or authorised media only. Do not commit private images, prompts,
  generated videos, model weights, API tokens or cloud URLs.
- Keep evidence and prompts out of public repositories unless reviewed and
  intentionally sanitised.
- Avoid passing sensitive prompts as command-line text; use a local prompt file
  and remember that its digest may still reveal equality between known prompts.
- A SHA-256 match only indicates that the bytes match the recorded digest. It
  does not prove who created the file, when it was created, or that the content
  is authentic.
- A hash-only prompt record can still be susceptible to guessing for short or
  predictable prompts. Do not treat it as anonymisation.
