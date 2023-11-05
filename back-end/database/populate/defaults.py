import mysql.connector
import pandas as pd

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
    # db = mysql.connector.connect(
    #     host = "database",
    #     user = "root",
    #     password = "dsa3101",
    #     database = "secdb"
    #     )
    return db


def add_user_roles(filepath):
    
    db = establish_sql_connection()
    cursor = db.cursor()
    print(f'db established: {db.is_connected()}')

    file = open(filepath, 'r')
    values = file.read().split("\n")
    values = list(map(lambda x: f'(\'{x}\')',values))
    values = ", ".join(values)
    query = f'INSERT INTO User_roles(role) VALUES {values};'

    cursor.execute(query)
    db.commit()
    print(f"Number of rows affected: {cursor.rowcount}")

    cursor.close()
    db.close()

    return query

add_user_roles('User_roles.txt')

## Checks
db = establish_sql_connection()
cursor = db.cursor()
query = "SELECT * from User_roles"
cursor.execute(query)
result = cursor.fetchall()
print(result)
cursor.close()
db.close()


# cursor = db.cursor()
#     query = "INSERT INTO\
#         FROM customers\
#             ORDER BY customer_id DESC"
#     cursor.execute(query)
#     result = cursor.fetchall()


