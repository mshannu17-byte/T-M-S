# =========================================================
# CARELINE TELEMEDICINE SYSTEM
# MySQL Database Connection
# =========================================================

import mysql.connector
from mysql.connector import Error

from config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
    DB_PORT
)


def get_db_connection():
    """
    Creates and returns a MySQL database connection.
    """

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )

        if connection.is_connected():
            return connection

    except Error as error:
        print(f"Database connection error: {error}")

    return None


def execute_query(query, params=None):
    """
    Executes INSERT, UPDATE, or DELETE queries.
    """

    connection = get_db_connection()

    if connection is None:
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(query, params or ())
        connection.commit()

        return True

    except Error as error:
        print(f"Query execution error: {error}")
        connection.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        connection.close()


def fetch_one(query, params=None):
    """
    Fetches one record from the database.
    """

    connection = get_db_connection()

    if connection is None:
        return None

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params or ())

        return cursor.fetchone()

    except Error as error:
        print(f"Fetch error: {error}")

        return None

    finally:
        if cursor:
            cursor.close()

        connection.close()


def fetch_all(query, params=None):
    """
    Fetches multiple records from the database.
    """

    connection = get_db_connection()

    if connection is None:
        return []

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(query, params or ())

        return cursor.fetchall()

    except Error as error:
        print(f"Fetch error: {error}")

        return []

    finally:
        if cursor:
            cursor.close()

        connection.close()