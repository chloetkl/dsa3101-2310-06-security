import mysql.connector
import pandas as pd
import bcrypt
import time


def establish_sql_connection(max_retries=10, retry_interval=5):
    db = None
    cursor = None
    retries = 0
    while retries < max_retries:
        try:
            # note: for testing purposes, run on localhost
            # db = mysql.connector.connect(
            #     host = "localhost",
            #     port = 1001,
            #     user = "root",
            #     password = "dsa3101",
            #     database = "secdb"
            #     )

            # uncomment below for dockerised usage
            db = mysql.connector.connect(
                host="database",
                user="root",
                password="dsa3101",
                database="secdb"
            )
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
        

# ADD incidents from csv
def add_incidents_from_csv(filepath):
    try: 
        ## establish connection
        db, cursor = establish_sql_connection()
        if db is None:
            print("add_incidents_from_csv | Failed to establish a database connection.")
            return
        # print(f'add_incidents_from_csv | db established: {db.is_connected()}')

        ## read unique Incidents
        df = pd.read_csv(filepath)
        unique_incidents= df[['IncidentID','Description','Building','Incidents']].drop_duplicates()
        unique_incidents = unique_incidents.rename(columns={
            'Building': 'Location',
            'Incidents': 'Incident Type'
        })

        incidents_added = 0
        duplicated = 0
        # Populate Incidents table with unique Incidents
        for index, row in unique_incidents.iterrows():
            try:
                # id
                id = row['IncidentID']
                #description
                description = row['Description']
                #location_id
                location = row['Location']
                query = f"SELECT id FROM Incident_locations WHERE location = '{location}'"
                cursor.execute(query)
                location_id = cursor.fetchone()[0]
                #incident_type_id
                incident_type = row['Incident Type']
                query = f"SELECT id FROM Incident_types WHERE type = '{incident_type}'"
                cursor.execute(query)
                incident_type_id = cursor.fetchone()[0]
                query = f"INSERT INTO Incidents(id,description,location_id,incident_type_id) VALUES \
                    ('{id}','{description}','{location_id}','{incident_type_id}')"
                cursor.execute(query)
                incidents_added += 1
            except mysql.connector.Error as err:
                if 'Duplicate' in str(err):
                    duplicated += 1
                else:
                    print(f"add_incidents_from_csv | Error: {err}")
        
        print(f"add_incidents_from_csv | Unique incidents added: {incidents_added}")
        print(f"add_incidents_from_csv | Incidents already in database: {incidents_added}")
        db.commit()

        ## read logs
        df['Time'] = pd.to_datetime(df['Time'],format="%d/%m/%y %H:%M")
        incident_logs = df[['IncidentID','Status','Priority','Time','User']].drop_duplicates()
        logs_added = 0
        duplicated = 0
        for index, row in incident_logs.iterrows():
            try:
                id = row['IncidentID']
                status = row['Status']
                priority = row['Priority']
                time = row['Time']
                user = row['User']
                query = f"SELECT id FROM Users WHERE username = '{user}'"
                cursor.execute(query)
                user_id = cursor.fetchone()[0]
                notes = ""

                ## Insert
                query = f"INSERT INTO Incident_logs(incident_id,status, priority,time,user_id,notes) VALUES \
                    ('{id}','{status}','{priority}','{time}','{user_id}','{notes}')"
                cursor.execute(query)
                logs_added +=1
            except mysql.connector.Error as err:
                if 'Duplicate' in str(err):
                    duplicated += 1
                else:
                    print(f"add_incidents_from_csv | Error adding log of incident {id} at {time} to Incidents: {err}")
        
        print(f"add_incidents_from_csv | Incident logs added: {logs_added}")
        print(f"add_incidents_from_csv | Incident logs already in database: {duplicated}")
        db.commit()
        
        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        print(f"add_incident_locations | database error: {err}")

add_incidents_from_csv("./add_incidents/data_v0.4(back).csv")


## Checks
# db = establish_sql_connection()
# cursor = db.cursor()
# query = "SELECT * from User_roles"
# cursor.execute(query)
# User_roles = cursor.fetchall()
# print(f'User_roles: {User_roles}')
# cursor.close()
# db.close()
