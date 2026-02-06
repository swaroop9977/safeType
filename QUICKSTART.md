# SafeType+ Quick Start

Get SafeType+ running in under 10 minutes!

## Prerequisites Check

```powershell
# Check Python (need 3.10+)
python --version

# Check Node.js (need 16+)
node --version

# Check npm
npm --version
```

If any are missing, install from:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

## 5-Step Setup

### 1️⃣ Backend Setup (3 minutes)

```powershell
cd d:\pilot\safeType+\backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create config file
cp .env.example .env

# Start server
python app.py
```

**Leave this terminal open!** Backend is now running on `http://localhost:5000`

### 2️⃣ Frontend Setup (2 minutes)

Open a **new terminal**:

```powershell
cd d:\pilot\safeType+\frontend

# Install dependencies
npm install

# Start development server
npm start
```

Browser will open automatically at `http://localhost:3000`

### 3️⃣ Verify Installation

1. Type text in the text box
2. Wait 1.5 seconds or click "Scan Now"
3. You should see risk analysis appear!

### 4️⃣ Test with Examples

Click these buttons to test:
- **"Load Safe Example"** - Should show LOW risk
- **"Load Risky Example"** - Should show HIGH risk with suggestions

### 5️⃣ Try Image Scanning

1. Switch to "Scan Image" tab
2. Upload any screenshot with text
3. Click "Scan Image"
4. See extracted text and risk analysis!

## Optional: Install Tesseract (for better OCR)

**Windows**:
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install (keep default path)
3. Edit `backend\.env`:
   ```env
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```
4. Restart backend

**macOS**: `brew install tesseract`
**Linux**: `sudo apt-get install tesseract-ocr`

## Common Issues

**Backend won't start?**
- Check if port 5000 is free
- Make sure virtual environment is activated
- Verify all dependencies installed: `pip list`

**Frontend shows blank page?**
- Check browser console (F12)
- Verify backend is running
- Clear cache and refresh

**"Cannot connect to server"?**
- Check backend terminal is still running
- Try: `http://localhost:5000/api/status` in browser

## What You Can Do

✅ Scan text for PII and phishing patterns  
✅ Upload images and extract text via OCR  
✅ View color-coded risk assessments  
✅ See highlighted risky text  
✅ Get safer alternative suggestions  
✅ Understand detection reasons  

## Next Steps

1. **Read the docs**: `README.md` for full details
2. **Run evaluation**: `python backend/evaluation/run_evaluation.py`
3. **Customize**: Edit `backend/.env` to tune thresholds
4. **Explore code**: Check the modular architecture

## API Test (curl)

```powershell
# Test text scanning
curl -X POST http://localhost:5000/api/scan/text `
  -H "Content-Type: application/json" `
  -d '{\"text\": \"My email is test@example.com and phone is 555-1234\"}'
```

## Need Help?

- 📖 See `SETUP_GUIDE.md` for detailed instructions
- 🔧 See `TROUBLESHOOTING.md` for common issues
- 🏗️ See `ARCHITECTURE.md` for system design

---

**Congratulations!** SafeType+ is ready to protect privacy! 🎉🔒
