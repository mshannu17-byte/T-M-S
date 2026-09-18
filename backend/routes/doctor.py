# =========================================================
# CARELINE TELEMEDICINE SYSTEM
# Doctor Routes
# =========================================================

from flask import Blueprint, request, jsonify

from database import get_db_connection


doctor_bp = Blueprint("doctor", __name__)


# =========================================================
# GET DOCTOR PROFILE
# =========================================================

@doctor_bp.route("/profile/<int:user_id>", methods=["GET"])
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
                u.status,

                d.id AS doctor_id,
                d.specialization,
                d.qualification,
                d.experience,
                d.license_number,
                d.consultation_fee,
                d.about

            FROM users u

            JOIN doctors d
                ON u.id = d.user_id

            WHERE u.id = %s
              AND u.role = 'doctor'
            """,
            (user_id,)
        )

        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({
                "success": False,
                "message": "Doctor not found."
            }), 404

        return jsonify({
            "success": True,
            "doctor": doctor
        }), 200

    except Exception as error:

        print("Doctor profile error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load doctor profile."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# UPDATE DOCTOR PROFILE
# =========================================================

@doctor_bp.route("/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):

    data = request.get_json() or {}

    full_name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()

    specialization = data.get(
        "specialization",
        ""
    ).strip()

    qualification = data.get(
        "qualification",
        ""
    ).strip()

    experience = data.get(
        "experience",
        0
    )

    consultation_fee = data.get(
        "consultation_fee",
        0
    )

    about = data.get(
        "about",
        ""
    ).strip()

    if not full_name:
        return jsonify({
            "success": False,
            "message": "Full name is required."
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

        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE users
            SET full_name = %s,
                phone = %s
            WHERE id = %s
              AND role = 'doctor'
            """,
            (
                full_name,
                phone,
                user_id
            )
        )

        cursor.execute(
            """
            UPDATE doctors
            SET specialization = %s,
                qualification = %s,
                experience = %s,
                consultation_fee = %s,
                about = %s
            WHERE user_id = %s
            """,
            (
                specialization,
                qualification,
                experience,
                consultation_fee,
                about,
                user_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Doctor profile updated successfully."
        }), 200

    except Exception as error:

        connection.rollback()

        print("Doctor profile update error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to update doctor profile."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET APPOINTMENT REQUESTS
# =========================================================

@doctor_bp.route(
    "/appointments/<int:user_id>",
    methods=["GET"]
)
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

                p.id AS patient_id,
                pu.id AS patient_user_id,
                pu.full_name AS patient_name,
                pu.email AS patient_email,
                pu.phone AS patient_phone,

                p.date_of_birth,
                p.gender,
                p.blood_group,
                p.address

            FROM appointments a

            JOIN doctors d
                ON a.doctor_id = d.id

            JOIN patients p
                ON a.patient_id = p.id

            JOIN users pu
                ON p.user_id = pu.id

            WHERE d.user_id = %s

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

        print("Doctor appointments error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load appointments."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# ACCEPT APPOINTMENT
# =========================================================

@doctor_bp.route(
    "/appointments/<int:appointment_id>/accept",
    methods=["PUT"]
)
def accept_appointment(appointment_id):

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

            JOIN doctors d
                ON a.doctor_id = d.id

            WHERE a.id = %s
              AND d.user_id = %s
              AND a.status = 'pending'
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
                "message": "Appointment request not found."
            }), 404

        # Demo consultation link
        meeting_link = (
            f"/consultation.html?appointment_id="
            f"{appointment_id}"
        )

        cursor.execute(
            """
            UPDATE appointments
            SET status = 'accepted',
                meeting_link = %s
            WHERE id = %s
            """,
            (
                meeting_link,
                appointment_id
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Appointment accepted successfully.",
            "meeting_link": meeting_link
        }), 200

    except Exception as error:

        connection.rollback()

        print("Accept appointment error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to accept appointment."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# REJECT APPOINTMENT
# =========================================================

@doctor_bp.route(
    "/appointments/<int:appointment_id>/reject",
    methods=["PUT"]
)
def reject_appointment(appointment_id):

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

            JOIN doctors d
                ON a.doctor_id = d.id

            WHERE a.id = %s
              AND d.user_id = %s
              AND a.status = 'pending'
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
                "message": "Appointment request not found."
            }), 404

        cursor.execute(
            """
            UPDATE appointments
            SET status = 'rejected',
                meeting_link = NULL
            WHERE id = %s
            """,
            (appointment_id,)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Appointment rejected."
        }), 200

    except Exception as error:

        connection.rollback()

        print("Reject appointment error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to reject appointment."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# COMPLETE CONSULTATION
# =========================================================

@doctor_bp.route(
    "/consultations/complete",
    methods=["POST"]
)
def complete_consultation():

    data = request.get_json() or {}

    user_id = data.get("user_id")
    appointment_id = data.get("appointment_id")

    symptoms = data.get(
        "symptoms",
        ""
    ).strip()

    diagnosis = data.get(
        "diagnosis",
        ""
    ).strip()

    prescription = data.get(
        "prescription",
        ""
    ).strip()

    doctor_notes = data.get(
        "doctor_notes",
        ""
    ).strip()

    if not user_id or not appointment_id:
        return jsonify({
            "success": False,
            "message": "Doctor and appointment are required."
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

        # Verify doctor owns appointment
        cursor.execute(
            """
            SELECT
                a.id,
                a.patient_id,
                a.doctor_id

            FROM appointments a

            JOIN doctors d
                ON a.doctor_id = d.id

            WHERE a.id = %s
              AND d.user_id = %s
              AND a.status = 'accepted'
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
                "message": "Accepted appointment not found."
            }), 404

        # Create consultation record
        cursor.execute(
            """
            INSERT INTO consultations
            (
                appointment_id,
                patient_id,
                doctor_id,
                symptoms,
                diagnosis,
                prescription,
                doctor_notes
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                appointment_id,
                appointment["patient_id"],
                appointment["doctor_id"],
                symptoms,
                diagnosis,
                prescription,
                doctor_notes
            )
        )

        # Mark appointment as completed
        cursor.execute(
            """
            UPDATE appointments
            SET status = 'completed'
            WHERE id = %s
            """,
            (appointment_id,)
        )

        # Add digital medical record
        cursor.execute(
            """
            INSERT INTO medical_records
            (
                patient_id,
                doctor_id,
                record_type,
                title,
                description
            )
            VALUES
            (%s, %s, %s, %s, %s)
            """,
            (
                appointment["patient_id"],
                appointment["doctor_id"],
                "Consultation",
                "Doctor Consultation Record",
                diagnosis
            )
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Consultation completed successfully."
        }), 200

    except Exception as error:

        connection.rollback()

        print("Complete consultation error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to complete consultation."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET PATIENT DETAILS
# =========================================================

@doctor_bp.route(
    "/patient/<int:patient_id>",
    methods=["GET"]
)
def get_patient_details(patient_id):

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
                p.id AS patient_id,
                u.id AS user_id,
                u.full_name,
                u.email,
                u.phone,
                p.date_of_birth,
                p.gender,
                p.address,
                p.blood_group,
                p.emergency_contact

            FROM patients p

            JOIN users u
                ON p.user_id = u.id

            WHERE p.id = %s
            """,
            (patient_id,)
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

        print("Patient details error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load patient details."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET DOCTOR'S CONSULTATION HISTORY
# =========================================================

@doctor_bp.route(
    "/consultations/<int:user_id>",
    methods=["GET"]
)
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

                pu.full_name AS patient_name,
                pu.email AS patient_email

            FROM consultations c

            JOIN doctors d
                ON c.doctor_id = d.id

            JOIN patients p
                ON c.patient_id = p.id

            JOIN users pu
                ON p.user_id = pu.id

            WHERE d.user_id = %s

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

        print("Doctor consultation history error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load consultation history."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()