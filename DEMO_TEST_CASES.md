# SafeType+ Demo Test Cases

## Text Scanner Test Cases

### ✅ Test Case 1: Safe Text (Expected: LOW Risk)
```
Hi team, let's schedule a meeting next week to discuss the project timeline. 
Looking forward to collaborating with everyone!
```
**Expected Result:**
- Risk Level: Low (0.0-0.2)
- No PII detected
- Benign intent
- No suggestions needed

---

### ⚠️ Test Case 2: Medium Risk - Contact Info
```
Thanks for your interest! You can reach me at john.doe@email.com 
or call me at 555-123-4567 anytime.
```
**Expected Result:**
- Risk Level: Medium (0.4-0.5)
- PII Detected: Email, Phone
- Suggestions: Redacted version, guidance
- Highlights: Email and phone highlighted

**Key Demo Points:**
- Show email and phone highlighted in different colors
- Point out the safer suggestions
- Explain why it's medium vs high risk

---

### 🚨 Test Case 3: High Risk - Financial + Phishing
```
URGENT! Your account has been suspended. 
Please verify your credit card 4532-1508-3406-1234 immediately 
or contact us at 555-987-6543. Click here now to avoid penalties!
```
**Expected Result:**
- Risk Level: High (0.7-0.9)
- PII Detected: Credit card (Luhn valid), phone
- Phishing Keywords: URGENT, suspended, immediately, Click here
- Intent: Suspicious/Phishing
- Multiple suggestions provided

**Key Demo Points:**
- Show high risk score with red meter
- Multiple PII types detected
- Phishing keywords highlighted differently
- 3-4 safer suggestion types
- Module breakdown showing both PII (high) and NLP (high)

---

### 🚨 Test Case 4: Identity Theft Risk
```
Please send me your SSN (123-45-6789) and date of birth (01/15/1990) 
for verification. Also need your passport number A1234567.
```
**Expected Result:**
- Risk Level: High (0.8+)
- PII Detected: SSN, Date of Birth, Passport
- High severity PII types
- Strong warning in reasons

**Key Demo Points:**
- Critical PII detected (SSN, Passport)
- Explain severity weighting
- Show confidence intervals

---

### 🌍 Test Case 5: Multilingual (Spanish)
```
¡Urgente! Tu cuenta bancaria ha sido suspendida. 
Haz clic aquí inmediatamente para verificar tu información.
```
**Expected Result:**
- Language detected: Spanish (es)
- Phishing keywords in Spanish detected
- Risk Level: Medium-High
- Intent: Suspicious

**Key Demo Points:**
- Show language detection in metadata
- Spanish phishing keywords recognized
- Multilingual capability

---

### 📧 Test Case 6: Business Context - Lower Risk
```
For official correspondence, please write to support@company.com. 
Our office is located at 123 Business Street, New York. 
Office hours: Monday-Friday, 9 AM - 5 PM.
```
**Expected Result:**
- Risk Level: Low-Medium (0.2-0.4)
- Email detected (but corporate context)
- Address detected (but business location)
- Intent: Benign

**Key Demo Points:**
- Context matters
- Business emails have lower risk
- System understands intent

---

## Image Scanner Test Cases

### 🖼️ Test Case 7: Screenshot with Form
**Preparation:** Create a simple screenshot with text containing:
```
Name: John Smith
Email: john.smith@example.com
Phone: (555) 123-4567
Credit Card: 4532-1508-3406-1234
```

**Expected Result:**
- OCR extracts text successfully
- All PII detected from extracted text
- OCR confidence score shown
- High risk assessment

**Key Demo Points:**
- Show original image preview
- Show extracted text
- Highlight that OCR feeds into same analysis pipeline
- Real-world use case: checking screenshots before sharing

---

### 🖼️ Test Case 8: Receipt/Invoice Image
**Preparation:** Screenshot of a fake receipt/invoice with:
- Business name
- Date
- Items
- Maybe partial credit card number

**Expected Result:**
- OCR extracts structured text
- Detects any financial information
- Medium risk if partial CC visible

**Key Demo Points:**
- Practical application
- Prevents accidental sharing of financial documents

---

## Quick Demo Flow (5 minutes)

### Opening (30 seconds)
"SafeType+ is an AI-powered system that analyzes text and images BEFORE submission to detect privacy risks and suggest safer alternatives."

