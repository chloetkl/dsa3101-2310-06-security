import mysql.connector
import pandas as pd
import bcrypt

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

# user_roles
def add_user_roles(filepath):

    try: 
        ## establish connection
        db = establish_sql_connection()
        cursor = db.cursor()
        print(f'db established: {db.is_connected()}')

        ## read users from path and change to QUERY format
        file = open(filepath, 'r')
        values = file.read().split("\n")
        values = list(map(lambda x: f'(\'{x}\')',values))
        values = ", ".join(values)
        query = f'INSERT INTO User_roles(role) VALUES {values};'

        cursor.execute(query)
        db.commit()
        print(f"Number of rows affected: {cursor.rowcount}")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        cursor.close()
        db.close()

# add users
def add_user(username, password, role, email=None):
    try: 
        ## establish connection
        db = establish_sql_connection()
        cursor = db.cursor()
        print(f'db established: {db.is_connected()}')

        ## generate hash and salt
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(password.encode('utf-8'), salt)

        ## get role id
        query = f'SELECT id FROM User_roles \
                                 where role = \'{role}\';'
        cursor.execute(query)
        role_id=cursor.fetchall()[0][0]

        ## insert query
        query = f"\
            INSERT INTO Users\
            (email, username, role_id, salt, hash)\
            VALUES (\'{email}\', \'{username}\', {role_id}, \'{salt.decode('utf-8')}\', \'{hash.decode('utf-8')}\')"
        cursor.execute(query)
        db.commit()

    except mysql.connector.Error as err:
        print(f"Database error: {err}")

    finally:
        cursor.close()
        db.close()

# authenticate user
def authenticate(user,password):
    try:
        db = establish_sql_connection()
        cursor = db.cursor()
        query = f"SELECT hash from Users where username = \'{user}\'"
        cursor.execute(query)
        hash_stored = cursor.fetchall()

        ## Check username
        if len(hash_stored) == 0:
            print("User not found")
            return False
        
        ## Check password
        hash_stored = hash_stored[0][0]
        query = f"SELECT salt from Users where username = \'{user}\'"
        cursor.execute(query)
        salt = cursor.fetchall()[0][0]
        hash_entered = bcrypt.hashpw(password.encode('utf-8'),salt.encode('utf-8'))
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    
    finally:
        cursor.close()
        db.close()

    ## Check results
    authenticated = (hash_stored == hash_entered.decode('utf-8'))
    
    return authenticated

# incident_location_groups


# incident_location


# incident_types

## perform adds
add_user_roles('User_roles.txt')



## Checks
db = establish_sql_connection()
cursor = db.cursor()
query = "SELECT * from User_roles"
cursor.execute(query)
User_roles = cursor.fetchall()
print(f'User_roles: {User_roles}')
cursor.close()
db.close()


# cursor = db.cursor()
#     query = "INSERT INTO\
#         FROM customers\
#             ORDER BY customer_id DESC"
#     cursor.execute(query)
#     result = cursor.fetchall()


