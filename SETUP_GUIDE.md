# SafeType+ Setup Guide

Complete step-by-step guide to set up and run SafeType+.

## System Requirements

- **OS**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.10, 3.11, or 3.12 ONLY (⚠️ 3.13+ NOT supported due to spaCy)
- **Node.js**: 16.x or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB free space for models and dependencies

## Installation Steps

### 1. Clone or Extract Project

```powershell
cd d:\pilot\safeType+
```

### 2. Backend Setup

#### Step 2.1: Create Virtual Environment

**Windows (check Python version first):**
```powershell
cd backend
python --version

# If Python 3.10-3.12, use:
python -m venv .venv

# If you have Python 3.13+ installed, use py launcher to select 3.10:
py -3.10 -m venv .venv
```

**macOS/Linux:**
```bash
cd backend
python3.10 -m venv .venv
```

#### Step 2.2: Activate Virtual Environment

**Windows (PowerShell)**:
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD)**:
```cmd
.\.venv\Scripts\activate.bat
```

**macOS/Linux**:
```bash
source .venv/bin/activate
```

#### Step 2.3: Install Python Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Transformers (NLP/AI models)
- spaCy (NER/entity extraction)
- PyTesseract (OCR)
- OpenCV (image processing)
- And all other dependencies

#### Step 2.4: Initialize AI Models

SafeType+ uses transformer-based AI for intelligent phishing and PII detection. Models are automatically downloaded on first startup, but you can pre-download them:

**Option A: Automatic** (recommended for quick start)
```powershell
# Models will download when you first run:
python app.py
```
This will download:
- DistilBERT (intent classification) ~268 MB
- spaCy NER (entity extraction) ~40 MB
- Optional: Multilingual models ~800 MB

**Option B: Pre-download** (for CI/CD or offline environments)
```powershell
python setup_models.py
```

**Option C: English-only** (faster, 300 MB instead of 1.1 GB)
```powershell
python setup_models.py --no-multilingual
```

For complete model setup details, see [MODEL_SETUP.md](MODEL_SETUP.md).

#### Step 2.5: Install Tesseract OCR

**Windows**:
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
3. Note installation path (usually `C:\Program Files\Tesseract-OCR\tesseract.exe`)

**macOS** (using Homebrew):
```bash
brew install tesseract
```

**Linux** (Ubuntu/Debian):
```bash
sudo apt-get install tesseract-ocr
```

#### Step 2.6: Configure Environment

1. Copy example configuration:
```powershell
Copy-Item .env.example .env
```

2. Edit `.env` file (use Notepad or VS Code):
```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=False

# Tesseract Path (Windows example)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Leave other settings as default for now
```

**Note**: On macOS/Linux, Tesseract is usually in PATH, so you can leave `TESSERACT_PATH` empty.

#### Step 2.7: Test Backend Installation

```powershell
python -c "import flask, transformers, spacy, cv2; print('All imports successful!')"
```

If no errors appear, backend dependencies are correctly installed.

#### Step 2.8: Start Backend Server

```powershell
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
 * Loaded spaCy model: en_core_web_sm
```

**Keep this terminal open** - the backend needs to keep running.

### 3. Frontend Setup

Open a **new terminal window**.

#### Step 3.1: Navigate to Frontend

```powershell
cd d:\pilot\safeType+\frontend
```

#### Step 3.2: Install Node Dependencies

```powershell
npm install
```

This will install:
- React and React DOM
- TypeScript
- Tailwind CSS
- Axios
- And all other dependencies

**Note**: This may take 2-5 minutes depending on internet speed.

#### Step 3.3: Configure API URL (Optional)

Create `.env` file in `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

This is optional - the default will work if backend is on localhost:5000.

#### Step 3.4: Start Frontend Development Server

```powershell
npm start
```

This will:
- Compile the TypeScript code
- Start development server
- Automatically open browser at `http://localhost:3000`

## 4. Verify Installation

### Backend Verification

