# =========================================================
# CARELINE TELEMEDICINE SYSTEM
# Patient Routes
# =========================================================

from flask import Blueprint, request, jsonify

from database import get_db_connection


patient_bp = Blueprint("patient", __name__)


# =========================================================
# GET PATIENT PROFILE
# =========================================================

@patient_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):

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
                u.id AS user_id,
                u.full_name,
                u.email,
                u.phone,
                p.id AS patient_id,
                p.date_of_birth,
                p.gender,
                p.address,
                p.blood_group,
                p.emergency_contact
            FROM users u
            JOIN patients p
                ON u.id = p.user_id
            WHERE u.id = %s
              AND u.role = 'patient'
            """,
            (user_id,)
        )

        patient = cursor.fetchone()

        if not patient:
            return jsonify({
                "success": False,
                "message": "Patient not found."
            }), 404

        return jsonify({
            "success": True,
            "patient": patient
        }), 200

    except Exception as error:

        print("Profile error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load patient profile."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# UPDATE PATIENT PROFILE
# =========================================================

@patient_bp.route("/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):

    data = request.get_json() or {}

    full_name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()
    date_of_birth = data.get("date_of_birth")
    gender = data.get("gender", "").strip()
    address = data.get("address", "").strip()
    blood_group = data.get("blood_group", "").strip()
    emergency_contact = data.get("emergency_contact", "").strip()

    if not full_name:
        return jsonify({
            "success": False,
            "message": "Full name is required."
        }), 400

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET full_name = %s,
                phone = %s
            WHERE id = %s
              AND role = 'patient'
            """,
            (
                full_name,
                phone,
                user_id
            )
        )

        cursor.execute(
            """
            UPDATE patients
            SET date_of_birth = %s,
                gender = %s,
                address = %s,
                blood_group = %s,
                emergency_contact = %s
            WHERE user_id = %s
            """,
            (
                date_of_birth,
                gender,
                address,
                blood_group,
                emergency_contact,
                user_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Profile updated successfully."
        }), 200

    except Exception as error:

        connection.rollback()

        print("Update profile error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to update profile."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET ALL APPROVED DOCTORS
# =========================================================

@patient_bp.route("/doctors", methods=["GET"])
def get_doctors():

    specialization = request.args.get(
        "specialization",
        ""
    ).strip()

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        if specialization:

            cursor.execute(
                """
                SELECT
                    d.id AS doctor_id,
                    u.id AS user_id,
                    u.full_name,
                    u.email,
                    u.phone,
                    d.specialization,
                    d.qualification,
                    d.experience,
                    d.license_number,
                    d.consultation_fee,
                    d.about
                FROM doctors d
                JOIN users u
                    ON d.user_id = u.id
                WHERE u.role = 'doctor'
                  AND u.status = 'active'
                  AND d.specialization LIKE %s
                ORDER BY u.full_name
                """,
                (
                    f"%{specialization}%",
                )
            )

        else:

            cursor.execute(
                """
                SELECT
                    d.id AS doctor_id,
                    u.id AS user_id,
                    u.full_name,
                    u.email,
                    u.phone,
                    d.specialization,
                    d.qualification,
                    d.experience,
                    d.license_number,
                    d.consultation_fee,
                    d.about
                FROM doctors d
                JOIN users u
                    ON d.user_id = u.id
                WHERE u.role = 'doctor'
                  AND u.status = 'active'
                ORDER BY u.full_name
                """
            )

        doctors = cursor.fetchall()

        return jsonify({
            "success": True,
            "doctors": doctors
        }), 200

    except Exception as error:

        print("Doctors error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load doctors."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# BOOK APPOINTMENT
# =========================================================

@patient_bp.route("/appointments", methods=["POST"])
def book_appointment():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    doctor_id = data.get("doctor_id")
    appointment_date = data.get("appointment_date")
    appointment_time = data.get("appointment_time")
    reason = data.get("reason", "").strip()

    if not user_id or not doctor_id:
        return jsonify({
            "success": False,
            "message": "Patient and doctor are required."
        }), 400

    if not appointment_date or not appointment_time:
        return jsonify({
            "success": False,
            "message": "Appointment date and time are required."
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

        # Find patient
        cursor.execute(
            """
            SELECT id
            FROM patients
            WHERE user_id = %s
            """,
            (user_id,)
        )

        patient = cursor.fetchone()

        if not patient:
            return jsonify({
                "success": False,
                "message": "Patient profile not found."
            }), 404

        patient_id = patient["id"]

        # Check doctor
        cursor.execute(
            """
            SELECT d.id
            FROM doctors d
            JOIN users u
                ON d.user_id = u.id
            WHERE d.id = %s
              AND u.role = 'doctor'
              AND u.status = 'active'
            """,
            (doctor_id,)
        )

        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({
                "success": False,
                "message": "Doctor not found or not approved."
            }), 404

        # Prevent duplicate time booking
        cursor.execute(
            """
            SELECT id
            FROM appointments
            WHERE doctor_id = %s
              AND appointment_date = %s
              AND appointment_time = %s
              AND status IN ('pending', 'accepted')
            """,
            (
                doctor_id,
                appointment_date,
                appointment_time
            )
        )

        existing = cursor.fetchone()

        if existing:
            return jsonify({
                "success": False,
                "message": "This appointment time is already requested."
            }), 409

        cursor.execute(
            """
            INSERT INTO appointments
            (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                reason,
                status
            )
            VALUES (%s, %s, %s, %s, %s, 'pending')
            """,
            (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                reason
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Appointment request submitted successfully.",
            "appointment_id": cursor.lastrowid
        }), 201

    except Exception as error:

        connection.rollback()

        print("Appointment booking error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to book appointment."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET PATIENT APPOINTMENTS
# =========================================================

@patient_bp.route("/appointments/<int:user_id>", methods=["GET"])
def get_appointments(user_id):

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
                a.id,
                a.appointment_date,
                a.appointment_time,
                a.reason,
                a.status,
                a.meeting_link,
                a.created_at,

                d.id AS doctor_id,
                u.full_name AS doctor_name,
                d.specialization,
                d.qualification

            FROM appointments a

            JOIN patients p
                ON a.patient_id = p.id

            JOIN doctors d
                ON a.doctor_id = d.id

            JOIN users u
                ON d.user_id = u.id

            WHERE p.user_id = %s

            ORDER BY
                a.appointment_date DESC,
                a.appointment_time DESC
            """,
            (user_id,)
        )

        appointments = cursor.fetchall()

        return jsonify({
            "success": True,
            "appointments": appointments
        }), 200

    except Exception as error:

        print("Patient appointments error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load appointments."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# CANCEL APPOINTMENT
# =========================================================

@patient_bp.route("/appointments/<int:appointment_id>/cancel", methods=["PUT"])
def cancel_appointment(appointment_id):

    data = request.get_json() or {}

    user_id = data.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "User ID is required."
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
            SELECT a.id
            FROM appointments a
            JOIN patients p
                ON a.patient_id = p.id
            WHERE a.id = %s
              AND p.user_id = %s
              AND a.status IN ('pending', 'accepted')
            """,
            (
                appointment_id,
                user_id
            )
        )

        appointment = cursor.fetchone()

        if not appointment:
            return jsonify({
                "success": False,
                "message": "Appointment cannot be cancelled."
            }), 404

        cursor.execute(
            """
            UPDATE appointments
            SET status = 'cancelled'
            WHERE id = %s
            """,
            (appointment_id,)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Appointment cancelled successfully."
        }), 200

    except Exception as error:

        connection.rollback()

        print("Cancel appointment error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to cancel appointment."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# COMPLETE APPOINTMENT
# =========================================================

@patient_bp.route(
    "/appointments/<int:appointment_id>/complete",
    methods=["PUT"]
)
def complete_appointment(appointment_id):

    data = request.get_json() or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "User ID is required."
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
            SELECT a.id
            FROM appointments a
            JOIN patients p
                ON a.patient_id = p.id
            WHERE a.id = %s
              AND p.user_id = %s
              AND a.status IN ('accepted', 'completed')
            """,
            (appointment_id, user_id)
        )

        appointment = cursor.fetchone()

        if not appointment:
            return jsonify({
                "success": False,
                "message": "Accepted appointment not found."
            }), 404

        cursor.execute(
            """
            UPDATE appointments
            SET status = 'completed'
            WHERE id = %s
            """,
            (appointment_id,)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Consultation completed successfully."
        }), 200

    except Exception as error:
        connection.rollback()
        print("Complete appointment error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to complete appointment."
        }), 500

    finally:
        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET PATIENT MEDICAL RECORDS
# =========================================================

@patient_bp.route("/records/<int:user_id>", methods=["GET"])
def get_medical_records(user_id):

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
                mr.id,
                mr.record_type,
                mr.title,
                mr.description,
                mr.file_path,
                mr.created_at,

                u.full_name AS doctor_name,
                d.specialization

            FROM medical_records mr

            JOIN patients p
                ON mr.patient_id = p.id

            LEFT JOIN doctors d
                ON mr.doctor_id = d.id

            LEFT JOIN users u
                ON d.user_id = u.id

            WHERE p.user_id = %s

            ORDER BY mr.created_at DESC
            """,
            (user_id,)
        )

        records = cursor.fetchall()

        return jsonify({
            "success": True,
            "records": records
        }), 200

    except Exception as error:

        print("Medical records error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load medical records."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET CONSULTATION HISTORY
# =========================================================

@patient_bp.route("/consultations/<int:user_id>", methods=["GET"])
def get_consultations(user_id):

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
                c.id,
                c.appointment_id,
                c.symptoms,
                c.diagnosis,
                c.prescription,
                c.doctor_notes,
                c.consultation_date,

                u.full_name AS doctor_name,
                d.specialization

            FROM consultations c

            JOIN patients p
                ON c.patient_id = p.id

            JOIN doctors d
                ON c.doctor_id = d.id

            JOIN users u
                ON d.user_id = u.id

            WHERE p.user_id = %s

            ORDER BY c.consultation_date DESC
            """,
            (user_id,)
        )

        consultations = cursor.fetchall()

        return jsonify({
            "success": True,
            "consultations": consultations
        }), 200

    except Exception as error:

        print("Consultation history error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load consultation history."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# AI CHAT MESSAGE
# =========================================================

@patient_bp.route("/chat", methods=["POST"])
def chat():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    message = data.get("message", "").strip()

    if not user_id or not message:
        return jsonify({
            "success": False,
            "message": "User ID and message are required."
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

        # Find patient
        cursor.execute(
            """
            SELECT id
            FROM patients
            WHERE user_id = %s
            """,
            (user_id,)
        )

        patient = cursor.fetchone()

        if not patient:
            return jsonify({
                "success": False,
                "message": "Patient not found."
            }), 404

        patient_id = patient["id"]

        # Save patient message
        cursor.execute(
            """
            INSERT INTO chat_messages
            (patient_id, sender, message)
            VALUES (%s, 'patient', %s)
            """,
            (
                patient_id,
                message
            )
        )

        # Basic safe response for the project demo.
        ai_response = (
            "Thank you for sharing your concern. "
            "This AI chat is for general information only. "
            "It cannot diagnose medical conditions. "
            "For serious, worsening, or emergency symptoms, "
            "please contact a qualified healthcare professional "
            "or emergency service."
        )

        # Save AI response
        cursor.execute(
            """
            INSERT INTO chat_messages
            (patient_id, sender, message)
            VALUES (%s, 'ai', %s)
            """,
            (
                patient_id,
                ai_response
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "response": ai_response
        }), 200

    except Exception as error:

        connection.rollback()

        print("Chat error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to process chat message."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET CHAT HISTORY
# =========================================================

@patient_bp.route("/chat/<int:user_id>", methods=["GET"])
def get_chat_history(user_id):

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
                cm.id,
                cm.sender,
                cm.message,
                cm.created_at

            FROM chat_messages cm

            JOIN patients p
                ON cm.patient_id = p.id

            WHERE p.user_id = %s

            ORDER BY cm.created_at ASC
            """,
            (user_id,)
        )

        messages = cursor.fetchall()

        return jsonify({
            "success": True,
            "messages": messages
        }), 200

    except Exception as error:

        print("Chat history error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load chat history."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()