#!/usr/bin/env python3
"""Check annotation quality and flag problematic responses.

This script identifies annotations with quality issues:
- Abnormally long responses (>10KB by default)
- Repetitive patterns (e.g., "!#system" loops)
- Failed JSON parsing (from error field)
- Extreme token counts

Usage:
    python scripts/check_annotation_quality.py annotations/nsd/
    python scripts/check_annotation_quality.py annotations/nsd/ --max-length 5000
    python scripts/check_annotation_quality.py annotations/nsd/ --output-csv report.csv
    python scripts/check_annotation_quality.py annotations/nsd/ --list-files-only
"""

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image_annotation.utils.validation import (
    detect_repetitive_pattern,
    validate_structured_inventory_schema,
)


def check_annotation_quality(
    annotation_dir: Path,
    max_response_length: int = 10000,
    max_token_ratio: float = 10.0,
    pattern: str = "shared*.json",
) -> dict:
    """Check annotation quality across all files.

    Args:
        annotation_dir: Directory containing annotation JSON files
        max_response_length: Maximum response length in characters
        max_token_ratio: Maximum ratio between max and median tokens for a prompt type
        pattern: Glob pattern for files

    Returns:
        Dict with quality check results
    """
    files = sorted(annotation_dir.glob(pattern))
    print(f"Checking {len(files)} files in {annotation_dir}...")

    issues = []
    stats = defaultdict(lambda: {"lengths": [], "tokens": []})
    files_with_issues = set()

    for file_path in files:
        try:
            with open(file_path) as f:
                data = json.load(f)

            image_id = data.get("image", {}).get("id", file_path.stem)

            for ann_idx, ann in enumerate(data.get("annotations", [])):
                if not ann or not isinstance(ann, dict):
                    continue

                model = ann.get("model", "unknown")

                for prompt_key, prompt_data in ann.get("prompts", {}).items():
                    if not prompt_data or not isinstance(prompt_data, dict):
                        continue
                    response = prompt_data.get("response", "")
                    error = prompt_data.get("error")
                    token_metrics = prompt_data.get("token_metrics") or {}
                    total_tokens = token_metrics.get("total_tokens", 0) if token_metrics else 0

                    # Collect stats
                    stats[prompt_key]["lengths"].append(len(response))
                    if total_tokens:
                        stats[prompt_key]["tokens"].append(total_tokens)

                    # Check for issues
                    issue_types = []

                    # 1. Response too long
                    if len(response) > max_response_length:
                        issue_types.append("too_long")

                    # 2. JSON parsing error
                    if error and "JSON parsing failed" in error:
                        issue_types.append("json_parse_error")

                    # 3. Repetitive pattern (only flag extreme cases)
                    pattern_info = detect_repetitive_pattern(response, min_repeats=50)
                    if pattern_info:
                        issue_types.append("repetitive_pattern")

                    # 4. Empty response
                    if not response or len(response.strip()) == 0:
                        issue_types.append("empty_response")

                    # 5. Schema validation for structured_inventory
                    schema_errors = []
                    if prompt_key == "structured_inventory" and prompt_data.get("response_data"):
                        schema_errors = validate_structured_inventory_schema(
                            prompt_data["response_data"]
                        )
                        if schema_errors:
                            issue_types.append("invalid_schema")

                    if issue_types:
                        files_with_issues.add(file_path.name)
                        issues.append(
                            {
                                "file": file_path.name,
                                "image_id": image_id,
                                "model": model,
                                "prompt": prompt_key,
                                "issue_types": ",".join(issue_types),
                                "response_length": len(response),
                                "total_tokens": total_tokens,
                                "error": error or "",
                                "pattern_info": (
                                    f"{pattern_info['pattern'][:30]}... x{pattern_info['count']}"
                                    if pattern_info
                                    else ""
                                ),
                                "schema_errors": "; ".join(schema_errors) if schema_errors else "",
                            }
                        )

        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            files_with_issues.add(file_path.name)
            issues.append(
                {
                    "file": file_path.name,
                    "image_id": file_path.stem,
                    "model": "unknown",
                    "prompt": "unknown",
                    "issue_types": "file_error",
                    "response_length": 0,
                    "total_tokens": 0,
                    "error": str(e),
                    "pattern_info": "",
                }
            )

    return {
        "issues": issues,
        "stats": stats,
        "files_with_issues": sorted(files_with_issues),
        "total_files": len(files),
    }


