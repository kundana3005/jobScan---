# ─── MODULE 2: PREPROCESSING MODULE - BACKEND ───────────────────
# Handles: Scan Job form, Search Jobs, Text Preprocessing

from flask import Blueprint, render_template, request, redirect, url_for, session
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)

# Blueprint pointing to module2 frontend folder
preprocessing_bp = Blueprint(
    'preprocessing',
    __name__,
    template_folder='../frontend'
)

stop_words = set(stopwords.words('english'))


# ─── TEXT PREPROCESSING FUNCTION ────────────────────────────────

def preprocess(text):
    """
    Clean raw text:
    1. Lowercase
    2. Remove symbols
    3. Remove stopwords
    """
    text  = text.lower()
    text  = re.sub(r'[^a-z\s]', '', text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return ' '.join(words)


# ─── ROUTES ─────────────────────────────────────────────────────

@preprocessing_bp.route('/scan')
def scan():
    if 'user_email' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html')


@preprocessing_bp.route('/search')
def search():
    if 'user_email' not in session:
        return redirect(url_for('auth.login'))

    jobs = [
        # ── IT / SOFTWARE ──
        {
            "title"           : "Python Developer",
            "company"         : "TechCorp India",
            "location"        : "Bangalore, India",
            "salary"          : "6-10 LPA",
            "category"        : "IT / Software",
            "work_type"       : "Hybrid",
            "experience"      : "2-4 years",
            "education"       : "B.E / B.Tech in Computer Science",
            "skills"          : ["Python", "Flask", "Django", "REST APIs", "MySQL", "Git"],
            "responsibilities": [
                "Develop and maintain Python-based web applications",
                "Design and implement REST APIs for frontend integration",
                "Write clean, testable and efficient code",
                "Collaborate with frontend developers and designers",
                "Participate in code reviews and sprint planning"
            ]
        },
        {
            "title"           : "Frontend Developer",
            "company"         : "WebSolutions Pvt Ltd",
            "location"        : "Hyderabad, India",
            "salary"          : "5-8 LPA",
            "category"        : "IT / Software",
            "work_type"       : "Onsite",
            "experience"      : "1-3 years",
            "education"       : "B.E / B.Tech or BCA",
            "skills"          : ["HTML", "CSS", "JavaScript", "React", "Bootstrap", "Git"],
            "responsibilities": [
                "Build responsive and accessible web interfaces",
                "Convert UI/UX designs into working code",
                "Optimize web pages for performance and speed",
                "Work with backend developers on API integration",
                "Fix cross-browser compatibility issues"
            ]
        },
        {
            "title"           : "Data Scientist",
            "company"         : "Analytics Hub",
            "location"        : "Pune, India",
            "salary"          : "10-15 LPA",
            "category"        : "IT / Software",
            "work_type"       : "Hybrid",
            "experience"      : "3-5 years",
            "education"       : "M.Tech / M.Sc in Data Science",
            "skills"          : ["Python", "Machine Learning", "Pandas", "NumPy", "Scikit-learn", "Tableau"],
            "responsibilities": [
                "Build and evaluate machine learning models",
                "Analyze large datasets to find patterns",
                "Create dashboards and data visualizations",
                "Present findings to business stakeholders",
                "Collaborate with engineers to deploy models"
            ]
        },
        {
            "title"           : "DevOps Engineer",
            "company"         : "CloudBase Technologies",
            "location"        : "Bangalore, India",
            "salary"          : "12-18 LPA",
            "category"        : "IT / Software",
            "work_type"       : "Remote",
            "experience"      : "3-6 years",
            "education"       : "B.Tech in Computer Science or IT",
            "skills"          : ["Docker", "Kubernetes", "AWS", "CI/CD", "Jenkins", "Linux"],
            "responsibilities": [
                "Build and maintain CI/CD pipelines",
                "Manage cloud infrastructure on AWS",
                "Automate deployment and monitoring processes",
                "Ensure system reliability and uptime",
                "Collaborate with development teams on releases"
            ]
        },
        {
            "title"           : "Android Developer",
            "company"         : "AppStudio India",
            "location"        : "Delhi, India",
            "salary"          : "6-11 LPA",
            "category"        : "IT / Software",
            "work_type"       : "Hybrid",
            "experience"      : "2-4 years",
            "education"       : "B.Tech / BCA in Computer Science",
            "skills"          : ["Java", "Kotlin", "Android SDK", "Firebase", "REST APIs", "Git"],
            "responsibilities": [
                "Design and build Android mobile applications",
                "Integrate REST APIs and third-party libraries",
                "Ensure app performance and quality",
                "Fix bugs and improve application performance",
                "Publish apps on Google Play Store"
            ]
        },
        {
            "title"           : "Machine Learning Engineer",
            "company"         : "AI Innovations Pvt Ltd",
            "location"        : "Bangalore, India",
            "salary"          : "14-20 LPA",
            "category"        : "IT / Software",
            "work_type"       : "Remote",
            "experience"      : "3-5 years",
            "education"       : "M.Tech in AI/ML or Computer Science",
            "skills"          : ["Python", "TensorFlow", "PyTorch", "NLP", "Deep Learning", "MLOps"],
            "responsibilities": [
                "Design and train deep learning models",
                "Deploy ML models into production",
                "Optimize model performance and accuracy",
                "Research latest ML techniques",
                "Work with data engineers on pipelines"
            ]
        },
        {
            "title"           : "Full Stack Developer",
            "company"         : "StartupNest",
            "location"        : "Remote",
            "salary"          : "9-15 LPA",
            "category"        : "IT / Software",
            "work_type"       : "Remote",
            "experience"      : "3-5 years",
            "education"       : "B.Tech in Computer Science",
            "skills"          : ["React", "Node.js", "Python", "MongoDB", "REST APIs", "AWS"],
            "responsibilities": [
                "Build end-to-end web applications",
                "Develop frontend with React and backend with Node.js",
                "Design and manage databases",
                "Deploy applications on cloud platforms",
                "Write unit tests and documentation"
            ]
        },
        {
            "title"           : "UI/UX Designer",
            "company"         : "DesignFirst Agency",
            "location"        : "Hyderabad, India",
            "salary"          : "5-9 LPA",
            "category"        : "IT / Software",
            "work_type"       : "Hybrid",
            "experience"      : "2-4 years",
            "education"       : "B.Des or B.Tech with design portfolio",
            "skills"          : ["Figma", "Adobe XD", "Sketch", "Wireframing", "Prototyping", "User Research"],
            "responsibilities": [
                "Design intuitive user interfaces",
                "Create wireframes, prototypes and mockups",
                "Conduct user research and usability testing",
                "Collaborate with developers for implementation",
                "Maintain and improve design systems"
            ]
        },
        # ── MARKETING ──
        {
            "title"           : "Digital Marketing Manager",
            "company"         : "BrandBoost Agency",
            "location"        : "Mumbai, India",
            "salary"          : "5-9 LPA",
            "category"        : "Marketing",
            "work_type"       : "Hybrid",
            "experience"      : "3-5 years",
            "education"       : "MBA in Marketing or BBA",
            "skills"          : ["SEO", "SEM", "Google Ads", "Social Media", "Analytics", "Content Strategy"],
            "responsibilities": [
                "Plan and execute digital marketing campaigns",
                "Manage SEO and SEM strategies",
                "Analyze campaign performance using Google Analytics",
                "Oversee social media presence",
                "Coordinate with content and design teams"
            ]
        },
        {
            "title"           : "Content Writer",
            "company"         : "Creative Minds",
            "location"        : "Remote",
            "salary"          : "3-5 LPA",
            "category"        : "Marketing",
            "work_type"       : "Remote",
            "experience"      : "1-2 years",
            "education"       : "BA in English / Mass Communication",
            "skills"          : ["Content Writing", "SEO Writing", "Blogging", "Copywriting", "WordPress"],
            "responsibilities": [
                "Write engaging blog posts and articles",
                "Create SEO optimized content",
                "Write social media posts and captions",
                "Edit and proofread content",
                "Research industry topics and trends"
            ]
        },
        {
            "title"           : "Brand Manager",
            "company"         : "ConsumerFirst Brands",
            "location"        : "Mumbai, India",
            "salary"          : "8-14 LPA",
            "category"        : "Marketing",
            "work_type"       : "Onsite",
            "experience"      : "4-7 years",
            "education"       : "MBA in Marketing",
            "skills"          : ["Brand Strategy", "Market Research", "Campaign Management", "Leadership"],
            "responsibilities": [
                "Define and execute brand strategy",
                "Manage brand identity across all channels",
                "Conduct market research and competitor analysis",
                "Plan and oversee marketing campaigns",
                "Monitor brand health and consumer perception"
            ]
        },
        {
            "title"           : "Email Marketing Specialist",
            "company"         : "LeadGen Solutions",
            "location"        : "Bangalore, India",
            "salary"          : "4-7 LPA",
            "category"        : "Marketing",
            "work_type"       : "Remote",
            "experience"      : "2-4 years",
            "education"       : "BBA / MBA in Marketing",
            "skills"          : ["Mailchimp", "HubSpot", "Email Copywriting", "A/B Testing", "Analytics"],
            "responsibilities": [
                "Design and send email marketing campaigns",
                "Segment email lists for targeted campaigns",
                "Write compelling email copy",
                "Analyze open rates and conversions",
                "Run A/B tests to improve performance"
            ]
        },
        # ── FINANCE ──
        {
            "title"           : "Financial Analyst",
            "company"         : "MoneyWise Corp",
            "location"        : "Mumbai, India",
            "salary"          : "7-12 LPA",
            "category"        : "Finance",
            "work_type"       : "Onsite",
            "experience"      : "2-4 years",
            "education"       : "B.Com / MBA in Finance / CA",
            "skills"          : ["Financial Modeling", "Excel", "Power BI", "Forecasting", "SAP"],
            "responsibilities": [
                "Analyze financial statements and reports",
                "Prepare financial models and forecasts",
                "Support budgeting and planning processes",
                "Present financial insights to management",
                "Monitor key financial performance indicators"
            ]
        },
        {
            "title"           : "Chartered Accountant",
            "company"         : "Deloitte India",
            "location"        : "Bangalore, India",
            "salary"          : "10-18 LPA",
            "category"        : "Finance",
            "work_type"       : "Hybrid",
            "experience"      : "3-6 years",
            "education"       : "CA qualification from ICAI",
            "skills"          : ["Auditing", "Tax Planning", "Financial Reporting", "Tally", "GST"],
            "responsibilities": [
                "Conduct statutory and internal audits",
                "Prepare and file tax returns",
                "Ensure compliance with financial regulations",
                "Advise clients on tax planning",
                "Review financial statements for accuracy"
            ]
        },
        {
            "title"           : "Risk Analyst",
            "company"         : "SafeGuard Finance",
            "location"        : "Hyderabad, India",
            "salary"          : "6-10 LPA",
            "category"        : "Finance",
            "work_type"       : "Hybrid",
            "experience"      : "2-4 years",
            "education"       : "MBA Finance / FRM certification",
            "skills"          : ["Risk Assessment", "Excel", "Statistical Analysis", "Python", "Reporting"],
            "responsibilities": [
                "Identify and assess financial risks",
                "Develop risk mitigation strategies",
                "Prepare risk reports for management",
                "Monitor market and credit risk indicators",
                "Ensure regulatory compliance"
            ]
        },
        # ── HEALTHCARE ──
        {
            "title"           : "Clinical Data Analyst",
            "company"         : "HealthTech Solutions",
            "location"        : "Hyderabad, India",
            "salary"          : "6-10 LPA",
            "category"        : "Healthcare",
            "work_type"       : "Hybrid",
            "experience"      : "2-4 years",
            "education"       : "B.Pharm / M.Sc Life Sciences",
            "skills"          : ["Clinical Trials", "SAS", "R", "Data Management", "Excel"],
            "responsibilities": [
                "Analyze clinical trial data for accuracy",
                "Prepare data analysis reports",
                "Ensure compliance with clinical data standards",
                "Support regulatory submissions",
                "Work with statisticians on study outcomes"
            ]
        },
        {
            "title"           : "Hospital Administrator",
            "company"         : "Apollo Hospitals",
            "location"        : "Chennai, India",
            "salary"          : "5-8 LPA",
            "category"        : "Healthcare",
            "work_type"       : "Onsite",
            "experience"      : "3-6 years",
            "education"       : "MBA in Hospital Administration",
            "skills"          : ["Hospital Management", "Patient Services", "Staff Coordination", "Budgeting"],
            "responsibilities": [
                "Oversee daily hospital operations",
                "Manage staff schedules and performance",
                "Ensure patient satisfaction and safety",
                "Handle hospital budgeting and procurement",
                "Liaise with doctors nurses and support staff"
            ]
        },
        {
            "title"           : "Healthcare IT Specialist",
            "company"         : "MedTech Systems",
            "location"        : "Bangalore, India",
            "salary"          : "7-12 LPA",
            "category"        : "Healthcare",
            "work_type"       : "Hybrid",
            "experience"      : "3-5 years",
            "education"       : "B.Tech in IT / Computer Science",
            "skills"          : ["EHR Systems", "HL7", "FHIR", "Database Management", "Python"],
            "responsibilities": [
                "Implement and maintain electronic health record systems",
                "Ensure interoperability between healthcare systems",
                "Train hospital staff on IT systems",
                "Maintain data security and patient privacy",
                "Troubleshoot technical issues in clinical systems"
            ]
        },
        {
            "title"           : "Medical Coder",
            "company"         : "MedBill India",
            "location"        : "Remote",
            "salary"          : "3-6 LPA",
            "category"        : "Healthcare",
            "work_type"       : "Remote",
            "experience"      : "1-3 years",
            "education"       : "B.Sc / Diploma with CPC certification",
            "skills"          : ["ICD-10", "CPT Coding", "Medical Billing", "HIPAA", "EHR Systems"],
            "responsibilities": [
                "Assign correct medical codes to diagnoses",
                "Review patient records for accurate coding",
                "Ensure compliance with HIPAA regulations",
                "Communicate with insurance companies",
                "Submit and follow up on medical claims"
            ]
        },
    ]

    return render_template('search.html', jobs=jobs, username=session['username'])