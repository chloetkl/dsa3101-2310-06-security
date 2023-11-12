import mysql.connector
import pandas as pd
import bcrypt
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


## ADD user
def add_user(username, password, role, email=None):
    
    ## establish connection
    db, cursor = establish_sql_connection()
    if db is None:
        print("add_user_roles | Failed to establish a database connection.")
        return
    # print(f'add_user | db established: {db.is_connected()}')

    ## generate hash and salt
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    ## get role id
    query = f'SELECT id FROM User_roles \
                                where role = \'{role}\';'
    cursor.execute(query)
    role_id=cursor.fetchone()[0]

    ## insert query
    query = f"\
        INSERT INTO Users\
        (email, username, role_id, salt, hash)\
        VALUES (\'{email}\', \'{username}\', {role_id}, \'{salt.decode('utf-8')}\', \'{hash.decode('utf-8')}\')"
    cursor.execute(query)
    db.commit()
    print(f"add_user | User added: {username}")

    cursor.close()
    db.close()

## AUTHENTICATE user
def authenticate(user,password):
    authenticated = False
    user_role = None

    db, cursor = establish_sql_connection()
    query = f"SELECT hash from Users where username = \'{user}\'"
    cursor.execute(query)
    hash_stored = cursor.fetchall()

    ## Check username
    if len(hash_stored) == 0:
        print("authenticate | User not found")
        return False
    
    ## Pull hash salt
    hash_stored = hash_stored[0][0]
    query = f"SELECT salt from Users where username = \'{user}\'"
    cursor.execute(query)
    salt = cursor.fetchone()[0]
    hash_entered = bcrypt.hashpw(password.encode('utf-8'),salt.encode('utf-8'))

    ## check results and role
    authenticated = bcrypt.checkpw(password.encode('utf-8'),hash_stored.encode('utf-8'))
    if authenticated:
        query = f"SELECT User_roles.role \
            FROM Users \
            LEFT JOIN User_roles ON Users.id = User_roles.id\
                WHERE Users.username = '{user}';"
        cursor.execute(query)
        user_role = cursor.fetchone()[0]

    cursor.close()
    db.close()
    
    return authenticated, user_role

print(authenticate("sec1","sec1")) ## Should be (True, security)
print(authenticate("sec1","random")) ## Should be (False, None)
print(authenticate("sec2","random")) ## Should be (False, None)