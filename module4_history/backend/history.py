# ─── MODULE 4: HISTORY MODULE - BACKEND ─────────────────────────
# Handles: View History, Clear History, Report Fake Job

from flask import Blueprint, render_template, request, redirect, url_for, session
import json

# Blueprint pointing to module4 frontend folder
history_bp = Blueprint(
    'history',
    __name__,
    template_folder='../frontend'
)

HISTORY_FILE = "history.json"
REPORTS_FILE = "reports.json"


# ─── HELPER FUNCTIONS ───────────────────────────────────────────
def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return []

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


# ─── ROUTES ─────────────────────────────────────────────────────

@history_bp.route('/history')
def history():
    if 'user_email' not in session:
        return redirect(url_for('auth.login'))

    history      = load_json(HISTORY_FILE)
    user_history = [h for h in history if h['user'] == session['user_email']]
    avg_confidence = round(
        sum(h['confidence'] for h in user_history) / len(user_history), 2
    ) if user_history else 0

    return render_template('history.html',
                           history=history,
                           current_user=session['user_email'],
                           username=session['username'],
                           avg_confidence=avg_confidence)


@history_bp.route('/clear_history')
def clear_history():
    if 'user_email' not in session:
        return redirect(url_for('auth.login'))

    history = load_json(HISTORY_FILE)
    history = [h for h in history if h['user'] != session['user_email']]
    save_json(HISTORY_FILE, history)
    return redirect(url_for('history.history'))


@history_bp.route('/report', methods=['GET', 'POST'])
def report():
    if 'user_email' not in session:
        return redirect(url_for('auth.login'))

    reports = load_json(REPORTS_FILE)

    if request.method == 'POST':
        job_title = request.form.get('job_title', '').strip()
        company   = request.form.get('company', '').strip()
        url       = request.form.get('url', '').strip()
        reason    = request.form.get('reason', '').strip()
        details   = request.form.get('details', '').strip()

        if not job_title or not company or not reason:
            return render_template('report.html',
                                   error="Please fill all required fields.",
                                   reports=reports,
                                   username=session['username'])

        reports.append({
            "job_title"  : job_title,
            "company"    : company,
            "url"        : url,
            "reason"     : reason,
            "details"    : details,
            "reported_by": session['user_email']
        })
        save_json(REPORTS_FILE, reports)

        return render_template('report.html',
                               success="Report submitted! Thank you.",
                               reports=reports,
                               username=session['username'])

    return render_template('report.html',
                           reports=reports,
                           username=session['username'])