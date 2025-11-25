# Annotation Quality Control

Standard tools and workflow for detecting and handling problematic VLM annotations.

## Problem

VLM responses can become corrupted during generation:
- Abnormally long responses (>10KB vs typical 1-2KB)
- Repetitive patterns (e.g., `!#system\n` loops)
- JSON parsing failures
- Empty responses

See [Issue #4](https://github.com/Annotation-Garden/image-annotation/issues/4).

## Available Tools

### Quality Check Script

`scripts/check_annotation_quality.py` - Analyzes annotations and generates quality reports.

```bash
# Run quality check with CSV export
python scripts/check_annotation_quality.py annotations/nsd/ --output-csv report.csv

# Custom threshold
python scripts/check_annotation_quality.py annotations/nsd/ --max-length 5000

# List files with issues only
python scripts/check_annotation_quality.py annotations/nsd/ --list-files-only
```

**Detects**:
- Response length >10KB (configurable)
- Repetitive patterns (50+ repetitions)
- JSON parse errors
- Empty responses
- Schema violations (optional with `--validate-schema`)

### Annotation Management Tools

`src/image_annotation/utils/annotation_tools.py` - Flag and remove problematic annotations.

```bash
# Flag problematic annotations
python src/image_annotation/utils/annotation_tools.py flag annotations/nsd/

# List flagged annotations
python src/image_annotation/utils/annotation_tools.py list-flagged annotations/nsd/

# Remove flagged annotations
python src/image_annotation/utils/annotation_tools.py remove-flagged annotations/nsd/
```

**Quality flags**: `too_long`, `repetitive_pattern`, `json_parse_error`, `empty_response`

### Re-annotation Script

`scripts/reannotate_missing_prompts.py` - Re-annotate only missing prompts.

```bash
# Dry run to see what would be re-annotated
python scripts/reannotate_missing_prompts.py --dry-run

# Run re-annotation
python scripts/reannotate_missing_prompts.py
```

## Standard Workflow

**Run quality checks after every annotation experiment.**

```bash
# 1. Detect issues
python scripts/check_annotation_quality.py annotations/nsd/ --output-csv quality_report.csv

# 2. Flag problematic annotations
python src/image_annotation/utils/annotation_tools.py flag annotations/nsd/

# 3. Review flagged annotations
python src/image_annotation/utils/annotation_tools.py list-flagged annotations/nsd/

# 4. Remove problematic data
python src/image_annotation/utils/annotation_tools.py remove-flagged annotations/nsd/

# 5. Verify cleanup
python scripts/check_annotation_quality.py annotations/nsd/
```

### Decision: Accept Missing vs Re-annotate

**Accept missing data (recommended)** when:
- Error rate <1% of total responses
- Failures concentrated in specific models/prompts
- Models consistently fail on same prompts

**Attempt re-annotation** when:
- Error rate >5%
- Failures appear transient (timeouts, network issues)
- First attempt at re-annotation

**Note**: After 1-2 retry attempts, accept missing data. Some models have inherent limitations on certain prompts. Missing data (<1%) is preferable to corrupted data and is handled gracefully by the system.

```bash
# Re-annotate missing prompts (optional)
python scripts/reannotate_missing_prompts.py

# Quality check again
python scripts/check_annotation_quality.py annotations/nsd/
```

## Case Study: Issue #4

**Analysis** of 30,000 responses (1,000 images × 6 models × 5 prompts):
- 143 problematic responses (0.5% of total)
- 139 files affected (13.9%)
- Concentrated in `structured_inventory` prompt (2.4% failure rate)

**Issue breakdown**:
- 66 responses >10KB (vs normal 1-3KB)
- 141 JSON parse errors
- 66 repetitive patterns
- 2 empty responses

**Resolution**:
1. Detected issues with quality check script
2. Flagged 143 problematic annotations
3. Removed corrupted data from annotation files
4. Attempted re-annotation - most models failed again
5. Accepted missing data as model limitations (<1% error rate)

**Result**: Clean dataset with 143 missing prompts (~0.5%). Frontend/backend handle missing data gracefully.

**Note**: Initial analysis showed 98.5% "invalid_schema" false positives - models returned valid JSON in alternative formats. Schema validation is now disabled by default (see [Issue #8](https://github.com/Annotation-Garden/image-annotation/issues/8)).

## Data Structure

Flagged annotations have `quality_flags` array:

```json
{
  "structured_inventory": {
    "prompt_text": "...",
    "response": "corrupted response...",
    "response_format": "json",
    "response_data": null,
    "error": "JSON parsing failed: ...",
    "quality_flags": ["too_long", "repetitive_pattern", "json_parse_error"],
    "token_metrics": {...},
    "performance_metrics": {...}
  }
}
```

Missing prompts are simply omitted from the `prompts` object - the frontend displays "No annotations available for this selection".

## Future Improvements

- LLM-based content validation (semantic coherence)
- Automatic retry logic with different temperature
- Response truncation/sanitization at generation time
- Track quality metrics over time per model
- Automated flagging during processing (not post-hoc)
