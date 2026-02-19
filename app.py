from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import hashlib
import pickle          # For loading saved model
import re              # For removing symbols
import nltk
from nltk.corpus import stopwords

# Download stopwords (only runs once)
nltk.download('stopwords', quiet=True)

# ─── LOAD MODEL AND TFIDF ───────────────────────────────────────
# Load the saved ML model and TF-IDF vectorizer
# These were created by train_model.py
try:
    with open('model/model.pkl', 'rb') as f:
        model = pickle.load(f)

    with open('model/tfidf.pkl', 'rb') as f:
        tfidf = pickle.load(f)

    print("✅ Model loaded successfully")

except FileNotFoundError:
    print("⚠️ Model not found. Please run train_model.py first.")
    model = None
    tfidf = None


# ─── PREPROCESSING FUNCTION ─────────────────────────────────────
stop_words = set(stopwords.words('english'))

def preprocess(text):
    """
    Clean raw text before feeding to ML model:
    1. Lowercase
    2. Remove symbols
    3. Remove stopwords
    """
    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove everything except letters
    text = re.sub(r'[^a-z\s]', '', text)

    # Step 3: Remove stopwords
    words = text.split()
    words = [w for w in words if w not in stop_words]

    return ' '.join(words) # Used to hash passwords — never store plain passwords

app = Flask(__name__)

# Secret key needed for session (keeps user logged in)
app.secret_key = "jobscan_secret_key_2024"

# Path to users file
USERS_FILE = "users.json"


# ─── HELPER FUNCTIONS ───────────────────────────────────────────

def load_users():
    """Load all users from users.json file"""
    if not os.path.exists(USERS_FILE):
        return {}  # Return empty dict if file doesn't exist yet
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    """Save users dictionary back to users.json"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Convert password to a hash so we never store plain text"""
    return hashlib.sha256(password.encode()).hexdigest()


# ─── ROUTES ─────────────────────────────────────────────────────

# Landing page — first page user sees
@app.route('/')
def landing():
    return render_template('landing.html')


# ── LOGIN ──
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        # Load existing users
        users = load_users()

        # Check if email exists and password matches
        if email not in users:
            return render_template('login.html', error="No account found with this email.")

        if users[email]['password'] != hash_password(password):
            return render_template('login.html', error="Incorrect password.")

        # Login successful — save user in session
        session['user_email'] = email
        session['username'] = users[email]['name']

        # Redirect to dashboard
        return redirect(url_for('dashboard'))

    # GET request — just show the login form
    return render_template('login.html')


# ── SIGNUP ──
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()

        # Validation checks
        if not name or not email or not password:
            return render_template('signup.html', error="All fields are required.")

        if password != confirm:
            return render_template('signup.html', error="Passwords do not match.")

        if len(password) < 6:
            return render_template('signup.html', error="Password must be at least 6 characters.")

        # Load existing users
        users = load_users()

        # Check if email already registered
        if email in users:
            return render_template('signup.html', error="This email is already registered.")

        # Save new user
        users[email] = {
            "name": name,
            "password": hash_password(password)
        }
        save_users(users)

        # Redirect to login with success message
        return render_template('login.html', success="Account created! Please login.")

    # GET request — show signup form
    return render_template('signup.html')


# ── DASHBOARD ──
@app.route('/dashboard')
def dashboard():
    # Check if user is logged in
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Pass username to dashboard template
    return render_template('dashboard.html', username=session['username'])


# ── LOGOUT ──
@app.route('/logout')
def logout():
    # Clear session data
    session.clear()
    return redirect(url_for('landing'))


# ── PLACEHOLDER ROUTES for dashboard buttons ──
@app.route('/scan')
def scan():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')  # Job scan form from Module 1

# ── SEARCH JOB PAGE ──
@app.route('/search')
def search():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Sample job listings data
    # In a real project this would come from a database
    jobs = [
        # IT / Software
        {
            "title": "Python Developer",
            "company": "TechCorp India",
            "location": "Bangalore, India",
            "salary": "6-10 LPA",
            "category": "IT / Software",
            "description": "Looking for an experienced Python developer with Flask and Django skills."
        },
        {
            "title": "Frontend Developer",
            "company": "WebSolutions Pvt Ltd",
            "location": "Hyderabad, India",
            "salary": "5-8 LPA",
            "category": "IT / Software",
            "description": "Build beautiful web interfaces using HTML, CSS, React and Bootstrap."
        },
        {
            "title": "Data Scientist",
            "company": "Analytics Hub",
            "location": "Pune, India",
            "salary": "10-15 LPA",
            "category": "IT / Software",
            "description": "Work on ML models, data pipelines and business intelligence dashboards."
        },
        {
            "title": "Cybersecurity Analyst",
            "company": "SecureNet Ltd",
            "location": "Chennai, India",
            "salary": "8-12 LPA",
            "category": "IT / Software",
            "description": "Monitor and protect company systems from cyber threats and vulnerabilities."
        },

        # Marketing
        {
            "title": "Digital Marketing Manager",
            "company": "BrandBoost Agency",
            "location": "Mumbai, India",
            "salary": "5-9 LPA",
            "category": "Marketing",
            "description": "Manage SEO, SEM, social media campaigns and content strategy."
        },
        {
            "title": "Content Writer",
            "company": "Creative Minds",
            "location": "Remote",
            "salary": "3-5 LPA",
            "category": "Marketing",
            "description": "Write engaging blog posts, social media content and marketing copy."
        },
        {
            "title": "Social Media Executive",
            "company": "GrowthHack Media",
            "location": "Delhi, India",
            "salary": "3-6 LPA",
            "category": "Marketing",
            "description": "Handle Instagram, LinkedIn and Twitter accounts for multiple brands."
        },

        # Finance
        {
            "title": "Financial Analyst",
            "company": "MoneyWise Corp",
            "location": "Mumbai, India",
            "salary": "7-12 LPA",
            "category": "Finance",
            "description": "Analyze financial data, prepare reports and support investment decisions."
        },
        {
            "title": "Chartered Accountant",
            "company": "Deloitte India",
            "location": "Bangalore, India",
            "salary": "10-18 LPA",
            "category": "Finance",
            "description": "Handle audits, tax planning and financial compliance for enterprise clients."
        },
        {
            "title": "Investment Banker",
            "company": "Capital First",
            "location": "Mumbai, India",
            "salary": "15-25 LPA",
            "category": "Finance",
            "description": "Support mergers, acquisitions and fundraising for corporate clients."
        },

        # Healthcare
        {
            "title": "Clinical Data Analyst",
            "company": "HealthTech Solutions",
            "location": "Hyderabad, India",
            "salary": "6-10 LPA",
            "category": "Healthcare",
            "description": "Analyze patient data and clinical trial results to support medical research."
        },
        {
            "title": "Hospital Administrator",
            "company": "Apollo Hospitals",
            "location": "Chennai, India",
            "salary": "5-8 LPA",
            "category": "Healthcare",
            "description": "Manage hospital operations, staff coordination and patient services."
        },
        {
            "title": "Medical Coder",
            "company": "MedBill India",
            "location": "Remote",
            "salary": "3-6 LPA",
            "category": "Healthcare",
            "description": "Assign medical codes to diagnoses and procedures for billing purposes."
        },
    ]

    return render_template('search.html', jobs=jobs, username=session['username'])

