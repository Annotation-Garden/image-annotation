"""Add the Claude Opus 4.8 `vision_neuro` annotation (description + post-QA/QC HED) to every
NSD annotation file, prepended so it becomes the frontend default.

Source data comes from the word-blurb run (a sibling repo):
  - data/aws_opus_desc/<stem>.json     Opus-4.8 vision description (+ token usage)
  - data/aws_opus_hed_qc/<stem>.json   image-verified, re-validated HED 8.4.0 string
  - prompts/vision_neuro.txt           the exact prompt used for the descriptions

The new entry is inserted at annotations[0]; the frontend derives its model dropdown order and
its sticky default from array order, so prepending makes `claude-opus-4-8` / `vision_neuro` the
default selection. Idempotent: re-running merges the `vision_neuro` prompt into an existing
`claude-opus-4-8` entry (preserving any other prompt keys) rather than discarding it.

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


def load_source(desc_f: Path, hed_f: Path) -> tuple[dict, dict]:
    return json.loads(desc_f.read_text()), json.loads(hed_f.read_text())


def build_prompt_entry(desc: dict, hed: dict, prompt_text: str) -> tuple[dict, bool]:
    """Return (prompt entry, usage_ok). usage_ok is False when token usage was not fully recorded."""
    usage = desc.get("usage") or {}
    itok, otok = usage.get("input_tokens"), usage.get("output_tokens")
    usage_ok = isinstance(itok, int) and isinstance(otok, int)
    ttok = (itok or 0) + (otok or 0)
    entry = {
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
    return entry, usage_ok


def preflight(files: list[Path], desc_dir: Path, hed_dir: Path) -> None:
    """Validate every source pair (exists, parseable, required non-empty keys) BEFORE any write,
    so a malformed/incomplete source can never leave the dataset half-populated."""
    problems: list[str] = []
    for fp in files:
        stem = fp.name.replace("_annotations.json", "")
        desc_f, hed_f = desc_dir / f"{stem}.json", hed_dir / f"{stem}.json"
        if not desc_f.exists() or not hed_f.exists():
            problems.append(f"{stem}: missing source file")
            continue
        try:
            desc, hed = load_source(desc_f, hed_f)
        except json.JSONDecodeError as e:
            problems.append(f"{stem}: malformed source JSON ({e})")
            continue
        if not (desc.get("image_description") or "").strip():
            problems.append(f"{stem}: empty/absent image_description")
        if not (hed.get("hed_string") or "").strip():
            problems.append(f"{stem}: empty/absent hed_string")
    if problems:
        raise SystemExit(
            f"Pre-flight failed for {len(problems)} stems; aborting before any write:\n  "
            + "\n  ".join(problems[:10])
            + ("\n  ..." if len(problems) > 10 else "")
        )


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
    preflight(files, desc_dir, hed_dir)

    updated = refreshed = 0
    missing_usage: list[str] = []
    for fp in files:
        stem = fp.name.replace("_annotations.json", "")
        try:
            desc, hed = load_source(desc_dir / f"{stem}.json", hed_dir / f"{stem}.json")
            prompt_entry, usage_ok = build_prompt_entry(desc, hed, prompt_text)
            if not usage_ok:
                missing_usage.append(stem)

            data = json.loads(fp.read_text())
            if "annotations" not in data or not isinstance(data["annotations"], list):
                raise ValueError("annotation file has no 'annotations' array")
            anns = data["annotations"]

            existing = next((a for a in anns if a.get("model") == MODEL), None)
            merged_prompts = {**(existing.get("prompts") if existing else {}), PROMPT_NAME: prompt_entry}
            total = sum((p.get("token_metrics") or {}).get("total_tokens") or 0 for p in merged_prompts.values())
            entry = {
                "model": MODEL,
                "temperature": TEMPERATURE,
                "prompts": merged_prompts,
                "metrics": {"total_tokens": total},
            }
            data["annotations"] = [entry, *[a for a in anns if a.get("model") != MODEL]]

            tmp = fp.with_suffix(".json.tmp")  # atomic write: full temp file, then rename
            tmp.write_text(json.dumps(data, indent=2, default=str))
            tmp.replace(fp)
            updated += 1
            if existing is not None:
                refreshed += 1
        except Exception as e:  # noqa: BLE001 - re-raise with the failing stem for context
            raise RuntimeError(f"failed on stem {stem} ({fp}): {e}") from e

    print(f"updated {updated}/{len(files)} annotation files "
          f"(prepended {MODEL}/{PROMPT_NAME}; {refreshed} pre-existing entries merged)")
    if missing_usage:
        print(f"WARNING: {len(missing_usage)} stems had incomplete token usage "
              f"(total_tokens may be 0): {missing_usage[:5]}")


if __name__ == "__main__":
    main()
