# Common Issues and Solutions

Quick reference for troubleshooting SafeType+ setup and runtime issues.

## Backend Issues

### Installation Problems

#### Issue: `pip install` fails with permission error
**Error**: `ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied`

**Solution**:
```powershell
# Use --user flag
pip install --user -r requirements.txt

# OR activate virtual environment first
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Issue: spaCy model download fails
**Error**: `Can't find model 'en_core_web_sm'`

**Solution**:
```powershell
# Try direct download
python -m spacy download en_core_web_sm

# If that fails, download manually
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl
```

#### Issue: Tesseract not found
**Error**: `TesseractNotFoundError: tesseract is not installed`

**Solution**:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install with default options
3. Add to .env:
```env
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Runtime Problems

#### Issue: Port 5000 already in use
**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:
```powershell
# Option 1: Kill process using port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Option 2: Change port in app.py
# Edit app.py line: app.run(host='0.0.0.0', port=5001, debug=True)
```

#### Issue: CORS errors in browser
**Error**: `Access-Control-Allow-Origin header is missing`

**Solution**:
1. Verify Flask-CORS is installed: `pip install flask-cors`
2. Check CORS config in `app.py`:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```
3. Restart backend server

#### Issue: Slow model loading
**Symptom**: First request takes 10+ seconds

**Solution**:
- This is normal behavior (models load on first use)
- Models are cached after first load
- Subsequent requests will be fast
- To preload, add to `app.py`:
```python
@app.before_first_request
def preload_models():
    from services.nlp_intent import nlp_intent
    nlp_intent.classify_intent("test")
```

#### Issue: Memory errors during processing
**Error**: `MemoryError` or system freeze

**Solution**:
1. Reduce text length limit in routes
2. Add pagination for large datasets
3. Increase system RAM
4. Use smaller model:
```python
# In nlp_intent.py
model_name = "distilbert-base-uncased"  # Smaller variant
```

### API Errors

#### Issue: 400 Bad Request on text scan
**Error**: `"error": "Text field is required"`

**Solution**:
- Verify request has `Content-Type: application/json`
- Check JSON structure:
```json
{
  "text": "your text here"
}
```

#### Issue: 500 Internal Server Error
**Error**: Generic 500 error

**Solution**:
1. Check backend terminal for stack trace
2. Common causes:
   - Missing model
   - Invalid configuration
   - Malformed input
3. Enable debug mode in `.env`: `FLASK_DEBUG=True`

## Frontend Issues

### Installation Problems

#### Issue: `npm install` fails
**Error**: Various npm errors

**Solution**:
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json -Force

# Reinstall
npm install
```

#### Issue: TypeScript compilation errors
**Error**: Type errors during `npm start`

**Solution**:
1. Ensure TypeScript is installed: `npm install typescript`
2. Check tsconfig.json exists
3. Restart VS Code if using it
4. Clear build: `npm run build`

### Runtime Problems

#### Issue: Cannot connect to backend
**Error**: `Could not connect to server`

**Solution**:
1. Verify backend is running: `http://localhost:5000/api/status`
2. Check `.env` file:
```env
REACT_APP_API_URL=http://localhost:5000/api
```
3. Disable VPN/proxy
4. Check firewall settings

#### Issue: Blank page after start
**Symptom**: Browser shows blank page

**Solution**:
1. Open DevTools (F12) and check Console tab
2. Clear browser cache: Ctrl+Shift+Delete
3. Try incognito/private mode
4. Check for JavaScript errors
5. Verify all files compiled: Check terminal output

#### Issue: Styles not loading (Tailwind)
**Symptom**: Unstyled or broken layout