# ── VIEW HISTORY ──
@app.route('/history')
def history():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Load history from file
    try:
        with open('history.json', 'r') as f:
            history = json.load(f)
    except:
        history = []

    # Calculate average confidence for this user's scans
    user_history = [h for h in history if h['user'] == session['user_email']]

    if user_history:
        avg_confidence = round(
            sum(h['confidence'] for h in user_history) / len(user_history), 2
        )
    else:
        avg_confidence = 0

    return render_template('history.html',
                           history=history,
                           current_user=session['user_email'],
                           username=session['username'],
                           avg_confidence=avg_confidence)


# ── CLEAR HISTORY ──
@app.route('/clear_history')
def clear_history():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Load all history
    try:
        with open('history.json', 'r') as f:
            history = json.load(f)
    except:
        history = []

    # Remove only current user's history
    # Other users history stays safe
    history = [h for h in history if h['user'] != session['user_email']]

    # Save back
    with open('history.json', 'w') as f:
        json.dump(history, f, indent=4)

    return redirect(url_for('history'))
# ── REPORT FAKE JOB ──
@app.route('/report', methods=['GET', 'POST'])
def report():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    # Load existing reports
    try:
        with open('reports.json', 'r') as f:
            reports = json.load(f)
    except:
        reports = []

    if request.method == 'POST':
        # Get form data
        job_title = request.form.get('job_title', '').strip()
        company   = request.form.get('company', '').strip()
        url       = request.form.get('url', '').strip()
        reason    = request.form.get('reason', '').strip()
        details   = request.form.get('details', '').strip()

        # Validate
        if not job_title or not company or not reason:
            return render_template('report.html',
                                   error="Please fill all required fields.",
                                   reports=reports,
                                   username=session['username'])

        # Create report entry
        new_report = {
            "job_title"   : job_title,
            "company"     : company,
            "url"         : url,
            "reason"      : reason,
            "details"     : details,
            "reported_by" : session['user_email']
        }

        # Add to reports list and save
        reports.append(new_report)
        with open('reports.json', 'w') as f:
            json.dump(reports, f, indent=4)

        return render_template('report.html',
                               success="Report submitted successfully! Thank you for keeping others safe.",
                               reports=reports,
                               username=session['username'])

    # GET request — show report form
    return render_template('report.html',
                           reports=reports,
                           username=session['username'])

# ── JOB SCAN (from Module 1) ──
# ── JOB SCAN WITH REAL PREDICTION ──
@app.route('/predict', methods=['POST'])
def predict():
    if 'user_email' not in session:
        return redirect(url_for('login'))

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
                               error="Description too short. Please add more details.")

    # Step 3: Check model is loaded
    if model is None or tfidf is None:
        return render_template('index.html',
                               error="Model not loaded. Please run train_model.py first.")

    # Step 4: Preprocess the input text
    # Combine company name and description for better accuracy
    combined = company + ' ' + description
    cleaned  = preprocess(combined)

    # Step 5: Convert cleaned text to TF-IDF numbers
    input_tfidf = tfidf.transform([cleaned])

    # Step 6: Predict using Naive Bayes model
    prediction = model.predict(input_tfidf)[0]

    # Step 7: Get confidence score (probability)
    probability    = model.predict_proba(input_tfidf)[0]
    confidence     = round(max(probability) * 100, 2)

    # Step 8: Convert prediction to label
    # Model returns 1 for Fake, 0 for Real
    result = "FAKE" if prediction == 1 else "REAL"

    # Step 9: Save to history
    history_entry = {
        "user"       : session['user_email'],
        "company"    : company,
        "salary"     : salary,
        "description": description[:100] + "...",  # Save first 100 chars only
        "result"     : result,
        "confidence" : confidence
    }

    # Load existing history
    try:
        with open('history.json', 'r') as f:
            history = json.load(f)
    except:
        history = []

    # Add new entry and save
    history.append(history_entry)
    with open('history.json', 'w') as f:
        json.dump(history, f, indent=4)

    # Step 10: Send result back to scan page
    return render_template('result.html',
                       result=result,
                       confidence=confidence,
                       company=company,
                       salary=salary,
                       description=description,
                       username=session['username'])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
