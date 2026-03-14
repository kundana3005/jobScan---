# ─── MODULE 3: PREDICTION MODULE - BACKEND ──────────────────────
# Handles: Receiving form data, preprocessing, ML prediction

from flask import Blueprint, render_template, request, redirect, url_for, session
import pickle
import json
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

# Blueprint pointing to module3 frontend folder
prediction_bp = Blueprint(
    'prediction',
    __name__,
    template_folder='../frontend'
)

stop_words = set(stopwords.words('english'))

# ─── LOAD MODEL ─────────────────────────────────────────────────
try:
    with open('model/model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('model/tfidf.pkl', 'rb') as f:
        tfidf = pickle.load(f)
    print("✅ Model loaded successfully")
except FileNotFoundError:
    print("⚠️ Model not found. Run train_model.py first.")
    model = None
    tfidf = None


# ─── PREPROCESSING FUNCTION ─────────────────────────────────────
def preprocess(text):
    text  = text.lower()
    text  = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return ' '.join(words)


# ─── FAKE KEYWORDS LIST ─────────────────────────────────────────
# These words/phrases are strong indicators of fake jobs
FAKE_KEYWORDS = [
    'registration fee', 'joining fee', 'pay fee',
    'bank account details', 'bank details',
    'whatsapp', 'telegram',
    'no experience needed', 'no qualification',
    'guaranteed income', 'guaranteed payment',
    'earn $', 'earn usd', 'earn money fast',
    'work from home earn', 'instant selection',
    'already selected', 'no interview',
    'limited slots', 'apply immediately',
    'send your details', 'personal details required',
    'aadhar card', 'passport copy',
    'part time earn', 'daily payment guaranteed',
    'housewives welcome', 'freshers earn',
    '500 per day', '1000 per day',
    '5000 per week', '3000 per week',
    'copy paste work', 'clicking ads',
    'no target', 'no boss',
    'urgent hiring work from home',
    'pay small fee', 'refundable deposit'
]


def check_fake_keywords(text):
    """
    Check if text contains obvious fake job keywords
    Returns True if 2 or more fake keywords found
    """
    text_lower = text.lower()
    found      = []

    for keyword in FAKE_KEYWORDS:
        if keyword in text_lower:
            found.append(keyword)

    return len(found) >= 2, found


# ─── ROUTES ─────────────────────────────────────────────────────
@prediction_bp.route('/predict', methods=['POST'])
def predict():
    if 'user_email' not in session:
        return redirect(url_for('auth.login'))

    # Step 1: Get form data
    company     = request.form.get('company', '').strip()
    salary      = request.form.get('salary', '').strip()
    description = request.form.get('description', '').strip()

    # Step 2: Validate input
    if not description:
        return render_template('index.html',
                               error="Please enter a job description.")

    if len(description) < 20:
        return render_template('index.html',
                               error="Description too short.")

    if model is None or tfidf is None:
        return render_template('index.html',
                               error="Model not loaded. Run train_model.py first.")

    # Step 3: Layer 1 — Check for obvious fake keywords
    is_keyword_fake, found_keywords = check_fake_keywords(
        company + ' ' + salary + ' ' + description
    )

    if is_keyword_fake:
        # Keyword detection overrides ML model
        result     = "FAKE"
        confidence = round(90 + (len(found_keywords) * 1.5), 2)
        confidence = min(confidence, 99.0)  # Cap at 99%

    else:
        # Step 4: Layer 2 — Use ML model for prediction
        combined    = company + ' ' + description
        cleaned     = preprocess(combined)
        input_tfidf = tfidf.transform([cleaned])
        prediction  = model.predict(input_tfidf)[0]
        probability = model.predict_proba(input_tfidf)[0]
        confidence  = round(max(probability) * 100, 2)
        result      = "FAKE" if prediction == 1 else "REAL"

    # Step 5: Save to history
    try:
        with open('history.json', 'r') as f:
            history = json.load(f)
    except:
        history = []

    history.append({
        "user"       : session['user_email'],
        "company"    : company,
        "salary"     : salary,
        "description": description[:100] + "...",
        "result"     : result,
        "confidence" : confidence
    })

    with open('history.json', 'w') as f:
        json.dump(history, f, indent=4)

    # Step 6: Return result to result page
    return render_template('result.html',
                           result=result,
                           confidence=confidence,
                           company=company,
                           salary=salary,
                           description=description,
                           username=session['username'])