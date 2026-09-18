# =========================================================
# CARELINE TELEMEDICINE SYSTEM
# Admin Routes
# =========================================================

from flask import Blueprint, request, jsonify

from database import get_db_connection


admin_bp = Blueprint("admin", __name__)


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin_bp.route("/dashboard", methods=["GET"])
def dashboard():

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        # Total patients
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE role = 'patient'
            """
        )

        total_patients = cursor.fetchone()["total"]

        # Total approved doctors
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE role = 'doctor'
              AND status = 'active'
            """
        )

        total_doctors = cursor.fetchone()["total"]

        # Pending doctors
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE role = 'doctor'
              AND status = 'pending'
            """
        )

        pending_doctors = cursor.fetchone()["total"]

        # Total appointments
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM appointments
            """
        )

        total_appointments = cursor.fetchone()["total"]

        # Completed consultations
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM appointments
            WHERE status = 'completed'
            """
        )

        completed_consultations = cursor.fetchone()["total"]

        return jsonify({
            "success": True,
            "statistics": {
                "total_patients": total_patients,
                "total_doctors": total_doctors,
                "pending_doctors": pending_doctors,
                "total_appointments": total_appointments,
                "completed_consultations": completed_consultations
            }
        }), 200

    except Exception as error:

        print("Admin dashboard error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load dashboard."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET PENDING DOCTOR REQUESTS
# =========================================================

@admin_bp.route(
    "/doctors/pending",
    methods=["GET"]
)
def pending_doctors():

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
                u.created_at,

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

            WHERE u.role = 'doctor'
              AND u.status = 'pending'

            ORDER BY u.created_at DESC
            """
        )

        doctors = cursor.fetchall()

        return jsonify({
            "success": True,
            "doctors": doctors
        }), 200

    except Exception as error:

        print("Pending doctors error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load pending doctors."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# APPROVE DOCTOR
# =========================================================

@admin_bp.route(
    "/doctors/<int:doctor_id>/approve",
    methods=["PUT"]
)
def approve_doctor(doctor_id):

    connection = get_db_connection()

    if connection is None:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        }), 500

    cursor = None

    try:

        cursor = connection.cursor(dictionary=True)

        # Check doctor
        cursor.execute(
            """
            SELECT
                d.id,
                d.user_id,
                u.status
            FROM doctors d
            JOIN users u
                ON d.user_id = u.id
            WHERE d.id = %s
              AND u.role = 'doctor'
            """,
            (doctor_id,)
        )

        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({
                "success": False,
                "message": "Doctor not found."
            }), 404

        if doctor["status"] == "active":
            return jsonify({
                "success": False,
                "message": "Doctor is already approved."
            }), 400

        cursor.execute(
            """
            UPDATE users
            SET status = 'active'
            WHERE id = %s
              AND role = 'doctor'
            """,
            (doctor["user_id"],)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Doctor approved successfully."
        }), 200

    except Exception as error:

        connection.rollback()

        print("Approve doctor error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to approve doctor."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# REJECT DOCTOR
# =========================================================

@admin_bp.route(
    "/doctors/<int:doctor_id>/reject",
    methods=["PUT"]
)
def reject_doctor(doctor_id):

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
                d.id,
                d.user_id,
                u.status

            FROM doctors d

            JOIN users u
                ON d.user_id = u.id

            WHERE d.id = %s
              AND u.role = 'doctor'
            """,
            (doctor_id,)
        )

        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({
                "success": False,
                "message": "Doctor not found."
            }), 404

        cursor.execute(
            """
            UPDATE users
            SET status = 'rejected'
            WHERE id = %s
              AND role = 'doctor'
            """,
            (doctor["user_id"],)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Doctor registration rejected."
        }), 200

    except Exception as error:

        connection.rollback()

        print("Reject doctor error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to reject doctor."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET ALL DOCTORS
# =========================================================

@admin_bp.route(
    "/doctors",
    methods=["GET"]
)
def get_doctors():

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
                u.created_at,

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

            WHERE u.role = 'doctor'

            ORDER BY u.created_at DESC
            """
        )

        doctors = cursor.fetchall()

        return jsonify({
            "success": True,
            "doctors": doctors
        }), 200

    except Exception as error:

        print("All doctors error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load doctors."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# DELETE / DEACTIVATE DOCTOR
# =========================================================

@admin_bp.route(
    "/doctors/<int:doctor_id>",
    methods=["DELETE"]
)
def delete_doctor(doctor_id):

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
                d.id,
                d.user_id
            FROM doctors d
            JOIN users u
                ON d.user_id = u.id
            WHERE d.id = %s
              AND u.role = 'doctor'
            """,
            (doctor_id,)
        )

        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({
                "success": False,
                "message": "Doctor not found."
            }), 404

        # We deactivate instead of permanently deleting.
        # This protects existing appointment and medical
        # record relationships.

        cursor.execute(
            """
            UPDATE users
            SET status = 'inactive'
            WHERE id = %s
              AND role = 'doctor'
            """,
            (doctor["user_id"],)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Doctor deactivated successfully."
        }), 200

    except Exception as error:

        connection.rollback()

        print("Delete doctor error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to deactivate doctor."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# REACTIVATE DOCTOR
# =========================================================

@admin_bp.route(
    "/doctors/<int:doctor_id>/reactivate",
    methods=["PUT"]
)
def reactivate_doctor(doctor_id):

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
                d.id,
                d.user_id,
                u.status

            FROM doctors d

            JOIN users u
                ON d.user_id = u.id

            WHERE d.id = %s
              AND u.role = 'doctor'
            """,
            (doctor_id,)
        )

        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({
                "success": False,
                "message": "Doctor not found."
            }), 404

        cursor.execute(
            """
            UPDATE users
            SET status = 'active'
            WHERE id = %s
              AND role = 'doctor'
            """,
            (doctor["user_id"],)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Doctor reactivated successfully."
        }), 200

    except Exception as error:

        connection.rollback()

        print("Reactivate doctor error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to reactivate doctor."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET ALL PATIENTS
# =========================================================

@admin_bp.route(
    "/patients",
    methods=["GET"]
)
def get_patients():

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
                p.id AS patient_id,
                u.full_name,
                u.email,
                u.phone,
                u.status,
                p.date_of_birth,
                p.gender,
                p.address,
                p.blood_group,
                p.emergency_contact,
                u.created_at

            FROM users u

            JOIN patients p
                ON u.id = p.user_id

            WHERE u.role = 'patient'

            ORDER BY u.created_at DESC
            """
        )

        patients = cursor.fetchall()

        return jsonify({
            "success": True,
            "patients": patients
        }), 200

    except Exception as error:

        print("All patients error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load patients."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()


# =========================================================
# GET ALL APPOINTMENTS
# =========================================================

@admin_bp.route(
    "/appointments",
    methods=["GET"]
)
def get_appointments():

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

                pu.full_name AS patient_name,
                pu.email AS patient_email,

                du.full_name AS doctor_name,
                d.specialization

            FROM appointments a

            JOIN patients p
                ON a.patient_id = p.id

            JOIN users pu
                ON p.user_id = pu.id

            JOIN doctors d
                ON a.doctor_id = d.id

            JOIN users du
                ON d.user_id = du.id

            ORDER BY
                a.appointment_date DESC,
                a.appointment_time DESC
            """
        )

        appointments = cursor.fetchall()

        return jsonify({
            "success": True,
            "appointments": appointments
        }), 200

    except Exception as error:

        print("All appointments error:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load appointments."
        }), 500

    finally:

        if cursor:
            cursor.close()

        connection.close()