### Text Demo (2 minutes)
1. **Safe text** → Show it works, doesn't over-flag
2. **High risk text** (Case 3) → Show full feature set:
   - Risk meter animation
   - Highlighted text with colors
   - Detection breakdown
   - Safer suggestions (key differentiator!)

### Image Demo (1.5 minutes)
1. Upload screenshot with PII
2. Show OCR extraction
3. Show analysis results

### Technical Overview (1 minute)
"Behind the scenes: Multi-layered detection with regex, NER, transformer-based intent classification, and OCR. Explainable AI with module breakdown."

### Closing (30 seconds)
"Key differentiator: We don't just warn—we educate with safer alternatives. Fully privacy-preserving with local processing."

---

## Backup Examples (If Things Go Wrong)

### If API is slow:
"The first request loads the ML models into memory—subsequent requests are much faster. This is expected behavior."

### If OCR fails:
"OCR accuracy depends on image quality. Let me show you the text scanner which is the core functionality."

### If detection misses something:
"The system is tunable via thresholds. In production, we'd fine-tune based on domain-specific requirements."

---

## Interactive Q&A Scenarios

### Q: "Can it detect obfuscated PII?"
**Demo:** Type `user [at] example [dot] com`
**Result:** Won't detect (by design - deliberately obfuscated)
**Answer:** "Correct! If users intentionally obfuscate, they're already privacy-aware. We focus on accidental exposure."

### Q: "What about false positives?"
**Demo:** Type `Call me at 1234567890`
**Result:** Should detect (valid 10-digit)
**Answer:** "We use validation like Luhn algorithm for credit cards and sequential digit detection. Configurable thresholds let organizations tune sensitivity."

### Q: "Performance at scale?"
**Answer:** "Current: Academic demo. Production would use Gunicorn workers, Redis caching, and load balancing. Typical response time under 500ms after model warm-up."

---

## Technical Deep-Dive Points (If Asked)

### **Architecture:**
- Backend: Flask (Python), Frontend: React + TypeScript
- Models: DistilBERT (60% faster than BERT), spaCy NER
- OCR: PyTesseract + OpenCV preprocessing

### **Risk Scoring:**
```
risk_score = (pii_score × 0.6) + (nlp_score × 0.4)
```
- PII weighted higher (privacy priority)
- Tunable via configuration

### **Multilingual:**
- 6 languages supported
- Language-specific phishing keywords
- Automatic language detection

### **Evaluation:**
- Classification metrics: Accuracy, Precision, Recall, F1
- Regression metrics: MAE, RMSE, R²
- Dataset loader for custom evaluation

---

## Emergency Troubleshooting During Demo

### Backend not responding:
1. Check terminal: Is Flask running? Look for errors
2. Check URL: `http://localhost:5000/api/status`
3. Restart: `python app.py`

### Frontend not loading:
1. Check terminal: `npm start` running?
2. Check URL: `http://localhost:3000`
3. Clear cache: Ctrl+Shift+Delete

### Model loading slow:
"This is the first request loading the transformer models. Let me show you the code while it processes..."

---

## Impressive Stats to Mention

✅ **10+ PII types** detected (email, phone, CC, SSN, passport, etc.)  
✅ **6 languages** supported with multilingual models  
✅ **4 validation methods** (regex, NER, Luhn, sequential detection)  
✅ **4 types of suggestions** (redacted, rewritten, guidance, templates)  
✅ **Explainable AI** with module breakdown and confidence intervals  
✅ **Zero data storage** - complete privacy preservation  
✅ **Sub-second** response time (after model warmup)  

---

## Best Practices for Demo

1. ⏰ **Test everything 30 mins before** - Start both servers, test all cases
2. 📱 **Have backup** - Screenshots of working demo in case of issues
3. 🎯 **Start simple** - Safe text first, build to complex
4. 🗣️ **Explain as you go** - Don't just click, narrate what's happening
5. ⚡ **Keep momentum** - Don't get stuck on one issue, move forward
6. 💡 **Emphasize differentiator** - Suggestions, not just warnings
7. 📊 **Show explainability** - Open detection breakdown, show confidence
8. 🎬 **End strong** - Summarize key points, invite questions

**Good luck with your presentation! 🚀**
