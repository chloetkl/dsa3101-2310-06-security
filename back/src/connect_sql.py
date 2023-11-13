import mysql.connector
import time

def establish_sql_connection(max_retries=10, retry_interval=10):
    db = None
    cursor = None
    retries = 0
    while retries < max_retries:
        try:
            # note: for testing purposes, run on localhost
            db = mysql.connector.connect(
                host = "localhost",
                port = 1001,
                user = "root",
                password = "dsa3101",
                database = "secdb"
                )

            # uncomment below for dockerised usage
            # db = mysql.connector.connect(
            #     host="database",
            #     user="root",
            #     password="dsa3101",
            #     database="secdb"
            # )

            cursor = db.cursor()
            break  # If connection succeeds, exit the loop
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            print(f"Attempt {retries + 1}: Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)  # Wait for a few seconds before retrying
            retries += 1

    if db is None:
        print("Failed to establish a database connection.")
    return db,cursor
