#!/usr/bin/env python
"""Re-annotate missing prompts in existing annotation files.

This script detects which prompts are missing from which models in each file
and re-runs ONLY those missing prompts, preserving the existing good annotations.
"""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from tqdm import tqdm

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from image_annotation.services.vlm_service import VLMPrompt, VLMService


def create_comprehensive_prompts() -> list[VLMPrompt]:
    """Create the comprehensive set of prompts for NSD annotation."""
    return [
        VLMPrompt(
            id="general_description",
            text=(
                "Provide a detailed description of this image in approximately 150 words. "
                "Focus on the main subjects or objects, the setting or background, prominent colors, "
                "the overall mood or atmosphere, and any notable actions or interactions. Describe what "
                "makes this image distinctive or interesting. Form the response as a continuous paragraph."
            ),
            expected_format="text",
        ),
        VLMPrompt(
            id="foreground_background",
            text=(
                "Analyze the spatial organization of this image. Identify and describe what is in "
                "the foreground (closest to the viewer), middle ground, and background. Explain how "
                "these layers relate to each other and contribute to the overall composition. "
                "Maximum 150 words, presented as a continuous paragraph."
            ),
            expected_format="text",
        ),
        VLMPrompt(
            id="entities_interactions",
            text=(
                "Identify all significant entities (people, animals, objects) in this image and "
                "describe their interactions or relationships. What are they doing? How do they "
                "relate to each other spatially or contextually? Include any notable actions, "
                "gestures, or connections between entities. Maximum 150 words, as a continuous paragraph."
            ),
            expected_format="text",
        ),
        VLMPrompt(
            id="mood_emotions",
            text=(
                "Describe the mood and emotions conveyed by this image. What feelings does it evoke? "
                "Consider whether the overall tone is positive, negative, or neutral. Explain what "
                "visual elements contribute to this emotional atmosphere. Form the response as a "
                "continuous paragraph. Maximum 200 words."
            ),
            expected_format="text",
        ),
        VLMPrompt(
            id="structured_inventory",
            text=(
                "Analyze this image and create a JSON object documenting all visible items. "
                "Structure the output with these exact three levels:\n"
                "Level 1 (Categories): Use only these four keys: 'human', 'animal', 'man-made', 'natural'\n"
                "Level 2 (Item names): Specific names of detected items (e.g., 'person', 'dog', 'car', 'tree')\n"
                "Level 3 (Attributes): Use ONLY these keys for each item:\n"
                "  • count: number of instances (integer)\n"
                "  • location: position in image (use terms like: left/center/right, top/middle/bottom, foreground/background)\n"
                "  • color: main color(s) if applicable (array of strings)\n"
                "  • size: relative size (small/medium/large)\n"
                "  • description: any other relevant details that don't fit above categories (string)\n"
                "Output valid JSON only. Include only categories that contain detected items. "
                "If an attribute doesn't apply to an item (e.g., color for sky), omit that key "
                "rather than using null. The 'description' field should capture important "
                "characteristics like actions, states, or specific features not covered by other keys."
            ),
            expected_format="json",
        ),
    ]


def find_missing_prompts(annotation_file: Path) -> dict:
    """Find which prompts are missing for which models in an annotation file.

    Returns:
        Dict mapping model names to lists of missing prompt IDs
    """
    with open(annotation_file) as f:
        data = json.load(f)

    expected_prompts = {
        'general_description',
        'foreground_background',
        'entities_interactions',
        'mood_emotions',
        'structured_inventory'
    }

    missing = {}
    for ann in data.get('annotations', []):
        model = ann.get('model')
        existing_prompts = set(ann.get('prompts', {}).keys())
        missing_prompts = expected_prompts - existing_prompts

        if missing_prompts:
            missing[model] = sorted(missing_prompts)

    return missing