1. Open browser and go to: `http://localhost:5000/api/status`
2. You should see JSON response:
```json
{
  "status": "operational",
  "modules": {
    "pii_detection": "ready",
    "ner": "ready",
    ...
  }
}
```

### Frontend Verification

1. Browser should automatically open at `http://localhost:3000`
2. Click any "Get started" / launch button on the landing page
3. You should see the SafeType+ scanner interface
4. Try typing text in the text scanner
5. After ~1.5 seconds, it should auto-scan

## 5. First Test

### Test Text Scanning

1. Click "Risky Example" button
2. Wait for auto-scan or click "Scan Now"
3. You should see:
   - Risk meter showing "High" risk
   - Highlighted text with PII
   - Reasons for risk assessment
   - Safer alternative suggestions

### Test Image Scanning

1. Switch to "Scan Image" tab
2. Upload a screenshot with text
3. Click "Scan Image"
4. You should see:
   - Extracted text from image
   - Risk analysis
   - Any detected PII in the image

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'flask'`
- **Solution**: Make sure virtual environment is activated and dependencies are installed
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Issue**: `OSError: [E050] Can't find model 'en_core_web_sm'`
- **Solution**: Download spaCy model
```powershell
python -m spacy download en_core_web_sm
```

**Issue**: `TesseractNotFoundError`
- **Solution**: 
  1. Verify Tesseract is installed
  2. Set correct path in `.env` file
  3. Or install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki

**Issue**: Port 5000 already in use
- **Solution**: Either stop the other service or change port in `app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
```

### Frontend Issues

**Issue**: `npm: command not found`
- **Solution**: Install Node.js from https://nodejs.org/

**Issue**: Port 3000 already in use
- **Solution**: The system will prompt to use a different port. Type 'Y' to accept.

**Issue**: "Cannot connect to server"
- **Solution**: 
  1. Verify backend is running on port 5000
  2. Check `.env` file has correct API URL
  3. Disable any firewall blocking localhost

**Issue**: Blank page after `npm start`
- **Solution**: 
  1. Check browser console for errors (F12)
  2. Try clearing cache and reloading
  3. Verify all npm packages installed: `npm install`

## Running Evaluation

To test the system with labeled datasets:

```powershell
cd backend
python evaluation/run_evaluation.py
```

This will:
1. Create a sample dataset if none exists
2. Run predictions on all samples
3. Compute metrics (accuracy, precision, recall, F1)
4. Save report to `evaluation_report.txt`

### Using Custom Dataset

```powershell
python evaluation/run_evaluation.py path/to/dataset.json output_report.txt
```

Dataset format:
```json
[
  {"text": "Safe message", "label": 0},
  {"text": "Phishing attempt", "label": 1}
]
```

## Development Tips

### Backend Development

- Current `app.py` runs with `debug=False` and `use_reloader=False`
- Restart backend manually after backend code changes
- Check logs in terminal for debugging
- Use `logger.debug()` for detailed logging

### Frontend Development

- Code changes hot-reload automatically
- Open DevTools (F12) for debugging
- Check Network tab for API calls

### Recommended VS Code Extensions

- Python
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense

## Production Deployment

**Note**: This is an academic project. For production:

1. Set `FLASK_ENV=production` in backend `.env`
2. Use production WSGI server (gunicorn/waitress)
3. Build frontend: `npm run build`
4. Serve frontend build with nginx/Apache
5. Add proper security headers
6. Enable HTTPS
7. Set up rate limiting
8. Add authentication if needed

## Getting Help

If you encounter issues:

1. Check this guide first
2. Review error messages carefully
3. Check terminal/console logs
4. Verify all prerequisites are installed
5. Try restarting both servers

## Next Steps

After successful setup:

1. Explore the UI and test different text samples
2. Try uploading images with text
3. Review the code structure
4. Run evaluation on custom datasets
5. Modify configuration to test different thresholds
6. Experiment with custom detection rules

---

**Congratulations!** You now have SafeType+ running locally. 🎉
