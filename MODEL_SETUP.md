# SafeType+ AI Model Setup Guide

## Overview

SafeType+ uses **AI-powered** detection leveraging state-of-the-art transformer models and NER systems. This guide walks you through initializing these models.

## Quick Start

### Option 1: Automatic Setup (Recommended)

The models are automatically downloaded when you first start the Flask server:

```bash
cd backend
python app.py
```

The server will:
1. Display "Initializing AI models at startup..."
2. Download DistilBERT (English intent classifier)
3. Download spaCy NER model (entity extraction)
4. Optionally download multilingual models
5. Start serving once models are ready

### Option 2: Pre-Download Models (For CI/CD or Offline Setup)

Download models without starting the server:

```bash
cd backend
python setup_models.py
```

#### Variants:

```bash
# Full setup (English + Multilingual models)
python setup_models.py

# English-only (faster, smaller)
python setup_models.py --no-multilingual

# Verbose output
python setup_models.py --verbose
```

## Models Included

### Required Models
| Model | Size | Purpose | Load Time |
|-------|------|---------|-----------|
| `distilbert-base-uncased-finetuned-sst-2-english` | ~268 MB | Intent classification (phishing detection) | ~5-10s |
| `en_core_web_sm` | ~40 MB | Named Entity Recognition (person/org/location) | ~1-2s |

### Optional Multilingual Models
| Model | Size | Purpose |
|-------|------|---------|
| `cardiffnlp/twitter-xlm-roberta-base-sentiment` | ~713 MB | Multilingual intent classification |
| `xx_ent_wiki_sm` | ~94 MB | Multilingual NER |

**Total download**: ~1.1 GB (with multilingual) or ~300 MB (English-only)

## Configuration

Control model initialization via environment variables or `.env` file:

```bash
# Enable/disable multilingual models
ENABLE_MULTILINGUAL=True

# Specify model names (advanced)
NLP_MODEL=distilbert-base-uncased-finetuned-sst-2-english
SPACY_MODEL=en_core_web_sm

# Language detection
ENABLE_LANGUAGE_DETECTION=True
DEFAULT_LANGUAGE=en
```

## Verification

### Check Models After Startup

The `/api/status` endpoint returns model status:

```bash
curl http://localhost:5000/api/status
```

Response:
```json
{
  "status": "operational",
  "ai_models": "operational",
  "modules": {
    "nlp_intent": "ready",
    "ner": "ready",
    "pii_detection": "ready",
    "ocr": "ready"
  },
  "models_loaded": {
    "transformers_en": "loaded",
    "spacy_en": "loaded"
  }
}
```

### Test End-to-End

```bash
curl -X POST http://localhost:5000/api/scan/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "My credit card is 4532-1234-5678-9010. Please verify urgently!"
  }'
```

You should see:
- `"pii_detection": "ready"` → Regex detected credit card
- `"nlp_intent": "ready"` → Transformer detected phishing pattern ("urgently")
- Combined risk score reflecting both detections

## Fallback Behavior

If models fail to load:
- PII detection uses **regex patterns** (still functional)
- Intent classification uses **keyword patterns** (phishing keywords)
- NER skips (NER detection disabled)
- `/api/status` returns `"ai_models": "degraded (using fallback detection)"`

**Note**: Fallback is intentional and doesn't break the system. All core features remain functional.

## Troubleshooting

### Models Not Downloading

**Problem**: Stuck on "Downloading model..."

**Solution**:
```bash
# Check internet connection
ping huggingface.co

# Manually download with verbose output
python setup_models.py --verbose

# Try with smaller English-only setup
python setup_models.py --no-multilingual
```

### Out of Memory

**Problem**: "CUDA out of memory" or allocation error

**Solution**:
```bash
# Force CPU-only mode
export PYTORCH_ENABLE_MPS_FALLBACK=1
python app.py
```

### spaCy Download Errors

**Problem**: "Doesn't support spacy models > 3.0"

**Solution**:
```bash
# Ensure Python 3.10-3.12 (not 3.13+)
python --version

# Manually download spaCy model
python -m spacy download en_core_web_sm
```

## Advanced: Custom Models

To use custom fine-tuned models:

1. **Replace model names** in `.env`:
   ```bash
   NLP_MODEL=your-user/your-finetuned-distilbert
   SPACY_MODEL=./path/to/your_model
   ```

2. **Restart the server**:
   ```bash
   python app.py
   ```

## Production Deployment

### Docker

Include model download in your Dockerfile:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
RUN pip install -r requirements.txt
RUN python setup_models.py --no-multilingual
CMD ["python", "app.py"]
```

### Cloud (AWS/GCP/Azure)

Pre-cache models in your instance:

```bash
# During image build
python setup_models.py --no-multilingual

# Models cached in ~/.cache/huggingface/
# and ~/.cache/spacy/
```

### Offline Deployment

1. Download models on a machine with internet:
   ```bash
   python setup_models.py
   ```

2. Copy cache directories:
   ```bash
   ~/.cache/huggingface/
   ~/.cache/spacy/
   ```

3. Deploy with cached models (no internet required)

## Storage Locations

Models are cached in standard locations:

- **HuggingFace Transformers**: `~/.cache/huggingface/hub/`
- **spaCy**: `~/.cache/spacy/`
- **OCR Data**: `backend/tessdata/` (bundled)

**Total disk usage**: ~1.1 GB (with multilingual) or ~300 MB (production)

## Next Steps

1. ✅ Models Downloaded → Ready to scan
2. Run backend tests: `pytest backend/tests/`
3. Start frontend: `npm start` (from `frontend/`)
4. Try the web UI or Chrome extension

For more details, see [QUICKSTART.md](QUICKSTART.md) and [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
