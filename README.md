# Image Annotation Tool - Annotation Garden Initiative

🌐 **Part of the [Annotation Garden Initiative](https://annotation.garden)**

A VLM-based image annotation system adapted for the Annotation Garden ecosystem. This tool provides collaborative annotation capabilities for static image datasets, starting with the Natural Scene Dataset (NSD).

## About Annotation Garden

The Annotation Garden Initiative (AGI) establishes an open infrastructure for collaborative, multi-layered annotation of stimuli used in neuroscience research. This tool serves as the primary interface for annotating static image datasets in the AGI ecosystem.

## Key Features

- **Multi-model support**: OLLAMA, OpenAI GPT-4V, Anthropic Claude
- **Batch processing**: Handle 25k+ annotations with real-time progress
- **Web dashboard**: Interactive visualization with AGI branding
- **HED integration**: Hierarchical Event Descriptors for semantic annotations
- **BIDS-compliant**: Output follows stimuli-BIDS specifications
- **Annotation tools**: Reorder, filter, export, and manipulate annotations
- **Research-ready**: Structured JSON output with comprehensive metrics

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OLLAMA (for local models)
- API keys for OpenAI/Anthropic (optional)

### Installation

```bash
# Clone from Annotation Garden
git clone https://github.com/Annotation-Garden/image-annotation.git
cd image-annotation

# Python environment
conda activate torch-312  # or create: conda create -n torch-312 python=3.12
pip install -e .

# Frontend
cd frontend && npm install
```

### Quick Usage

```bash
# Start OLLAMA (for local models)
ollama serve

# Test VLM service
python -m image_annotation.services.vlm_service

# Run frontend dashboard (with AGI branding)
cd frontend && npm run dev
# Visit http://localhost:3000

# Configuration
cp config/config.example.json config/config.json
# Edit config.json with API keys and image paths
```

## AGI Integration

### Design Elements
- AGI logo positioned top-left in all interfaces
- AGI color theme throughout dashboard
- Consistent with annotation.garden website design

### HED Integration
This tool includes enhanced support for Hierarchical Event Descriptors (HED):
- HED tag suggestions during annotation
- HED validation for annotations
- Export annotations with HED tags

### BIDS Compliance
Annotations follow stimuli-BIDS specifications:
- Standardized events.tsv format
- JSON sidecars with annotation schema
- Compatible with neuroimaging datasets

## Architecture

- **Backend**: FastAPI with OLLAMA/OpenAI/Anthropic integration
- **Frontend**: Next.js dashboard with AGI branding
- **Storage**: JSON files with database support for large datasets
- **Processing**: Stateless VLM calls with comprehensive metrics

### Inference Platform

All performance metrics in this repository were generated using an **NVIDIA GeForce RTX 4090 GPU** with OLLAMA for local model inference. See [Quality Control](docs/quality-control.md#inference-platform) for details.

## Annotation Tools

Powerful CLI tools for post-processing annotations:

```python
from image_annotation.utils import reorder_annotations, remove_model, export_to_csv

# Reorder model annotations
reorder_annotations("annotations/", ["best_model", "second_best"])

# Remove underperforming models
remove_model("annotations/", "poor_model")

# Export for analysis
export_to_csv("annotations/", "results.csv", include_metrics=True)
```

## Programmatic Usage

```python
from image_annotation.services.vlm_service import VLMService, VLMPrompt

# Initialize and process
service = VLMService(model="gemma3:4b")
results = service.process_batch(
    image_paths=["path/to/image.jpg"],
    prompts=[VLMPrompt(id="describe", text="Describe this image")],
    models=["gemma3:4b", "llava:latest"]
)

# Results include comprehensive metrics
for result in results:
    print(f"Tokens: {result.token_metrics.total_tokens}")
    print(f"Speed: {result.performance_metrics.tokens_per_second}/sec")
```

## Development

```bash
# Test with real data (no mocks)
pytest tests/ --cov

# Format code
ruff check --fix . && ruff format .
```

## NSD Research Usage

1. **Download NSD images** to `/path/to/NSD_stimuli/shared1000/`
2. **Configure models** in `config/config.json`
3. **Process in batches** using `VLMService.process_batch()`
4. **Post-process** with annotation tools
5. **Export results** to CSV for analysis

See [CONTRIBUTING.md](https://github.com/Annotation-Garden/management/blob/main/CONTRIBUTING.md) for detailed research workflows.

## Contributing

See [CONTRIBUTING.md](https://github.com/Annotation-Garden/management/blob/main/CONTRIBUTING.md) in the management repository for AGI contribution guidelines.

## Related Repositories

- [Management](https://github.com/Annotation-Garden/management): Organizational documentation
- [Assets](https://github.com/Annotation-Garden/assets): AGI branding and design guidelines
- [Website](https://github.com/Annotation-Garden/annotation-garden.github.io): Main AGI website

## License

This project is licensed under CC-BY-NC-SA 4.0 - see the [LICENSE](LICENSE.md) file for details.

## Acknowledgments

- Natural Scene Dataset (NSD) team
- Annotation Garden Initiative community
- LangChain and OLLAMA communities
- Original tool by neuromechanist
