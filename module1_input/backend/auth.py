# ─── MODULE 1: INPUT MODULE - BACKEND ───────────────────────────
# Handles: Landing, Login, Signup, Dashboard, Logout

from flask import Blueprint, render_template, request, redirect, url_for, session
import json
import os
import hashlib

# Blueprint with frontend folder as template folder
auth_bp = Blueprint(
    'auth',
    __name__,
    template_folder='../frontend',
    static_folder='../static'
)

USERS_FILE = "users.json"


# ─── HELPER FUNCTIONS ───────────────────────────────────────────
# ─── HELPER FUNCTIONS ───────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "..", "..", "users.json")


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─── ROUTES ─────────────────────────────────────────────────────

@auth_bp.route('/')
def landing():
    return render_template('landing.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        users    = load_users()

        if email not in users:
            return render_template('login.html',
                                   error="No account found with this email.")

        if users[email]['password'] != hash_password(password):
            return render_template('login.html',
                                   error="Incorrect password.")

        session['user_email'] = email
        session['username']   = users[email]['name']
        return redirect(url_for('auth.dashboard'))

    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm  = request.form.get('confirm_password', '').strip()

        if not name or not email or not password:
            return render_template('signup.html',
                                   error="All fields are required.")

        if password != confirm:
            return render_template('signup.html',
                                   error="Passwords do not match.")

        if len(password) < 6:
            return render_template('signup.html',
                                   error="Password must be at least 6 characters.")

        users = load_users()

        if email in users:
            return render_template('signup.html',
                                   error="This email is already registered.")

        users[email] = {
            "name"    : name,
            "password": hash_password(password)
        }
        save_users(users)
        return render_template('login.html',
                               success="Account created! Please login.")

    return render_template('signup.html')

@auth_bp.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html',
                           username=session['username'])

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.landing'))
