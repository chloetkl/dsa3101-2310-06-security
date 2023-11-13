import mysql.connector
from connect_sql import establish_sql_connection
import pandas as pd
import bcrypt
import time

# user_roles
def add_user_roles(filepath):

    try: 
        ## establish connection
        db, cursor = establish_sql_connection()
        if db is None:
            print("add_user_roles | Failed to establish a database connection.")
            return
        # print(f'add_user_roles | db established: {db.is_connected()}')

        ## read users from path and change to QUERY format
        file = open(filepath, 'r')
        values = file.read().split("\n")
        values = list(map(lambda x: f'(\'{x}\')',values))
        values = ", ".join(values)
        query = f'INSERT INTO User_roles(role) VALUES {values};'

        cursor.execute(query)
        db.commit()
        print(f"add_user_roles | User roles added: {cursor.rowcount}")

        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"add_user_roles | database error: {err}")

# ADD incident_location_groups and incident_locations
def add_incident_locations(filepath):
    try: 
        ## establish connection
        db, cursor = establish_sql_connection()
        if db is None:
            print("add_incident_locations | Failed to establish a database connection.")
            return

        ## read incident locations from CSV file
        df = pd.read_csv(filepath)
        unique_locations = df['Location'].unique()

        # Populate Incident_location_groups table with unique locations
        location_groups_added = 0
        for location in unique_locations:
            try:
                query = f"INSERT INTO Incident_location_groups(location_group) VALUES ('{location}')"
                cursor.execute(query)
                db.commit()
                location_groups_added += 1
            except mysql.connector.Error as err:
                print(f"add_incident_locations | Error adding location group: {err}")
        print(f"add_incident_locations | Location Groups added: {location_groups_added}")
        # Map CSV columns to MySQL columns and insert data into Incident_location table
        locations_added = 0
        for index, row in df.iterrows():
            building = row['Buildings']
            location = row['Location']
            latitude = row['Latitude']
            longitude = row['Longitude']
            residence = row['Residence']

            # Get location_group_id from Incident_location_groups table
            query = f"SELECT id FROM Incident_location_groups WHERE location_group = '{location}'"
            cursor.execute(query)
            location_group_id = cursor.fetchone()[0]

            # Insert data into Incident_location table
            try:
                query = f"INSERT INTO Incident_locations(location, location_group_id, latitude, longitude, is_residence) VALUES ('{building}', {location_group_id}, {latitude}, {longitude}, {residence})"
                cursor.execute(query)
                db.commit()
                locations_added += 1
            except mysql.connector.Error as err:
                print(f"add_incident_locations | Error adding incident location: {err}")

        print(f"add_incident_locations | Locations added: {locations_added}")
        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"add_incident_locations | database error: {err}")


# ADD incident_types


def add_incident_types(filepath):
    try: 
        ## establish connection
        db, cursor = establish_sql_connection()
        if db is None:
            print("add_incident_types | Failed to establish a database connection.")
            return
        # print(f'add_incident_types | db established: {db.is_connected()}')

        ## read incident types from path
        with open(filepath, 'r') as file:
            lines = file.readlines()
            values = [tuple(line.strip().split(", ")) for line in lines]

        # Format values for the query
        formatted_values = ", ".join([f"('{type}', '{priority}')" for type, priority in values])

        query = f'INSERT INTO Incident_types(type, default_priority) VALUES {formatted_values};'

        cursor.execute(query)
        db.commit()
        print(f"add_incident_types | Incident types added: {cursor.rowcount}")

        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"add_incident_types | database error: {err}")


## perform default adds
print("Perform default adds")
add_user_roles('./populate/User_roles.txt')
add_incident_types('./populate/Incident_types.txt')
add_incident_locations("./populate/Incident_location.csv")

## ADD user
def add_user(username, password, role, email=None):
    try: 
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

    except mysql.connector.Error as err:
        print(f"add_user | database error: {err}")

add_user("sec1", "sec1", "security", email=None)
add_user("sec2", "sec2", "security", email=None)
add_user("sec3", "sec3", "security", email=None)
add_user("sec4", "sec4", "security", email=None)
add_user("sec5", "sec5", "security", email=None)
add_user("analytics1", "analytics1", "analytics", email=None)
add_user("analytics2", "analytics2", "analytics", email=None)
add_user("analytics3", "analytics3", "analytics", email=None)

## AUTHENTICATE user
def authenticate(user,password):
    try:
        db, cursor = establish_sql_connection()
        if db is None:
            print("add_user_roles | Failed to establish a database connection.")
            return
        query = f"SELECT hash from Users where username = \'{user}\'"
        cursor.execute(query)
        hash_stored = cursor.fetchall()

        ## Check username
        if len(hash_stored) == 0:
            print("authenticate | User not found")
            return False
        
        ## Pull shash salt
        hash_stored = hash_stored[0][0]
        query = f"SELECT salt from Users where username = \'{user}\'"
        cursor.execute(query)
        salt = cursor.fetchone()[0]
        hash_entered = bcrypt.hashpw(password.encode('utf-8'),salt.encode('utf-8'))

        cursor.close()
        db.close()
    
    except mysql.connector.Error as err:
        print(f"authenticate | database error: {err}")


    ## Check results
    authenticated = bcrypt.checkpw(password.encode('utf-8'),hash_stored.encode('utf-8'))
    
    return authenticated



## Checks
# db = establish_sql_connection()
# cursor = db.cursor()
# query = "SELECT * from User_roles"
# cursor.execute(query)
# User_roles = cursor.fetchall()
# print(f'User_roles: {User_roles}')
# cursor.close()
# db.close()
