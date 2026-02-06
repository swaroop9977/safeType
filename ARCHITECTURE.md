# SafeType+ Architecture Documentation

## System Overview

SafeType+ is a multi-layered AI-powered privacy protection system designed with modularity, explainability, and extensibility in mind.

## Architecture Principles

1. **Modular Design**: Each component is self-contained and testable
2. **Explainable AI**: Every decision is traceable and interpretable
3. **Privacy-First**: No unnecessary data retention
4. **Extensible**: Easy to add new detection methods or models
5. **Performance-Conscious**: Optimized for real-time analysis

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                  (React + TypeScript)                        │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Text     │  │   Image    │  │   Risk     │            │
│  │  Scanner   │  │  Scanner   │  │   Meter    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│           │              │                │                 │
│           └──────────────┴────────────────┘                 │
│                          │                                  │
│                    API Service Layer                        │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTP/JSON
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                      Backend API                             │
│                      (Flask)                                 │
│                          │                                   │
│         ┌────────────────┴────────────────┐                 │
│         │                                 │                 │
│    ┌────▼──────┐                  ┌──────▼─────┐            │
│    │   Text    │                  │   Image    │            │
│    │   Route   │                  │   Route    │            │
│    └────┬──────┘                  └──────┬─────┘            │
│         │                                 │                 │
│         └─────────────┬───────────────────┘                 │
│                       │                                     │
│         ┌─────────────┴─────────────┐                       │
│         │                           │                       │
│    ┌────▼─────┐              ┌──────▼──────┐               │
│    │   PII    │              │     NLP     │               │
│    │ Detection│              │   Intent    │               │
│    │          │              │ Classifier  │               │
│    │ • Regex  │              │             │               │
│    │ • NER    │              │ • Transform.│               │
│    └────┬─────┘              │ • Keywords  │               │
│         │                    └──────┬──────┘               │
│         │                           │                       │
│         └─────────────┬─────────────┘                       │
│                       │                                     │
│                  ┌────▼─────┐                               │
│                  │   Risk   │                               │
│                  │  Engine  │                               │
│                  │          │                               │
│                  │ • Scoring│                               │
│                  │ • Explain│                               │
│                  └────┬─────┘                               │
│                       │                                     │
│                  ┌────▼─────┐                               │
│                  │Suggestion│                               │
│                  │  Engine  │                               │
│                  │          │                               │
│                  │ • Rewrite│                               │
│                  │ • Redact │                               │
│                  └──────────┘                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

#### 1. **API Service** (`src/services/api.ts`)
- **Purpose**: Centralized HTTP client for backend communication
- **Responsibilities**:
  - Request/response formatting
  - Error handling
  - Type safety with TypeScript interfaces
- **Key Features**:
  - Axios-based HTTP client
  - Timeout handling (30s)
  - Automatic error transformation

#### 2. **Scanner Components**
- **TextScanner**: 
  - Real-time text analysis with debouncing
  - Auto-scan after 1.5s of inactivity
  - Example text loading
- **ImageScanner**:
  - Drag-and-drop upload
  - Image preview
  - OCR result display

#### 3. **Visualization Components**
- **RiskMeter**: Color-coded risk visualization
- **HighlightedText**: Inline text highlighting
- **SuggestionsList**: Alternative suggestions display
- **DetectionsSummary**: Detailed breakdown

### Backend Layer

#### 1. **API Routes** (`routes/`)

**scan_text.py**:
```python
POST /api/scan/text
→ Validate input
→ PII detection (regex + NER)
→ NLP intent classification
→ Risk computation
→ Suggestion generation
→ Return comprehensive response
```

**scan_image.py**:
```python
POST /api/scan/image
→ Validate image
→ OCR extraction
→ Text analysis pipeline
→ Image-specific risk factors
→ Return results with OCR data
```

#### 2. **Detection Services** (`services/`)

**PII Detection** (`pii_regex.py` + `pii_ner.py`):
- **Regex Detector**:
  - Pattern-based detection
  - Luhn algorithm for credit cards
  - Phone number validation
  - Email extraction
