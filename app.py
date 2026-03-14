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

    jobs = [

        # ── IT / SOFTWARE ──────────────────────────────────────
        {
            "title"          : "Python Developer",
            "company"        : "TechCorp India",
            "location"       : "Bangalore, India",
            "salary"         : "6-10 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Hybrid",
            "experience"     : "2-4 years",
            "education"      : "B.E / B.Tech in Computer Science",
            "skills"         : ["Python", "Flask", "Django", "REST APIs", "MySQL", "Git"],
            "responsibilities": [
                "Develop and maintain Python-based web applications",
                "Design and implement REST APIs for frontend integration",
                "Write clean, testable and efficient code",
                "Collaborate with frontend developers and designers",
                "Participate in code reviews and sprint planning"
            ]
        },
        {
            "title"          : "Frontend Developer",
            "company"        : "WebSolutions Pvt Ltd",
            "location"       : "Hyderabad, India",
            "salary"         : "5-8 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Onsite",
            "experience"     : "1-3 years",
            "education"      : "B.E / B.Tech or BCA",
            "skills"         : ["HTML", "CSS", "JavaScript", "React", "Bootstrap", "Git"],
            "responsibilities": [
                "Build responsive and accessible web interfaces",
                "Convert UI/UX designs into working code",
                "Optimize web pages for performance and speed",
                "Work with backend developers on API integration",
                "Fix cross-browser compatibility issues"
            ]
        },
        {
            "title"          : "Data Scientist",
            "company"        : "Analytics Hub",
            "location"       : "Pune, India",
            "salary"         : "10-15 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Hybrid",
            "experience"     : "3-5 years",
            "education"      : "M.Tech / M.Sc in Data Science or Statistics",
            "skills"         : ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn", "Tableau"],
            "responsibilities": [
                "Build and evaluate machine learning models",
                "Analyze large datasets to find patterns and insights",
                "Create dashboards and data visualizations",
                "Present findings to business stakeholders",
                "Collaborate with engineers to deploy models"
            ]
        },
        {
            "title"          : "Cybersecurity Analyst",
            "company"        : "SecureNet Ltd",
            "location"       : "Chennai, India",
            "salary"         : "8-12 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Onsite",
            "experience"     : "2-4 years",
            "education"      : "B.Tech in IT / Cybersecurity certification",
            "skills"         : ["Network Security", "Penetration Testing", "SIEM", "Firewalls", "Python", "Linux"],
            "responsibilities": [
                "Monitor systems for security threats and vulnerabilities",
                "Conduct penetration testing and risk assessments",
                "Respond to security incidents and breaches",
                "Implement security policies and procedures",
                "Train staff on cybersecurity best practices"
            ]
        },
        {
            "title"          : "DevOps Engineer",
            "company"        : "CloudBase Technologies",
            "location"       : "Bangalore, India",
            "salary"         : "12-18 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Remote",
            "experience"     : "3-6 years",
            "education"      : "B.Tech in Computer Science or IT",
            "skills"         : ["Docker", "Kubernetes", "AWS", "CI/CD", "Jenkins", "Linux", "Terraform"],
            "responsibilities": [
                "Build and maintain CI/CD pipelines",
                "Manage cloud infrastructure on AWS or Azure",
                "Automate deployment and monitoring processes",
                "Ensure system reliability and uptime",
                "Collaborate with development teams on releases"
            ]
        },
        {
            "title"          : "Android Developer",
            "company"        : "AppStudio India",
            "location"       : "Delhi, India",
            "salary"         : "6-11 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Hybrid",
            "experience"     : "2-4 years",
            "education"      : "B.Tech / BCA in Computer Science",
            "skills"         : ["Java", "Kotlin", "Android SDK", "Firebase", "REST APIs", "Git"],
            "responsibilities": [
                "Design and build Android mobile applications",
                "Integrate REST APIs and third-party libraries",
                "Ensure app performance and quality",
                "Fix bugs and improve application performance",
                "Publish and maintain apps on Google Play Store"
            ]
        },
        {
            "title"          : "Machine Learning Engineer",
            "company"        : "AI Innovations Pvt Ltd",
            "location"       : "Bangalore, India",
            "salary"         : "14-20 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Remote",
            "experience"     : "3-5 years",
            "education"      : "M.Tech in AI/ML or Computer Science",
            "skills"         : ["Python", "TensorFlow", "PyTorch", "NLP", "Deep Learning", "MLOps"],
            "responsibilities": [
                "Design and train deep learning models",
                "Deploy ML models into production environments",
                "Optimize model performance and accuracy",
                "Research and implement latest ML techniques",
                "Work with data engineers on pipeline development"
            ]
        },
        {
            "title"          : "Database Administrator",
            "company"        : "DataSafe Corp",
            "location"       : "Mumbai, India",
            "salary"         : "7-12 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Onsite",
            "experience"     : "3-5 years",
            "education"      : "B.Tech in Computer Science or IT",
            "skills"         : ["MySQL", "PostgreSQL", "Oracle", "MongoDB", "SQL", "Backup & Recovery"],
            "responsibilities": [
                "Install, configure and maintain database systems",
                "Monitor database performance and optimize queries",
                "Implement data backup and recovery procedures",
                "Manage database security and access controls",
                "Troubleshoot database issues and outages"
            ]
        },
        {
            "title"          : "UI/UX Designer",
            "company"        : "DesignFirst Agency",
            "location"       : "Hyderabad, India",
            "salary"         : "5-9 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Hybrid",
            "experience"     : "2-4 years",
            "education"      : "B.Des or B.Tech with design portfolio",
            "skills"         : ["Figma", "Adobe XD", "Sketch", "Wireframing", "Prototyping", "User Research"],
            "responsibilities": [
                "Design intuitive user interfaces for web and mobile",
                "Create wireframes, prototypes and mockups",
                "Conduct user research and usability testing",
                "Collaborate with developers for implementation",
                "Maintain and improve design systems"
            ]
        },
        {
            "title"          : "Full Stack Developer",
            "company"        : "StartupNest",
            "location"       : "Remote",
            "salary"         : "9-15 LPA",
            "category"       : "IT / Software",
            "work_type"      : "Remote",
            "experience"     : "3-5 years",
            "education"      : "B.Tech in Computer Science",
            "skills"         : ["React", "Node.js", "Python", "MongoDB", "REST APIs", "AWS", "Git"],
            "responsibilities": [
                "Build end-to-end web applications",
                "Develop frontend with React and backend with Node.js",
                "Design and manage databases",
                "Deploy applications on cloud platforms",
                "Write unit tests and documentation"
            ]
        },

        # ── MARKETING ──────────────────────────────────────────
        {
            "title"          : "Digital Marketing Manager",
            "company"        : "BrandBoost Agency",
            "location"       : "Mumbai, India",
            "salary"         : "5-9 LPA",
            "category"       : "Marketing",
            "work_type"      : "Hybrid",
            "experience"     : "3-5 years",
            "education"      : "MBA in Marketing or BBA",
            "skills"         : ["SEO", "SEM", "Google Ads", "Social Media", "Analytics", "Content Strategy"],
            "responsibilities": [
                "Plan and execute digital marketing campaigns",
                "Manage SEO and SEM strategies",
                "Analyze campaign performance using Google Analytics",
                "Oversee social media presence and engagement",
                "Coordinate with content and design teams"
            ]
        },
        {
            "title"          : "Content Writer",
            "company"        : "Creative Minds",
            "location"       : "Remote",
            "salary"         : "3-5 LPA",
            "category"       : "Marketing",
            "work_type"      : "Remote",
            "experience"     : "1-2 years",
            "education"      : "BA in English / Mass Communication",
            "skills"         : ["Content Writing", "SEO Writing", "Blogging", "Copywriting", "Research", "WordPress"],
            "responsibilities": [
                "Write engaging blog posts and articles",
                "Create SEO optimized content for websites",
                "Write social media posts and captions",
                "Edit and proofread content before publishing",
                "Research industry topics and trends"
            ]
        },
        {
            "title"          : "Social Media Executive",
            "company"        : "GrowthHack Media",
            "location"       : "Delhi, India",
            "salary"         : "3-6 LPA",
            "category"       : "Marketing",
            "work_type"      : "Onsite",
            "experience"     : "1-3 years",
            "education"      : "BBA / BA in Mass Communication",
            "skills"         : ["Instagram", "LinkedIn", "Twitter", "Canva", "Content Calendar", "Analytics"],
            "responsibilities": [
                "Manage social media accounts for multiple brands",
                "Create and schedule daily content posts",
                "Engage with followers and respond to comments",
                "Track social media performance metrics",
                "Run paid social media campaigns"
            ]
        },
        {
            "title"          : "Brand Manager",
            "company"        : "ConsumerFirst Brands",
            "location"       : "Mumbai, India",
            "salary"         : "8-14 LPA",
            "category"       : "Marketing",
            "work_type"      : "Onsite",
            "experience"     : "4-7 years",
            "education"      : "MBA in Marketing",
            "skills"         : ["Brand Strategy", "Market Research", "Campaign Management", "P&L Management", "Leadership"],
            "responsibilities": [
                "Define and execute brand strategy",
                "Manage brand identity across all channels",
                "Conduct market research and competitor analysis",
                "Plan and oversee marketing campaigns",
                "Monitor brand health and consumer perception"
            ]
        },
        {
            "title"          : "Email Marketing Specialist",
            "company"        : "LeadGen Solutions",
            "location"       : "Bangalore, India",
            "salary"         : "4-7 LPA",
            "category"       : "Marketing",
            "work_type"      : "Remote",
            "experience"     : "2-4 years",
            "education"      : "BBA / MBA in Marketing",
            "skills"         : ["Mailchimp", "HubSpot", "Email Copywriting", "A/B Testing", "Segmentation", "Analytics"],
            "responsibilities": [
                "Design and send email marketing campaigns",
                "Segment email lists for targeted campaigns",
                "Write compelling email copy and subject lines",
                "Analyze open rates, click rates and conversions",
                "Run A/B tests to improve campaign performance"
            ]
        },

        # ── FINANCE ────────────────────────────────────────────
        {
            "title"          : "Financial Analyst",
            "company"        : "MoneyWise Corp",
            "location"       : "Mumbai, India",
            "salary"         : "7-12 LPA",
            "category"       : "Finance",
            "work_type"      : "Onsite",
            "experience"     : "2-4 years",
            "education"      : "B.Com / MBA in Finance / CA",
            "skills"         : ["Financial Modeling", "Excel", "Power BI", "Forecasting", "Budgeting", "SAP"],
            "responsibilities": [
                "Analyze financial statements and reports",
                "Prepare financial models and forecasts",
                "Support budgeting and planning processes",
                "Present financial insights to management",
                "Monitor key financial performance indicators"
            ]
        },
        {
            "title"          : "Chartered Accountant",
            "company"        : "Deloitte India",
            "location"       : "Bangalore, India",
            "salary"         : "10-18 LPA",
            "category"       : "Finance",
            "work_type"      : "Hybrid",
            "experience"     : "3-6 years",
            "education"      : "CA qualification from ICAI",
            "skills"         : ["Auditing", "Tax Planning", "Financial Reporting", "Tally", "GST", "IFRS"],
            "responsibilities": [
                "Conduct statutory and internal audits",
                "Prepare and file tax returns",
                "Ensure compliance with financial regulations",
                "Advise clients on tax planning strategies",
                "Review financial statements for accuracy"
            ]
        },
        {
            "title"          : "Investment Banker",
            "company"        : "Capital First",
            "location"       : "Mumbai, India",
            "salary"         : "15-25 LPA",
            "category"       : "Finance",
            "work_type"      : "Onsite",
            "experience"     : "4-8 years",
            "education"      : "MBA in Finance from top institute / CA",
            "skills"         : ["Valuation", "Financial Modeling", "M&A", "Due Diligence", "Excel", "Pitchbooks"],
            "responsibilities": [
                "Advise clients on mergers and acquisitions",
                "Prepare financial models and valuation reports",
                "Conduct due diligence for deals",
                "Pitch investment opportunities to clients",
                "Manage relationships with institutional investors"
            ]
        },
        {
            "title"          : "Risk Analyst",
            "company"        : "SafeGuard Finance",
            "location"       : "Hyderabad, India",
            "salary"         : "6-10 LPA",
            "category"       : "Finance",
            "work_type"      : "Hybrid",
            "experience"     : "2-4 years",
            "education"      : "MBA Finance / B.Com with FRM certification",
            "skills"         : ["Risk Assessment", "Excel", "Statistical Analysis", "Basel III", "Python", "Reporting"],
            "responsibilities": [
                "Identify and assess financial and operational risks",
                "Develop risk mitigation strategies",
                "Prepare risk reports for senior management",
                "Monitor market and credit risk indicators",
                "Ensure compliance with regulatory requirements"
            ]
        },
        {
            "title"          : "Accounts Manager",
            "company"        : "RetailChain India",
            "location"       : "Chennai, India",
            "salary"         : "5-8 LPA",
            "category"       : "Finance",
            "work_type"      : "Onsite",
            "experience"     : "3-5 years",
            "education"      : "B.Com / M.Com / MBA Finance",
            "skills"         : ["Tally", "GST Filing", "Accounts Payable", "Accounts Receivable", "MIS Reports", "Excel"],
            "responsibilities": [
                "Manage day-to-day accounting operations",
                "Prepare monthly MIS reports",
                "Handle GST filing and compliance",
                "Oversee accounts payable and receivable",
                "Coordinate with auditors during audit season"
            ]
        },

        # ── HEALTHCARE ─────────────────────────────────────────
        {
            "title"          : "Clinical Data Analyst",
            "company"        : "HealthTech Solutions",
            "location"       : "Hyderabad, India",
            "salary"         : "6-10 LPA",
            "category"       : "Healthcare",
            "work_type"      : "Hybrid",
            "experience"     : "2-4 years",
            "education"      : "B.Pharm / M.Sc Life Sciences / Bioinformatics",
            "skills"         : ["Clinical Trials", "SAS", "R", "Data Management", "CDISC", "Excel"],
            "responsibilities": [
                "Analyze clinical trial data for accuracy",
                "Prepare data analysis reports for research teams",
                "Ensure compliance with clinical data standards",
                "Support regulatory submissions with data",
                "Work with statisticians on study outcomes"
            ]
        },
        {
            "title"          : "Hospital Administrator",
            "company"        : "Apollo Hospitals",
            "location"       : "Chennai, India",
            "salary"         : "5-8 LPA",
            "category"       : "Healthcare",
            "work_type"      : "Onsite",
            "experience"     : "3-6 years",
            "education"      : "MBA in Hospital Administration / MHA",
            "skills"         : ["Hospital Management", "Patient Services", "Staff Coordination", "Budgeting", "Compliance"],
            "responsibilities": [
                "Oversee daily hospital operations",
                "Manage staff schedules and performance",
                "Ensure patient satisfaction and safety standards",
                "Handle hospital budgeting and procurement",
                "Liaise with doctors, nurses and support staff"
            ]
        },
        {
            "title"          : "Medical Coder",
            "company"        : "MedBill India",
            "location"       : "Remote",
            "salary"         : "3-6 LPA",
            "category"       : "Healthcare",
            "work_type"      : "Remote",
            "experience"     : "1-3 years",
            "education"      : "B.Sc / Diploma with CPC certification",
            "skills"         : ["ICD-10", "CPT Coding", "Medical Billing", "HIPAA", "EHR Systems", "Attention to Detail"],
            "responsibilities": [
                "Assign correct medical codes to diagnoses",
                "Review patient records for accurate coding",
                "Ensure compliance with HIPAA regulations",
                "Communicate with insurance companies",
                "Submit and follow up on medical claims"
            ]
        },
        {
            "title"          : "Healthcare IT Specialist",
            "company"        : "MedTech Systems",
            "location"       : "Bangalore, India",
            "salary"         : "7-12 LPA",
            "category"       : "Healthcare",
            "work_type"      : "Hybrid",
            "experience"     : "3-5 years",
            "education"      : "B.Tech in IT / Computer Science",
            "skills"         : ["EHR Systems", "HL7", "FHIR", "Database Management", "Python", "Healthcare Compliance"],
            "responsibilities": [
                "Implement and maintain electronic health record systems",
                "Ensure interoperability between healthcare systems",
                "Train hospital staff on IT systems",
                "Maintain data security and patient privacy",
                "Troubleshoot technical issues in clinical systems"
            ]
        },
        {
            "title"          : "Pharmacovigilance Analyst",
            "company"        : "PharmaSafe India",
            "location"       : "Mumbai, India",
            "salary"         : "5-9 LPA",
            "category"       : "Healthcare",
            "work_type"      : "Hybrid",
            "experience"     : "2-4 years",
            "education"      : "B.Pharm / M.Pharm / MBBS",
            "skills"         : ["Adverse Event Reporting", "MedDRA", "Oracle Argus", "Regulatory Writing", "ICH Guidelines"],
            "responsibilities": [
                "Monitor and report adverse drug reactions",
                "Prepare safety reports for regulatory submissions",
                "Review medical literature for safety signals",
                "Ensure compliance with ICH and WHO guidelines",
                "Coordinate with global pharmacovigilance teams"
            ]
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
