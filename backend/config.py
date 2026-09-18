# =========================================================
# CARELINE TELEMEDICINE SYSTEM
# Database Configuration
# =========================================================

import os


# MySQL database settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "careline123")
DB_NAME = os.getenv("DB_NAME", "careline_db")
DB_PORT = int(os.getenv("DB_PORT", "3306"))


# Flask application settings
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "careline-development-secret-key"
)


# Application settings
APP_NAME = "CareLine Telemedicine System"
APP_VERSION = "1.0.0"