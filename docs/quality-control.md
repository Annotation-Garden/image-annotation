# Annotation Quality Control

Tools for detecting and handling problematic annotations in the image annotation dataset.

## Problem

During annotation generation, some VLM responses can become corrupted:
- **Abnormally long responses** (>10KB vs typical 1-2KB)
- **Repetitive patterns** (e.g., `!#system\n` repeated thousands of times)
- **JSON parsing failures** for structured responses
- **Invalid schema** for `structured_inventory` responses

See [Issue #4](https://github.com/Annotation-Garden/image-annotation/issues/4) for details.

## Tools

### 1. Quality Check Script

**Location**: `scripts/check_annotation_quality.py`

Analyzes annotation files and generates a quality report.

**Features**:
- Detects abnormally long responses
- Identifies repetitive patterns
- Validates JSON schema for `structured_inventory`
- Tracks JSON parsing errors
- Generates statistics and exports to CSV

**Usage**:
```bash
# Basic quality check
python scripts/check_annotation_quality.py annotations/nsd/

# Custom length threshold
python scripts/check_annotation_quality.py annotations/nsd/ --max-length 5000

# Export to CSV for analysis
python scripts/check_annotation_quality.py annotations/nsd/ --output-csv issues.csv

# Just list problematic files
python scripts/check_annotation_quality.py annotations/nsd/ --list-files-only
```

**Validation Checks**:

1. **Response Length**: Flags responses >10KB (configurable)
2. **Repetitive Patterns**: Detects same sequence repeated 50+ times
3. **JSON Parse Errors**: Identifies failed JSON parsing
4. **Empty Responses**: Flags missing or empty responses
5. **Schema Validation** (for `structured_inventory`):
   - Level 1: Only `human`, `animal`, `man-made`, `natural` categories
   - Level 2: Item names (any string)
   - Level 3: Only `count`, `location`, `color`, `size`, `description` attributes

### 2. Annotation Tools with Flagging

**Location**: `src/image_annotation/utils/annotation_tools.py`

Extended annotation manipulation tools with quality flagging support.

**New Commands**:

```bash
# Flag problematic annotations (adds quality_flags field)
python src/image_annotation/utils/annotation_tools.py flag annotations/nsd/

# Flag with custom length threshold
python src/image_annotation/utils/annotation_tools.py flag annotations/nsd/ 5000

# List all flagged annotations
python src/image_annotation/utils/annotation_tools.py list-flagged annotations/nsd/

# Remove flagged annotations (prepares for re-annotation)
python src/image_annotation/utils/annotation_tools.py remove-flagged annotations/nsd/
```

**Quality Flags**:
- `too_long`: Response exceeds length threshold
- `repetitive_pattern`: Detected repetitive sequences
- `json_parse_error`: JSON parsing failed
- `empty_response`: Response is missing or empty

## Workflow

### 1. Detect Issues

Run quality check on annotation directory:

```bash
python scripts/check_annotation_quality.py annotations/nsd/ --output-csv quality_report.csv
```

Review the report to understand the scope and types of issues.

### 2. Flag Problematic Annotations

Add `quality_flags` to annotations needing review or re-annotation:

```bash
python src/image_annotation/utils/annotation_tools.py flag annotations/nsd/
```

This modifies the JSON files in-place, adding a `quality_flags` array to problematic prompt responses.

### 3. Review Flagged Annotations

List all flagged annotations for manual review:

```bash
python src/image_annotation/utils/annotation_tools.py list-flagged annotations/nsd/
```

### 4. Remove for Re-annotation

Remove flagged annotations from files so they can be re-processed:

```bash
python src/image_annotation/utils/annotation_tools.py remove-flagged annotations/nsd/
```

This removes the prompt data for flagged annotations, preparing the files for re-annotation with the VLM service.

### 5. Re-run Annotation

Use the standard processing scripts to re-generate the removed annotations:

```bash
python scripts/process_nsd_dataset.py --resume
```

The resume functionality will detect missing prompts and re-annotate only those.

## Example: Fixing Issue #4

Based on analysis, we found:
- **66 responses >10KB** (normal is 1-3KB)
- **1,570 invalid schema** in `structured_inventory`
- **141 JSON parse errors**
- Most issues in `qwen2.5vl:7b` model

**Steps to fix**:

1. **Run quality check**:
   ```bash
   python scripts/check_annotation_quality.py annotations/nsd/ --output-csv issue4_report.csv
   ```

2. **Flag problematic annotations**:
   ```bash
   python src/image_annotation/utils/annotation_tools.py flag annotations/nsd/
   ```

3. **Review specific cases**:
   ```bash
   # Look at the worst cases
   sort -t, -k6 -n issue4_report.csv | tail -20
   ```

4. **Decide on action**:
   - For `too_long` and `repetitive_pattern`: Remove and re-annotate
   - For `invalid_schema`: Review if fixable or needs re-annotation
   - For `json_parse_error`: Remove and re-annotate

5. **Remove flagged annotations**:
   ```bash
   python src/image_annotation/utils/annotation_tools.py remove-flagged annotations/nsd/
   ```

6. **Re-annotate**:
   ```bash
   python scripts/process_nsd_dataset.py --resume
   ```

## Data Structure

### Flagged Annotation Example

```json
{
  "structured_inventory": {
    "prompt_text": "...",
    "response": "corrupted response with repetition...",
    "response_format": "json",
    "response_data": null,
    "error": "JSON parsing failed: ...",
    "quality_flags": ["too_long", "repetitive_pattern", "json_parse_error"],
    "token_metrics": {...},
    "performance_metrics": {...}
  }
}
```

The `quality_flags` array is added only to prompts with detected issues.

## Future Improvements

- [ ] Add LLM-based content validation (semantic coherence)
- [ ] Implement automatic retry logic with different temperature
- [ ] Add response truncation/sanitization at generation time
- [ ] Track quality metrics over time per model
- [ ] Automated flagging during processing (not post-hoc)