def print_summary(results: dict):
    """Print summary of quality check results."""
    issues = results["issues"]
    total_files = results["total_files"]
    files_with_issues = results["files_with_issues"]

    print(f"\n{'='*70}")
    print("ANNOTATION QUALITY REPORT")
    print(f"{'='*70}")
    print(f"Total files checked: {total_files}")
    print(f"Files with issues: {len(files_with_issues)} ({len(files_with_issues)/total_files*100:.1f}%)")
    print(f"Total issues found: {len(issues)}")

    if issues:
        print(f"\n{'Issue Type Distribution':}")
        print("-" * 70)
        issue_type_counts = Counter()
        for issue in issues:
            for issue_type in issue["issue_types"].split(","):
                issue_type_counts[issue_type] += 1

        for issue_type, count in issue_type_counts.most_common():
            print(f"  {issue_type:30s}: {count:4d}")

        print(f"\n{'Issues by Model':}")
        print("-" * 70)
        model_counts = Counter(issue["model"] for issue in issues)
        for model, count in model_counts.most_common():
            print(f"  {model:30s}: {count:4d}")

        print(f"\n{'Issues by Prompt Type':}")
        print("-" * 70)
        prompt_counts = Counter(issue["prompt"] for issue in issues)
        for prompt, count in prompt_counts.most_common():
            print(f"  {prompt:30s}: {count:4d}")

        # Response length statistics for problematic prompts
        print(f"\n{'Response Length Statistics (for issues)':}")
        print("-" * 70)
        lengths = [issue["response_length"] for issue in issues if issue["response_length"] > 0]
        if lengths:
            lengths_sorted = sorted(lengths)
            print(f"  Min: {min(lengths):,} chars")
            print(f"  Median: {lengths_sorted[len(lengths_sorted)//2]:,} chars")
            print(f"  Max: {max(lengths):,} chars")
            print(f"  Mean: {sum(lengths)//len(lengths):,} chars")

    # Statistics for all prompts
    print(f"\n{'Overall Response Statistics by Prompt Type':}")
    print("-" * 70)
    for prompt_key, data in sorted(results["stats"].items()):
        lengths = data["lengths"]
        if lengths:
            lengths_sorted = sorted(lengths)
            median_length = lengths_sorted[len(lengths_sorted) // 2]
            max_length = max(lengths)
            print(f"\n  {prompt_key}:")
            print(f"    Response length - Median: {median_length:,} | Max: {max_length:,} | Samples: {len(lengths)}")
            if max_length > median_length * 5:
                print(f"    ⚠️  Max is {max_length/median_length:.1f}x larger than median")


def export_to_csv(issues: list[dict], output_path: Path):
    """Export issues to CSV file."""
    if not issues:
        print("No issues to export")
        return

    fieldnames = [
        "file",
        "image_id",
        "model",
        "prompt",
        "issue_types",
        "response_length",
        "total_tokens",
        "error",
        "pattern_info",
        "schema_errors",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(issues)

    print(f"\n✓ Exported {len(issues)} issues to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Check annotation quality and identify problematic responses"
    )
    parser.add_argument("directory", type=Path, help="Directory containing annotation files")
    parser.add_argument(
        "--max-length",
        type=int,
        default=10000,
        help="Maximum response length in characters (default: 10000)",
    )
    parser.add_argument(
        "--pattern", default="shared*.json", help="Glob pattern for files (default: shared*.json)"
    )
    parser.add_argument("--output-csv", type=Path, help="Export issues to CSV file")
    parser.add_argument(
        "--list-files-only",
        action="store_true",
        help="Only list files with issues (one per line)",
    )

    args = parser.parse_args()

    if not args.directory.exists():
        print(f"Error: Directory not found: {args.directory}")
        return 1

    # Run quality check
    results = check_annotation_quality(
        args.directory, max_response_length=args.max_length, pattern=args.pattern
    )

    if args.list_files_only:
        # Just print files with issues
        for filename in results["files_with_issues"]:
            print(filename)
    else:
        # Print full report
        print_summary(results)

        if args.output_csv:
            export_to_csv(results["issues"], args.output_csv)

    return 0


if __name__ == "__main__":
    exit(main())
