"""Tools for manipulating annotation JSON files."""

import json
from pathlib import Path
from typing import Any

from tqdm import tqdm


def _normalize_paths(
    paths: str | Path | list[str | Path],
    pattern: str = "*.json",
    exclude_pattern: str | None = None,
) -> list[Path]:
    """Normalize input paths to a list of file paths."""
    if isinstance(paths, list):
        return [Path(p) for p in paths]

    path = Path(paths)
    if path.is_file():
        return [path]
    elif path.is_dir():
        files = list(path.glob(pattern))
        if exclude_pattern:
            files = [f for f in files if not f.name.startswith(exclude_pattern)]
        return files
    else:
        raise ValueError(f"Path does not exist: {path}")


def reorder_annotations(  # noqa: C901
    paths: str | Path | list[str | Path],
    model_order: list[str],
    pattern: str = "*.json",
    exclude_pattern: str | None = None,
    in_place: bool = True,
    output_dir: str | Path | None = None,
) -> dict[str, Any] | int:
    """
    Reorder annotations in JSON file(s) according to specified model order.

    Args:
        paths: Path to file, directory, or list of paths
        model_order: List of model names in desired order
        pattern: Glob pattern for directory search (default: "*.json")
        exclude_pattern: Optional pattern to exclude files
        in_place: If True, modify files in place
        output_dir: Optional directory to save reordered files

    Returns:
        For single file: The reordered annotation data dict
        For multiple files: Number of files processed
    """
    # Normalize input to list of files
    files = _normalize_paths(paths, pattern, exclude_pattern)

    # Process files
    single_file = len(files) == 1
    processed = 0
    last_data = None

    for file_path in tqdm(files, desc="Reordering annotations", disable=single_file):
        try:
            with open(file_path) as f:
                data = json.load(f)

            if "annotations" not in data:
                if single_file:
                    raise ValueError(f"No 'annotations' field found in {file_path}")
                print(f"Warning: No 'annotations' field in {file_path}")
                continue

            # Create a mapping of model names to annotations
            model_map = {ann["model"]: ann for ann in data["annotations"]}

            # Build reordered list
            reordered = []
            for model in model_order:
                if model in model_map:
                    reordered.append(model_map[model])

            # Add any remaining models not in the specified order
            for ann in data["annotations"]:
                if ann["model"] not in model_order:
                    reordered.append(ann)

            data["annotations"] = reordered
            last_data = data

            # Save the file
            if in_place:
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
            elif output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / file_path.name
                with open(output_file, "w") as f:
                    json.dump(data, f, indent=2)

            processed += 1

        except Exception as e:
            if single_file:
                raise
            print(f"Error processing {file_path}: {e}")

    return last_data if single_file else processed


def remove_model(  # noqa: C901
    paths: str | Path | list[str | Path],
    model_name: str,
    pattern: str = "*.json",
    exclude_pattern: str | None = None,
    in_place: bool = True,
    output_dir: str | Path | None = None,
) -> dict[str, Any] | int:
    """
    Remove a specific model's annotations from JSON file(s).

    Args:
        paths: Path to file, directory, or list of paths
        model_name: Name of the model to remove
        pattern: Glob pattern for directory search (default: "*.json")
        exclude_pattern: Optional pattern to exclude files
        in_place: If True, modify files in place
        output_dir: Optional directory to save modified files

    Returns:
        For single file: The modified annotation data dict
        For multiple files: Number of files where model was removed
    """
    # Normalize input to list of files
    files = _normalize_paths(paths, pattern, exclude_pattern)

    # Process files
    single_file = len(files) == 1
    files_with_removals = 0
    total_removed = 0
    last_data = None

    for file_path in tqdm(files, desc=f"Removing {model_name}", disable=single_file):
        try:
            with open(file_path) as f:
                data = json.load(f)

            if "annotations" not in data:
                if single_file:
                    raise ValueError(f"No 'annotations' field found in {file_path}")
                continue

            # Filter out the specified model
            original_count = len(data["annotations"])
            data["annotations"] = [ann for ann in data["annotations"] if ann["model"] != model_name]
            removed_count = original_count - len(data["annotations"])

            if removed_count == 0 and single_file:
                print(f"Model '{model_name}' not found in {file_path}")
            elif removed_count == 0 and not single_file:
                # Silent for batch operations
                continue

            if removed_count > 0:
                files_with_removals += 1
                total_removed += removed_count

            last_data = data

            # Save the file
            if in_place:
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
            elif output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / file_path.name
                with open(output_file, "w") as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            if single_file:
                raise
            print(f"Error processing {file_path}: {e}")

    if not single_file:
        print(
            f"Removed {model_name} from {files_with_removals} files "
            f"(total {total_removed} annotations)"
        )

    return last_data if single_file else files_with_removals


def get_annotation_stats(directory: str | Path, pattern: str = "shared*.json") -> dict[str, Any]:
    """
    Get statistics about annotations in a directory.

    Args:
        directory: Directory containing annotation files
        pattern: Glob pattern to match files

    Returns:
        Dictionary with statistics
    """
    directory = Path(directory)
    files = list(directory.glob(pattern))

    model_counts = {}
    total_annotations = 0
    files_processed = 0

    for file_path in files:
        try:
            with open(file_path) as f:
                data = json.load(f)

            if "annotations" in data:
                files_processed += 1
                for ann in data["annotations"]:
                    model = ann.get("model", "unknown")
                    model_counts[model] = model_counts.get(model, 0) + 1
                    total_annotations += 1
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return {
        "files_processed": files_processed,
        "total_annotations": total_annotations,
        "model_counts": model_counts,
        "models": list(model_counts.keys()),
    }


def filter_annotations_by_tokens(  # noqa: C901
    paths: str | Path | list[str | Path],
    max_tokens: int | None = None,
    min_tokens: int | None = None,
    pattern: str = "*.json",
    exclude_pattern: str | None = None,
    in_place: bool = False,
    output_dir: str | Path | None = None,
) -> dict[str, Any] | int:
    """
    Filter annotations based on token count criteria in JSON file(s).

    Args:
        paths: Path to file, directory, or list of paths
        max_tokens: Maximum total tokens allowed
        min_tokens: Minimum total tokens required
        pattern: Glob pattern for directory search (default: "*.json")
        exclude_pattern: Optional pattern to exclude files
        in_place: If True, modify files in place
        output_dir: Optional directory to save filtered files

    Returns:
        For single file: The filtered annotation data dict
        For multiple files: Number of files processed
    """
    # Normalize input to list of files
    files = _normalize_paths(paths, pattern, exclude_pattern)

    # Process files
    single_file = len(files) == 1
    processed = 0
    last_data = None

    for file_path in tqdm(files, desc="Filtering annotations", disable=single_file):
        try:
            with open(file_path) as f:
                data = json.load(f)

            if "annotations" not in data:
                if single_file:
                    raise ValueError(f"No 'annotations' field found in {file_path}")
                continue

            filtered_annotations = []
            for ann in data["annotations"]:
                # Calculate total tokens across all prompts
                total_tokens = 0
                for _prompt_key, prompt_data in ann.get("prompts", {}).items():
                    if "token_metrics" in prompt_data:
                        total_tokens += prompt_data["token_metrics"].get("total_tokens", 0)

                # Apply filters
                if max_tokens and total_tokens > max_tokens:
                    continue
                if min_tokens and total_tokens < min_tokens:
                    continue

                filtered_annotations.append(ann)

            data["annotations"] = filtered_annotations
            last_data = data

            # Save the file
            if in_place:
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)
            elif output_dir:
                output_dir = Path(output_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / file_path.name
                with open(output_file, "w") as f:
                    json.dump(data, f, indent=2)

            processed += 1

        except Exception as e:
            if single_file:
                raise
            print(f"Error processing {file_path}: {e}")

    return last_data if single_file else processed


def export_to_csv(
    directory: str | Path,
    output_file: str | Path,
    pattern: str = "shared*.json",
    include_metrics: bool = False,
) -> None:
    """
    Export annotations to CSV format.

    Args:
        directory: Directory containing annotation files
        output_file: Path to output CSV file
        pattern: Glob pattern to match files
        include_metrics: Whether to include token and performance metrics
    """
    import csv

    directory = Path(directory)
    output_file = Path(output_file)
    files = sorted(directory.glob(pattern))

    # Prepare CSV headers
    headers = ["image_id", "image_path", "model", "prompt_type", "response"]
    if include_metrics:
        headers.extend(["input_tokens", "output_tokens", "total_tokens", "generation_duration_ms"])

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        for file_path in tqdm(files, desc="Exporting to CSV"):
            try:
                with open(file_path) as f:
                    data = json.load(f)

                image_id = data["image"]["id"]
                image_path = data["image"]["path"]

                for ann in data.get("annotations", []):
                    model = ann["model"]

                    for prompt_key, prompt_data in ann.get("prompts", {}).items():
                        row = {
                            "image_id": image_id,
                            "image_path": image_path,
                            "model": model,
                            "prompt_type": prompt_key,
                            "response": prompt_data.get("response", ""),
                        }

                        if include_metrics:
                            token_metrics = prompt_data.get("token_metrics", {})
                            perf_metrics = prompt_data.get("performance_metrics", {})
                            row.update(
                                {
                                    "input_tokens": token_metrics.get("input_tokens", ""),
                                    "output_tokens": token_metrics.get("output_tokens", ""),
                                    "total_tokens": token_metrics.get("total_tokens", ""),
                                    "generation_duration_ms": perf_metrics.get(
                                        "generation_duration_ms", ""
                                    ),
                                }
                            )

                        writer.writerow(row)

            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    print(f"Exported annotations to {output_file}")


def flag_problematic_annotations(  # noqa: C901
    paths: str | Path | list[str | Path],
    max_response_length: int = 10000,
    pattern: str = "*.json",
    exclude_pattern: str | None = None,
    in_place: bool = True,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Flag problematic annotations by adding quality_flags field to prompts.

    Checks for:
    - Abnormally long responses
    - Repetitive patterns
    - JSON parsing errors
    - Empty responses

    Args:
        paths: Path to file, directory, or list of paths
        max_response_length: Maximum response length before flagging
        pattern: Glob pattern for directory search (default: "*.json")
        exclude_pattern: Optional pattern to exclude files
        in_place: If True, modify files in place
        output_dir: Optional directory to save flagged files

    Returns:
        Dict with statistics about flagged annotations
    """
    # Normalize input to list of files
    files = _normalize_paths(paths, pattern, exclude_pattern)

    # Process files
    single_file = len(files) == 1
    flagged_files = 0
    total_flagged = 0
    flagged_by_type = {}

    for file_path in tqdm(files, desc="Flagging problematic annotations", disable=single_file):
        try:
            with open(file_path) as f:
                data = json.load(f)

            if "annotations" not in data:
                if single_file:
                    raise ValueError(f"No 'annotations' field found in {file_path}")
                continue

            file_had_flags = False

            for ann in data["annotations"]:
                for prompt_key, prompt_data in ann.get("prompts", {}).items():
                    response = prompt_data.get("response", "")
                    error = prompt_data.get("error")
                    flags = []

                    # Check 1: Response too long
                    if len(response) > max_response_length:
                        flags.append("too_long")

                    # Check 2: Repetitive pattern (check for extreme cases only)
                    if len(response) > 1000:
                        # Check for known corruption patterns
                        sample = response[-500:]  # Check last 500 chars
                        if "!#system" in sample:
                            flags.append("repetitive_pattern")
                        # Check for same short sequence (2-10 chars) repeated 50+ times
                        # This catches real corruption without flagging normal JSON structure
                        for pattern_len in range(2, 11):
                            if len(response) < pattern_len:
                                continue
                            pattern_check = response[:pattern_len]
                            count = response.count(pattern_check)
                            if count >= 50:
                                flags.append("repetitive_pattern")
                                break

                    # Check 3: JSON parsing error
                    if error and "JSON parsing failed" in error:
                        flags.append("json_parse_error")

                    # Check 4: Empty response
                    if not response or len(response.strip()) == 0:
                        flags.append("empty_response")

                    # Add flags if any issues found
                    if flags:
                        prompt_data["quality_flags"] = flags
                        file_had_flags = True
                        total_flagged += 1

                        for flag in flags:
                            flagged_by_type[flag] = flagged_by_type.get(flag, 0) + 1
                    else:
                        # Remove quality_flags if present but no issues
                        prompt_data.pop("quality_flags", None)

            if file_had_flags:
                flagged_files += 1

                # Save the file
                if in_place:
                    with open(file_path, "w") as f:
                        json.dump(data, f, indent=2)
                elif output_dir:
                    output_dir = Path(output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_file = output_dir / file_path.name
                    with open(output_file, "w") as f:
                        json.dump(data, f, indent=2)

        except Exception as e:
            if single_file:
                raise
            print(f"Error processing {file_path}: {e}")

    return {
        "flagged_files": flagged_files,
        "total_flagged": total_flagged,
        "flagged_by_type": flagged_by_type,
        "total_files": len(files),
    }


def remove_flagged_annotations(  # noqa: C901
    paths: str | Path | list[str | Path],
    flag_types: list[str] | None = None,
    pattern: str = "*.json",
    exclude_pattern: str | None = None,
    in_place: bool = True,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Remove annotations that have quality_flags set.

    This prepares files for re-annotation by removing problematic prompts.

    Args:
        paths: Path to file, directory, or list of paths
        flag_types: Optional list of flag types to remove (if None, removes all flagged)
        pattern: Glob pattern for directory search (default: "*.json")
        exclude_pattern: Optional pattern to exclude files
        in_place: If True, modify files in place
        output_dir: Optional directory to save modified files

    Returns:
        Dict with statistics about removed annotations
    """
    # Normalize input to list of files
    files = _normalize_paths(paths, pattern, exclude_pattern)

    # Process files
    single_file = len(files) == 1
    files_modified = 0
    total_removed = 0

    for file_path in tqdm(files, desc="Removing flagged annotations", disable=single_file):
        try:
            with open(file_path) as f:
                data = json.load(f)

            if "annotations" not in data:
                if single_file:
                    raise ValueError(f"No 'annotations' field found in {file_path}")
                continue

            file_was_modified = False

            for ann in data["annotations"]:
                prompts_to_remove = []

                for prompt_key, prompt_data in ann.get("prompts", {}).items():
                    flags = prompt_data.get("quality_flags", [])

                    if flags:
                        # Check if we should remove this prompt
                        should_remove = False
                        if flag_types is None:
                            # Remove all flagged
                            should_remove = True
                        else:
                            # Remove only if has one of the specified flag types
                            for flag in flags:
                                if flag in flag_types:
                                    should_remove = True
                                    break

                        if should_remove:
                            prompts_to_remove.append(prompt_key)
                            total_removed += 1
                            file_was_modified = True

                # Remove the prompts
                for prompt_key in prompts_to_remove:
                    del ann["prompts"][prompt_key]

            if file_was_modified:
                files_modified += 1

                # Save the file
                if in_place:
                    with open(file_path, "w") as f:
                        json.dump(data, f, indent=2)
                elif output_dir:
                    output_dir = Path(output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_file = output_dir / file_path.name
                    with open(output_file, "w") as f:
                        json.dump(data, f, indent=2)

        except Exception as e:
            if single_file:
                raise
            print(f"Error processing {file_path}: {e}")

    return {
        "files_modified": files_modified,
        "total_removed": total_removed,
        "total_files": len(files),
    }


def list_flagged_annotations(
    directory: str | Path, pattern: str = "shared*.json"
) -> list[dict[str, Any]]:
    """List all flagged annotations in a directory.

    Args:
        directory: Directory containing annotation files
        pattern: Glob pattern to match files

    Returns:
        List of dicts with flagged annotation info
    """
    directory = Path(directory)
    files = list(directory.glob(pattern))

    flagged = []

    for file_path in files:
        try:
            with open(file_path) as f:
                data = json.load(f)

            image_id = data.get("image", {}).get("id", file_path.stem)

            for ann in data.get("annotations", []):
                model = ann.get("model", "unknown")

                for prompt_key, prompt_data in ann.get("prompts", {}).items():
                    flags = prompt_data.get("quality_flags", [])

                    if flags:
                        flagged.append(
                            {
                                "file": file_path.name,
                                "image_id": image_id,
                                "model": model,
                                "prompt": prompt_key,
                                "flags": flags,
                                "response_length": len(prompt_data.get("response", "")),
                                "error": prompt_data.get("error"),
                            }
                        )

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return flagged


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python annotation_tools.py <command> [args]")
        print("Commands:")
        print("  stats <path> - Get annotation statistics")
        print("  reorder <path> - Reorder annotations to standard order")
        print("  remove <path> <model> - Remove a model from file(s)")
        print("  export <directory> <output.csv> - Export to CSV")
        print("  flag <path> [max_length] - Flag problematic annotations")
        print("  list-flagged <directory> - List all flagged annotations")
        print("  remove-flagged <path> - Remove flagged annotations for re-processing")
        print("\nPath can be a file, directory, or multiple files")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stats":
        if len(sys.argv) < 3:
            print("Usage: python annotation_tools.py stats <path>")
            sys.exit(1)
        stats = get_annotation_stats(sys.argv[2])
        print(f"Files processed: {stats['files_processed']}")
        print(f"Total annotations: {stats['total_annotations']}")
        print("Model counts:")
        for model, count in sorted(stats["model_counts"].items()):
            print(f"  {model}: {count}")

    elif command == "reorder":
        if len(sys.argv) < 3:
            print("Usage: python annotation_tools.py reorder <path>")
            sys.exit(1)
        model_order = [
            "qwen2.5vl:7b",
            "qwen2.5vl:32b",
            "gemma3:4b",
            "gemma3:12b",
            "gemma3:27b",
            "mistral-small3.2:24b",
        ]
        result = reorder_annotations(sys.argv[2], model_order, pattern="shared*.json")
        if isinstance(result, int):
            print(f"Reordered {result} files")
        else:
            print("File reordered successfully")

    elif command == "remove":
        if len(sys.argv) < 4:
            print("Usage: python annotation_tools.py remove <path> <model>")
            sys.exit(1)
        result = remove_model(sys.argv[2], sys.argv[3], pattern="shared*.json")
        if isinstance(result, int):
            print(f"Processed {result} files")
        else:
            print("Model removed from file")

    elif command == "export":
        if len(sys.argv) < 4:
            print("Usage: python annotation_tools.py export <directory> <output.csv>")
            sys.exit(1)
        export_to_csv(sys.argv[2], sys.argv[3], pattern="shared*.json")
        print(f"Exported to {sys.argv[3]}")

    elif command == "flag":
        if len(sys.argv) < 3:
            print("Usage: python annotation_tools.py flag <path> [max_length]")
            sys.exit(1)
        max_length = int(sys.argv[3]) if len(sys.argv) > 3 else 10000
        result = flag_problematic_annotations(
            sys.argv[2], max_response_length=max_length, pattern="shared*.json"
        )
        print(f"Flagged {result['total_flagged']} annotations in {result['flagged_files']} files")
        print("By flag type:")
        for flag_type, count in result["flagged_by_type"].items():
            print(f"  {flag_type}: {count}")

    elif command == "list-flagged":
        if len(sys.argv) < 3:
            print("Usage: python annotation_tools.py list-flagged <directory>")
            sys.exit(1)
        flagged = list_flagged_annotations(sys.argv[2])
        print(f"Found {len(flagged)} flagged annotations:")
        for item in flagged:
            print(
                f"  {item['file']:50s} | {item['model']:25s} | "
                f"{item['prompt']:25s} | {item['flags']}"
            )

    elif command == "remove-flagged":
        if len(sys.argv) < 3:
            print("Usage: python annotation_tools.py remove-flagged <path>")
            sys.exit(1)
        result = remove_flagged_annotations(sys.argv[2], pattern="shared*.json")
        print(
            f"Removed {result['total_removed']} flagged annotations from "
            f"{result['files_modified']} files"
        )
