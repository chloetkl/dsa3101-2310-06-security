import mysql.connector


def establish_sql_connection():
    db = mysql.connector.connect(
        host = "database",
        user = "root",
        password = "dsa3101",
        database = "secdb"
        )
    return db