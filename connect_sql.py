import mysql.connector

def establish_sql_connection():
    # note: for testing purposes, run on localhost
    # db = mysql.connector.connect(
    #     host = "localhost",
    #     port = 1001,
    #     user = "root",
    #     password = "dsa3101",
    #     database = "secdb"
    # )
    # uncomment below for dockerised usage
    db = mysql.connector.connect(
        host = "database",
        user = "root",
        password = "dsa3101",
        database = "secdb"
        )

    cursor = db.cursor()
    return db, cursor