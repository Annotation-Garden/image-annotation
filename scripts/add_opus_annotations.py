"""Add the Claude Opus 4.8 `vision_neuro` annotation (description + post-QA/QC HED) to every
NSD annotation file, prepended so it becomes the frontend default.

Source data comes from the word-blurb run (a sibling repo):
  - data/aws_opus_desc/<stem>.json     Opus-4.8 vision description (+ token usage)
  - data/aws_opus_hed_qc/<stem>.json   image-verified, re-validated HED 8.4.0 string
  - prompts/vision_neuro.txt           the exact prompt used for the descriptions

The new entry is inserted at annotations[0]; the frontend derives its model dropdown order and
its sticky default from array order, so prepending makes `claude-opus-4-8` / `vision_neuro` the
default selection. Idempotent: a pre-existing `claude-opus-4-8` entry is refreshed in place.

Usage:
    python3 scripts/add_opus_annotations.py [--word-blurb /path/to/word-blurb]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

MODEL = "claude-opus-4-8"
PROMPT_NAME = "vision_neuro"
TEMPERATURE = 1.0  # Opus 4.8 only accepts temperature=1 (real, not a placeholder)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WB = Path("/Users/yahya/Documents/git/word-blurb")


def build_entry(desc: dict, hed: dict, prompt_text: str) -> dict:
    usage = desc.get("usage") or {}
    itok = usage.get("input_tokens")
    otok = usage.get("output_tokens")
    ttok = (itok or 0) + (otok or 0)
    return {
        "model": MODEL,
        "temperature": TEMPERATURE,
        "prompts": {
            PROMPT_NAME: {
                "prompt_text": prompt_text,
                "response": desc["image_description"],
                "response_format": "text",
                "response_data": None,
                "error": None,
                "hed_annotation": hed["hed_string"],
                # real token usage from the description call; no per-image timing was recorded,
                # so performance_metrics is intentionally omitted rather than fabricated.
                "token_metrics": {"input_tokens": itok, "output_tokens": otok, "total_tokens": ttok},
            }
        },
        "metrics": {"total_tokens": ttok},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--word-blurb", type=Path, default=DEFAULT_WB)
    ap.add_argument("--ann-dir", type=Path, default=REPO_ROOT / "annotations/nsd")
    args = ap.parse_args()

    desc_dir = args.word_blurb / "data/aws_opus_desc"
    hed_dir = args.word_blurb / "data/aws_opus_hed_qc"
    prompt_text = (args.word_blurb / "prompts/vision_neuro.txt").read_text().strip()

    files = sorted(args.ann_dir.glob("shared*_annotations.json"))
    if not files:
        raise SystemExit(f"No annotation files under {args.ann_dir}")

    # Pre-flight: every annotation file must have both source records, else abort before any
    # write so the dataset is never left half-populated.
    missing = [
        fp.name.replace("_annotations.json", "")
        for fp in files
        if not (desc_dir / f"{fp.name.replace('_annotations.json', '')}.json").exists()
        or not (hed_dir / f"{fp.name.replace('_annotations.json', '')}.json").exists()
    ]
    if missing:
        raise SystemExit(
            f"Missing word-blurb source for {len(missing)} stems (e.g. {missing[:5]}); "
            "aborting before any write."
        )

    updated = refreshed = 0
    for fp in files:
        stem = fp.name.replace("_annotations.json", "")
        desc = json.loads((desc_dir / f"{stem}.json").read_text())
        hed = json.loads((hed_dir / f"{stem}.json").read_text())
        entry = build_entry(desc, hed, prompt_text)
        data = json.loads(fp.read_text())
        anns = data.get("annotations", [])
        kept = [a for a in anns if a.get("model") != MODEL]
        if len(kept) != len(anns):
            refreshed += 1
        data["annotations"] = [entry, *kept]  # prepend -> default selection
        fp.write_text(json.dumps(data, indent=2, default=str))
        updated += 1

    print(f"updated {updated}/{len(files)} annotation files "
          f"(prepended {MODEL}/{PROMPT_NAME}; {refreshed} pre-existing entries refreshed)")


if __name__ == "__main__":
    main()