- **NER Detector**:
  - spaCy-based entity recognition
  - PERSON, ORG, GPE detection
  - Confidence scoring
  - Deduplication with regex results

**NLP Intent** (`nlp_intent.py`):
- Transformer-based classification (DistilBERT)
- Keyword-based phishing detection
- Sentiment manipulation analysis
- Combined scoring (transformer 40% + keywords 60%)

**OCR Service** (`ocr_service.py`):
- Image preprocessing (grayscale, threshold, denoise)
- PyTesseract integration
- Confidence scoring
- Image type detection

#### 3. **Risk Engine** (`risk_engine.py`)

**Scoring Formula**:
```python
# Individual module scores
pii_score = compute_pii_score(detections, text_length)
nlp_score = compute_nlp_score(intent_probs)
ocr_score = compute_ocr_score(ocr_conf, pii_in_image)

# Weighted combination
if ocr_score > 0:
    combined_pii = (pii_score + ocr_score) / 2
else:
    combined_pii = pii_score

risk_score = (combined_pii * 0.6) + (nlp_score * 0.4)
```

**Risk Level Mapping**:
- `0.0 - 0.3`: Low
- `0.3 - 0.6`: Medium
- `0.6 - 1.0`: High

**Key Features**:
- Per-module breakdown
- Confidence intervals
- Human-readable reasons
- Detection summary

#### 4. **Suggestion Engine** (`suggestion_engine.py`)

**Suggestion Types**:

1. **Redacted Version**:
   ```python
   "My email is john@example.com"
   → "My email is [Email address removed]"
   ```

2. **Rewritten Version**:
   ```python
   "Call me at 555-1234"
   → "You can contact me privately for details."
   ```

3. **Guidance**:
   ```python
   "Consider sharing contact details through 
    direct messages or private channels."
   ```

4. **Templates**:
   ```python
   "For contact information, please visit my 
    profile or send me a direct message."
   ```

#### 5. **Utility Modules** (`utils/`)

**Highlighter** (`highlighter.py`):
- Text span highlighting
- Category mapping (PII/phishing/NER)
- Severity classification
- Explanation token extraction

**Scoring Utils** (`scoring_utils.py`):
- PII score computation with logarithmic scaling
- NLP score with intent risk weights
- Regression metrics (MAE, RMSE, R²)
- Confidence interval calculation

### Evaluation Layer

#### Metrics Calculator (`evaluation/metrics.py`)

**Binary Classification**:
- Accuracy: (TP + TN) / Total
- Precision: TP / (TP + FP)
- Recall: TP / (TP + FN)
- F1-Score: 2 × (Precision × Recall) / (Precision + Recall)

**Multiclass Classification**:
- Macro averaging (unweighted mean)
- Micro averaging (aggregate then compute)
- Per-class metrics

**Regression**:
- MAE (Mean Absolute Error)
- MSE (Mean Squared Error)
- RMSE (Root MSE)
- R² (Coefficient of determination)

#### Dataset Loader (`evaluation/dataset_loader.py`)

**Supported Formats**:
- CSV with configurable columns
- JSON with flexible schema

**Features**:
- Label parsing (text/numeric)
- Train/test splitting
- Dataset balancing (under/oversample)
- Sample dataset generation

## Data Flow

### Text Scanning Flow

```
1. User Input
   ↓
2. Frontend Debounce (1.5s)
   ↓
3. API Request (POST /api/scan/text)
   ↓
4. Backend Validation
   ↓
5. Parallel Detection
   ├── Regex PII Detection
   ├── NER Entity Detection
   └── NLP Intent Classification
   ↓
6. PII Deduplication
   ↓
7. Risk Score Computation
   ├── PII Score (weighted by severity)
   ├── NLP Score (weighted by intent)
   └── Combined Score (60% PII + 40% NLP)
   ↓
8. Suggestion Generation (if Medium/High)
   ├── Redacted version
   ├── Rewritten version
   ├── Guidance text
   └── Template suggestions
   ↓
9. Response Formation
   ↓
10. Frontend Visualization
    ├── Risk Meter
    ├── Highlighted Text
    ├── Suggestions List
    └── Detection Summary
```

### Image Scanning Flow

