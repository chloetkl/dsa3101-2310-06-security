import mysql.connector

def establish_sql_connection():
    # note: for testing purposes, run on localhost
    db = mysql.connector.connect(
        host = "localhost",
        port = 1001,
        user = "root",
        password = "dsa3101",
        database = "secdb"
    )
    # uncomment below for dockerised usage
    db = mysql.connector.connect(
        host = "database",
        user = "root",
        password = "dsa3101",
        database = "secdb"
        )

    cursor = db.cursor()
    return db, cursor

def get_location_id(building):
    db, cursor = establish_sql_connection()
    building = building.upper()
    query = f"SELECT id FROM Incident_locations WHERE location = '{building}'"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else None

def get_incident_type_id(incident_type):
    db, cursor = establish_sql_connection()
    incident_type = incident_type.upper()
    query = f"SELECT id FROM Incident_types WHERE type = '{incident_type}'"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else None
