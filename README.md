# SafeType+

**AI-powered pre-submission privacy and phishing assistant**

SafeType+ is an industry-grade academic project that analyzes user text and images BEFORE submission, explains risks, and suggests safer alternatives instead of only warning.

## 🎯 Project Overview

SafeType+ is a proactive security system that combines multiple AI/ML techniques to:
- Detect personally identifiable information (PII)
- Identify phishing and social engineering patterns
- Extract and analyze text from images (OCR)
- Provide explainable risk scores
- **Suggest safer alternatives** (key differentiator)

## 🏗️ Architecture

### Tech Stack

**Backend (Python 3.10-3.12)**
- **Framework**: Flask
- **NLP**: HuggingFace Transformers (DistilBERT), spaCy NER
- **OCR/CV**: PyTesseract, OpenCV
- **Data Processing**: NumPy, Pandas

**Frontend (React + TypeScript)**
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios

### Project Structure

```
safeType+/
├── backend/
│   ├── app.py                 # Flask application entry point
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   │
│   ├── routes/                # API endpoints
│   │   ├── scan_text.py      # Text scanning endpoint
│   │   └── scan_image.py     # Image scanning endpoint
│   │
│   ├── services/              # Core detection services
│   │   ├── pii_regex.py      # Regex-based PII detection
│   │   ├── pii_ner.py        # NER-based PII detection
│   │   ├── nlp_intent.py     # Intent classification
│   │   ├── ocr_service.py    # OCR processing
│   │   ├── risk_engine.py    # Risk scoring engine
│   │   └── suggestion_engine.py  # Safer alternatives generator
│   │
│   ├── utils/                 # Utility modules
│   │   ├── highlighter.py    # Text highlighting
│   │   └── scoring_utils.py  # Scoring functions
│   │
│   └── evaluation/            # Evaluation tools
│       ├── metrics.py        # Metrics computation
│       ├── dataset_loader.py # Dataset management
│       └── run_evaluation.py # Evaluation script
│
└── frontend/
    ├── package.json          # Node dependencies
    ├── tailwind.config.js    # Tailwind configuration
    ├── tsconfig.json         # TypeScript configuration
    │
    ├── public/
    │   └── index.html       # HTML template
    │
    └── src/
        ├── App.tsx          # Main application component
        ├── index.tsx        # Entry point
        ├── index.css        # Global styles
        │
        ├── services/
        │   └── api.ts       # API service layer
        │
        └── components/      # React components
            ├── Header.tsx
            ├── Footer.tsx
            ├── TextScanner.tsx
            ├── ImageScanner.tsx
            ├── RiskMeter.tsx
            ├── HighlightedText.tsx
            ├── SuggestionsList.tsx
            └── DetectionsSummary.tsx
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.10, 3.11, or 3.12** (⚠️ NOT 3.13+ due to spaCy compatibility)
- Node.js 16+ and npm
- Tesseract OCR (for image analysis)

### Backend Setup

1. **Navigate to backend directory**
```powershell
cd backend
```

2. **Create virtual environment**

**Windows (if you have multiple Python versions):**
```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (single Python 3.10-3.12):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

4. **Download spaCy models**
```powershell
python -m spacy download en_core_web_sm
python -m spacy download xx_ent_wiki_sm
```