```
1. User Upload
   ↓
2. Frontend Preview
   ↓
3. API Request (multipart/form-data)
   ↓
4. Backend Image Validation
   ↓
5. Image Preprocessing
   ├── Grayscale conversion
   ├── Noise reduction
   └── Thresholding
   ↓
6. OCR Text Extraction
   ↓
7. Text Analysis Pipeline (same as above)
   ↓
8. OCR-Enhanced Risk Score
   ├── OCR confidence
   ├── PII in image
   └── Blended with text PII score
   ↓
9. Response with OCR Data
   ↓
10. Frontend Display
    ├── Extracted Text
    ├── Risk Analysis
    └── Suggestions
```

## Design Decisions

### 1. Why Flask over FastAPI?
- **Simplicity**: Easier for academic demonstration
- **Maturity**: Well-documented with extensive community
- **Synchronous**: Simpler error handling for educational purposes
- **Trade-off**: Performance vs. clarity (chose clarity)

### 2. Why Regex + NER Combination?
- **Complementary**: Regex for structured patterns, NER for context
- **Accuracy**: Reduces false positives through deduplication
- **Performance**: Regex is fast for known patterns
- **Flexibility**: Easy to add new patterns without retraining

### 3. Why DistilBERT over BERT?
- **Speed**: 60% faster, 40% smaller
- **Accuracy**: Retains 97% of BERT's performance
- **Resource**: Lower memory footprint
- **Academic**: Good balance for demonstrations

### 4. Why 60/40 PII/NLP Weight?
- **PII Priority**: Privacy violations are critical
- **Context Matters**: Intent classification adds nuance
- **Empirical**: Tested on sample datasets
- **Tunable**: Easily adjustable in config

### 5. Why Client-Side Debouncing?
- **Performance**: Reduces server load
- **UX**: Smoother typing experience
- **Cost**: Less API calls
- **Trade-off**: Slight delay vs. instant feedback

## Scalability Considerations

### Current Limitations
- Single-threaded Flask server
- In-memory model loading
- No caching layer
- No rate limiting by default

### Production Enhancements
1. **Server**: Use Gunicorn/uWSGI with workers
2. **Caching**: Redis for model results
3. **Queue**: Celery for async processing
4. **Database**: PostgreSQL for logging/analytics
5. **CDN**: CloudFront for frontend
6. **Load Balancer**: nginx for distribution

## Security Considerations

### Current Implementation
- Input validation (length, format)
- CORS configuration
- No data persistence by default
- Client-side sanitization

### Production Requirements
- Authentication (JWT/OAuth)
- Rate limiting (per-user/IP)
- Input sanitization (SQL injection, XSS)
- HTTPS enforcement
- API key management
- Audit logging

## Testing Strategy

### Unit Tests (To Be Implemented)
```python
# Example structure
tests/
├── test_pii_regex.py
├── test_pii_ner.py
├── test_nlp_intent.py
├── test_risk_engine.py
└── test_suggestion_engine.py
```

### Integration Tests
```python
# Example structure
tests/
├── test_api_text.py
├── test_api_image.py
└── test_end_to_end.py
```

### Performance Tests
- Response time benchmarks
- Memory profiling
- Concurrent request handling
- Model loading time

## Monitoring & Observability

### Recommended Metrics
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Model inference time
- Detection accuracy over time
- User engagement (scans per session)

### Logging Strategy
```python
# Current implementation
logger.info(f"Scanning text ({len(text)} characters)")
logger.debug(f"Detected {len(pii)} PII items")
logger.error(f"Error during OCR: {error}")
```

## Extension Points

### Adding New PII Type
1. Add pattern to `pii_regex.py`
2. Update severity in `scoring_utils.py`
3. Add icon/color in frontend
4. Update documentation

### Adding New NLP Model
1. Implement in `nlp_intent.py`
2. Update scoring in `risk_engine.py`
3. Add configuration option
4. Benchmark performance

### Adding New Suggestion Type
1. Implement in `suggestion_engine.py`
2. Update API response schema
3. Add frontend rendering
4. Test with examples

---

This architecture supports the academic goals of SafeType+ while maintaining production-quality code organization and extensibility.