def reannotate_missing(
    annotation_file: Path,
    image_dir: Path,
    service: VLMService,
    prompts_by_id: dict,
    dry_run: bool = False,
) -> dict:
    """Re-annotate missing prompts in a file.

    Returns:
        Dict with statistics about what was re-annotated
    """
    with open(annotation_file) as f:
        data = json.load(f)

    image_id = data['image']['id']
    image_name = data['image']['name']

    # Try to find the image file (may have different extension)
    image_path = image_dir / image_name
    if not image_path.exists():
        # Try changing extension to .jpg
        image_path_jpg = image_dir / image_name.replace('.png', '.jpg')
        if image_path_jpg.exists():
            image_path = image_path_jpg
        else:
            return {"error": f"Image not found: {image_path} or {image_path_jpg}", "reannotated": 0}

    missing_by_model = find_missing_prompts(annotation_file)

    if not missing_by_model:
        return {"reannotated": 0}

    reannotated_count = 0

    for ann in data['annotations']:
        model = ann.get('model')
        if model not in missing_by_model:
            continue

        missing_prompt_ids = missing_by_model[model]
        temperature = ann.get('temperature', 0.3)

        for prompt_id in missing_prompt_ids:
            if dry_run:
                print(f"  [DRY RUN] Would re-annotate: {image_id} | {model} | {prompt_id}")
                reannotated_count += 1
                continue

            prompt = prompts_by_id[prompt_id]
            print(f"  Re-annotating: {model} | {prompt_id}...", end=" ")

            try:
                result = service.annotate_image(image_path, prompt, model)

                # Add the result to the annotation
                ann['prompts'][prompt_id] = {
                    "prompt_text": result.prompt_text,
                    "response": result.response,
                    "response_format": result.response_format,
                    "response_data": result.response_data,
                    "error": result.error,
                    "token_metrics": (
                        result.token_metrics.model_dump() if result.token_metrics else None
                    ),
                    "performance_metrics": (
                        result.performance_metrics.model_dump() if result.performance_metrics else None
                    ),
                }

                if result.error:
                    print(f"❌ Error: {result.error}")
                else:
                    if result.token_metrics and result.performance_metrics:
                        print(
                            f"✅ {result.token_metrics.total_tokens} tokens, "
                            f"{result.performance_metrics.tokens_per_second:.1f} tok/s"
                        )
                    else:
                        print("✅")

                reannotated_count += 1

            except Exception as e:
                print(f"❌ Failed: {e}")
                # Add error result
                ann['prompts'][prompt_id] = {
                    "prompt_text": prompt.text,
                    "response": "",
                    "response_format": prompt.expected_format,
                    "response_data": None,
                    "error": str(e),
                    "token_metrics": None,
                    "performance_metrics": None,
                }
                reannotated_count += 1

    # Save the updated file
    if not dry_run and reannotated_count > 0:
        with open(annotation_file, 'w') as f:
            json.dump(data, f, indent=2)

    return {"reannotated": reannotated_count}


def main():
    parser = argparse.ArgumentParser(
        description="Re-annotate missing prompts in existing annotation files"
    )
    parser.add_argument(
        "--annotation-dir",
        type=Path,
        default=Path("annotations/nsd"),
        help="Directory containing annotation files",
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=Path("images/downsampled"),
        help="Directory containing images",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Generation temperature",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually re-annotating",
    )
    parser.add_argument(
        "--pattern",
        default="shared*.json",
        help="File pattern to match",
    )

    args = parser.parse_args()

    if not args.annotation_dir.exists():
        print(f"Error: Annotation directory not found: {args.annotation_dir}")
        return 1

    if not args.image_dir.exists():
        print(f"Error: Image directory not found: {args.image_dir}")
        return 1

    # Create prompts lookup
    prompts = create_comprehensive_prompts()
    prompts_by_id = {p.id: p for p in prompts}

    # Initialize VLM service
    service = None if args.dry_run else VLMService(temperature=args.temperature)

    # Find all annotation files
    files = sorted(args.annotation_dir.glob(args.pattern))

    # Find files with missing prompts
    files_with_missing = []
    for fpath in files:
        missing = find_missing_prompts(fpath)
        if missing:
            files_with_missing.append((fpath, missing))

    print(f"Found {len(files_with_missing)} files with missing prompts")

    if not files_with_missing:
        print("Nothing to do!")
        return 0

    if args.dry_run:
        print("\nDRY RUN MODE - No actual re-annotation will be performed\n")

    # Re-annotate
    total_reannotated = 0

    for fpath, missing in tqdm(files_with_missing, desc="Re-annotating"):
        print(f"\n{fpath.name}:")
        for model, prompt_ids in missing.items():
            print(f"  {model}: missing {prompt_ids}")

        result = reannotate_missing(
            fpath,
            args.image_dir,
            service,
            prompts_by_id,
            dry_run=args.dry_run
        )

        if "error" in result:
            print(f"  ❌ {result['error']}")
        else:
            total_reannotated += result['reannotated']

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Files processed: {len(files_with_missing)}")
    print(f"  Prompts re-annotated: {total_reannotated}")
    if args.dry_run:
        print(f"\n  (DRY RUN - no changes were made)")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    exit(main())
