# =========================================================
# CARELINE TELEMEDICINE SYSTEM
# Authentication Routes
# =========================================================

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection


auth_bp = Blueprint("auth", __name__)


# =========================================================
# REGISTER PATIENT
# =========================================================

@auth_bp.route("/register/patient", methods=["POST"])
def register_patient():

    data = request.get_json() or {}

    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    password = data.get("password", "")

    date_of_birth = data.get("date_of_birth")
    gender = data.get("gender")
    address = data.get("address", "").strip()
    blood_group = data.get("blood_group")
    emergency_contact = data.get("emergency_contact", "").strip()

    if not full_name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Name, email and password are required."
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        # Check whether email already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

        hashed_password = generate_password_hash(password)

        # Create user
        cursor.execute(
            """
            INSERT INTO users
            (full_name, email, phone, password, role, status)
            VALUES (%s, %s, %s, %s, 'patient', 'active')
            """,
            (
                full_name,
                email,
                phone,
                hashed_password
            )
        )

        user_id = cursor.lastrowid

        # Create patient profile
        cursor.execute(
            """
            INSERT INTO patients
            (
                user_id,
                date_of_birth,
                gender,
                address,
                blood_group,
                emergency_contact
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                date_of_birth,
                gender,
                address,
                blood_group,
                emergency_contact
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Patient registered successfully."
        }), 201

    except Exception as error:

        connection.rollback()

        print("Patient registration error:", error)

        return jsonify({
            "success": False,
            "message": "Registration failed."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# DOCTOR REGISTRATION
# =========================================================

@auth_bp.route("/register/doctor", methods=["POST"])
def register_doctor():

    data = request.get_json() or {}

    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone", "").strip()
    password = data.get("password", "")

    specialization = data.get("specialization", "").strip()
    qualification = data.get("qualification", "").strip()
    experience = data.get("experience", 0)
    license_number = data.get("license_number", "").strip()
    consultation_fee = data.get("consultation_fee", 0)
    about = data.get("about", "").strip()

    if not full_name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Name, email and password are required."
        }), 400

    if not specialization:
        return jsonify({
            "success": False,
            "message": "Specialization is required."
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        # Check email
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({
                "success": False,
                "message": "Email already registered."
            }), 409

        hashed_password = generate_password_hash(password)

        # Create doctor user
        cursor.execute(
            """
            INSERT INTO users
            (full_name, email, phone, password, role, status)
            VALUES (%s, %s, %s, %s, 'doctor', 'pending')
            """,
            (
                full_name,
                email,
                phone,
                hashed_password
            )
        )

        user_id = cursor.lastrowid

        # Create doctor profile
        cursor.execute(
            """
            INSERT INTO doctors
            (
                user_id,
                specialization,
                qualification,
                experience,
                license_number,
                consultation_fee,
                about
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                specialization,
                qualification,
                experience,
                license_number,
                consultation_fee,
                about
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Doctor registration submitted for admin approval."
        }), 201

    except Exception as error:

        connection.rollback()

        print("Doctor registration error:", error)

        return jsonify({
            "success": False,
            "message": "Doctor registration failed."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                full_name,
                email,
                phone,
                password,
                role,
                status
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        # Doctor must be approved
        if user["role"] == "doctor" and user["status"] != "active":

            if user["status"] == "pending":
                message = "Your doctor account is waiting for admin approval."

            elif user["status"] == "rejected":
                message = "Your doctor registration was rejected by admin."

            else:
                message = "Your doctor account is inactive."

            return jsonify({
                "success": False,
                "message": message
            }), 403

        if user["status"] != "active":
            return jsonify({
                "success": False,
                "message": "Your account is inactive."
            }), 403

        if not check_password_hash(
            user["password"],
            password
        ):
            return jsonify({
                "success": False,
                "message": "Invalid email or password."
            }), 401

        # Don't send password to frontend
        user.pop("password", None)

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "user": user
        }), 200

    except Exception as error:

        print("Login error:", error)

        return jsonify({
            "success": False,
            "message": "Login failed."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# FORGOT PASSWORD
# =========================================================

@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():

    data = request.get_json() or {}

    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        # Don't reveal whether an email exists
        if not user:
            return jsonify({
                "success": True,
                "message": "If the email exists, password reset instructions can be sent."
            }), 200

        return jsonify({
            "success": True,
            "message": "Password reset request received."
        }), 200

    except Exception as error:

        print("Forgot password error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to process request."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()