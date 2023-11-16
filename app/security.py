from functools import wraps
from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from flask_login import login_required, current_user

import pandas as pd
from datetime import datetime

from connect_sql import establish_sql_connection, get_location_id, get_incident_type_id
from back.analytics.map_pin import generate_map_points

security_bp = Blueprint('security', __name__)

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.is_authenticated and current_user.role == required_role:
                return func(*args, **kwargs)
            else:
                return f"Unauthorized, page only accessible to {required_role}", 403  # Adjust the response accordingly
        return wrapper
    return decorator

## Security Page
@security_bp.route('/security', methods=['GET'])
@login_required
@role_required('security')
def security():
    user_id = current_user.id
    print(f"User {user_id} is authenticated")

    try:
        db,cursor = establish_sql_connection()
        query = f'SELECT Incident_logs.incident_id,\
            Incidents.description,\
            Incident_logs.priority,\
            Incident_types.type,\
            Incident_location_groups.location_group,\
            Incident_locations.location,\
            Incident_locations.latitude,\
            Incident_locations.longitude,\
            Users.username,\
            Incident_logs.time,\
            Incident_logs.status\
            FROM Incident_logs\
            LEFT JOIN Incidents ON Incident_logs.incident_id = Incidents.id\
            LEFT JOIN Incident_locations ON Incidents.location_id = Incident_locations.id\
            LEFT JOIN Incident_location_groups ON Incident_locations.location_group_id = Incident_location_groups.id\
            LEFT JOIN Incident_types ON Incidents.incident_type_id = Incident_types.id\
            LEFT JOIN Users ON Incident_logs.user_id = Users.id\
            ORDER BY Incident_logs.time DESC;'
        cursor.execute(query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        data = pd.DataFrame(result, columns = columns)

        # Grouping by specified columns and aggregating time column
        data = data.groupby(['incident_id', 'description', 'priority', 'type', 'location_group',
                                        'location', 'latitude', 'longitude']).agg(
                                            FirstUpdate=('time', 'min'), LatestUpdate=('time', 'max'),
                                            username=('username', 'first'), 
                                            status=('status', 'first') 
                                            ).reset_index() 
        data = data.sort_values('LatestUpdate', ascending=False)
        now = datetime.now()
        data = data[data['LatestUpdate'] <= now]
        data.rename(columns={'incident_id': 'IncidentID', 'description':'Description','priority': 'Priority', 
                            'type':'Incidents', 'location_group':'Location', 'location':'Building', 
                            'latitude':'Latitude', 'longitude':'Longitude', 'username':'User', 
                            'time': 'LatestUpdate', 'status':'Status'}, inplace=True)
        data['FirstUpdate'] = pd.to_datetime(data['FirstUpdate'])
        data['LatestUpdate'] = pd.to_datetime(data['LatestUpdate'])


        data = data[['IncidentID', 'Description', 'Priority', 'Incidents', 'Location', 'Building', 'Latitude', 'Longitude', 'User', 'FirstUpdate', 'LatestUpdate', 'Status']]

        
        data['FirstUpdate'] = pd.to_datetime(data['FirstUpdate'])
        data['Date'] = data['FirstUpdate'].dt.date
        data['Time'] = data['FirstUpdate'].dt.time
        data.rename(columns={'IncidentID': 'Incident ID',
                'Incidents': 'Incident Type',
            'User': 'User Added'}, inplace=True)
        data = data[['Incident ID','Description','Date','Time',
                'Incident Type','Location','Building','Status','Priority',
                'User Added','Latitude','Longitude'
                ]]
        data_dict = data.to_dict(orient='records')

        return render_template('security.html', data=data_dict), 200
    
    except Exception as e:
        return jsonify({'error': e}), 500
    

@security_bp.route('/security/update-incident', methods=['POST'])
@login_required
@role_required('security')
def update_incident():
    try:
        db,cursor = establish_sql_connection()

        incident_id = request.form['incident_id']
        status = request.form['status']
        priority = request.form['priority']
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        notes = ""
        user_id = current_user.id

        query = f"INSERT INTO Incident_logs(incident_id, status, priority, time, user_id, notes) VALUES\
                ('{incident_id}', '{status}', '{priority}', '{time}', '{user_id}', '{notes}')"
        cursor.execute(query)
        db.commit()
        return jsonify({'message': f'Status of {incident_id} has changed to {status}'}), 200
        

    except Exception as e:
        db.rollback()
        return jsonify({'error': f'Failed to add data due to {e}'}), 500
    
    finally:
        cursor.close()
        db.close()

@security_bp.route('/security/generate-map-pin', methods=['GET'])
@login_required
@role_required('security')
def map_pin_generation():
    try:
        return generate_map_points(), 200
    except Exception as e:
        error_message = f"Error generating map pins: {e}"
        return jsonify({'error': error_message}), 500

@security_bp.route('/security/add-incident-report', methods=['POST'])
@login_required
@role_required('security')
def add_incident_report():
    user_id = current_user.id
    print(f"User {user_id} is authenticated")
    try:
        new_report = {
            'Description': request.form['description'],
            'Incident Type': request.form['type'],
            'Datetime': request.form['datetime'],
            'Priority': request.form['priority'],
            'Location': request.form['building'],
            'Status': request.form['status'],
        }

        db,cursor = establish_sql_connection()

        ## Add incident
        description = new_report['Description']
        location_id = get_location_id(new_report['Location'])
        incident_type_id = get_incident_type_id(new_report['Incident Type'])
        query = f"INSERT INTO Incidents (description, location_id, incident_type_id) \
            VALUES ('{description}', '{location_id}', '{incident_type_id}')"
        cursor.execute(query)
        db.commit()

        ## Add incident logs(s)
        incident_id = cursor.lastrowid
        ## Add both open and close logs if new incident is close
        status = new_report['Status']
        priority = new_report['Priority']
        time = new_report['Datetime']
        notes = ""

        ## Add open log if new incident is open
        if status == 'Close':
            query = f"INSERT INTO Incident_logs(incident_id,status, priority,time,user_id,notes) VALUES \
                    ('{incident_id}','Open','{priority}','{time}','{user_id}','{notes}')"
            cursor.execute(query)
            db.commit()
            query = f"INSERT INTO Incident_logs(incident_id,status, priority,time,user_id,notes) VALUES \
                    ('{incident_id}','Close','{priority}','{time}','{user_id}','{notes}')"
            cursor.execute(query)
            db.commit()
        else:
            query = f"INSERT INTO Incident_logs(incident_id,status, priority,time,user_id,notes) VALUES \
                    ('{incident_id}','{status}','{priority}','{time}','{user_id}','{notes}')"
            cursor.execute(query)
            db.commit()

        ## success
        return jsonify({'message': f'New incident added successfully. Incident code: {incident_id}'}), 200

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {e}")
        db.rollback()  # Rollback the changes in case of an error
        return jsonify({'error': f'Failed to add data due to {e}'}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()