5. **Install Tesseract OCR** (Windows)
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and note the path (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`)

6. **Configure environment**
```powershell
Copy-Item .env.example .env
# Edit .env and set TESSERACT_PATH if needed
```

7. **Run the backend**
```powershell
python app.py
```

Backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
```powershell
cd frontend
```

2. **Install dependencies**
```powershell
npm install
```

3. **Configure API URL** (optional)
Create `.env` file:
```
REACT_APP_API_URL=http://localhost:5000/api
```

4. **Start development server**
```powershell
npm start
```

Frontend will be available at `http://localhost:3000`

On first load, click a `Get started` / launch button on the landing page to open the scanner UI.

## 🔬 Core Functionality

### 1. Text Analysis Pipeline

**Input**: Raw user text

**Processing**:
1. Regex-based PII detection (email, phone, SSN, Aadhaar, credit cards)
2. spaCy NER for entities (PERSON, ORG, GPE, etc.)
3. Transformer intent classification (benign/suspicious/phishing)
4. Phishing keyword detection

**Output**:
- Detected PII with positions
- Intent probabilities
- Highlighted risky spans
- Explanation tokens
- Risk score and level

### 2. Image Analysis Pipeline

**Input**: Image file (PNG/JPG/JPEG/GIF/BMP)

**Processing**:
1. Image preprocessing (grayscale, threshold, noise reduction)
2. OCR text extraction via PyTesseract
3. Same text analysis pipeline as above
4. Confidence scoring

**Output**:
- Extracted text with confidence
- All text analysis results
- Image-specific risk factors

### 3. Explainable Risk Engine

**Scoring Formula**:
```
risk_score = (pii_score × 0.6) + (nlp_score × 0.4)
```

**Risk Levels**:
- **Low**: 0.0 - 0.3
- **Medium**: 0.3 - 0.6
- **High**: 0.6 - 1.0

**Output**:
- Final risk score
- Per-module breakdown (PII, NLP, OCR)
- Human-readable reasons
- Confidence intervals

### 4. Safer-Text Suggestion Engine

**Key Differentiator**: Provides actionable alternatives, not just warnings.

**Suggestion Types**:
1. **Redacted**: PII removed/masked
2. **Rewritten**: Context-aware rephrasing
3. **Guidance**: Alternative approaches
4. **Template**: Common safe patterns

**Example**:
```
Original: "My phone is 555-123-4567"
Suggestion: "You can contact me privately for details."
```

## 📡 API Endpoints

### POST `/api/scan/text`

Scan text for privacy and phishing risks.

**Request**:
```json
{
  "text": "Your text here",
  "include_suggestions": true,
  "include_highlights": true
}
```

**Response**:
```json
{
  "risk_score": 0.72,
  "risk_level": "High",
  "module_breakdown": {
    "pii": 0.8,
    "nlp": 0.6,
    "ocr": 0.0
  },
  "reasons": [
    "Phone number detected",
    "Phishing-like urgency detected"
  ],
  "detected_pii": [...],
  "highlights": [...],
  "safer_suggestions": [...]
}
```

### POST `/api/scan/image`

Extract and analyze text from images.

**Request**: multipart/form-data
- `image`: Image file
- `preprocess`: true/false

**Response**: Same structure as text scan + OCR data

## 📊 Evaluation

### Running Evaluation

```powershell
cd backend
python evaluation/run_evaluation.py [dataset_path] [output_report]
```

**Metrics Computed**:
- Accuracy
- Precision
- Recall
- F1-Score
- MAE, RMSE, R² (for risk scores)

### Creating Custom Dataset

Dataset format (JSON):
```json
[
  {
    "text": "Sample text",
    "label": 0
  }
]
```

Labels: `0` = benign, `1` = phishing/malicious

## 🎨 Frontend Features

### Text Scanner
- Real-time analysis with debounce
- Auto-scan after 1.5s of inactivity
- Visual risk meter with color coding
- Highlighted risky text spans
- Safer alternative suggestions
- Detailed detection breakdown

### Image Scanner
- Drag-and-drop upload
- Image preview
- OCR text extraction display
- All text analysis features
- Image-specific risk factors

### User Experience
- Clean, modern interface
- Color-coded risk levels
- Explainable results
- Copy-to-clipboard for suggestions
- Responsive design

## 🔒 Privacy & Security

SafeType+ is built with privacy-first principles:

✅ **No persistent storage by default** (configurable via environment settings)  
✅ **Client-side processing** where possible  
✅ **Local model execution**  
✅ **No external inference API calls** for core functionality  
✅ **Transparent processing** with explainable results  

## 🧪 Testing Examples

### Safe Text
```
Hi team, let's schedule a meeting for next week.
```

### Risky Text
```
URGENT! Your account has been suspended. 
Click here to verify your credit card 4111-1111-1111-1111 
or call 555-123-4567 immediately!
```

## 📈 Performance Considerations

- **Text Analysis**: ~100-500ms for typical messages
- **Image OCR**: ~1-3s depending on image size
- **Model Loading**: ~2-5s on first request (cached thereafter)

## 🛠️ Configuration

Edit `backend/.env`:

```env
# Risk Scoring Weights
PII_WEIGHT=0.6
NLP_WEIGHT=0.4

# Thresholds
LOW_RISK_THRESHOLD=0.3
HIGH_RISK_THRESHOLD=0.6

# Privacy
ENABLE_LOGGING=False
STORE_DATA=False
```

## 🔮 Future Enhancements

- [ ] Browser extension integration
- [ ] Expand language support (additional languages and locale-specific patterns)
- [ ] Custom trained phishing models
- [ ] Real-time collaborative filtering
- [ ] Advanced OCR with layout analysis
- [ ] Integration with messaging platforms

## 📚 Academic Use

This project is designed for academic research and demonstrations. Key features for academic evaluation:

- **Modular architecture** for easy component testing
- **Evaluation module** with standard metrics
- **Explainable AI** with transparent scoring
- **Documented design decisions** in code
- **Dataset tools** for custom evaluations

## 🤝 Contributing

This is an academic project. For improvements:
1. Document your changes
2. Add tests if applicable
3. Update evaluation metrics
4. Maintain code quality

## 📄 License

Academic/Educational Use

## 👨‍💻 Author

SafeType+ Team - January 2026

---

**Note**: This is an academic project demonstrating AI/ML techniques for privacy protection. Not intended for production use without further hardening and testing.
