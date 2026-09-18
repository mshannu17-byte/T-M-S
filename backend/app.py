# =========================================================
# CARELINE TELEMEDICINE SYSTEM
# Main Flask Application
# =========================================================

import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from routes.auth import auth_bp
from routes.patient import patient_bp
from routes.doctor import doctor_bp
from routes.admin import admin_bp


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)


# ---------------------------------------------------------
# Create Flask application
# ---------------------------------------------------------

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

CORS(app)


# ---------------------------------------------------------
# Application settings
# ---------------------------------------------------------

app.config["JSON_SORT_KEYS"] = False


# ---------------------------------------------------------
# Register API routes
# ---------------------------------------------------------

app.register_blueprint(
    auth_bp,
    url_prefix="/api/auth"
)

app.register_blueprint(
    patient_bp,
    url_prefix="/api/patient"
)

app.register_blueprint(
    doctor_bp,
    url_prefix="/api/doctor"
)

app.register_blueprint(
    admin_bp,
    url_prefix="/api/admin"
)


# ---------------------------------------------------------
# Home page
# ---------------------------------------------------------

@app.route("/")
def home():
    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.route("/api/health")
def health_check():
    return jsonify({
        "success": True,
        "message": "CareLine Telemedicine System is running",
        "status": "online"
    })


# ---------------------------------------------------------
# Error handlers
# ---------------------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "success": False,
        "message": "The requested page or API endpoint was not found."
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "message": "An internal server error occurred."
    }), 500


# ---------------------------------------------------------
# Run application
# ---------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )