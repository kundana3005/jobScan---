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


# ─── ROUTES ─────────────────────────────────────────────────────
@prediction_bp.route('/predict', methods=['POST'])
def predict():
    if 'user_email' not in session:
        return redirect(url_for('auth.login'))

    # Get form data
    company     = request.form.get('company', '').strip()
    salary      = request.form.get('salary', '').strip()
    description = request.form.get('description', '').strip()

    # Validate
    if not description:
        return render_template('index.html',
                               error="Please enter a job description.")

    if len(description) < 20:
        return render_template('index.html',
                               error="Description too short.")

    if model is None or tfidf is None:
        return render_template('index.html',
                               error="Model not loaded. Run train_model.py first.")

    # Preprocess and predict
    combined    = company + ' ' + description
    cleaned     = preprocess(combined)
    input_tfidf = tfidf.transform([cleaned])
    prediction  = model.predict(input_tfidf)[0]
    probability = model.predict_proba(input_tfidf)[0]
    confidence  = round(max(probability) * 100, 2)
    result      = "FAKE" if prediction == 1 else "REAL"

    # Save to history
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

    return render_template('result.html',
                           result=result,
                           confidence=confidence,
                           company=company,
                           salary=salary,
                           description=description,
                           username=session['username'])