**Solution**:
1. Verify Tailwind is installed: `npm list tailwindcss`
2. Check `tailwind.config.js` exists
3. Verify `index.css` has Tailwind directives:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```
4. Restart dev server: `npm start`

#### Issue: Image upload not working
**Error**: File upload fails silently

**Solution**:
1. Check file size (max 10MB)
2. Verify file format (PNG, JPG, GIF)
3. Check browser console for errors
4. Test with small image first
5. Verify backend accepts multipart/form-data

## Evaluation Issues

#### Issue: Sample dataset not created
**Error**: FileNotFoundError when running evaluation

**Solution**:
```powershell
# Manually create sample dataset
cd backend
python -c "from evaluation.dataset_loader import DatasetLoader; dl = DatasetLoader(); dl.create_sample_dataset('evaluation/sample_dataset.json')"
```

#### Issue: Low accuracy in evaluation
**Symptom**: Poor metrics on test dataset

**Solution**:
1. Verify dataset labels are correct
2. Check data format (JSON/CSV)
3. Adjust risk thresholds in `.env`:
```env
LOW_RISK_THRESHOLD=0.25
HIGH_RISK_THRESHOLD=0.55
```
4. Balance dataset if needed

## Performance Issues

#### Issue: Slow text scanning
**Symptom**: Takes >5 seconds per request

**Solution**:
1. Check text length (should be <10,000 chars)
2. Disable debug logging:
```env
FLASK_DEBUG=False
ENABLE_LOGGING=False
```
3. Ensure models are cached (not reloading each time)

#### Issue: OCR very slow
**Symptom**: Image scanning takes >10 seconds

**Solution**:
1. Resize large images before upload (frontend side)
2. Disable preprocessing if not needed
3. Check Tesseract installation
4. Use lower quality images for testing

## Model Issues

#### Issue: Intent classification always returns "benign"
**Symptom**: All texts classified as safe

**Solution**:
1. Verify DistilBERT model loaded correctly
2. Check keyword patterns in `nlp_intent.py`
3. Test with known phishing examples
4. Adjust scoring weights in `risk_engine.py`

#### Issue: Too many false positives
**Symptom**: Normal text marked as high risk

**Solution**:
1. Tune PII severity weights in `scoring_utils.py`
2. Adjust risk thresholds in `.env`
3. Improve regex patterns to reduce false matches
4. Add whitelisting for common patterns

## OS-Specific Issues

### Windows

#### Issue: PowerShell script execution disabled
**Error**: `cannot be loaded because running scripts is disabled`

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Issue: Long path errors
**Error**: Path too long errors

**Solution**:
1. Enable long paths in Windows:
   - Run `gpedit.msc`
   - Navigate to: Computer Configuration > Administrative Templates > System > Filesystem
   - Enable "Enable Win32 long paths"
2. Or move project to shorter path (e.g., `C:\safeType`)

### macOS/Linux

#### Issue: Permission denied when activating venv
**Error**: Permission denied on activate script

**Solution**:
```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

#### Issue: Tesseract not in PATH
**Error**: tesseract: command not found

**Solution**:
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Verify installation
which tesseract
```

## Debug Checklist

When something isn't working:

1. ✅ Backend server is running
2. ✅ Frontend dev server is running
3. ✅ Virtual environment is activated
4. ✅ All dependencies are installed
5. ✅ Configuration files are correct
6. ✅ Models are downloaded
7. ✅ Ports are not blocked
8. ✅ No firewall blocking localhost
9. ✅ Check terminal logs for errors
10. ✅ Check browser console for errors

## Getting More Help

If issue persists:

1. **Check logs**: Look at both backend terminal and browser console
2. **Isolate the problem**: Test individual components
3. **Verify environment**: Ensure all prerequisites met
4. **Test with examples**: Use provided example texts/images
5. **Review documentation**: Check README and SETUP_GUIDE

## Reporting Issues

When reporting a problem, include:

- Operating system and version
- Python version: `python --version`
- Node version: `node --version`
- Full error message and stack trace
- Steps to reproduce
- What you've already tried

---

Most issues can be resolved by carefully following the setup guide and checking the logs.
