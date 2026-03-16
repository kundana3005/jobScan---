# ─── MAIN APP ───────────────────────────────────────────────────
# This file connects all 4 modules together using Flask Blueprints

from flask import Flask

# Import all module blueprints
from module1_input.backend.auth                  import auth_bp
from module2_preprocessing.backend.preprocessing import preprocessing_bp
from module3_prediction.backend.prediction       import prediction_bp
from module4_history.backend.history             import history_bp

# Create Flask app
# static_folder points to module1_input/static so CSS loads correctly
app = Flask(__name__, static_folder='module1_input/static')
app.secret_key = "jobscan_secret_key_2024"

# Register all module blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(preprocessing_bp)
app.register_blueprint(prediction_bp)
app.register_blueprint(history_bp)

# Run app
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
